import os
import sqlite3
import json
import http.server
import socketserver

DB_NAME = "database.db"

# 1. INITIALIZING STRUCTURAL PERSISTENT SQLITE3 LOCAL DATABASE SCHEMAS
def init_database():
    print("[DATABASE] Connecting to storage engine layer...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id TEXT PRIMARY KEY, name TEXT NOT NULL,
            gov_count INTEGER NOT NULL, pvt_count INTEGER NOT NULL,
            distance_km REAL NOT NULL, base_cost INTEGER NOT NULL,
            km_rate INTEGER NOT NULL, hospitals TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM locations")
    if cursor.fetchone() == 0:
        print("[DATABASE] Seeding regional spatial index matrices...")
        mock_data = [
            ("madhapur", "Madhapur Core Area", 4, 9, 6.8, 450, 35, "Medicover Hospitals, Madhapur | Image Hospitals"),
            ("gachibowli", "Gachibowli Financial Hub", 3, 12, 9.4, 550, 40, "Continental Hospitals | AIG Hospitals"),
            ("jubilee hills", "Jubilee Hills Checkpost", 6, 7, 3.2, 350, 30, "Apollo Hospitals | Indo-American Hospital"),
            ("kondapur", "Kondapur Botanical Zone", 2, 8, 8.1, 500, 35, "KIMS Hospital | Ar时代 Healthcare")
        ]
        cursor.executemany("INSERT INTO locations VALUES (?, ?, ?, ?, ?, ?, ?, ?)", mock_data)
        conn.commit()
        print("[DATABASE] Seeding sequence safely completed.")
    conn.close()

# 2. EMITTING COHESIVE INTERFACE LAYOUT STRUCTURES
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RescuNet MVP Prototype</title>
    <style>
        body {
            background-color: #020617; color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            margin: 0; padding: 0; min-height: 100vh; display: flex; flex-direction: column;
        }
        header {
            background-color: #0f172a; border-bottom: 1px solid #1e293b; padding: 16px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .header-title-box { display: flex; align-items: center; gap: 12px; }
        .logo-badge { background-color: #e11d48; padding: 8px 12px; border-radius: 8px; font-weight: bold; }
        .prototype-tag { font-size: 0.75rem; background-color: rgba(244, 63, 94, 0.2); color: #f43f5e; padding: 2px 8px; border-radius: 9999px; margin-left: 8px; border: 1px solid rgba(244, 63, 94, 0.3); }
        .security-badge { font-size: 0.75rem; color: #10b981; background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 6px 12px; border-radius: 6px; }
        main { max-width: 1200px; width: 95%; margin: 20px auto; display: grid; grid-template-columns: 1fr; gap: 24px; }
        @media (min-width: 768px) { main { grid-template-columns: 5fr 7fr; } }
        .panel-card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); }
        .panel-title { font-size: 0.875rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 16px 0; font-weight: bold; }
        .input-group { margin-bottom: 16px; position: relative; }
        .input-label { font-size: 0.65rem; color: #94a3b8; font-weight: bold; display: block; margin-bottom: 6px; letter-spacing: 0.05em; text-transform: uppercase; }
        .input-field { width: 92%; background-color: #020617; border: 1px solid #1e293b; border-radius: 8px; padding: 10px 14px; color: #cbd5e1; font-size: 0.875rem; }
        .input-field:focus { outline: none; border-color: #3b82f6; }
        .suggestions-dropdown { position: absolute; top: 100%; left: 0; width: 98%; background-color: #0f172a; border: 1px solid #334155; border-radius: 8px; z-index: 50; max-height: 180px; overflow-y: auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); margin-top: 4px; display: none; }
        .suggestion-item { padding: 10px 14px; cursor: pointer; font-size: 0.825rem; border-bottom: 1px solid #1e293b; color: #cbd5e1; }
        .suggestion-item:hover { background-color: #1e293b; color: #fff; }
        .suggestion-item:last-child { border-bottom: none; }
        .tabs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
        .tab-btn { background-color: #020617; border: 2px solid #1e293b; border-radius: 12px; padding: 14px; color: #94a3b8; cursor: pointer; text-align: center; transition: all 0.3s ease; }
        .tab-btn.active-gov { border-color: #f43f5e; color: #fff; box-shadow: 0 0 15px rgba(244,63,94,0.15); }
        .tab-btn.active-pvt { border-color: #fbbf24; color: #fff; box-shadow: 0 0 15px rgba(251,191,36,0.15); }
        .tab-icon { font-size: 1.5rem; margin-bottom: 4px; }
        .tab-title { font-size: 0.75rem; font-weight: bold; display: block; }
        .tab-sub { font-size: 0.65rem; color: #10b981; display: block; margin-top: 2px; }
        .pricing-invoice-panel { background-color: #020617; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 16px; display: none; }
        .invoice-line { display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b; margin-bottom: 4px; }
        .invoice-total { display: flex; justify-content: space-between; font-size: 0.875rem; font-weight: bold; color: #fbbf24; border-top: 1px dashed #1e293b; padding-top: 6px; margin-top: 6px; }
        .radar-status-bar { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; background-color: #020617; padding: 10px; border-radius: 8px; border: 1px solid #1e293b; margin-bottom: 16px; font-size: 0.75rem; text-align: center; }
        .radar-count-label { font-size: 0.875rem; font-weight: bold; margin-top: 2px; }
        .action-btn { width: 100%; background-color: #e11d48; color: white; border: none; padding: 14px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 0.875rem; letter-spacing: 0.025em; transition: background 0.2s; }
        .action-btn:hover { background-color: #be123c; }
        .action-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .timeline-box { position: relative; padding-left: 24px; border-left: 2px solid #1e293b; margin-left: 10px; }
        .timeline-step { position: relative; margin-bottom: 24px; }
        .timeline-dot { position: absolute; left: -33px; top: 2px; width: 16px; height: 16px; border-radius: 50%; background-color: #334155; color: #94a3b8; font-size: 9px; font-weight: bold; display: flex; align-items: center; justify-content: center; }
        .timeline-step.active .timeline-dot { background-color: #fbbf24; color: #020617; }
        .timeline-step.completed .timeline-dot { background-color: #10b981; color: #020617; }
        .timeline-text { font-weight: bold; margin: 0; font-size: 0.875rem; color: #64748b; }
        .timeline-step.active .timeline-text, .timeline-step.completed .timeline-text { color: #e2e8f0; }
        .timeline-sub { font-size: 0.75rem; color: #475569; margin: 4px 0 0 0; }
        .timeline-step.active .timeline-sub { color: #94a3b8; }
        .map-wrapper { display: flex; flex-direction: column; height: 100%; }
        .map-header { background-color: #1e293b; border-bottom: 1px solid #334155; padding: 10px 16px; border-top-left-radius: 12px; border-top-right-radius: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; }
        .map-viewport { background-color: #020617; height: 260px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; position: relative; overflow: hidden; border: 1px solid #1e293b; border-top: none; }
        .map-grid { position: absolute; inset: 0; opacity: 0.05; background-image: linear-gradient(#94a3b8 1px, transparent 1px), linear-gradient(90deg, #94a3b8 1px, transparent 1px); background-size: 20px 20px; }
        .eta-badge { font-family: monospace; background-color: #020617; color: #f43f5e; padding: 4px 8px; border-radius: 6px; border: 1px solid #334155; font-weight: bold; }
        .patient-node { position: absolute; top: 50%; left: 33.333%; transform: translate(-50%, -50%); text-align: center; z-index: 10; display: none; }
        .patient-icon { background-color: #2563eb; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #fff; font-size: 14px; box-shadow: 0 0 10px rgba(37,99,235,0.5); }
        .ambulance-sprite { position: absolute; top: 25%; left: 85%; transform: translate(-50%, -50%); text-align: center; z-index: 20; display: none; transition: all 0.15s linear; }
        .amb-icon-bg { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #fff; font-size: 16px; }
        .icon-rose { background-color: #e11d48; box-shadow: 0 0 15px rgba(225,29,72,0.4); }
        .icon-amber { background-color: #d97706; box-shadow: 0 0 15px rgba(217,119,6,0.4); }
        .node-label { font-size: 0.6rem; font-weight: bold; display: block; margin-top: 4px; background: rgba(2,6,23,0.8); padding: 2px 6px; border-radius: 4px; border: 1px solid #1e293b; white-space: nowrap; }
        .label-blue { color: #93c5fd; }
        .label-rose { color: #f43f5e; }
        .label-amber { color: #fbbf24; }
        .map-watermark { position: absolute; inset: 0; background: rgba(2,6,23,0.3); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #475569; font-family: monospace; letter-spacing: 0.05em; text-transform: uppercase; transition: opacity 0.3s; }
        .display-none { display: none !important; }
        .terminal-panel { background-color: #020617; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; font-family: monospace; font-size: 0.75rem; height: 160px; display: flex; flex-direction: column; margin-top: 20px; }
        .terminal-header { color: #475569; border-bottom: 1px solid #1e293b; padding-bottom: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; font-weight: bold; }
        .terminal-stream { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
        .log-time { color: #334155; margin-right: 6px; font-weight: bold; }
    </style>
</head>
<body>
    <header>
        <div class="header-title-box">
            <div class="logo-badge">🚨 RescuNet</div>
            <span class="prototype-tag">MVP PROTOTYPE</span>
        </div>
        <div class="security-badge">● JWT Integrity Secure</div>
    </header>
    <main>
        <section style="display: flex; flex-direction: column; gap: 20px;">
            <div class="panel-card">
                <p class="panel-title">Allocation Nodes</p>
                <div class="input-group">
                    <span class="input-label">Manually Type Location (e.g. Madhapur, Gachibowli)</span>
                    <input type="text" id="locationInput" class="input-field" placeholder="Type neighborhood name..." onkeyup="handleLocationTyping(this.value)">
                    <div id="suggestionsDropdown" class="suggestions-dropdown"></div>
                </div>
                <div class="input-group">
                    <span class="input-label">SELECT STRATEGIC PIPELINE TIER</span>
                    <div class="tabs-grid">
                        <div id="btnGov" onclick="selectTier('gov')" class="tab-btn active-gov">
                            <div class="tab-icon">🚒</div>
                            <span class="tab-title">108 Gov</span>
                            <span class="tab-sub">₹0 Free Core</span>
                        </div>
                        <div id="btnPvt" onclick="selectTier('pvt')" class="tab-btn">
                            <div class="tab-icon">🤝</div>
                            <span class="tab-title">Private Fleet</span>
                            <span class="tab-sub" id="pvtSub" style="color: #64748b;">Market API</span>
                        </div>
                    </div>
                </div>
                <div id="priceInvoice" class="pricing-invoice-panel">
                    <div class="invoice-line"><span>Ecosystem Base Flag Rate</span><span id="invoiceBase">₹0</span></div>
                    <div class="invoice-line"><span>Distance Metric Rate (<span id="invoiceKmText">0</span> KM)</span><span id="invoiceDist">₹0</span></div>
                    <div class="invoice-total"><span>Total Projected Cost</span><span id="invoiceTotalCost">₹0</span></div>
                </div>
                <button id="dispatchBtn" onclick="startDispatch()" class="action-btn" disabled>Select Location From Suggestions</button>
            </div>
            <div class="panel-card">
                <p class="panel-title">Ecosystem Proximity Radar (Live)</p>
                <div class="radar-status-bar">
                    <div style="border-right: 1px solid #1e293b;">
                        <span style="color: #f43f5e; font-weight: bold;">Gov 108 Available</span>
                        <div class="radar-count-label" id="govRadarCount">--</div>
                    </div>
                    <div>
                        <span style="color: #fbbf24; font-weight: bold;">Private Idling</span>
                        <div class="radar-count-label" id="pvtRadarCount">--</div>
                    </div>
                </div>
                <p class="panel-title" style="margin-top: 16px; font-size: 0.75rem;">State Machine Tracker</p>
                <div class="timeline-box" id="timeline">
                    <div class="timeline-step" id="step1"><div class="timeline-dot" id="dot1">1</div><p class="timeline-text">Geocoding & Safety Checks</p><p class="timeline-sub" id="sub1">Awaiting client location submission loop...</p></div>
                    <div class="timeline-step" id="step2"><div class="timeline-dot" id="dot2">2</div><p class="timeline-text">Querying Fleet Registry Assets</p><p class="timeline-sub" id="sub2">Locating operational signatures via radius indices.</p></div>
                    <div class="timeline-step" id="step3"><div class="timeline-dot" id="dot3">3</div><p class="timeline-text">Handshake Secured & Dispatched</p><p class="timeline-sub" id="sub3">Awaiting tunnel layer activation loops.</p></div>
                </div>
            </div>
        </section>
        <section class="map-wrapper">
            <div class="map-header"><span style="font-weight: bold; color: #94a3b8;">🛰️ SIMULATED VIEWPORT</span><span class="eta-badge" id="etaDisplay">ETA: STANDBY</span></div>
            <div class="map-viewport">
                <div class="map-grid"></div>
                <svg style="position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none;"><line id="routeLine" x1="33.333%" y1="50%" x2="85%" y2="25%" stroke="#f43f5e" stroke-width="2" stroke-dasharray="5" class="display-none" /></svg>
                <div class="patient-node" id="patientUiNode"><div class="patient-icon">👤</div><span class="node-label label-blue" id="patientLabelText">Patient Node</span></div>
                <div id="ambulanceSprite" class="ambulance-sprite"><div id="ambIconBg" class="amb-icon-bg icon-rose"><span id="ambIcon">🚒</span></div><span id="ambLabel" class="node-label label-rose">Gov 108</span></div>
                <div id="idleWatermark" class="map-watermark">Awaiting Simulation Loop Trigger</div>
            </div>
            <div class="terminal-panel">
                <div class="terminal-header"><span>SYSTEM CORE DATA LOGGER</span><span style="color: #10b981;">● ONLINE</span></div>
                <div id="terminalStream" class="terminal-stream"></div>
            </div>
        </section>
    </main>
    <script>
        let selectedEcosystem = 'gov'; let simulationInterval = null; let selectedLocation = null;
        const locationDatabase = {
            "madhapur": { name: "Madhapur Core Area", govCount: 4, pvtCount: 9, distanceKm: 6.8, baseCost: 450, kmRate: 35, hospitals: ["Medicover Hospitals, Madhapur", "Image Hospitals"] },
            "gachibowli": { name: "Gachibowli Financial Hub", govCount: 3, pvtCount: 12, distanceKm: 9.4, baseCost: 550, kmRate: 40, hospitals: ["Continental Hospitals", "AIG Hospitals"] },
            "jubilee hills": { name: "Jubilee Hills Checkpost", govCount: 6, pvtCount: 7, distanceKm: 3.2, baseCost: 350, kmRate: 30, hospitals: ["Apollo Hospitals", "Indo-American Hospital"] },
            "kondapur": { name: "Kondapur Botanical Zone", govCount: 2, pvtCount: 8, distanceKm: 8.1, baseCost: 500, kmRate: 35, hospitals: ["KIMS Hospital", "Ar时代 Healthcare"] }
        };
        window.addEventListener('DOMContentLoaded', () => {
            const s = document.getElementById('terminalStream'); if (!s) return; const t = new Date().toLocaleTimeString();
            s.innerHTML += `<div><span class="log-time">[${t}]</span> <span style="color:#10b981;">[SYSTEM] Core database pipeline synchronized.</span></div>`;
            s.innerHTML += `<div><span class="log-time">[${t}]</span> <span style="color:#10b981;">[SYSTEM] Hybrid regional tariff arrays active.</span></div>`;
        });
        function handleLocationTyping(v) {
            const d = document.getElementById('suggestionsDropdown'); d.innerHTML = ''; if (!v || simulationInterval) { d.style.display = 'none'; return; }
            const k = v.toLowerCase().trim(); const m = Object.keys(locationDatabase).filter(x => x.includes(k));
            if (m.length > 0) { d.style.display = 'block'; m.forEach(x => { const i = document.createElement('div'); i.className = 'suggestion-item'; i.innerText = locationDatabase[x].name; i.onclick = () => selectLocation(x); d.appendChild(i); }); } else { d.style.display = 'none'; }
        }
        function selectLocation(x) {
            selectedLocation = locationDatabase[x]; document.getElementById('locationInput').value = selectedLocation.name; document.getElementById('suggestionsDropdown').style.display = 'none';
            document.getElementById('govRadarCount').innerText = selectedLocation.govCount + " Units Active"; document.getElementById('pvtRadarCount').innerText = selectedLocation.pvtCount + " Units Idling";
            document.getElementById('patientLabelText').innerText = "Location: " + selectedLocation.name; document.getElementById('patientUiNode').style.display = 'block'; document.getElementById('ambulanceSprite').style.display = 'block';
            const b = document.getElementById('dispatchBtn'); b.disabled = false; b.innerText = "⚡ Initialize Routing Instance"; calculateInvoice();
            logToTerminal(`Location locked: ${selectedLocation.name}. Nearby Facilities: ${selectedLocation.hospitals.join(' | ')}`);
        }
        function calculateInvoice() {
            if (!selectedLocation) return; const p = document.getElementById('priceInvoice');
            if (selectedEcosystem === 'pvt') { p.style.display = 'block'; const dC = Math.round(selectedLocation.distanceKm * selectedLocation.kmRate); const gT = selectedLocation.baseCost + dC; document.getElementById('invoiceBase').innerText = `₹${selectedLocation.baseCost}`; document.getElementById('invoiceKmText').innerText = selectedLocation.distanceKm; document.getElementById('invoiceDist').innerText = `₹${dC}`; document.getElementById('invoiceTotalCost').innerText = `₹${gT}`; } else { p.style.display = 'none'; }
        }
        function logToTerminal(m, y = 'info') { const s = document.getElementById('terminalStream'); if (!s) return; const t = new Date().toLocaleTimeString(); let c = '#cbd5e1'; if (y === 'warn') c = '#fbbf24'; if (y === 'success') c = '#22d3ee'; s.innerHTML += `<div><span class="log-time">[${t}]</span> <span style="color:${c}">${m}</span></div>`; s.scrollTop = s.scrollHeight; }
        function selectTier(t) {
            if (simulationInterval) return; selectedEcosystem = t; const bG = document.getElementById('btnGov'); const bP = document.getElementById('btnPvt'); const pS = document.getElementById('pvtSub'); const aL = document.getElementById('ambLabel'); const aI = document.getElementById('ambIcon'); const aB = document.getElementById('ambIconBg'); const rL = document.getElementById('routeLine');
            if (t === 'gov') { bG.className = "tab-btn active-gov"; bP.className = "tab-btn"; pS.style.color = "#64748b"; if (aL) { aL.innerText = "Gov 108"; aL.className = "node-label label-rose"; } if (aI) aI.innerText = "🚒"; if (aB) aB.className = "amb-icon-bg icon-rose"; if (rL) rL.setAttribute('stroke', '#f43f5e'); } else { bG.className = "tab-btn"; bP.className = "tab-btn active-pvt"; pS.style.color = "#fbbf24"; if (aL) { aL.innerText = "Pvt Med-Cab"; aL.className = "node-label label-amber"; } if (aI) aI.innerText = "🚑"; if (aB) aB.className = "amb-icon-bg icon-amber"; if (rL) rL.setAttribute('stroke', '#f59e0b'); } calculateInvoice(); logToTerminal(`Routing tier switched to ${t === 'gov' ? 'Government 108' : 'Private Aggregator Network'}.`);
        }
        function startDispatch() {
            if (!selectedLocation || simulationInterval) return; const w = document.getElementById('idleWatermark'); if (w) w.classList.add('display-none');
            const a = document.getElementById('ambulanceSprite'); const r = document.getElementById('routeLine'); const b = document.getElementById('dispatchBtn'); const e = document.getElementById('etaDisplay');
            if (a) { a.style.left = '85%'; a.style.top = '25%'; } if (r) r.classList.add('display-none'); if (e) { e.innerText = "ETA: SPINNING UP"; e.style.color = "#fbbf24"; } if (b) { b.disabled = true; b.innerText = "🚨 DISPATCH ACTIVE"; }
            document.getElementById('step2').className = "timeline-step"; document.getElementById('dot2').innerHTML = "2"; document.getElementById('step3').className = "timeline-step"; document.getElementById('dot3').innerHTML = "3";
            logToTerminal(`Initializing emergency dispatch route allocation for ${selectedLocation.name}...`, 'warn');
            setTimeout(() => { document.getElementById('dot1').innerHTML = "✓"; document.getElementById('step1').className = "timeline-step completed"; logToTerminal(`Target suggestions verified from local cluster: ${selectedLocation.hospitals.join(' & ')}`, 'success'); document.getElementById('step2').className = "timeline-step active"; }, 1000);
            setTimeout(() => { document.getElementById('dot2').innerHTML = "✓"; document.getElementById('step2').className = "timeline-step completed"; if (r) { r.classList.remove('display-none'); r.setAttribute('x2', '85%'); r.setAttribute('y2', '25%'); } logToTerminal(`Secure link assigned to available cluster node: AMB-${selectedEcosystem.toUpperCase()}-9942`, 'success'); document.getElementById('step3').className = "timeline-step active"; }, 2500);
            setTimeout(() => { document.getElementById('dot3').innerHTML = "●"; logToTerminal("Commencing geographic tracking mechanics loop.", 'success'); runAnimation(); }, 4000);
        }
        function runAnimation() {
            const a = document.getElementById('ambulanceSprite'); const r = document.getElementById('routeLine'); const e = document.getElementById('etaDisplay'); const b = document.getElementById('dispatchBtn');
            let sL = 85, sT = 25, tL = 33.333, tT = 50, p = 0;
            simulationInterval = setInterval(() => {
                p += 2;
                if (p <= 100) {
                    let cL = sL + (tL - sL) * (p / 100); let cT = sT + (tT - sT) * (p / 100);
                    if (a) { a.style.left = cL + '%'; a.style.top = cT + '%'; } if (r) { r.setAttribute('x2', cL + '%'); r.setAttribute('y2', cT + '%'); }
                    let m = Math.ceil(12 * (1 - (p / 100))); if (e) { e.innerText = `ETA: ${m} MINS`; }
                    if (p % 20 === 0) { logToTerminal(`Telemetry Sync: Radius delta remaining -> ${(selectedLocation.distanceKm * (1 - (p / 100))).toFixed(2)} KM`); }
                } else {
                    clearInterval(simulationInterval); simulationInterval = null; document.getElementById('dot3').innerHTML = "✓"; document.getElementById('step3').className = "timeline-step completed";
                    if (e) { e.innerText = "ARRIVED"; e.style.color = "#10b981"; } if (r) r.classList.add('display-none'); logToTerminal("Vehicle arrived safely at target scene coordinates.", 'success');
                    if (b) { b.disabled = false; b.innerText = "⚡ Initialize Routing Instance"; }
                }
            }, 150);
        }
    </script>
</body>
</html>
"""

# 3. RUNTIME PIPELINE BUILDER & RELATIONAL DATABASE AUTOMATION ENGINE
def run():
    print("[SYSTEM] Starting structural asset build compilation...")
    init_database()
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("[SYSTEM] Native client interface cleanly generated inside 'index.html'.")
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        print("\n" + "="*65)
        print("🚀 LOCAL MICROSERVER STACK STABILIZED ON PORT 8000")
        print("👉 Laptop Preview Portal Link: http://localhost:8000")
        print("👉 Tunneling Reference: Use local port 8000 for Pinggy or ngrok hooks.")
        print("="*65 + "\n")
        print("[SYSTEM] Operational socket monitoring layer listening for incoming client tunnels...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SYSTEM] Relational database environment session closed safely.")

if __name__ == "__main__":
    run()
