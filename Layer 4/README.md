# Layer 4 — Node-RED

Visual flow: HiveMQ se message aao → Leakage Detection function → Debug me
reading dikhao, aur leak ho to alag LEAK ALERT debug me dikhao.

## Chalane ke liye chahiye (computer/server par)

Node-RED phone par seedha nahi chalta — iske liye computer ya server
chahiye jahan Node.js ho. Phone par sirf ye flow file dekh sakte ho.

```bash
# Node.js install hone ke baad:
npm install -g --unsafe-perm node-red
node-red
```

Browser: http://localhost:1880

## Import karo

1. Node-RED kholo → upar-right menu (3 lines) → Import → `flows.json` select karo.
2. **HiveMQ broker node par double-click karo** aur ye bharo:
   - Server: HiveMQ console se keenbee cluster ka host
     (jaise `xxxx.s1.eu.hivemq.cloud`)
   - Port: `8883`
   - Enable secure (SSL/TLS) connection: ON
   - Username/Password: HiveMQ console → Access Management → MQTT Credentials
     wale (HiveMQ website ka login password nahi)
3. **Deploy** dabao (upar-right laal button).
4. Right side **Debug** tab kholo.

## Kya dikhega

- **All readings:** har aane wali reading (pressure, temperature, flow, leakage).
- **LEAK ALERT:** sirf tab jab status `Possible Leakage` ho.
- **Simulate node:** bina HiveMQ ke bhi test karne ke liye — ye har 2 second
  me khud simulated reading banata hai, aur wahi leakage logic lagta hai.
  Is node ko disable kar dena jab asli HiveMQ data chal raha ho, warna
  dono data mix ho jayenge (node par click → Disable).

## Logic (Python wali hi)

Pressure < 6.2 = +2, sudden drop > 0.8 = +2, Flow > 240 = +1, Temp > 55 = +1.
Score 3+ = Possible Leakage, 2 = Warning, 0–1 = Normal.
Ye logic `Leakage Detection` function node ke andar likha hai — wahan
khud padh aur viva me samjha sakte ho.
