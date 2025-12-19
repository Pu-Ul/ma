import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="POKER RADAR + EXPORT", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 10px; }
        .bb-selector { display: flex; justify-content: space-around; margin-bottom: 12px; background: #111; padding: 5px; border-radius: 8px; }
        .bb-btn { flex: 1; margin: 0 3px; font-size: 0.75rem; padding: 10px 0; background: #222; border: 1px solid #444; color: #888; border-radius: 5px; }
        .bb-btn.active { background: #ffcc00 !important; color: #000 !important; font-weight: bold; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; max-width: 400px; margin: 0 auto; }
        .c-btn { padding: 15px 0; font-size: 1.4rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 6px; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; font-weight: bold; }
        .suit-main { display: flex; gap: 8px; margin: 12px auto; max-width: 400px; }
        .s-btn { flex: 1; padding: 15px; font-size: 1rem; font-weight: bold; border-radius: 8px; border: 1px solid #333; background: #1a1a1a; color: #555; }
        .s-btn.active-s { background: #0055ff !important; color: #fff !important; }
        .s-btn.active-o { background: #444 !important; color: #fff !important; }
        #res { display: none; margin-top: 10px; border: 2px solid #00ff00; background: #050505; padding: 15px; border-radius: 12px; }
        .dec { font-size: 2.2rem; font-weight: bold; margin-bottom: 2px; }
        .btn-clear { width: 100%; padding: 18px; background: #e74c3c; color: #fff; font-size: 1.3rem; font-weight: bold; border: none; border-radius: 10px; margin-top: 12px; }

        /* SECCIÓN HISTORIAL Y EXPORTACIÓN */
        .history-section { margin-top: 25px; text-align: left; background: #111; padding: 15px; border-radius: 10px; border: 1px solid #222; }
        .history-title { color: #ffcc00; font-size: 0.9rem; margin-bottom: 10px; display: block; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-bottom: 10px; }
        td { padding: 8px 5px; border-bottom: 1px solid #222; }
        .h-push { color: #00ff00; font-weight: bold; }
        .h-fold { color: #ff4444; }
        
        .btn-exp { width: 100%; padding: 10px; background: #27ae60; color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; margin-bottom: 5px; }
        .btn-del { width: 100%; padding: 8px; background: transparent; color: #555; border: 1px solid #333; border-radius: 5px; font-size: 0.7rem; }

        .footer { margin-top: 30px; padding: 15px; font-size: 0.9rem; color: #444; }
        .footer b { color: #00ff00; }
    </style>
</head>
<body>
    <div class="bb-selector">
        <button class="bb-btn" id="bb1" onclick="setBB(10)"> <10 BB </button>
        <button class="bb-btn active" id="bb2" onclick="setBB(30)"> 10-40 BB </button>
        <button class="bb-btn" id="bb3" onclick="setBB(50)"> 40+ BB </button>
    </div>

    <div class="grid" id="g"></div>
    
    <div class="suit-main">
        <button class="s-btn" id="btnS" onclick="setS(true)">SUITED (s)</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">OFFSUIT (o)</button>
    </div>

    <div id="res">
        <div id="dec" class="dec"></div>
        <div id="dream" style="font-size: 0.8rem; color: #ffcc00; margin: 10px 0;"></div>
        <button class="btn-clear" onclick="reset()">SIGUIENTE MANO</button>
    </div>

    <div class="history-section">
        <span class="history-title">📈 HISTORIAL DE TENDENCIAS</span>
        <table id="hTable">
            <tbody id="hBody"></tbody>
        </table>
        <button onclick="exportHistory()" class="btn-exp">📤 COPIAR HISTORIAL (BACKUP)</button>
        <button onclick="clearHistory()" class="btn-del">BORRAR TODO</button>
    </div>

    <div class="footer">Developed by <b>PauGaR</b></div>

    <script>
        const cards = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null; let bbs = 30;

        function init() {
            const g = document.getElementById('g'); g.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button');
                b.innerText = c; b.className = "c-btn";
                b.onclick = () => {
                    if(sel.length < 2) {
                        sel.push(c); b.classList.add('active');
                        if(sel.length === 2) {
                            if(sel[0] === sel[1]) { same = false; calc(); }
                            else if(same !== null) calc();
                        }
                    }
                };
                g.appendChild(b);
            });
            updateHistoryTable();
        }

        function setBB(v) { 
            bbs = v; 
            document.querySelectorAll('.bb-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
        }

        function setS(v) { 
            same = v; 
            document.getElementById('btnS').className = v ? "s-btn active-s" : "s-btn";
            document.getElementById('btnO').className = !v ? "s-btn active-o" : "s-btn";
            if(sel.length == 2) calc();
        }

        function calc() {
            const h1 = sel[0], h2 = sel[1];
            const idx1 = cards.indexOf(h1), idx2 = cards.indexOf(h2);
            const isP = h1 === h2;
            let d = document.getElementById('dec'), dr = document.getElementById('dream');
            
            document.getElementById('res').style.display = 'block';

            let action = ""; let colorClass = "";
            if (isP && idx1 <= 4) { action = "PUSH"; colorClass = "h-push"; d.style.color = "#00ff00"; }
            else if (h1 === 'A' && (idx2 <= 2 || same)) { action = "RAISE"; colorClass = "h-push"; d.style.color = "#00ff00"; }
            else { action = "FOLD"; colorClass = "h-fold"; d.style.color = "#ff4444"; }
            
            d.innerText = action;
            dr.innerText = isP ? "SUEÑO: PÓKER / FULL" : (same ? "SUEÑO: COLOR NUT" : "SUEÑO: ESCALERA/PARES");

            saveToHistory(`${h1}${h2}${isP?'':(same?'s':'o')}`, bbs, action, colorClass);
        }

        function saveToHistory(mano, bb, acc, cls) {
            let history = JSON.parse(localStorage.getItem('poker_hist')) || [];
            history.unshift({mano, bb, acc, cls, fecha: new Date().toLocaleTimeString()});
            if(history.length > 20) history.pop();
            localStorage.setItem('poker_hist', JSON.stringify(history));
            updateHistoryTable();
        }

        function updateHistoryTable() {
            let history = JSON.parse(localStorage.getItem('poker_hist')) || [];
            document.getElementById('hBody').innerHTML = history.map(h => 
                `<tr><td>${h.mano}</td><td>${h.bb}BB</td><td class="${h.cls}">${h.acc}</td><td style="color:#333;font-size:0.6rem">${h.fecha}</td></tr>`
            ).join('');
        }

        function exportHistory() {
            let history = JSON.parse(localStorage.getItem('poker_hist')) || [];
            let text = "HISTORIAL PAUGAR:\\n" + history.map(h => `${h.fecha} - ${h.mano} (${h.bb}BB): ${h.acc}`).join("\\n");
            navigator.clipboard.writeText(text).then(() => alert("¡Historial copiado! Pégalo en tus notas."));
        }

        function clearHistory() { if(confirm("¿Borrar todo?")) { localStorage.removeItem('poker_hist'); updateHistoryTable(); } }

        function reset() {
            sel = []; same = null;
            document.getElementById('res').style.display = 'none';
            document.getElementById('btnS').className = "s-btn";
            document.getElementById('btnO').className = "s-btn";
            init();
        }

        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=1100, scrolling=True)
