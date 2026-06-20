import json
from flask import Blueprint, jsonify

radio_bp = Blueprint('radio_bp', __name__)

@radio_bp.route('/radio/mon', methods=['GET'])
def get_channel1():
    with open("data/radio/mon.json", "r", encoding="utf-8") as mon:
        return jsonify(json.load(mon))

@radio_bp.route('/radio/tue', methods=['GET'])
def get_channel2():
    with open("data/radio/tue.json", "r", encoding="utf-8") as tue:
        return jsonify(json.load(tue))

@radio_bp.route('/radio/wed', methods=['GET'])
def get_channel3():
    with open("data/radio/wed.json", "r", encoding="utf-8") as wed:
        return jsonify(json.load(wed))

@radio_bp.route('/radio/thu', methods=['GET'])
def get_channel4():
    with open("data/radio/thu.json", "r", encoding="utf-8") as thu:
        return jsonify(json.load(thu))

@radio_bp.route('/radio/fri', methods=['GET'])
def get_channel5():
    with open("data/radio/fri.json", "r", encoding="utf-8") as fri:
        return jsonify(json.load(fri))

@radio_bp.route('/radio/sat', methods=['GET'])
def get_channel6():
    with open("data/radio/sat.json", "r", encoding="utf-8") as sat:
        return jsonify(json.load(sat))

@radio_bp.route('/radio/sun', methods=['GET'])
def get_channel7():
    with open("data/radio/sun.json", "r", encoding="utf-8") as sun:
        return jsonify(json.load(sun))
