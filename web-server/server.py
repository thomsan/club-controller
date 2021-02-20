from flask import Flask, request, render_template, jsonify, send_from_directory
import esp8226_udp
import numpy as np
app = Flask(__name__, static_url_path='/static')

color = "#ffff"

@app.route('/')
def index():
    return render_template('index.html')
    
def byteToBoolArray(bytes):
    values = []
    bValues = bytearray(bytes)
    for value in bValues:
        values.append(bool(value))
    return values

@app.route('/gpio', methods=['GET', 'POST'])
def gpio():
    if request.method == 'GET':
        values = byteToBoolArray(esp8226_udp.values)
        print(values)
        return jsonify(values)

    else:
        data = request.json
        if(data["value"]):
            esp8226_udp.values[data["id"]] = 1
        else:
            esp8226_udp.values[data["id"]] = 0
        esp8226_udp.update()
        return jsonify(byteToBoolArray(esp8226_udp.values))

@app.route('/color', methods=['GET', 'POST'])
def color():
    global color
    if request.method == 'GET':
        print(color)
        return jsonify(color)

    else:
        data = request.json
        if(data["value"]):
            color = data["value"]
        return jsonify(color)

if __name__ == '__main__':

    app.run()
