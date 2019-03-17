from app import app
from flask import request, jsonify, abort, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt, json, pymongo, random
#import straight_matrix as sm

'''*****************************************************
                Connection to MongoDB
*****************************************************'''

host = 'localhost'
port = 27017
client = MongoClient(host, port)

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


# Game Start

@app.route('/game/start', methods = ['POST'])
def start():
    try:
        username = request.get_json()['username']
        collection = connectToDB('tets', 'users')
        data = {
            'days' : {},
            'leaderboard': {},
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
       

# Game Turns

@app.route('/game/turn', methods=['POST', 'GET'])
def turn():
    if request.method == 'POST':
        try:
            request_json = request.get_json()
            token = request_json['token'] 
            payload = decodeJwt(token)
            day = payload['day']        #day
            step = payload['step']      #step
            score = payload['score']   
            session_token = payload['session_token']
            meta = sendInfoToConsumer(day = day, step = step, session_token = session_token, meta = request_json['products'])     #dbexchage + getting meta
            day, step, consumer = getNewConsumer(session_token, day, step, score )
            token = generateJwt(payload, day = day, step = step, score = meta['score'])
            collection = connectToDB('tets', 'users')
            id = collection.update_one(
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
            consumer = {'type': '', 'data': {}}

            meta = {}
            response = make_response(jsonify( token = token, consumer = consumer, meta = meta), 200) 
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as err:
            abort(err)

def sendInfoToConsumer( session_token, day = 0, step = 0, score = 0, meta = {}):
    if day != 0:
        collection = connectToDB('tets', 'users')
        consumer = collection.find_one({'_id' : ObjectId(session_token)}) 
        consumer = consumer['days'][str(step + 7 * day)]['consumer']
        meta = test(meta)
        print(meta)
        collection = connectToDB('food', 'data1')
        for item in meta:
            if item['isBought']:
                score += collection.find_one({'_id' : ObjectId(item['_id'])})['price']        
        value =  { str(step + day * 7) :  {
                                        'result' : {
                                                                'score' : score, 
                                                                'meta' : meta
                                                            }
        }}
        collection.update_one(
            {'_id' : ObjectId(session_token)},
            {'$set': {'days' : value}}
        )
    return { 'score' : score, 'meta' : meta }

def getNewConsumer(session_token, day = 0, step = 0, score = 0):
    step = (step + 1) % 8
    if step == 0:
        step += 1
        day += 1
    consumer = testGetConsumer()
    consumer['item'][0]['_id'] = str(consumer['item'][0]['_id'])
    value = { str(step + day * 7) : {
                                        'consumer': consumer
                                    }
    }
    collection = connectToDB('tets', 'users')
    id = collection.update_one(
        {'_id' : ObjectId(session_token)},
        {'$set': {'days' : value}}#write resp from bot
    )
    return [day, step, consumer]
    
@app.route('/game/score', methods = ['POST'])
def score():
    try:
        token = request.get_json()['token'] 
        day = request.get_json()['day']

        '''
        запрос к бд
        '''

        leaderboard = {}
        response = make_response(jsonify( token = token, leaderboard = leaderboard), 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as err:
        abort(err)

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

def test(data):
    for item in data:
        item['isBought'] = random.choice([True, False])
    return data
def testGetConsumer():
    collection = connectToDB('food', 'mods')
    return {'type': '', 'item': list(collection.aggregate([{'$sample' : { 'size' : 1}}]))}