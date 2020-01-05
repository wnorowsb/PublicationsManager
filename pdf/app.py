from flask import Flask, make_response, request, render_template, url_for, flash, redirect,request,abort, jsonify
#from Crypto.Cipher import AES
import os

from dotenv import load_dotenv
import requests
from werkzeug.utils import secure_filename
#filename_coder = AES.new('This is a key123', AES.MODE_CFB, 16 * '\x00' )
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route('/upload', methods=['POST', 'OPTIONS'])
def send():
    file = request.files.get('file')
    file.save('file.csv')
    return 'Succeed'

@app.route('/files', methods=['GET'])
def listFiles():
    ids = {'1': 'file1', '2':'file2', '3': 'file3'}
    return jsonify(ids)

def redirect(location):
  response = make_response('', 303)
  response.headers["Location"] = location
  return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
