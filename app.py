from flask import Flask, request
import pickle
from redis import Redis

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
        'author' : request.form['author'],
        'title' : request.form['title']
    })
    binary = pickle.dumps(doc)
    redis.set(key, binary)
    
    uncoded = pickle.loads(redis.get(key))
    return uncoded.data['author'], 201

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
    return pickle.loads(pub)

@app.route('/publications/<id>', methods = ['DELETE'])
def delPub(id):
    auth = request.headers['Authorization']
    auth = auth.split(':')
    if(auth[0]!='user' or auth[1]!='password'):
        return 'Wrong authorization data', 400
    key = auth[0] + '/' + str(id)
    resp = redis.delete(key)
    return str(resp)

@app.route('/publications', methods = ['GET'])
def start():
    ret = redis.keys("user*")
    pubs = redis.mget(ret)
    pub = pickle.loads(pubs[0])

    return pub


if __name__ == "__main__":
    app.run(debug=True)