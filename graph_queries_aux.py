#SPACY
import spacy
from spacy.matcher import Matcher

#create  nlp object
nlp = spacy.load("es_core_news_lg")

#GRAFENO
from grafeno import pipeline
import yaml

import os

#checks if two texts are similar
def similar(txt1, txt2):
    doc1 = nlp(txt1.lower().replace('¿', '').replace('?', ''))
    doc2 = nlp(txt2.lower().replace('¿', '').replace('?', ''))
    #print(txt1)
    #print(txt2)
    #print('SIMILITUD: ',doc1.similarity(doc2))
    if doc1.similarity(doc2) > 0.8:
        return doc1.similarity(doc2)
    else:
        sep = txt2.split(", ")
        for s in sep:
            s = doc1.similarity(nlp(s))
            if s > 0.8:
                return s
        return 0

def createGraphQuery(text, questionNumber):
    # Load Grafeno pipeline config
    config = yaml.safe_load(open(os.getcwd() + '/configs/custom.yaml'))
    
    # Run the pipeline on the text to obtain Neo4j query representin the graph obtained
    query = pipeline.run({ **config, 'text': text })
    
    return(query.replace('PX', 'P' + str(questionNumber)))

def createDateQuery(text, questionNumber):
    lines = text.splitlines()
    answer = ''
    if len(lines) > 1:
        for i in range(1, len(lines)):
            answer = answer + '. ' + lines[i]
    # Create doc
    doc = nlp(answer)

    # Initialize the matcher with the shared vocab
    matcher = Matcher(nlp.vocab)

    # Add date recognition patterns to the matcher
    # Year pattern (from 1900 to 2199)
    YearPattern = [[{"TEXT": {"REGEX": "(19|20|21)\d\d"}}]]
    # Day of the month pattern (ex: 23 de enero)
    DayMonthPattern = [[{"IS_DIGIT": True}, {"LOWER": "de"}, {"LOWER": {"REGEX": "^(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)$"}}]]
    # Month pattern (from enero to diciembre)
    MonthPattern = [[{"LOWER": {"REGEX": "^(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)$"}}]]
    # Day of the week pattern (from lunes to martes)
    DayPattern = [[{"LOWER": {"REGEX": "^(lunes|martes|miercoles|jueves|viernes|sabado|domingo)$"}}]]
    matcher.add("year", YearPattern)
    matcher.add("day", DayMonthPattern)
    matcher.add("month", MonthPattern)
    matcher.add("dayWeek", DayPattern)
    
    # Call the matcher on the doc
    matches = matcher(doc)

    # Iterate over the matches to find dates
    dates = {}
    for match_id, start, end in matches:
        # Get the matched span
        matched_span = doc[start:end]
        dates[doc.vocab.strings[match_id]] = matched_span.text
        
    # Insert matches into Neo4j cypher query
    # It merges a node with the matches as properties
    # Creates a relationship with the verb node of the same question, if it exists
    query = ''
    if dates and len(dates)>0:
        query = ('MERGE (n:DATE {' +', '.join('{}: {!r}'.format(k, str(dates[k])) for k in dates) +
                '}) SET n:PX, n._temp_id=\'0\';\n' + 
                'MATCH (n:PX:VERB), (m {_temp_id: \'0\'}) CREATE (n)-[r:CONTEXT]->(m);\n' +
                'MATCH (n) REMOVE n._temp_id;')
    return createGraphQuery(lines[0], questionNumber) + '\n' + query.replace('PX', 'P' + str(questionNumber))
    
def createTextQuery(text, questionNumber):
    lines = text.splitlines()
    answer = ''
    if len(lines) > 1:
        for i in range(1, len(lines)):
            answer = answer + '. ' + lines[i]
    query = 'CREATE (n:TEXT:PX {{concept: \'{}\'}});'.format(answer);
    return query.replace('PX', 'P' + str(questionNumber))

#produces the results based on the mode
def process(text, questionNumber, mode):
    if mode == 0: return createGraphQuery(text, questionNumber)
    elif mode == 1: return createDateQuery(text, questionNumber)
    elif mode == 2: return createTextQuery(text, questionNumber)

