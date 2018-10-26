import numpy as np
import cv2
from urllib.request import urlopen, Request
import os
import sys
import keras as K
import json
from flask import Flask
import socket
from flask import request


def pad_to_square(img):
    pad = 20
    horizontal = max(0, img.shape[0] - img.shape[1]) // 2 + pad
    vertical = max(0, img.shape[1] - img.shape[0]) // 2 + pad
    padded = cv2.copyMakeBorder(img, vertical, vertical, horizontal, horizontal, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    scaled = cv2.resize(padded, dsize=(128,128), interpolation = cv2.INTER_LINEAR)
    return scaled

def normalize(img):
    norm = np.zeros(img.shape)
    norm = cv2.normalize(img, norm, 0, 255, cv2.NORM_MINMAX)
    return norm

def url_to_image(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    reg_url = url
    req = Request(url=reg_url, headers=headers)
    resp = urlopen(req)

    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


def init():

    global model  
    global labels
    global default_img_url

    # Default url
    default_img_url = "https://shop.epictv.com/sites/default/files/ae42ad29e70ba8ce6b67d3bdb6ab5c6e.jpeg"

    print("Executing init() method...")
    print("Python version: " + str(sys.version) + ", keras version: " + K.__version__)

    # Load the model 
    labels = ['axes','boots','carabiners','crampons','gloves','hardshell_jackets','harnesses','helmets','insulated_jackets','pulleys','rope','tents']
    model = K.models.load_model('model_ch4.h5')
    return

def run(inputString):

    responses = []
    request = json.loads(inputString)
    
    #for url in base64Dict.items():
    #    img_url = url
    try:    
    	print("Predicting URL: ", request['img_url'])
    	img_url = request['img_url']
    except:
    	print("Wrong URL provided. Predicting default URL: ", default_img_url)

    try:
        img = normalize(pad_to_square(url_to_image(img_url)))
    except:
    	print("Wrong URL. Predicting default URL: ", default_img_url)
    	img = normalize(pad_to_square(url_to_image(default_img_url)))
    	img_url = default_img_url
    
    y_pred  = model.predict([[img]])

    resp = {"img_url":  img_url, "prediction": str(labels[np.argmax(y_pred)])}

    responses.append(resp)

    return json.dumps(responses)

app = Flask(__name__)

def get_prediction(test_img_url):
    
    img_dict = {"img_url": test_img_url}
    body = json.dumps(img_dict)
    return run(body)

@app.route("/")
def predict():
    return get_prediction(request.args.get('url')) 

# Test run
if __name__ == "__main__":
    init()
    test_img_url = "https://www.monkeysports.eu/media/catalog/product/cache/9/image/800x/9df78eab33525d08d6e5fb8d27136e95/b/a/bauer-re-akt-100-hockey-helmet-26.jpg"
    get_prediction(test_img_url)
    app.run(host='0.0.0.0', port=8080)
