from flask import Flask, request, Response, jsonify, redirect
import pickle
from redis import Redis
from flask_hal.link import Link
import json
# First Party Libs
from flask_hal import HAL, document

redis = Redis(host='redis', port=6379)

app = Flask(__name__)
HAL(app)  # Initialise HAL
n_pub = 0

@app.route('/publications/', methods = ['POST'])
def addPub():
    auth = request.headers['Authorization']
    auth = auth.split(':')
    if(auth[0]!='user' or auth[1]!='password'):
        return 'Wrong authorization data', 400

    n_pub = redis.get('n_pub')
    if(n_pub == None):
        redis.set('n_pub', '0')
        n_pub = 0
    n_pub = int(n_pub) 
    n_pub+=1
    redis.set('n_pub', n_pub)
    key = auth[0] + '/' + str(n_pub)

    doc = document.Document(data={
        'id' : n_pub,
        'author' : request.form['author'],
        'title' : request.form['title'],
    },
    links= [Link('delete', '/publications/' + str(n_pub), type = 'DELETE'),
            Link('get', '/publications/' + str(n_pub), type = 'GET')
            Link('linkFile', '/publications/' + str(n_pub)+'/files/<fid>', type = 'POST')
            Link('unLinkFile', '/publications/' + str(n_pub)+'/files/<fid>', type = 'DELETE')])
    binary = pickle.dumps(doc)
    redis.set(key, binary)
    
    uncoded = pickle.loads(redis.get(key))
    return uncoded.data['author'] + str(n_pub), 201

@app.route('/publications/<id>', methods = ['GET'])
def getPub(id):
    auth = request.headers['Authorization']
    auth = auth.split(':')
    if(auth[0]!='user' or auth[1]!='password'):
        return 'Wrong authorization data', 400
    key = auth[0] + '/' + str(id)
    pub = redis.get(key)
    if (pub is None):
        return "Wrong publication id", 404
    return pickle.loads(pub).to_json()

@app.route('/publications/<id>', methods = ['DELETE'])
def delPub(id):
    auth = request.headers['Authorization']
    auth = auth.split(':')
    if(auth[0]!='user' or auth[1]!='password'):
        return 'Wrong authorization data', 400
    key = auth[0] + '/' + str(id)
    resp = redis.delete(key)
    return str(resp)

@app.route('/publications/', methods = ['GET'])
def listPub():
    auth = request.headers['Authorization']
    auth = auth.split(':')
    if(auth[0]!='user' or auth[1]!='password'):
        return 'Wrong authorization data', 400
    ret = redis.keys("user*")
    pubList = []
    pubs = redis.mget(ret)
    for pub in pubs:
        pub = pickle.loads(pub)
        pubShort = doc = document.Document(data={
        'id' : pub.data['id'],
        },
        links= [Link('view', '/publications/' + str(pub.data['id']))])
        pubList.append(pubShort.to_json())
    resp = {key: value for key, value in enumerate(pubList)}
    return resp

@app.route('/files', methods = ['POST'])
def addFile():
    return redirect('pdf/upload', 303)

@app.route('/files', methods = ['GET'])
def getFiles():
    return redirect('pdf/listFiles', 303)

@app.route('/files/<fid>', methods = ['DELETE'])
def delFile(fid):
    return redirect('pdf/delete?fid='+str(fid), 303)

@app.route('/files/<fid>', methods = ['GET'])
def getFile(fid):
    return redirect('pdf/download?fid='+str(fid), 303)

@app.route('/publications/<id>/files/<fid>', methods = ['POST'])
def linkFile(id, fid):
    auth = request.headers['Authorization']
    auth = auth.split(':')
    if(auth[0]!='user' or auth[1]!='password'):
        return 'Wrong authorization data', 400
    key = auth[0] + '/' + str(id)
    pub = redis.get(key)
    pub = pickle.loads(pub)
    pub.links.append(Link('file'+str(fid), '/files'+ str(fid), type='POST'))
    pub = pickle.dumps(pub)
    redis.set(key, pub)
    answ = redis.get(key)
    return pickle.loads(answ).to_json()


@app.route('/publications/<id>/files/<fid>', methods = ['DELETE'])
def unLinkFile(id, fid):
    auth = request.headers['Authorization']
    auth = auth.split(':')
    if(auth[0]!='user' or auth[1]!='password'):
        return 'Wrong authorization data', 400
    key = auth[0] + '/' + str(id)
    pub = redis.get(key)
    pub = pickle.loads(pub)
    newLinks = []
    for link in pub.links:
        if link.rel != 'file'+str(fid):
            newLinks.append(link)
    
    pub.links = newLinks

    pub = pickle.dumps(pub)
    redis.set(key, pub)
    answ = redis.get(key)
    return pickle.loads(answ).to_json()

if __name__ == "__main__":
    app.run(debug=True)