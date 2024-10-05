from flask import Flask, jsonify, render_template, request

from app.coordinates import generate_search_coordinates_for_layered_search
from app.settings import app_settings

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('map.html', mapbox_token=app_settings.mapbox_token)


@app.route('/calculate_coordinates', methods=['POST'])
def calculate_coordinates():
    data = request.get_json()
    longitude = data['longitude']
    latitude = data['latitude']
    radius = data['radius'] * 1000
    layers = data['layers']
    state = data.get('state')
    all_coordinates = generate_search_coordinates_for_layered_search(f'{latitude},{longitude}', radius, layers, state)
    return jsonify(all_coordinates)


@app.route('/check_password', methods=['POST'])
def check_password():
    data = request.get_json()
    password = data['password']

    if password == app_settings.password:
        return jsonify({'message': 'Success', 'status': 200, 'token': app_settings.mapbox_token})
    return jsonify({'message': 'Failure', 'status': 403})
