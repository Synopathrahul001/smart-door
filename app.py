from flask import Flask, request, send_file, render_template
from flask_cors import CORS
import requests
import os
import time
import numpy as np
import cv2

# 🔥 IMPORT AI
from ai_engine import process_image

app = Flask(__name__)
CORS(app)

# 🔥 FIREBASE
FIREBASE_URL = "https://smart-door-lock-715ba-default-rtdb.firebaseio.com/door.json"
SECRET_KEY = "secret123"

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🔥 UPDATE FIREBASE
def update_firebase(image_url, decision):
    data = {
        "image_url": image_url,
        "status": "visitor_detected",
        "decision": decision
    }
    requests.put(FIREBASE_URL, json=data)


@app.route('/')
def home():
    return render_template("index.html")


# 📸 RECEIVE IMAGE + RUN AI
@app.route('/upload', methods=['POST'])
def upload():

    if request.headers.get("Authorization") != SECRET_KEY:
        return "Unauthorized", 401

    try:
        data = request.get_data()

        filename = f"image_{int(time.time())}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 💾 Save image
        with open(filepath, "wb") as f:
            f.write(data)

        print("📸 Image saved:", filename)

        # 🔄 Convert to OpenCV format
        file_bytes = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # 🧠 RUN AI
        decision = process_image(img)

        # 🔗 IMAGE URL
        image_url = request.host_url + f"static/{filename}"

        # 🔥 UPDATE FIREBASE
        update_firebase(image_url, decision)

        print("📡 Firebase updated:", decision)

        return "OK", 200

    except Exception as e:
        print("❌ Error:", e)
        return "FAIL", 500


# 🔥 LATEST IMAGE
@app.route('/latest.jpg')
def latest():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    if not files:
        return "No image", 404
    return send_file(os.path.join(UPLOAD_FOLDER, files[0]), mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
