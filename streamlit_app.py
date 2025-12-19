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
        
        /* BOTONES SUPERIORES Y CARTAS */
        .btn-group { display: flex; justify-content: space-around; gap: 5px; margin-bottom: 10px; }
        .mini-btn { flex: 1; font-size: 0.7rem; padding: 12px 0; background: #222; border: 1px solid #444; color: #888; border-radius: 8px; font-weight: bold; }
        .mini-btn.active { background: #ffcc00 !important; color: #000 !important; border-color: #fff; }

        .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 10px; }
        .c-btn { padding: 12px 0; font-size: 1.1rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 8px; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        /* RESULTADO */
        #res { display: none; padding: 20px; border-radius: 20px; margin-top: 10px; border: 4px solid #00ff00; }
        .dec-txt { font-size: 3.5rem; font-weight: 900; margin: 0; }

        /* MÓDULO FLOP CON PINTAS */
        #flop-section { display: none; background: #111; padding: 15px; border-radius: 20px; border: 2px solid #00ff00; margin-top: 15px; }
        .flop-display { display: flex; justify-content: center; gap: 10px; margin-bottom: 15px; min-height: 90px; }
        
        .card-ui { 
            width: 55px; height: 80px; background: #fff; color: #000; 
            border-radius: 10px; display: flex; flex-direction: column; 
            justify-content: center; align-items: center; font-weight: 900; font-size: 1.3rem;
            box-shadow: 0 4px 10px rgba(0,255,0,0.2);
        }

        .suit-selector { display: flex; justify-content: center; gap: 10px; margin-top: 10px; display: none; }
        .pinta-btn { flex: 1; padding: 15px; font-size: 1.8rem; border-radius: 10px; border: 2px solid #444; background: #222; color: #fff; }
        .red-suit { color: #ff4444 !important; border-color: #ff4444 !important; }

        /* HISTORIAL */
        .hist-box { margin-top: 25px; text-align: left; background: #0a0a0a; padding: 15px; border-radius: 12px; border: 1px solid #222; }
        .h-item { font-size: 0.75rem; padding: 10px 0; border-bottom: 1px solid #222; }
        .v-input { background: #222; border: 1px solid #444; color: #ffcc00; padding: 6px; border-radius: 5px; width: 85px; font-weight: bold; }
        
        .btn-action { width: 100%; padding: 22px; font-size: 1.5rem; font-weight: 900; border-radius: 15px; margin-top: 15px; border: none; }
    </style>
</head>
<body>
    <div class="btn-group">
        <button class="mini-btn active">30 BB</button>
        <button class="mini-btn">LATE POS</button>
    </div>

    <span class="row-label">TUS CARTAS</span>
    <div class="grid" id="g"></div>
    <div class="btn-group">
        <button class="mini-btn" id="btnS" onclick="setS(true)">SUITED (s)</button>
        <button class="mini-btn" id="btnO" onclick="setS(false)">OFFSUIT (o)</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        <button class="btn-action" style="background:#00ff00; color:#000;" onclick="showFlop()">INGRESAR FLOP (PINTAS)</button>
        <button class="btn-action" style="background:#fff; color:#000;" onclick="reset()">OTRA MANO</button>
    </div>

    <div id="flop-section">
        <span class="row-label">TABLERO DE MESA (FLOP)</span>
        <div class="flop-display" id="flop-view"></div>
        
        <div id="card-grid-flop" class="grid"></div>
        
        <div id="suit-picker" class="suit-selector">
            <button class="pinta-btn" onclick="selectSuit('♠')">♠</button>
            <button class="pinta-btn red-suit" onclick="selectSuit('♥')">♥</button>
            <button class="pinta-btn red-suit" onclick="selectSuit('♦')">♦</button>
            <button class="pinta-btn" onclick="selectSuit('♣')">♣</button>
        </div>
        
        <div id="ana-flop" style="color:#ffcc00; font-size:0.9rem; margin-top:10px; font-weight:bold;"></div>
    </div>

    <div class="hist-box">
        <span style="color:#ffcc00; font-size:0.8rem; display:block; margin-bottom:10px;">HISTORIAL Y REGISTRO DE VILLANOS</span>
        <div id="hList"></div>
    </div>

    <script>
        const cards = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null; 
        let tempVal = null; let flopFinal = [];

        function init() {
            const g = document.getElementById('g'); g.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button'); b.innerText = c; b.className = "c-btn";
                b.onclick = () => { if(sel.length < 2) { sel.push(c); b.classList.add('active'); if(sel.length==2 && same!==null) calc(); } };
                g.appendChild(b);
            });
            
            const fg = document.getElementById('card-grid-flop'); fg.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button'); b.innerText = c; b.className = "c-btn";
                b.onclick = () => { if(flopFinal.length < 3) { tempVal = c; document.getElementById('suit-picker').style.display = 'flex'; } };
                fg.appendChild(b);
            });
            updateH();
        }

        function setS(v) { same = v; if(sel.length == 2) calc(); }

        function calc() {
            const h1 = sel[0], h2 = sel[1];
            const isGood = (h1==='A' || h1===h2 || (h1==='K' && same));
            const r = document.getElementById('res'); r.style.display = 'block';
            document.getElementById('dec').innerText = isGood ? "RAISE" : "FOLD";
            r.style.backgroundColor = isGood ? "#27ae60" : "#c0392b";
            saveH(sel.join("")+(same?'s':'o'), document.getElementById('dec').innerText);
        }

        function showFlop() { document.getElementById('flop-section').style.display = 'block'; }

        function selectSuit(suit) {
            if(!tempVal || flopFinal.length >= 3) return;
            flopFinal.push({v: tempVal, s: suit});
            
            const view = document.getElementById('flop-view');
            const isRed = (suit === '♥' || suit === '♦');
            view.innerHTML += `<div class="card-ui" style="color:${isRed?'red':'black'}"><span>${tempVal}</span><span>${suit}</span></div>`;
            
            document.getElementById('suit-picker').style.display = 'none';
            tempVal = null;
            if(flopFinal.length === 3) analyze();
        }

        function analyze() {
            const ana = document.getElementById('ana-flop');
            const suits = flopFinal.map(f => f.s);
            const isFlush = suits.every(s => s === suits[0]);
            const isPair = new Set(flopFinal.map(f => f.v)).size < 3;
            
            if(isFlush) ana.innerHTML = "⚠️ ¡PELIGRO! MESA DE COLOR (FLUSH)";
            else if(isPair) ana.innerHTML = "⚠️ ¡CUIDADO! MESA DOBLADA (POSIBLE FULL)";
            else ana.innerHTML = "✅ MESA LIMPIA";
        }

        function saveH(m, a) {
            let h = JSON.parse(localStorage.getItem('ph_v2')) || [];
            h.unshift({m, a, v: '', t: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})});
            if(h.length > 5) h.pop();
            localStorage.setItem('ph_v2', JSON.stringify(h));
            updateH();
        }

        function updateH() {
            let h = JSON.parse(localStorage.getItem('ph_v2')) || [];
            document.getElementById('hList').innerHTML = h.map((x, i) => `
                <div class="h-item">
                    ${x.t} | MIA: <b>${x.m}</b> | ACCIÓN: <b>${x.a}</b> | 
                    GANÓ CON: <input class="v-input" placeholder="ej. A♥K♥" onchange="updateV(${i}, this.value)" value="${x.v}">
                </div>`).join('');
        }

        function updateV(i, val) {
            let h = JSON.parse(localStorage.getItem('ph_v2'));
            h[i].v = val;
            localStorage.setItem('ph_v2', JSON.stringify(h));
        }

        function reset() {
            sel = []; same = null; flopFinal = [];
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
