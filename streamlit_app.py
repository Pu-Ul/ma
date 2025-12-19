import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR POKER PRO", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 10px; }
        
        /* SELECTOR DE CIEGAS */
        .bb-selector { display: flex; justify-content: space-around; margin-bottom: 12px; background: #111; padding: 6px; border-radius: 10px; border: 1px solid #333; }
        .bb-btn { flex: 1; margin: 0 4px; font-size: 0.8rem; padding: 12px 0; background: #222; border: 1px solid #444; color: #888; border-radius: 6px; cursor: pointer; }
        .bb-btn.active { background: #ffcc00 !important; color: #000 !important; font-weight: bold; border-color: #fff; }

        /* GRID DE CARTAS */
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; max-width: 400px; margin: 0 auto; }
        .c-btn { padding: 18px 0; font-size: 1.5rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 8px; cursor: pointer; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; font-weight: bold; }
        
        /* SELECTOR SUITED */
        .suit-main { display: flex; gap: 10px; margin: 15px auto; max-width: 400px; }
        .s-btn { flex: 1; padding: 18px; font-size: 1rem; font-weight: bold; border-radius: 10px; border: 2px solid #333; background: #1a1a1a; color: #666; cursor: pointer; }
        .s-btn.active-s { background: #0055ff !important; color: #fff !important; border-color: #fff; }
        .s-btn.active-o { background: #444 !important; color: #fff !important; border-color: #bbb; }

        /* RESULTADOS */
        #res { display: none; margin-top: 10px; border: 3px solid #00ff00; background: #050505; padding: 20px; border-radius: 15px; box-shadow: 0 0 15px rgba(0,255,0,0.3); }
        .dec { font-size: 2.6rem; font-weight: bold; margin-bottom: 5px; }
        
        .dream-container { background: #111; padding: 12px; border-radius: 10px; border-left: 5px solid #ffcc00; margin: 15px 0; text-align: left; }
        .dream-label { font-size: 0.7rem; color: #ffcc00; font-weight: bold; display: block; margin-bottom: 4px; }
        .dream-text { font-size: 1.1rem; color: #fff; font-weight: bold; }

        .btn-clear { width: 100%; padding: 22px; background: #e74c3c; color: #fff; font-size: 1.4rem; font-weight: bold; border: none; border-radius: 12px; margin-top: 15px; cursor: pointer; }

        /* HISTORIAL */
        .history-section { margin-top: 25px; text-align: left; background: #111; padding: 15px; border-radius: 10px; border: 1px solid #222; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        td { padding: 10px 5px; border-bottom: 1px solid #222; }
        .h-push { color: #00ff00; font-weight: bold; }
        .h-fold { color: #ff4444; }
        
        .btn-exp { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; margin: 10px 0; }
        .footer { margin-top: 30px; padding: 20px; font-size: 0.9rem; color: #444; border-top: 1px solid #111; }
        .footer b { color: #00ff00; text-shadow: 0 0 5px rgba(0,255,0,0.3); }
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
        <div class="dream-container">
            <span class="dream-label">✨ EL SUEÑO (POTENCIAL MAX)</span>
            <span id="dream" class="dream-text"></span>
        </div>
        <button class="btn-clear" onclick="reset()">SIGUIENTE MANO</button>
    </div>

    <div class="history-section">
        <span style="color:#ffcc00; font-weight:bold; font-size:0.9rem;">📈 TENDENCIAS PauGaR</span>
        <table><tbody id="hBody"></tbody></table>
        <button onclick="exportHistory()" class="btn-exp">📤 COPIAR HISTORIAL</button>
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
            if(sel.length == 2) calc();
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
            const dist = Math.abs(idx1 - idx2);
            
            document.getElementById('res').style.display = 'block';

            // Lógica El Sueño
            let dr = document.getElementById('dream');
            if (isP) dr.innerText = "PÓKER / FULL HOUSE";
            else if (same) dr.innerText = (dist === 1 || (h1==='A' && h2==='K')) ? "ESC. COLOR / COLOR NUT" : "COLOR AL " + h1;
            else if (dist <= 4) dr.innerText = "ESCALERA NUT";
            else dr.innerText = "DOBLES / TOP PAIR";

            // Lógica Decisión
            let d = document.getElementById('dec');
            let action = ""; let cls = "";
            if (isP && idx1 <= 5) { action = (bbs<15)?"ALL-IN":"RAISE"; cls="h-push"; d.style.color="#00ff00"; }
            else if (h1==='A' && (idx2<=3 || same)) { action = (bbs<12)?"SHOVE":"RAISE"; cls="h-push"; d.style.color="#00ff00"; }
            else { action = "FOLD"; cls="h-fold"; d.style.color="#ff4444"; }
            
            d.innerText = action;
            saveToHistory(`${h1}${h2}${isP?'':(same?'s':'o')}`, bbs, action, cls);
        }

        function saveToHistory(mano, bb, acc, cls) {
            let hist = JSON.parse(localStorage.getItem('p_hist')) || [];
            hist.unshift({mano, bb, acc, cls, t: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})});
            if(hist.length > 15) hist.pop();
            localStorage.setItem('p_hist', JSON.stringify(hist));
            updateHistoryTable();
        }

        function updateHistoryTable() {
            let hist = JSON.parse(localStorage.getItem('p_hist')) || [];
            document.getElementById('hBody').innerHTML = hist.map(h => 
                `<tr><td><b>${h.mano}</b></td><td>${h.bb}BB</td><td class="${h.cls}">${h.acc}</td><td style="color:#444;font-size:0.7rem">${h.t}</td></tr>`
            ).join('');
        }

        function exportHistory() {
            let hist = JSON.parse(localStorage.getItem('p_hist')) || [];
            let txt = "PAUGAR REPORT:\\n" + hist.map(h => `${h.t} - ${h.mano}: ${h.acc}`).join("\\n");
            navigator.clipboard.writeText(txt).then(() => alert("Copiado al portapapeles"));
        }

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
