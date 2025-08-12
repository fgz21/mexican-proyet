from flask import Flask, render_template, jsonify
from serverless_wsgi import handle_request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify({'message': 'Hola desde la API de Flask'})

def handler(event, context):
    return handle_request(app, event, context)