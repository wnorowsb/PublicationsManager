from flask import Flask, make_response, request, render_template, url_for, flash, redirect,request,abort
from forms import LoginForm, HomeForm, CreateForm
from redis import Redis
from dotenv import load_dotenv
import requests
import os
import json
from uuid import uuid4

app = Flask(__name__)
redis = Redis(host='redis', port=6379, decode_responses=True)
load_dotenv()

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route("/publications", methods = ['GET','POST'])
def publications():
    sessionId = request.cookies.get('hash')
    nick = redis.get(sessionId)
    form = HomeForm()
    #Przekazuje na sztywno haslo ktore jest akceptowane przez usluge, aby nie zmieniac zbyt mocno logiki modulu web
    response = requests.get('http://service:80/publications', headers= {"Authorization": nick + ":password"})
    response = json.loads(response.text)
    files = requests.get('http://service:80/files')
    files = json.loads(files.text)
    pubs=[]
    fs =[]
    for _, v in response.items():
        href = v["_links"]["view"]["href"]
        id = v["id"]
        pubs.append((id,href))

    for _, v in files.items():
        download = v["_links"]["download"]["href"]
        delete = v["_links"]["delete"]["href"]
        id = v["id"]
        name = v["name"]
        fs.append((id, name, download, delete))

    if form.validate_on_submit():
        files = { 'file': form.uploadFile.data }
        r = requests.post('http://pdf:5000/upload', files = files)
        return r.text
    
    if (nick == request.cookies.get('username')): 
        return render_template('publications.html', pubs=pubs, form = form, fs=fs)
        #return files.json()
    else:
        return render_template('publications.html' )


@app.route("/list", methods = ['GET'])
def listFiles():
    answ = requests.get('http://pdf:5000/list')
    ret = answ.text
    return str(ret)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if ( password == '123'):
            resp = make_response(redirect(url_for('publications')))
            resp.set_cookie('username', username)
            sessionId = str(uuid4())
            resp.set_cookie('hash', sessionId)
            redis.set(sessionId, username)

            return resp

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    redis.delete(request.cookies.get('hash'))
    return redirect(url_for('login'))

@app.route('/details', methods = ['GET', 'POST'])
def details():
    sessionId = request.cookies.get('hash')
    nick = redis.get(sessionId)
    address = request.args.get('address', None)
    response = requests.get( address, headers= {"Authorization": nick + ":password"})
    data = response.json()
    files = requests.get('http://service:80/files')
    files = json.loads(files.text)
    ids =[]
    for _, v in files.items():
        ids.append(v["id"])

    return render_template('details.html', data=data, ids=ids)

@app.route('/download')
def download():
    sessionId = request.cookies.get('hash')
    nick = redis.get(sessionId)
    address = request.args.get('address', None)
    response = requests.get( address, headers= {"Authorization": nick + ":password"})
    return redirect(url_for('publications'))

@app.route('/link', methods=['POST'])
def link():
    sessionId = request.cookies.get('hash')
    nick = redis.get(sessionId)
    address = request.args.get('address', None)
    id = request.form['fileId']
    address = address.replace('<fid>',str(id))
    response = requests.post( address, headers= {"Authorization": nick + ":password"})
    return True

@app.route('/unlink')
def unlink():
    sessionId = request.cookies.get('hash')
    nick = redis.get(sessionId)
    address = request.args.get('address', None)
    id = request.args.get('id', None)
    address = address.replace('<fid>',str(id))
    method = request.args.get('method', None)
    if method =='POST':
        response = requests.post( address, headers= {"Authorization": nick + ":password"})
    if method =='DELETE':
        response = requests.delete( address, headers= {"Authorization": nick + ":password"})
    return redirect(url_for('publications'))

@app.route('/delete')
def delete():
    sessionId = request.cookies.get('hash')
    nick = redis.get(sessionId)
    address = request.args.get('address', None)
    response = requests.delete( address, headers= {"Authorization": nick + ":password"})
    data = response.json()
    return redirect(url_for('publications'))
    #return response.text

@app.route('/add', methods = ['GET', 'POST'])
def add():
    form = CreateForm()
    sessionId = request.cookies.get('hash')
    nick = redis.get(sessionId)
    if form.validate_on_submit():
        data = {'author': form.author.data, 'title': form.title.data, 'year': form.year.data}
        response = requests.post('http://service/publications/', headers= {"Authorization": nick + ":password"}, data=data )
        return redirect(url_for('publications'))
        #return response.text
    return render_template('create.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=50)