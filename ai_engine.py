import requests
import face_recognition
import time
import os
from datetime import datetime, timedelta
import numpy as np
import cv2

# ---------------- CONFIG ----------------
FIREBASE_DECISION_URL = "https://smart-door-lock-715ba-default-rtdb.firebaseio.com/door/decision.json"
IMAGE_URL = "https://smart-door-86rk.onrender.com/latest.jpg"

# 🌙 NIGHT MODE
NIGHT_START = 21  # 9 PM
NIGHT_END = 6     # 6 AM

# 📁 LOAD KNOWN FACES
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FOLDER = os.path.join(BASE_DIR, "known_faces")

known_encodings = []
known_names = []

print("📁 Loading known faces...")

for file in os.listdir(KNOWN_FOLDER):
    path = os.path.join(KNOWN_FOLDER, file)

    img = face_recognition.load_image_file(path)
    enc = face_recognition.face_encodings(img)

    if len(enc) > 0:
        known_encodings.append(enc[0])
        known_names.append(file.split(".")[0])
        print("✅ Loaded:", file)

print("🎯 Total faces loaded:", len(known_names))

# ---------------- MEMORY ----------------
user_data = {}
MAX_ENTRIES = 3
BLOCK_TIME = 3600  # 1 hour

# ---------------- CONTROL ----------------
last_processed_time = 0
COOLDOWN = 5

# 🌙 NIGHT CHECK
def is_night():
    hour = datetime.now().hour
    return hour >= NIGHT_START or hour < NIGHT_END


# ---------------- MAIN LOOP ----------------
while True:
    try:
        print("\n📸 Checking image...")

        # COOLDOWN
        if time.time() - last_processed_time < COOLDOWN:
            time.sleep(1)
            continue

        # DOWNLOAD IMAGE
        response = requests.get(IMAGE_URL)

        if response.status_code != 200:
            print("❌ Failed to fetch image")
            time.sleep(3)
            continue

        file_bytes = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            print("❌ Image decode failed")
            time.sleep(3)
            continue

        # RESIZE
        small_img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        rgb = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb)

        decision = "WAITING"
        detected_names = []
        unknown_detected = False

        if len(face_locations) > 0:

            encodings = face_recognition.face_encodings(rgb, face_locations)

            for face_encoding in encodings:

                matches = face_recognition.compare_faces(
                    known_encodings, face_encoding, tolerance=0.45
                )
                distances = face_recognition.face_distance(
                    known_encodings, face_encoding
                )

                if len(distances) > 0:
                    best_match = np.argmin(distances)

                    if matches[best_match]:
                        name = known_names[best_match]
                        detected_names.append(name)
                        print(f"👤 Known: {name}")
                    else:
                        print("❌ Unknown detected")
                        unknown_detected = True
                else:
                    unknown_detected = True

            # ---------------- DECISION LOGIC ----------------

            # 🌙 NIGHT MODE
            if is_night():
                print("🌙 Night mode → manual approval required")
                decision = "WAITING"

            # 👥 MIXED OR UNKNOWN
            elif unknown_detected:
                print("⚠️ Mixed/Unknown → manual approval")
                decision = "WAITING"

            # ✅ ALL KNOWN
            else:
                print("✅ All persons are known")

                decision = "ALLOW"

                for name in detected_names:

                    if name not in user_data:
                        user_data[name] = {
                            "count": 0,
                            "blocked_until": None,
                            "deny_count": 0
                        }

                    user = user_data[name]

                    # ⛔ BLOCK CHECK
                    if user["blocked_until"] and datetime.now() < user["blocked_until"]:
                        print(f"⛔ {name} is BLOCKED")
                        decision = "DENY"
                        break

                    # 🎯 LIMIT CHECK
                    if user["count"] >= MAX_ENTRIES:
                        print(f"⚠️ {name} reached limit → manual required")
                        decision = "WAITING"
                        break

                # ✅ INCREMENT COUNTS
                if decision == "ALLOW":
                    for name in detected_names:
                        user_data[name]["count"] += 1
                        print(f"🔢 {name}: {user_data[name]['count']}/{MAX_ENTRIES}")

        else:
            print("⚠️ No face detected")
            decision = "WAITING"

        # ---------------- FIREBASE UPDATE ----------------
        requests.put(FIREBASE_DECISION_URL, json=decision)
        print("📡 Firebase:", decision)

        # ---------------- DENY TRACKING ----------------
        if decision == "DENY":
            for name in detected_names:
                if name not in user_data:
                    continue

                user_data[name]["deny_count"] += 1
                print(f"❌ {name} deny: {user_data[name]['deny_count']}")

                if user_data[name]["deny_count"] >= 3:
                    user_data[name]["blocked_until"] = datetime.now() + timedelta(seconds=BLOCK_TIME)
                    user_data[name]["deny_count"] = 0
                    print(f"⛔ {name} BLOCKED for 1 hour")

        # RESET DENY COUNT AFTER SUCCESS
        if decision == "ALLOW":
            for name in detected_names:
                user_data[name]["deny_count"] = 0

        last_processed_time = time.time()

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(2)