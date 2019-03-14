from app import app
from flask import request, jsonify, abort, make_response
import jwt
import json
import random,  requests

requests.get

def generateSessionToken():
    return ''.join([ chr(random.randint(65,90)) for i in range(random.randint(3,10))])

def generateJwt(username = 'user', day = 0, step = 0, score = 0 , jwToken = None):
    if jwToken == None:
        payload = {
                        'user'  : username,
                        'day'   : day,
                        'step'  : step,
                        'score' : score,
                'session_token' : generateSessionToken() 
            }
    else:
        payload = jwt.decode(jwToken, 'GameSession', algorithms = 'HS256')
    
    return jwt.encode(payload, "GameSession", algorithm = 'HS256').decode('utf-8')


@app.route('/')
@app.route('/game')
@app.route('/game/start', methods = ['POST'])
def start():
    try:
        username = request.get_json()['username']
        
        return jsonify(token = generateJwt(username))

    except Exception as err: 
        abort(err)

@app.route('/game/turn', methods=['POST', 'GET'])
def turn():
    if request.method == 'POST':
        try:
            token = request.get_json()['token']
            '''
#############################################
            Место для кода
#############################################  
            '''
            day = jwt.decode(token, 'GameSession', algorithms = 'HS256')["day"] + 1
            step = jwt.decode(token, 'GameSession', algorithms = 'HS256')["step"] + 1
            consumer = {'type': '', 'data': {}}
            return jsonify( token = generateJwt(day = day, step = step), consumer = consumer) 
        except KeyError:
            abort(401)
        except Exception as err:
            abort(err)
    if request.method == 'GET':
        try:
            token = request.args.get("token")
            print(token)
            consumer = {'type': '', 'data': {}}
            return jsonify( token = generateJwt(jwToken = token), consumer = consumer) 
        except:
            pass
