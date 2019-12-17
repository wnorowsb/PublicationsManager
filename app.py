from flask import Flask, request
import pickle
from redis import Redis

# First Party Libs
from flask_hal import HAL, document

redis = Redis(host='redis', port=6379)

app = Flask(__name__)
HAL(app)  # Initialise HAL
n_pub = 0

@app.route('/add', methods = ['POST'])
def hello():
    n_pub = redis.get('n_pub')
    if(n_pub == None):
        redis.set('n_pub', '0')
        n_pub = 0
    n_pub = int(n_pub) 
    n_pub+=1
    redis.set('n_pub', n_pub)
    key = request.form['username'] + '/' + str(n_pub)
    doc = document.Document(data={
        'author' : request.form['author'],
        'title' : request.form['title']
    })
    binary = pickle.dumps(doc)
    redis.set(key, binary)
    uncoded = pickle.loads(redis.get(key))
    return uncoded

@app.route('/test', methods = ['POST'])
def start():
    return request.form['author']


if __name__ == "__main__":
    app.run(debug=True)