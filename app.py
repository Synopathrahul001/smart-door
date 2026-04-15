from flask import Flask, request, send_file, render_template
from flask_cors import CORS
import requests
import os
import time

# 🧠 AI
import face_recognition
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# 🔥 FIREBASE
FIREBASE_URL = "https://smart-door-lock-715ba-default-rtdb.firebaseio.com/door.json"
SECRET_KEY = "secret123"

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🧠 LOAD KNOWN FACES
known_encodings = []
known_names = []

def load_faces():
    for file in os.listdir("known_faces"):
        path = os.path.join("known_faces", file)

        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(file.split(".")[0])
            print(f"✅ Loaded: {file}")

load_faces()

# 🧠 MEMORY SYSTEM (ENTRY + BLOCK)
user_data = {}

MAX_ENTRIES = 3
BLOCK_TIME = 3600  # 1 hour

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

# 📸 RECEIVE IMAGE + 🧠 AI
@app.route('/upload', methods=['POST'])
def upload():
    if request.headers.get("Authorization") != SECRET_KEY:
        return "Unauthorized", 401

    try:
        data = request.get_data()

        filename = f"image_{int(time.time())}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(data)

        print("📸 Image saved:", filename)

        # 🧠 FACE RECOGNITION
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)

        decision = "WAITING"

        if len(encodings) > 0:
            face_encoding = encodings[0]

            matches = face_recognition.compare_faces(known_encodings, face_encoding)

            if True in matches:

                index = matches.index(True)
                person_name = known_names[index]

                print(f"👤 Detected: {person_name}")

                # 🧠 INIT USER
                if person_name not in user_data:
                    user_data[person_name] = {
                        "count": 0,
                        "blocked_until": None
                    }

                user = user_data[person_name]

                # ⛔ CHECK BLOCK
                if user["blocked_until"] and datetime.now() < user["blocked_until"]:
                    print("⛔ User BLOCKED")
                    decision = "DENY"

                else:
                    # ✅ ENTRY COUNT CHECK
                    if user["count"] < MAX_ENTRIES:
                        user["count"] += 1
                        decision = "ALLOW"
                        print(f"✅ Entry {user['count']} / {MAX_ENTRIES}")

                    else:
                        # 🔒 BLOCK USER
                        user["blocked_until"] = datetime.now() + timedelta(seconds=BLOCK_TIME)
                        user["count"] = 0
                        decision = "DENY"
                        print("⛔ Blocked for 1 hour")

            else:
                print("❌ Unknown Person")

        else:
            print("⚠️ No face detected")

        # 🔗 IMAGE URL
        image_url = request.host_url + f"static/{filename}"

        # 🔥 UPDATE FIREBASE
        update_firebase(image_url, decision)

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
