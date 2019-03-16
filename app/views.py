from app import app
from flask import request, jsonify, abort, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt, json, pymongo

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
                        'day'   : 1,
                        'step'  : 0,
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
            payload =  decodeJwt(token)

            day = payload['day']

            step = payload['step']

            score = sendInfoToConsumer(request_json['products'])

            consumer = {'type': '', 'data': {}}
            value = {str(day) : {str(step) : {
                                                'consumer': consumer
                                             }
            }}#resp from bot
            
            id = collection.update_one(
                {'_id' : payload['session_token']},
                {'$set': {'days' : value}}#write resp from bot
            )


            token = generateJwt(payload, day = day + 1, step = step + 1, score = score)
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
            print(token)
            consumer = {'type': '', 'data': {}}
            
            meta = {}
            response = make_response(jsonify( token = token, consumer = consumer, meta = meta), 200) 
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as err:
            abort(err)

def sendInfoToConsumer(meta, collection):
    score = 0
    if day != 0:
        collection = connectToDB('food', 'data1')
        for i in meta:
            if meta['isBought']:
                score += collection.find_one({'_id' : meta['id']})['price']        
        value =  { str(day) : {str(step) : {
                                                'result' : {
                                                                'score' : score, 
                                                                'meta' : meta
                                                            }
        }}}

        id = collection.update_one(
            {'_id' : payload['session_token']},
            {'$set': {'days' : value}}
        )
    return score


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
        keys = list(filt.keys())
        filt = {
            keys[0] : { '$regex' : filt[keys[0]], '$options' : 'i'}
        }
        data = list(collection.find(filt, limit = size, skip = current))
        for i in range(len(data)):
            data[0]['_id'] = str(data[0]['_id'])
        meta = { 'searched' : collection.count_documents(filt) }
        response = make_response(jsonify(data = data, meta = meta), 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as err:
        abort(err)

'''*****************************************************
                    Help Code
*****************************************************'''

def test(products):
    pass