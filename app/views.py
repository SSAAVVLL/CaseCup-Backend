from app import app
from flask import request, jsonify, abort, make_response
from pymongo import MongoClient
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
        print(kwargs)
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
        payload = {
                        'user'  : username,
                        'day'   : 0,
                        'step'  : 0,
                        'score' : 0,
                'session_token' : generateSessionToken() 
            }
        token = generateJwt(payload)
        data = {
            'token': token,
            'days' : [],
            'leaderboard': []
        }
        ids = collection.insert_one(data).inserted_id
        print(ids)
        return jsonify(token = token)

    except Exception as err: 
        abort(err)
       

# Game Turns
@app.route('/game/turn', methods=['POST', 'GET'])
def turn():

    if request.method == 'POST':
        try:
            token = request.get_json()['token'] 
            now =  decodeJwt(token)
            print(0)
            day = now["day"] + 1
            step = now["step"] + 1

            score = now['score'] + 1
            consumer = {'type': '', 'data': {}}
            meta = {}
            token = generateJwt(now, day = day, step = step, score = score)
            print(0)
            return jsonify( token = token, consumer = consumer , meta = meta ) 
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
            return jsonify( token = token, consumer = consumer, meta = meta) 
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
        return jsonify( token = token, leaderboard = leaderboard)
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
        return jsonify(data = data)
    except Exception as err:
        abort(err)