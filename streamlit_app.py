import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar Total", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 5px; }
        .row-label { font-size: 0.7rem; color: #ffcc00; font-weight: bold; display: block; margin: 10px 0; text-transform: uppercase; }
        
        /* GRID DE CARTAS */
        .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 10px; }
        .c-btn { padding: 12px 0; font-size: 1.1rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 8px; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        /* SELECTOR DE PINTAS (PALOS) */
        .suit-grid { display: flex; justify-content: center; gap: 10px; margin-bottom: 10px; }
        .pinta-btn { flex: 1; padding: 15px; font-size: 1.5rem; border-radius: 10px; border: 2px solid #333; background: #111; color: #fff; }
        .red { color: #ff4444 !important; border-color: #ff4444 !important; }
        
        #res { display: none; padding: 20px; border-radius: 20px; margin-top: 10px; }
        .dec-txt { font-size: 3.5rem; font-weight: 900; margin: 0; }

        /* MÓDULO FLOP DINÁMICO */
        #flop-section { display: none; background: #111; padding: 15px; border-radius: 20px; border: 2px solid #00ff00; margin-top: 15px; }
        .flop-display { display: flex; justify-content: center; gap: 8px; margin-bottom: 15px; min-height: 80px; }
        .card-ui { width: 50px; height: 75px; background: #fff; color: #000; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-weight: 900; font-size: 1.1rem; }

        .hist-box { margin-top: 25px; text-align: left; background: #0a0a0a; padding: 15px; border-radius: 12px; border: 1px solid #222; }
        .h-item { font-size: 0.75rem; padding: 8px 0; border-bottom: 1px solid #222; }
        .v-input { background: #222; border: 1px solid #444; color: #ffcc00; padding: 5px; border-radius: 4px; width: 80px; font-weight: bold; }
        .btn-action { width: 100%; padding: 20px; font-size: 1.5rem; font-weight: 900; border-radius: 15px; margin-top: 15px; border: none; }
    </style>
</head>
<body>
    <span class="row-label">TUS CARTAS</span>
    <div class="grid" id="g"></div>
    <div class="suit-grid">
        <button class="pinta-btn" onclick="setS(true)">SUITED (s)</button>
        <button class="pinta-btn" onclick="setS(false)">OFF (o)</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        <button class="btn-action" style="background:#00ff00; color:#000;" onclick="showFlop()">INGRESAR FLOP (PINTAS)</button>
        <button class="btn-action" style="background:#fff; color:#000;" onclick="reset()">OTRA MANO</button>
    </div>

    <div id="flop-section">
        <span class="row-label">MESA (ELIGE CARTA + PINTA)</span>
        <div class="flop-display" id="flop-view"></div>
        <div class="grid" id="fg"></div>
        <div class="suit-grid">
            <button class="pinta-btn" onclick="addFlopPinta('♠')">♠</button>
            <button class="pinta-btn red" onclick="addFlopPinta('♥')">♥</button>
            <button class="pinta-btn red" onclick="addFlopPinta('♦')">♦</button>
            <button class="pinta-btn" onclick="addFlopPinta('♣')">♣</button>
        </div>
        <div id="ana" style="color:#ffcc00; font-size:0.8rem; margin-top:10px;"></div>
    </div>

    <div class="hist-box">
        <span style="color:#ffcc00; font-size:0.8rem;">HISTORIAL PauGaR</span>
        <div id="hList"></div>
    </div>

    <script>
        const cards = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null; 
        let currentFlopVal = null; let flopFinal = [];

        function init() {
            const g = document.getElementById('g'); g.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button'); b.innerText = c; b.className = "c-btn";
                b.onclick = () => { if(sel.length < 2) { sel.push(c); b.classList.add('active'); if(sel.length==2 && same!==null) calc(); } };
                g.appendChild(b);
            });
            const fg = document.getElementById('fg'); fg.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button'); b.innerText = c; b.className = "c-btn";
                b.onclick = () => { currentFlopVal = c; b.style.borderColor = "#ffcc00"; };
                fg.appendChild(b);
            });
            updateH();
        }

        function setS(v) { same = v; if(sel.length == 2) calc(); }

        function calc() {
            const h1 = sel[0], h2 = sel[1];
            const isGood = (h1==='A' || (h1==='K' && same) || h1===h2);
            const r = document.getElementById('res'); r.style.display = 'block';
            const d = document.getElementById('dec');
            d.innerText = isGood ? "PUSH" : "FOLD";
            r.style.backgroundColor = isGood ? "#27ae60" : "#c0392b";
            saveH(sel.join("")+(same?'s':'o'), d.innerText);
        }

        function showFlop() { document.getElementById('flop-section').style.display = 'block'; }

        function addFlopPinta(p) {
            if(!currentFlopVal || flopFinal.length >= 3) return;
            flopFinal.push({v: currentFlopVal, p: p});
            const fView = document.getElementById('flop-view');
            const isRed = (p === '♥' || p === '♦');
            fView.innerHTML += `<div class="card-ui" style="color:${isRed?'red':'black'}"><span>${currentFlopVal}</span><span>${p}</span></div>`;
            currentFlopVal = null;
            document.querySelectorAll('#fg .c-btn').forEach(b => b.style.borderColor = "#333");
            if(flopFinal.length === 3) checkDanger();
        }

        function checkDanger() {
            const suits = flopFinal.map(f => f.p);
            const counts = {}; suits.forEach(s => counts[s] = (counts[s] || 0) + 1);
            const ana = document.getElementById('ana');
            if(Object.values(counts).some(v => v === 3)) {
                ana.innerHTML = "⚠️ ¡PELIGRO! MESA COLOR (FLUSH). El villano puede tener el color.";
            } else if (new Set(flopFinal.map(f => f.v)).size < 3) {
                ana.innerHTML = "⚠️ ¡MESA DOBLADA! Cuidado con el Full House.";
            } else {
                ana.innerHTML = "✅ Mesa seca. Sin peligros evidentes.";
            }
        }

        function saveH(m, a) {
            let h = JSON.parse(localStorage.getItem('ph')) || [];
            h.unshift({m, a, v: '', t: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})});
            if(h.length > 5) h.pop();
            localStorage.setItem('ph', JSON.stringify(h));
            updateH();
        }

        function updateH() {
            let h = JSON.parse(localStorage.getItem('ph')) || [];
            document.getElementById('hList').innerHTML = h.map((x, i) => `
                <div class="h-item">
                    ${x.t} | <b>${x.m}</b> | ${x.a} | Villano: <input class="v-input" placeholder="ej. J♥" onchange="updateV(${i}, this.value)" value="${x.v}">
                </div>`).join('');
        }

        function updateV(i, val) {
            let h = JSON.parse(localStorage.getItem('ph'));
            h[i].v = val;
            localStorage.setItem('ph', JSON.stringify(h));
        }

        function reset() {
            sel = []; same = null; flopFinal = []; currentFlopVal = null;
            document.getElementById('res').style.display = 'none';
            document.getElementById('flop-section').style.display = 'none';
            document.getElementById('flop-view').innerHTML = "";
            init();
        }
        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=1350, scrolling=True)
