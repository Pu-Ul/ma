import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar Posicional", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 5px; }
        
        /* SELECTORES SUPERIORES (CIEGAS Y POSICIÓN) */
        .header-box { background: #111; padding: 8px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #222; }
        .row-label { font-size: 0.65rem; color: #ffcc00; font-weight: bold; display: block; margin-bottom: 5px; text-transform: uppercase; }
        .btn-group { display: flex; justify-content: space-around; margin-bottom: 8px; }
        .mini-btn { flex: 1; margin: 0 2px; font-size: 0.65rem; padding: 10px 0; background: #222; border: 1px solid #444; color: #888; border-radius: 5px; font-weight: bold; }
        .mini-btn.active { background: #ffcc00 !important; color: #000 !important; border-color: #fff; }

        /* TECLADO DE CARTAS */
        .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 10px; }
        .c-btn { padding: 12px 0; font-size: 1.1rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 6px; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        /* PALOS */
        .suit-box { display: flex; gap: 8px; margin-bottom: 10px; }
        .s-btn { flex: 1; padding: 15px; font-size: 0.9rem; border-radius: 10px; border: 2px solid #333; background: #111; color: #888; }
        .active-s { background: #0055ff !important; color: #fff !important; }
        .active-o { background: #444 !important; color: #fff !important; }

        /* RESULTADO SEMÁFORO */
        #res { display: none; padding: 20px; border-radius: 20px; margin-top: 5px; }
        .dec-txt { font-size: 3.5rem; font-weight: 900; margin: 0; text-shadow: 2px 2px #000; }
        
        /* VISUALIZACIÓN DEL SUEÑO */
        .dream-area { background: #111; margin-top: 10px; padding: 15px; border-radius: 15px; border: 2px solid #ffcc00; }
        .board { display: flex; justify-content: center; gap: 8px; margin-top: 5px; }
        .card-ui { 
            width: 50px; height: 75px; background: #fff; color: #000; 
            border-radius: 8px; display: flex; flex-direction: column; 
            justify-content: center; align-items: center; font-weight: 900; font-size: 1.1rem;
        }
        .red { color: #e74c3c; }

        /* BOTONES DE ACCIÓN POST-FLOP (PRÓXIMAMENTE) */
        .btn-reset { width: 100%; padding: 25px; background: #fff; color: #000; font-size: 2rem; font-weight: 900; border-radius: 15px; margin-top: 20px; }
        
        /* HISTORIAL */
        .hist-box { margin-top: 25px; text-align: left; background: #0a0a0a; padding: 15px; border-radius: 10px; border: 1px solid #222; }
        .h-item { font-size: 0.75rem; padding: 5px 0; border-bottom: 1px solid #222; display: flex; justify-content: space-between; }
        .btn-exp { width: 100%; padding: 12px; background: #27ae60; color: #fff; border: none; border-radius: 8px; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header-box">
        <span class="row-label">1. TUS CIEGAS (Stack)</span>
        <div class="btn-group">
            <button class="mini-btn" id="bb1" onclick="setBB(10)"> <10 BB </button>
            <button class="mini-btn active" id="bb2" onclick="setBB(30)"> 10-40 BB </button>
            <button class="mini-btn" id="bb3" onclick="setBB(50)"> 40+ BB </button>
        </div>
        
        <span class="row-label">2. TU POSICIÓN (Lugar en mesa)</span>
        <div class="btn-group">
            <button class="mini-btn" id="p1" onclick="setPos('EARLY')"> EARLY </button>
            <button class="mini-btn" id="p2" onclick="setPos('MID')"> MID </button>
            <button class="mini-btn active" id="p3" onclick="setPos('LATE')"> LATE (Btn) </button>
            <button class="mini-btn" id="p4" onclick="setPos('BLIND')"> CIEGAS </button>
        </div>
    </div>

    <div class="grid" id="g"></div>
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setS(true)">SUITED (s)</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">OFFSUIT (o)</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        <div class="dream-area">
            <span style="color:#ffcc00; font-size:0.8rem; font-weight:bold;" id="dRank">EL SUEÑO</span>
            <div class="board" id="board"></div>
        </div>
        <button class="btn-reset" onclick="reset()">SIGUIENTE</button>
    </div>

    <div class="hist-box">
        <span style="color:#ffcc00; font-size:0.8rem;">REPORTE DE SESIÓN PauGaR</span>
        <div id="hList" style="margin-top:10px;"></div>
        <button onclick="exportH()" class="btn-exp">📤 EXPORTAR REPORTE</button>
    </div>

    <script>
        const cards = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null; let bbs = 30; let pos = 'LATE';

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
            updateH();
        }

        function setBB(v) { 
            bbs = v; 
            document.querySelectorAll('.mini-btn').forEach(b => { if(b.id.startsWith('bb')) b.classList.remove('active'); });
            event.target.classList.add('active');
        }

        function setPos(v) {
            pos = v;
            document.querySelectorAll('.mini-btn').forEach(b => { if(b.id.startsWith('p')) b.classList.remove('active'); });
            event.target.classList.add('active');
        }

        function setS(v) { 
            same = v; 
            document.getElementById('btnS').classList.toggle('active-s', v);
            document.getElementById('btnO').classList.toggle('active-o', !v);
            if(sel.length == 2) calc();
        }

        function draw(v, s) {
            const isR = (s === '♥' || s === '♦');
            return `<div class="card-ui ${isR ? 'red' : ''}"><span>${v}</span><span>${s}</span></div>`;
        }

        function calc() {
            const h1 = sel[0], h2 = sel[1], idx1 = cards.indexOf(h1), idx2 = cards.indexOf(h2);
            const isP = h1 === h2;
            const res = document.getElementById('res');
            res.style.display = 'block';

            // DECISIÓN BASADA EN POSICIÓN Y STACK
            let action = "FOLD";
            let score = 0;
            if (isP) score += (13 - idx1) * 2;
            if (h1 === 'A' || h1 === 'K') score += 15;
            if (same) score += 5;
            if (pos === 'LATE') score += 10;
            if (pos === 'EARLY') score -= 10;

            if (score > 15 || (bbs < 15 && score > 5)) {
                action = (bbs < 15) ? "PUSH" : "RAISE";
                res.style.backgroundColor = "#27ae60";
            } else {
                action = "FOLD";
                res.style.backgroundColor = "#c0392b";
            }

            document.getElementById('dec').innerText = action;

            // JERARQUÍA VISUAL
            const board = document.getElementById('board');
            const dRank = document.getElementById('dRank');
            if (isP) {
                dRank.innerText = "SUEÑO: FULL HOUSE / SET";
                board.innerHTML = draw(h1, '♠') + draw(h1, '♦') + draw('K', '♥');
            } else if (same) {
                dRank.innerText = "SUEÑO: FLUSH (COLOR)";
                board.innerHTML = draw('10', '♥') + draw('7', '♥') + draw('2', '♥');
            } else {
                dRank.innerText = "SUEÑO: STRAIGHT (ESCALERA)";
                board.innerHTML = draw('Q', '♦') + draw('J', '♣') + draw('10', '♥');
            }

            saveH(sel.join("")+(same?'s':'o'), action);
        }

        function saveH(m, a) {
            let h = JSON.parse(localStorage.getItem('ph')) || [];
            h.unshift({m, a, t: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})});
            if(h.length > 20) h.pop();
            localStorage.setItem('ph', JSON.stringify(h));
            updateH();
        }

        function updateH() {
            let h = JSON.parse(localStorage.getItem('ph')) || [];
            document.getElementById('hList').innerHTML = h.map(x => `
                <div class="h-item">
                    <span>${x.t} - <b>${x.m}</b></span>
                    <span style="color:${x.a=='FOLD'?'#ff4444':'#00ff00'}">${x.a}</span>
                </div>`).join('');
        }

        function exportH() {
            let h = JSON.parse(localStorage.getItem('ph')) || [];
            let txt = "REPORTE PAUGAR:\\n" + h.map(x => `${x.t} ${x.m} -> ${x.a}`).join("\\n");
            navigator.clipboard.writeText(txt).then(() => alert("Copiado"));
        }

        function reset() {
            sel = []; same = null;
            document.getElementById('res').style.display = 'none';
            document.getElementById('btnS').classList.remove('active-s');
            document.getElementById('btnO').classList.remove('active-o');
            init();
        }
        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=1100, scrolling=True)
