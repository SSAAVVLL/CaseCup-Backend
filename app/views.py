from app import app
from flask import request, jsonify, abort, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt, json, pymongo, random
from straight_matrix import *

'''*****************************************************
                Connection to MongoDB
*****************************************************'''

host = 'localhost'
port = 27017
client = MongoClient(host, port)

'''*****************************************************
                    Matrix for Bots
*****************************************************'''

m_ids = init_ids()
dist_matrix = init_mat()
'''*****************************************************
                    Generates JWT
*****************************************************'''

def generateJwt(payload, **kwargs):
    if len(kwargs) != 0:
        for key in kwargs.keys():
            payload[key] = kwargs[key]
    
    return jwt.encode(payload, 'GameSession', algorithm = 'HS256').decode('utf-8')

def decodeJwt(jwToken):
    return jwt.decode(jwToken, 'GameSession', algorithm = 'HS256')
    
'''*****************************************************
                    Access to MongoDB
*****************************************************'''

def connectToDB(database, collection):
    return client[database][collection]

'''*****************************************************
                      Main Code
*****************************************************'''
@app.route('/')
@app.route('/game')




@app.route('/game/start', methods = ['POST'])
def start():
    try:
        username = request.get_json()['username']
        collection = connectToDB('tets', 'users')
        data = {
            'days' : [],
            'leaderboard': [],
            'token' : ''
        }
        session_token = str(collection.insert_one(data).inserted_id)
        payload = {
                        'user'  : username,
                        'day'   : 0,
                        'step'  : -1,
                        'score' : 0,
                'session_token' : session_token
            }
        token = generateJwt(payload)
        id = collection.update_one(
            {'_id' : ObjectId(session_token)},
            {'$set' : {'token' : token}}
        )
        response = make_response(jsonify(token = token), 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    except Exception as err: 
        abort(err)
       



@app.route('/game/turn', methods=['POST', 'GET'])
def turn():
    if request.method == 'POST':
        try:
            request_json = request.get_json()

            token = request_json['token'] 
            payload = decodeJwt(token)
            day = payload['day']        
            step = payload['step']      
            score = payload['score']   
            session_token = payload['session_token'] 

            meta = sendInfoToConsumer(user = payload['user'], day = day, step = step, session_token = session_token, meta = request_json['products']) 
            score = score + meta['score']

            day, step, consumer = getNewConsumer(session_token, day, step, score )

            token = generateJwt(payload, day = day, step = step, score = score)
            collection = connectToDB('tets', 'users')
            collection.update_one(
            {'_id' : ObjectId(session_token)},
            {'$set' : {'token' : token}}
            )
            response = make_response(jsonify( token = token, consumer = consumer , meta = meta ), 200)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except KeyError:
            abort(401)
        except Exception as err:
            abort(err)

    if request.method == 'GET':
        try:
            token = request.args.get('token')
            payload = decodeJwt(token)
            collection = connectToDB('tets', 'users')

            user = collection.find_one({'_id' : ObjectId(payload['session_token'])})
            for item in user['days']:
                if item['step'] == (payload['day'] * 7 + payload['step']):
                    if 'consumer' in item:
                        consumer = item['consumer'] 
            meta = user['days']
            response = make_response(jsonify( token = token, consumer = consumer, meta = meta), 200) 
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as err:
            abort(err)

def sendInfoToConsumer( session_token, user, day = 0, step = 0, score = 0, meta = {}):
    if day != 0:
        collection = connectToDB('tets', 'users')
        consumer = collection.find_one({'_id' : ObjectId(session_token)}) 
        for item in consumer['days']:
            if item['step'] == (day * 7 + step):
                if 'consumer' in item:
                    consumer = item['consumer']['item'][0]['_id']
                    break   
        meta, score = getResult(consumer, reformatTo(meta)) #meta
        botsRequest((step + day * 7), consumer, user, session_token, score)
        value =  { 'step' : step + day * 7, 
                 'result' : {
                                        'score' : score, 
                                        'meta' : meta
                                    }
                }
        сollection = connectToDB('tets', 'users')
        сollection.update_one(
            {'_id' : ObjectId(session_token)},
            {'$push': {'days' : value}}
        )
    return { 'score' : score, 'meta' : meta }

def getNewConsumer(session_token, day = 0, step = 0, score = 0):
    step = (step + 1) % 8
    if step == 0:
        step += 1
        day += 1
    consumer = testGetConsumer()
    consumer['item'][0]['_id'] = str(consumer['item'][0]['_id'])
    value = {  'step' : step + day * 7,
            'consumer': consumer
            }
    collection = connectToDB('tets', 'users')
    collection.update_one(
        {'_id' : ObjectId(session_token)},
        {'$push': {'days' : value}}#write resp from bot
    )
    return [day, step, consumer]
    
def botsRequest(step, consumer, username, session_token, score):
    global m_ids
    global dist_matrix
    leaderboard = {
        'step' : step,
        'scores' : {
            username : score,
            'Oleg_1' : getResult(consumer,random_bot(m_ids))[1], #testGenerateScore(score),
            'Oleg_2' : getResult(consumer, matrix_bot(consumer, m_ids, dist_matrix))[1],  #testGenerateScore(score),
            'Oleg_3' : getResult(consumer,random_bot(m_ids))[1]  #testGenerateScore(score)
            }
    }
    collection = connectToDB('tets', 'users')
    collection.update_one(
        {'_id' : ObjectId(session_token)},
        {'$push' : {'leaderboard' : leaderboard}}
    )
    
def getResult(consumer, meta):
    global m_ids
    global dist_matrix
    score = 0
    meta = metrix(consumer, meta, m_ids, dist_matrix)
    #meta = testSend(meta)
    collection = connectToDB('food', 'data1')
    for item in meta:
        if item['isBought']:
            score += collection.find_one({'_id' : ObjectId(item['_id'])})['price']    
    return [meta, score]

@app.route('/game/score', methods = ['GET'])
def score():
    try:

        token = request.args.get('token') 
        payload = decodeJwt(token)
        collection = connectToDB('tets', 'users')
        leaderboard = collection.find_one({'_id' : ObjectId(payload['session_token'])})
        leaderboard = leaderboard['leaderboard'][-1]
        response = make_response(jsonify( token = token, leaderboard = leaderboard), 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as err:
        abort(err)

@app.route('/game/history', methods = ['GET'])

@app.route('/items' , methods = ['POST'])
def items():
    try:
        request_json = request.get_json()
        current = request_json['current']
        size = request_json['size']
        filt = request_json['filter']
        collection = connectToDB('food', 'mods')
        if 'name' in filt:
            filt['name'] = { '$regex' : filt['name'], '$options' : 'i'}
        data = list(collection.find(filt, limit = size, skip = current).sort('name'))
        for item in data:
            data
        for i in range(len(data)):
            data[i]['_id'] = str(data[i]['_id'])
        meta = { 'searched' : collection.count_documents(filt) }
        response = make_response(jsonify(data = data, meta = meta), 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as err:
        abort(err)

'''*****************************************************
                    Help Code
*****************************************************'''

def testSend(data):
    for item in data:
        item['isBought'] = random.choice([True, False])
    return data
def testGetConsumer():
    collection = connectToDB('food', 'mods')
    return {'type': '', 'item': list(collection.aggregate([{'$sample' : { 'size' : 1}}]))}

def testGenerateScore(score):
    bot_score = random.randint(0, score + score // 2)
    if bot_score < 0:
        bot_score = 0
    return bot_score