# Compressor Leakage Detection and Monitoring Dashboard (Simulation-Based)

Python sensor data banayega → MQTT se HiveMQ Cloud tak bhejega → subscriber
data receive karke CSV me save karega → Streamlit dashboard readings, charts
aur leakage status dikhayega. Real compressor connect kiye bina, simulated
readings se poora system test ho jaata hai.

## 1. Setup (ek baar)

```bash
pip install -r requirements.txt
```

## 2. Bina HiveMQ ke demo (sabse pehle ye chalao)

```bash
python run_demo.py
streamlit run layer1/dashboard.py
```

Browser: http://localhost:8501 — Pressure, Temperature, Airflow charts aur
Leakage Status dikhega. Har 5th reading me leak inject hota hai, taaki
"Possible Leakage" bhi dikhe, sirf Normal hi nahi.

## 3. HiveMQ Cloud ke saath live (Layer 2)

### Step A — .env banao (password kabhi code me mat likho)

```bash
# Windows: copy .env.example .env
# Mac/Linux: cp .env.example .env
```

`.env` me asli values bharo:
- **Host:** HiveMQ Cloud console → cluster `keenbee` → Overview se copy karo
  (jaise `xxxx.s1.eu.hivemq.cloud`)
- **Username/Password:** HiveMQ Cloud console → **Access Management →
  MQTT Credentials** wale. ⚠️ Ye cluster ke login password se ALAG hote hain.
- **Port:** 8883 (TLS ke saath)

### Step B — 3 alag terminals me, isi order me

Terminal 1 (subscriber pehle, taaki koi message miss na ho):
```bash
python layer2/mqtt_sensor_subscriber.py
```

Terminal 2 (publisher):
```bash
python layer2/mqtt_sensor_publisher.py
```

Terminal 3 (live dashboard — seedha HiveMQ se data):
```bash
streamlit run layer2/dashboard_live.py
```

Ya CSV wala dashboard:
```bash
streamlit run layer1/dashboard.py
```
(Subscriber CSV likhta hai, isliye ye dashboard bhi live ho jaata hai.)

## 4. Connection failed: 5 ka fix (yehi tumhara atka hua part tha)

MQTT me `rc = 5` ka matlab sirf ek hai: **Not authorized — login reject hua.**
Ye network ya code ka error nahi hai, isliye code badalne se theek nahi hoga.

Checklist, isi order me:
1. `.env` me username/password me koi extra space to nahi.
2. Username/password **Access Management → MQTT Credentials** wale hon —
   HiveMQ website ka login password yahan kaam nahi karega.
3. Us credential ki Permissions me **Publish + Subscribe dono** allowed hon,
   topic `compressor/sensor` par (ya `*` par).
4. Cluster `keenbee` **Running** ho, Paused nahi.
5. Port **8883 + TLS** ho — is project ke code me ye pehle se hai.
6. Publisher aur subscriber ka **client_id alag** ho — is project me hai
   (`compressor-publisher-vyom` vs `compressor-subscriber-vyom`).

Inme se ek theek karte hi subscriber me `✅ Connected to HiveMQ Cloud`
aana chahiye. Agar phir bhi 5 aaye, to HiveMQ console me naya MQTT
credential banao (Publish + Subscribe, topic `compressor/sensor`) aur
`.env` me wahi naya wala daalo — purana credential hi kharab hona sabse
common case hai.

## 5. Leakage detection logic (viva ke liye)

| Sign | Rule |
|---|---|
| Pressure low | < 6.2 bar → +2 |
| Sudden drop | Pichhli reading se > 0.8 bar girawat → +2 |
| Flow high | > 240 L/min → +1 |
| Temperature high | > 55 °C → +1 |

Score 3+ = **Possible Leakage**, 2 = **Warning**, 0–1 = **Normal**.
Ek value hilne se alarm nahi — ek se zyada signs ek saath milne par hi
leak declare hota hai, isliye false alarm kam hain.

