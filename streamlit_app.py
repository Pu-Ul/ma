import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar Visual Final", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 10px; }
        
        /* GRID DE SELECCIÓN RÁPIDA */
        .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 10px; }
        .c-btn { padding: 12px 0; font-size: 1.1rem; background: #1a1a1a; color: #fff; border: 1px solid #444; border-radius: 8px; font-weight: bold; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        /* SELECTORES DE PALO */
        .suit-box { display: flex; gap: 10px; margin-bottom: 15px; }
        .s-btn { flex: 1; padding: 15px; font-size: 1rem; border-radius: 12px; border: 2px solid #333; background: #111; color: #888; font-weight: bold; }
        .active-s { background: #0055ff !important; color: #fff !important; border-color: #fff !important; }
        .active-o { background: #444 !important; color: #fff !important; border-color: #fff !important; }

        /* RESULTADO SEMÁFORO GIGANTE */
        #res { display: none; padding: 20px; border-radius: 20px; margin-top: 10px; }
        .dec-txt { font-size: 3.5rem; font-weight: 900; margin: 0; }
        
        /* EL TABLERO DEL SUEÑO (3 NIVELES VISUALES) */
        .dream-area { background: #111; margin-top: 20px; padding: 15px; border-radius: 20px; border: 3px solid #ffcc00; }
        .dream-label { font-size: 1rem; color: #ffcc00; font-weight: bold; margin-bottom: 15px; display: block; text-transform: uppercase; }
        
        .cards-row { display: flex; justify-content: center; gap: 10px; }
        .card-ui { 
            width: 60px; height: 90px; background: #fff; color: #000; 
            border-radius: 10px; display: flex; flex-direction: column; 
            justify-content: center; align-items: center; font-weight: 900; font-size: 1.4rem;
            box-shadow: 0 4px 8px rgba(255,255,255,0.2);
        }
        .red { color: #e74c3c; }
        .black { color: #2c3e50; }

        .btn-reset { width: 100%; padding: 25px; background: #fff; color: #000; font-size: 1.8rem; font-weight: bold; border-radius: 15px; margin-top: 25px; border: none; }
        .footer { font-size: 0.9rem; color: #444; margin-top: 20px; border-top: 1px solid #222; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="grid" id="g"></div>
    
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setS(true)">SUITED (s)</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">OFFSUIT (o)</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        
        <div class="dream-area">
            <span class="dream-label" id="dLevel"></span>
            <div class="cards-row" id="board"></div>
        </div>
        
        <button class="btn-reset" onclick="reset()">OTRA MANO</button>
    </div>

    <div class="footer">TERMINOLOGÍA PRO • <b>PauGaR</b></div>

    <script>
        const cards = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null;

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
        }

        function setS(v) { 
            same = v; 
            document.getElementById('btnS').classList.toggle('active-s', v);
            document.getElementById('btnO').classList.toggle('active-o', !v);
            if(sel.length == 2) calc();
        }

        function draw(v, s) {
            const isR = (s === '♥' || s === '♦');
            return `<div class="card-ui ${isR ? 'red' : 'black'}"><span>${v}</span><span>${s}</span></div>`;
        }

        function calc() {
            const h1 = sel[0], h2 = sel[1];
            const idx1 = cards.indexOf(h1), idx2 = cards.indexOf(h2);
            const isP = h1 === h2;
            const res = document.getElementById('res');
            const dLevel = document.getElementById('dLevel');
            const board = document.getElementById('board');
            
            res.style.display = 'block';

            // DECISIÓN (PUSH/FOLD)
            if (isP && idx1 <= 7 || h1 === 'A' || (h1 === 'K' && (same || idx2 <= 3))) { 
                document.getElementById('dec').innerText = "PUSH"; res.style.backgroundColor = "#27ae60"; 
            } else {
                document.getElementById('dec').innerText = "FOLD"; res.style.backgroundColor = "#c0392b";
            }

            // --- LOS 3 NIVELES DEL SUEÑO ---
            if (isP) {
                // NIVEL 1: PAREJAS (FULL HOUSE / POKER)
                dLevel.innerText = "NIVEL 1: FULL HOUSE";
                board.innerHTML = draw(h1, '♠') + draw(h1, '♦') + draw('K', '♥') + draw('K', '♣');
            } else if (same) {
                // NIVEL 2: MISMO PALO (FLUSH / COLOR)
                dLevel.innerText = "NIVEL 2: FLUSH (COLOR)";
                board.innerHTML = draw('10', '♥') + draw('7', '♥') + draw('2', '♥');
            } else {
                // NIVEL 3: CONECTORES (STRAIGHT / ESCALERA)
                dLevel.innerText = "NIVEL 3: STRAIGHT (ESCALERA)";
                if((h1==='A' && h2==='K') || (h1==='K' && h2==='A')) {
                    board.innerHTML = draw('Q', '♦') + draw('J', '♣') + draw('10', '♥');
                } else {
                    board.innerHTML = draw('J', '♠') + draw('10', '♦') + draw('9', '♣');
                }
            }
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
components.html(html_code, height=800, scrolling=True)
