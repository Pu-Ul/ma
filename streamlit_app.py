import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar de Alta Velocidad", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 5px; }
        .row-label { font-size: 0.65rem; color: #ffcc00; font-weight: bold; display: block; margin: 5px 0; text-transform: uppercase; }
        
        /* MATRIZ DE 52 CARTAS */
        .poker-grid { display: grid; grid-template-columns: repeat(13, 1fr); gap: 2px; margin-bottom: 5px; }
        .card-btn { padding: 8px 0; font-size: 0.7rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 4px; font-weight: bold; }
        .card-btn.picas { border-bottom: 3px solid #555; }
        .card-btn.coraz { border-bottom: 3px solid #ff4444; color: #ff8888; }
        .card-btn.diam { border-bottom: 3px solid #ff4444; color: #ff8888; }
        .card-btn.trebol { border-bottom: 3px solid #00ff00; color: #88ff88; }
        .card-btn.active { background: #fff !important; color: #000 !important; }

        /* DECISIÓN COMPACTA */
        #res { display: none; padding: 10px; border-radius: 10px; margin: 10px 0; border: 2px solid #fff; }
        .dec-txt { font-size: 1.8rem; font-weight: 900; margin: 0; }
        
        /* ÁREA DE MESA (FLOP) */
        #flop-area { display: none; background: #111; padding: 10px; border-radius: 10px; border: 1px solid #00ff00; }
        .flop-display { display: flex; justify-content: center; gap: 5px; margin: 5px 0; }
        .card-mini { width: 35px; height: 50px; background: #fff; color: #000; border-radius: 4px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 0.8rem; font-weight: bold; }

        .btn-reset { width: 100%; padding: 15px; background: #fff; color: #000; font-size: 1.2rem; font-weight: 900; border-radius: 8px; margin-top: 10px; border: none; }
        .ana-text { font-size: 0.8rem; color: #ffcc00; font-weight: bold; }
    </style>
</head>
<body>
    <span class="row-label">1. TUS 2 CARTAS (Toca 2)</span>
    <div id="grid-me" class="poker-grid"></div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        <div id="flop-area">
            <span class="row-label" style="color:#00ff00">2. EL FLOP (Toca 3 en la matriz)</span>
            <div id="flop-view" class="flop-display"></div>
            <p id="ana-flop" class="ana-text"></p>
        </div>
        <button class="btn-reset" onclick="reset()">OTRA MANO</button>
    </div>

    <script>
        const ranks = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        const suits = [
            {s:'♠', c:'picas'}, {s:'♥', c:'coraz'}, 
            {s:'♦', c:'diam'}, {s:'♣', c:'trebol'}
        ];
        let myHand = []; let flopHand = [];

        function createGrid(targetId, callback) {
            const container = document.getElementById(targetId);
            suits.forEach(suit => {
                ranks.forEach(rank => {
                    const b = document.createElement('button');
                    b.innerText = rank + suit.s;
                    b.className = `card-btn ${suit.c}`;
                    b.onclick = () => callback(rank, suit.s, b);
                    container.appendChild(b);
                });
            });
        }

        function handleMyHand(r, s, btn) {
            if(myHand.length < 2 && !btn.classList.contains('active')) {
                myHand.push({r, s});
                btn.classList.add('active');
                if(myHand.length === 2) calcPreflop();
            }
        }

        function handleFlop(r, s, btn) {
            if(flopHand.length < 3 && !btn.classList.contains('active')) {
                flopHand.push({r, s});
                btn.classList.add('active');
                renderFlop();
                if(flopHand.length === 3) analyzeMesa();
            }
        }

        function calcPreflop() {
            const res = document.getElementById('res');
            const dec = document.getElementById('dec');
            res.style.display = 'block';
            
            const r1 = myHand[0].r, r2 = myHand[1].r;
            const sameSuit = myHand[0].s === myHand[1].s;
            const isPair = r1 === r2;
            
            // Lógica compacta
            const good = (isPair || r1 === 'A' || r2 === 'A' || (r1 === 'K' && sameSuit));
            dec.innerText = good ? "RAISE / PUSH" : "FOLD";
            res.style.backgroundColor = good ? "#1b5e20" : "#b71c1c";
            
            if(good) document.getElementById('flop-area').style.display = 'block';
        }

        function renderFlop() {
            const view = document.getElementById('flop-view');
            view.innerHTML = flopHand.map(c => `
                <div class="card-mini" style="color:${(c.s=='♥'||c.s=='♦')?'red':'black'}">
                    <span>${c.r}</span><span>${c.s}</span>
                </div>`).join('');
        }

        function analyzeMesa() {
            const ana = document.getElementById('ana-flop');
            const allCards = [...myHand, ...flopHand];
            
            // Lógica de peligro simple
            const suitCounts = {};
            allCards.forEach(c => suitCounts[c.s] = (suitCounts[c.s] || 0) + 1);
            const flushDraw = Object.values(suitCounts).some(v => v >= 4);
            const isPairMesa = new Set(flopHand.map(f => f.r)).size < 3;

            if(flushDraw) ana.innerHTML = "⚠️ PROYECTO COLOR DETECTADO";
            else if(isPairMesa) ana.innerHTML = "⚠️ MESA DOBLADA: PELIGRO FULL";
            else ana.innerHTML = "✅ MESA SEGURA: EVALÚA TU PAR";
        }

        function reset() {
            myHand = []; flopHand = [];
            document.getElementById('res').style.display = 'none';
            document.getElementById('flop-area').style.display = 'none';
            document.querySelectorAll('.card-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('ana-flop').innerText = "";
        }

        createGrid('grid-me', (r, s, b) => {
            if(myHand.length < 2) handleMyHand(r, s, b);
            else handleFlop(r, s, b);
        });
    </script>
</body>
</html>
"""
components.html(html_code, height=900, scrolling=True)
