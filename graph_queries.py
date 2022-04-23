import json
from graph_queries_aux import process, similar

#NEO4J
from neo4j import GraphDatabase

def extractGraphs(lines, scriptPath):
    #load questions and results modes on dict
    with open(scriptPath, encoding='utf-8') as f:
        script = json.load(f)['preguntas']

    #get questions
    questions = list(script.keys())
    results = {}

    # Find the positions of the questions in the text lines, using similarity
    matches = [-1] * len(lines)
    for j in range(len(questions)):
        maxS = 0
        maxI = -1
        for i in range(len(lines)):
            if matches[i] == -1:
                s = similar(questions[j], lines[i][2:])
                if s > maxS and s > 0.7:
                    maxS = s
                    maxI = i
        if maxI != -1:
            matches[maxI] = j

    segment = ''
    queries = []
    segments = []

    # Process each question to obtain queries
    qNum = -1
    for i in range(len(lines)):
        if qNum != -1:
            if matches[i] != -1:
                segments.append(segment)
                queries.append(process(segment, qNum, script[questions[qNum]]))
                #print(segment + '\n\n')
                qNum = matches[i]
                segment = lines[i][2:]
            else:
                segment = segment + '\n' + lines[i][2:]

        elif matches[i] != -1:
            qNum = matches[i]
            segment = lines[i][2:]
        i += 1
    segments.append(segment)
    queries.append(process(segment, j, script[questions[j]]))
    #print(segment + '\n\n')    
    return (queries, segments)

def submitQueries(queries, port, user, pwd):
    #uri = "bolt://localhost:7687", auth=("neo4j", "password"
    data_base_connection = GraphDatabase.driver(uri = "bolt://localhost:" + str(port), auth=(user, pwd))
    session = data_base_connection.session()   
    for qs in queries:
        for q in qs.splitlines():
            session.run(q)
        
    session.run('match ()-[r]->() match (s)-[r]->(e) with s,e,type(r) as typ, tail(collect(r)) as coll foreach(x in coll | delete x);')