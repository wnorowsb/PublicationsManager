from flask import Flask, make_response, request, render_template, url_for, flash, redirect,request,abort, session, Response
from forms import LoginForm, HomeForm, CreateForm
from redis import Redis, StrictRedis
from dotenv import load_dotenv
import requests
import os
import json
from uuid import uuid4
from functools import wraps
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__)
redis = StrictRedis(host='redis', port=6379, decode_responses=True)
load_dotenv()

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/publications')

def event_stream(user):
    pubsub = redis.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(user)
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        yield 'data: %s\n\n' % message['data']

def post(user):
    redis.publish(user, 'There is new publication!')
    return True

#powinien dostawac indentyfikator
@app.route('/stream/<user>')
def stream(user):
    return Response(event_stream(user), mimetype="text/event-stream" )

@requires_auth
@app.route("/publications", methods = ['GET','POST'])
def publications():
    #sessionId = request.cookies.get('hash')
    nick = session['profile']['name']
    form = HomeForm()
    #Przekazuje na sztywno haslo ktore jest akceptowane przez usluge, aby nie zmieniac zbyt mocno logiki modulu web
    response = requests.get('http://service:80/publications/', headers= {"Authorization": nick + ":password"})
    response = json.loads(response.text)
    files = requests.get('http://service:80/files', headers= {"Authorization": nick + ":password"})
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
        r = requests.post('http://service/files', files = files, headers= {"Authorization": nick + ":password"})
        return r.text

    return render_template('publications.html', pubs=pubs, form = form, fs=fs, user = nick)



@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route('/login0')
def login0():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)

@app.route('/home')
def home():
  return render_template("home.html")

@requires_auth
@app.route('/details', methods = ['GET', 'POST'])
def details():
    nick = session['profile']['name']
    address = request.args.get('address', None)
    response = requests.get( address, headers= {"Authorization": nick + ":password"})
    data = response.json()
    files = requests.get('http://service:80/files', headers= {"Authorization": nick + ":password"})
    files = json.loads(files.text)
    ids =[]
    for _, v in files.items():
        ids.append(v["id"])
    return render_template('details.html', data=data, ids=ids)

@requires_auth
@app.route('/download')
def download():
    nick = session['profile']['name']
    address = request.args.get('address', None)
    response = requests.get( address, headers= {"Authorization": nick + ":password"})
    return redirect(request.referrer)

@app.route('/link', methods=['GET', 'POST'])
def link():
    nick = session['profile']['name']
    address = request.args.get('address', None)
    id = request.form['fileId']
    address = address.replace('<fid>',str(id))
    response = requests.post( address, headers= {"Authorization": nick + ":password"})
    return redirect(request.referrer)

@requires_auth
@app.route('/unlink')
def unlink():
    nick = session['profile']['name']
    address = request.args.get('address', None)
    id = request.args.get('id', None)
    address = address.replace('<fid>',str(id))
    method = request.args.get('method', None)
    if method =='DELETE':
        response = requests.delete( address, headers= {"Authorization": nick + ":password"})
    return redirect(request.referrer)

@requires_auth
@app.route('/delete')
def delete():
    nick = session['profile']['name']
    address = request.args.get('address', None)
    response = requests.delete( address, headers= {"Authorization": nick + ":password"})
    return redirect(url_for('publications'))

@requires_auth
@app.route('/add', methods = ['GET', 'POST'])
def add():
    form = CreateForm()
    nick = session['profile']['name']
    if form.validate_on_submit():
        data = {'author': form.author.data, 'title': form.title.data, 'year': form.year.data}
        response = requests.post('http://service/publications/', headers= {"Authorization": nick + ":password"}, data=data )
        redis.publish(nick, 'There is new publication!')
        return redirect(url_for('publications'))
    return render_template('create.html', form=form)


if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=50)
    app.run()