Normal ranges: Pressure 6.8–7.5 bar, Temperature 35–50 °C, Flow 180–220 L/min.
Leak pattern: Pressure 5.0–6.0 bar, Temperature 55–65 °C, Flow 250–300 L/min.

## 6. Files

| File | Kaam |
|---|---|
| `layer1/synthetic_data.py` | Data generate + leakage logic |
| `layer1/save_csv.py` | CSV me save |
| `layer1/mqtt_publisher.py` / `mqtt_subscriber.py` | Layer 1 local MQTT |
| `layer1/dashboard.py` | CSV wala Streamlit dashboard |
| `layer2/sensor_data.py` | Layer 2 sensor data (wahi logic) |
| `layer2/mqtt_sensor_publisher.py` | HiveMQ par publish (TLS, 8883) |
| `layer2/mqtt_sensor_subscriber.py` | HiveMQ se receive + CSV (FIXED) |
| `layer2/dashboard_live.py` | Seedha HiveMQ se live dashboard |
| `layer3/database.py` + `dashboard_db.py` | SQLite DB + DB wala dashboard |
| `layer3/mqtt_db_subscriber.py` | HiveMQ se seedha DB me save |
| `layer3/import_csv_to_db.py` | Purani CSV ko DB me daalo |
| `layer4/flows.json` | Node-RED flow (HiveMQ + simulation + leak alert) |
| `layer5/dashboard_login.py` + `auth.py` | Login wala dashboard, admin/viewer roles |
| `layer5/create_user.py` | Naya user banao (hashed password) |
| `mobile-dashboard.html` | Phone par bina install ke dekhne wala demo |
| `config.py` | `.env` se credentials padhta hai |
| `run_demo.py` | Bina HiveMQ ke demo data |

## 7. GitHub par daalna

```bash
git init
git add .
git commit -m "Compressor leakage dashboard - Layer 1 + Layer 2"
```

`.env` apne aap ignore ho jayega (`.gitignore` me hai) — password
GitHub par kabhi nahi jayega. `data/compressor_data.csv` bhi ignore hai.

## Layer 3 — SQLite database

CSV ke bajay database me data, taaki purana data filter karke dekh sako.

```bash
python layer3/database.py              # DB banao + 5 demo rows
python layer3/import_csv_to_db.py      # purani CSV DB me daalo (dobara nahi dalta)
streamlit run layer3/dashboard_db.py   # DB wala dashboard (total + leak count + filter)
```

HiveMQ se seedha DB me save karne ke liye (Layer 2 subscriber jaisa,
sirf CSV ke bajay DB):
```bash
python layer3/mqtt_db_subscriber.py
```

## Layer 4 — Node-RED (visual flow)

Node-RED computer/server par chalta hai, phone par seedha nahi.
Poori steps `layer4/README.md` me hain. Short me:

```bash
npm install -g --unsafe-perm node-red
node-red   # phir http://localhost:1880
```

Phir Node-RED me Import → `layer4/flows.json` → HiveMQ broker node me
apna host/username/password bharo (8883 + TLS) → Deploy → Debug tab me
dekho. Bina HiveMQ ke test ke liye flow me `Simulate` node bhi hai
(har 2 second me simulated reading banata hai).

## Layer 5 — Login / user access

Bina login ke dashboard ka data nahi dikhega.

```bash
python layer5/create_user.py          # apna user banao (admin/viewer)
streamlit run layer5/dashboard_login.py
```

Demo login (submission se pehle apne users bana ke ye badal dena):
- admin / admin123 — sab kuch: stats + CSV download
- viewer / viewer123 — sirf dekh sakta hai, download nahi

Password plain text me kabhi save nahi hote — `users.json` me sirf
salt + PBKDF2 hash hota hai, aur wo file GitHub par nahi jayegi
(`.gitignore` me hai). Apna user banane ke baad demo wale kaam karenge,
lekin apne wale hi use karna behtar hai.

## Aage ka kaam (abhi bhi baaki, complete mat samajhna)

- Alerts (leak par email/notification) + real sensors se actual readings
- HiveMQ live end-to-end test — iske liye tumhara asli `.env` chahiye
