
# 🔐 Smart Door Lock System with Web App Control & Intelligent Access Logic

## 📌 Overview

This project is an **IoT-based Smart Door Lock System** powered by **ESP32-CAM** and controlled through a **web application**. It integrates **face recognition with rule-based access control**, making it more secure than traditional smart locks.

The system not only identifies users as **known or unknown**, but also enforces a **limited entry policy**, ensuring controlled and secure access.

---

## 🌐 Web App Integration

The system is fully controlled through a **web application**, which allows:

* 📷 Viewing captured images from ESP32-CAM
* 🧠 Monitoring detected users (Known / Unknown)
* 🔓 Sending Unlock / Lock commands remotely
* 🔢 Tracking remaining entry count
* 🚨 Observing access decisions in real-time

---

## 🚀 Key Features

* 📷 Image capture using ESP32-CAM
* 🌐 Web-based remote control system
* 🧠 Known vs Unknown face detection
* 🔢 Entry limit system (Max 3 entries)
* 🔓 Smart unlocking mechanism
* 🚫 Security against unauthorized access
* ☁️ Backend + database integration (Firebase / Server)

---

## 🧠 Intelligent Access Logic

The system follows a **secure decision-making algorithm**:

### ✅ Known Person Only

* Door **unlocks**
* Entry count **decreases by 1**
* Access allowed only if count > 0

### ❌ Unknown Person Only

* Door **remains locked**
* No change in entry count

### 🚫 Known + Unknown Together

* Door **does NOT unlock**
* Prevents unauthorized entry with valid user

### 🔢 Entry Limit Rule

* Maximum entries allowed = **3**
* Each successful unlock reduces the count
* When count reaches **0 → Access denied for all users**

---

## ⚙️ System Workflow

1. ESP32-CAM captures image
2. Image is sent to backend server
3. Face recognition identifies:

   * Known / Unknown
4. Logic is applied
5. Result sent to web app
6. User can:

   * Monitor status
   * Control door remotely
7. ESP32 activates relay accordingly

---

## 🛠️ Tech Stack

* **Hardware:** ESP32-CAM, Relay Module, Solenoid Lock
* **Frontend:** Web Application (HTML, CSS, JS)
* **Backend:** Node.js / Flask
* **Database:** Firebase Realtime Database
* **Communication:** HTTP / HTTPS

---

## 🔧 Hardware Components

* ESP32-CAM
* FTDI Programmer
* Relay Module
* Solenoid Door Lock
* Power Supply (5V & 12V)
* Jumper Wires

---

## 🔌 Circuit Connections

### ESP32-CAM → Relay

* GPIO → IN
* GND → GND
* 5V → VCC

### Power Supply

* ESP32-CAM → 5V
* Solenoid Lock → 12V

---

## 💻 Installation & Setup

### 1️⃣ Upload Code

* Open Arduino IDE
* Select **AI Thinker ESP32-CAM**
* Upload code

---

### 2️⃣ Configure Wi-Fi

```cpp id="c9e3h6"
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_PASSWORD";
```

---

### 3️⃣ Run Backend Server

**Node.js**

```bash id="y0mz0s"
npm install
node server.js
```

**OR Python**

```bash id="q8iw1p"
python app.py
```

---

### 4️⃣ Open Web App

* Open browser
* Enter server URL
* Monitor and control door

---

## ▶️ Usage

1. Turn ON system
2. Open web app
3. Person appears in front of camera
4. System detects identity
5. Logic applied:

   * ✅ Unlock (valid case)
   * ❌ Stay locked (invalid case)
6. User can also manually control door from web app

---


## 🔐 Security Advantages

* Prevents **unauthorized entry**
* Blocks **mixed identity access (Known + Unknown)**
* Implements **controlled usage via entry limit**
* Provides **remote monitoring via web app**

---
## Flow Explanation
The system starts by capturing an image using ESP32-CAM
The image is sent to the backend for face recognition
Based on detection:
✅ Known person → Allowed (if entry count available)
❌ Unknown person → Denied
🚫 Mixed (Known + Unknown) → Denied
Web app is updated with the result
Door is controlled accordingly

----



## ⚠️ Limitations

* Requires stable internet connection
* Depends on face recognition accuracy
* Entry count reset must be managed

---

## 🔮 Future Enhancements

* Admin dashboard in web app
* Face recognition improvement using AI models
* Mobile app version
* Real-time notifications (SMS/Email)
* Auto-reset entry limit

---

## 👨‍💻 Author

**Rahul Shaw**

---

## 📄 License

For academic and educational use only.


