from app import app
from flask import request, jsonify, abort, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt, json, pymongo
from random import randint

'''*****************************************************
                Connection to MongoDB
*****************************************************'''

host = "localhost"
port = 27017
client = MongoClient(host, port)

'''*****************************************************
Generates constant session token for user identification
*****************************************************'''

def generateSessionToken():
    return ''.join([ chr(randint(65,90)) for i in range(randint(3,10))])

'''*****************************************************
                Generates JWT
*****************************************************'''

def generateJwt(payload, **kwargs):
    if len(kwargs) != 0:
        for key in kwargs.keys():
            payload[key] = kwargs[key]
    
    return jwt.encode(payload, "GameSession", algorithm = 'HS256').decode('utf-8')

def decodeJwt(jwToken):
    return jwt.decode(jwToken, "GameSession", algorithm = 'HS256')
    
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
        print(session_token)
        payload = {
                        'user'  : username,
                        'day'   : 0,
                        'step'  : 0,
                        'score' : 0,
                'session_token' : session_token
            }
        print(payload)
        token = generateJwt(payload)
        print(0)
        id = collection.update_one(
            {'_id' : ObjectId(session_token)},
            {'$set' : {'token' : token}}
        )
        print(id)
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
            req = request.get_json()
            token = req['token'] 
            now =  decodeJwt(token)
            day = now["day"]
            step = now["step"]
            #send to bot
            coll = connectToDB('tets', 'users')
            value = { str(day) : req['products']}
            id = coll.update_one(
                {"token" : token},
                 {"$set": {"days" : value}}#write resp from bot
            )
            score = now['score'] + 1
            id = coll.update_one(
                {"token" : token},
                {"$set": {"days" : value}}#write resp from bot
            )
            consumer = {'type': '', 'data': {}}

            meta = req['products']#resp from bot
            token = generateJwt(now, day = day + 1, step = step + 1, score = score)
            response = make_response(jsonify( token = token, consumer = consumer , meta = meta ), 200)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except KeyError:
            abort(401)
        except Exception as err:
            abort(err)

    if request.method == 'GET':
        try:
            token = request.args.get("token")
            print(token)
            consumer = {'type': '', 'data': {}}
            
            meta = {}
            response = make_response(jsonify( token = token, consumer = consumer, meta = meta), 200) 
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except Exception as err:
            abort(err)

@app.route('/game/score', methods = ['POST'])
def getLeaderboard():
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
def getCLaster():
    try:
        req = request.get_json()
        current = req['current']
        size = req['size']
        filt = req['filter']
        
        '''
        запрос к бд
        '''

        data = []
        response = make_response(jsonify(data = data), 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as err:
        abort(err)