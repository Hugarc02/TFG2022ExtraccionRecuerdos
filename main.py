import PySimpleGUI as sg
import traceback
import google
import neo4j.exceptions
from transcribe import transcribeAudio, uploadAudio
from graph_queries import extractGraphs, submitQueries
import gui_aux as ga

sg.theme("BlueMono")
tab1 = [
    [sg.Radio('Video', 'radio1', default = True, key = '-VIDEO-'), sg.Radio('Audio', 'radio1')],
    [sg.Text('Seleccionar archivo: ')], 
    [sg.Input(key='-FILE-'), sg.FileBrowse(key='-FILEB-')],
    [sg.Text('Seleccionar clave cuenta de servicio: ')],
    [sg.Input(key='-KEY-', tooltip = 'JSON'), sg.FileBrowse(key='-KEYB-')],
    [sg.Text('Insertar bucket de Google Cloud Storage: ')],
    [sg.Input('bucket-tfg-2021-2022', key='-BUCKET-')],
    [sg.Button('Obtener transcripción', key='-ATRANS-')],
]


tab2 = [
    [sg.Text('Insertar transcripción: ')],
    [sg.Multiline(size = (50,10), key = '-INSERT-')],
    [sg.Button('Subir transcripción', key='-MTRANS-')]
]
col1 = sg.Column([[sg.TabGroup([[sg.Tab('Transcripción Automática', tab1), 
                                 sg.Tab('Manual', tab2, key = '-TAB1-')]])],
                  [sg.Text('Seleccionar guión: ')], 
                  [sg.Input(key='-SCRIPT-'), sg.FileBrowse(key='-SCRIPT-')],
                  [sg.Text('Usuario Neo4j: ', size=(15,1)), sg.Text('Contraseña Neo4j: ', size=(15,1)), sg.Text('Puerto Neo4j: ', size=(15,1))], 
                  [sg.Input(key='-USER-', size=(17,1)), sg.Input(key='-PWD-', size=(17,1)), sg.Input(key='-PORT-', size=(16,1)),],
                  [sg.Button('Extraer Grafos', key='-EXTRACT-', disabled=True)],
                 ])
col2 = sg.Column([[sg.Frame(
    'Output:',[[sg.Multiline(key='-OUTPUT-', size=(60,22))]
],)]])

col3 = sg.Column([[sg.Frame('Opciones de salida:',[
    [ sg.Checkbox('Subir a neo4j', default=True, key='-NEO4J-', size=(9,1)),
     sg.Checkbox('Mostrar segmentos', key='-SEGMENTS-',  size=(13,1)),
    sg.Checkbox('Mostrar consultas', key='-QUERIES-',  size=(13,1))]
],)]])

col4 = sg.Column([[sg.Frame('Estatus del sistema:', [
    [sg.Text(background_color = 'white', key = '-STATUS-', size=(30,1))]
],)]])

layout = [[sg.Text('Extracción de Recuerdos de Videos ', font='Default 20'), sg.Column([[sg.Button('Ayuda', key='-HELP-')]], element_justification='right', expand_x=True)],
          [col1, col2],
          [col3, col4]]
###Building Window
window = sg.Window('Extracción de recuerdos de videos', layout)

while True:
    try:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            break
        # Manual transcription
        elif event == '-MTRANS-':
            ga.errorsManualTranscription(values['-INSERT-'])
            window['-OUTPUT-'].update(values['-INSERT-'])
            transcription = values['-INSERT-'].splitlines()
            window['-STATUS-'].update('TRANSCRIPCION LISTA', text_color='#0c7a02')
            window['-EXTRACT-'].update(disabled=False)
        # Automatic transcription
        elif event == '-ATRANS-':
            ga.errorsAutomaticTranscription(values['-FILE-'], values['-VIDEO-'], values['-KEY-'], values['-BUCKET-'])
            window['-EXTRACT-'].update(disabled=True)
            window['-STATUS-'].update('SUBIENDO AUDIO', text_color='#a88532')
            uploadAudio(values['-FILE-'], values['-VIDEO-'], values['-KEY-'], values['-BUCKET-'])
            window['-STATUS-'].update('TRANSCRIBIENDO AUDIO', text_color='#a88532')
            window.perform_long_operation(lambda : transcribeAudio(values['-BUCKET-']), '-END TRANSCRIPTION-')
        elif event == '-END TRANSCRIPTION-':
            transcription = values[event]
            window['-STATUS-'].update('TRANSCRIPCION LISTA', text_color='#0c7a02')
            window['-EXTRACT-'].update(disabled=False)
            for t in transcription:
                window['-OUTPUT-'].print(t + '\n')
        # Graph extraction
        elif event == '-EXTRACT-':
            ga.errorsGraphGeneration(values['-SCRIPT-'])
            window['-STATUS-'].update('GENERANDO GRAFOS', text_color='#a88532')
            window['-ATRANS-'].update(disabled=True)
            window['-MTRANS-'].update(disabled=True)
            window.perform_long_operation(lambda : extractGraphs(transcription, values['-SCRIPT-']), '-END GRAPHS-')
        elif event == '-END GRAPHS-':
            results = values[event]
            window['-STATUS-'].update('GRAFOS GENERADOS', text_color='#0c7a02')
            window['-ATRANS-'].update(disabled=False)
            window['-MTRANS-'].update(disabled=False)
            window['-OUTPUT-'].update('')
            if values['-SEGMENTS-'] or values['-QUERIES-']:
                for i in range(len(results[0])):
                    window['-OUTPUT-'].print('Pregunta ' + str(i+1) + '\n', font='bold')
                    if values['-SEGMENTS-']: window['-OUTPUT-'].print('Segmento:  \n' + results[1][i] + '\n', text_color = '#082567')
                    if values['-QUERIES-']: window['-OUTPUT-'].print('Consulta:  \n' + results[0][i] + '\n', text_color = '#01826B')
            if values['-NEO4J-']:
                ga.errorNeo4j(values['-USER-'], values['-PWD-'], values['-PORT-'])
                submitQueries(results[0], values['-PORT-'], values['-USER-'], values['-PWD-'])
        elif event == '-HELP-':
            sg.popup(ga.ayuda, title='Ayuda', )
    # error handling
    except google.api_core.exceptions.NotFound:
        window['-STATUS-'].update('ERROR', text_color='#990f0b')
        sg.popup_error(f'HA OCURRIDO UN ERROR:', 'Nombre de bucket incorrecto')
    except google.api_core.exceptions.Forbidden as e:
        window['-STATUS-'].update('ERROR', text_color='#990f0b')
        sg.popup_error(f'HA OCURRIDO UN ERROR:', 'Problema con el nombre de bucket o la clave de usuario de servicio.', e)
    except neo4j.exceptions.ServiceUnavailable as e:
        sg.popup_error(f'HA OCURRIDO UN ERROR:', 'No ha sido posible conectarse al puerto.', e)
    except neo4j.exceptions.AuthError as e:
        sg.popup_error(f'HA OCURRIDO UN ERROR:', 'No ha sido posible autorizarse, revise usuario y contraseña de Neo4j', e)
    except Exception as e:
        window['-STATUS-'].update('ERROR', text_color='#990f0b')
        sg.popup_error(f'HA OCURRIDO UN ERROR:', e)