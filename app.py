from flask import Flask, jsonify, render_template
from api.call_api import call_global, call_konochan, call_yandere

app = Flask(__name__)


@app.route('/')
def welcome_page():
    return render_template("index_api.html")


@app.route('/api')
def api_gen():
    all_post = call_global()
    return jsonify(all_post)


@app.route('/api/yandere', methods=["GET"])
def get_yandere():
    yandere_post = call_yandere()
    return jsonify(yandere_post)


@app.route('/api/konachan', methods=["GET"])
def get_konochan():
    konochan_post = call_konochan()
    return jsonify(konochan_post)
