# main.py
from flask import Flask, url_for, jsonify, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/foo', methods=['POST'])
def foo():
    # Run a Python script for processing data
    os.system("python accucary.py")
    return jsonify({"message": "you're a superstar"})

@app.route('/capture', methods=['POST'])
def capture():
    # Run a Python script for face detection
    os.system("python detect_face_live.py")
    return jsonify({"message": "detection phase completed"})

if __name__ == "__main__":
    app.run(port=8080, debug=True)
