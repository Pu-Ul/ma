import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Poker MTT Visual", layout="centered")

# Agregamos la función de limpiar en el JS
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; max-width: 380px; margin: 0 auto; padding: 10px; }
        button { padding: 15px; font-size: 1.4rem; background: #222; color: #fff; border: 2px solid #444; border-radius: 8px; cursor: pointer; }
        button.active { background: #00ff00 !important; color: #000 !important; border-color: #fff; }
        .suit-toggle { display: none; gap: 10px; max-width: 380px; margin: 10px auto; }
        .s-btn { flex: 1; padding: 15px; background: #333; color: #fff; border-radius: 8px; border: 2px solid #444; font-size: 0.9rem; }
        .s-btn.active { background: #007bff !important; }
        
        #res { display: none; margin-top: 15px; background: #111; padding: 15px; border-radius: 20px; border: 2px solid #333; }
        .banner { font-size: 2rem; margin-bottom: 15px; border-radius: 10px; padding: 5px; }
        
        /* BOTÓN LIMPIAR */
        .btn-clear { width: 90%; max-width: 380px; padding: 15px; margin: 20px auto; background: #c0392b; color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; display: block; }
        
        .option { margin-bottom: 15px; padding: 10px; border-bottom: 1px solid #222; }
        .opt-t { color: #ffcc00; font-size: 0.9rem; display: block; margin-bottom: 8px; }
        .cards { display: flex; justify-content: center; gap: 8px; margin-bottom: 5px; }
        .card { background: #fff; color: #000; width: 50px; height: 75px; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: bold; position: relative; }
        .card::after { content: '♥'; font-size: 0.7rem; position: absolute; bottom: 3px; right: 3px; color: red; }
        .black::after { content: '♠'; color: #000; }
        .txt { font-size: 1.1rem; font-weight: bold; color: #00ff00; }
    </style>
</head>
<body>
    <div class="grid" id="g"></div>
    <div class="suit-toggle" id="stog">
        <button class="s-btn" id="sT" onclick="setS(true)">SAME SUIT</button>
        <button class="s-btn" id="sF" onclick="setS(false)">OFFSUIT</button>
    </div>

    <div id="res">
        <div id="banner" class="banner"></div>
        <div class="option">
            <span class="opt-t">EL SUEÑO</span>
            <div class="cards" id="c1"></div>
            <div class="txt" id="t1"></div>
        </div>
        <div class="option">
            <span class="opt-t">OPCIÓN 2</span>
            <div class="cards" id="c2"></div>
            <div class="txt" id="t2"></div>
        </div>
        <button class="btn-clear" onclick="resetApp()">🔄 NUEVA MANO (LIMPIAR)</button>
    </div>

    <script>
        const rs = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null;
        const g = document.getElementById('g');

        function init() {
            g.innerHTML = "";
            rs.forEach(r => {
                const b = document.createElement('button');
                b.innerText = r;
                b.id = "btn-" + r;
                b.onclick = () => selectCard(r, b);
                g.appendChild(b);
            });
        }

        function selectCard(r, b) {
            if(sel.length < 2) {
                sel.push(r);
                b.classList.add('active');
                if(sel.length === 2) {
                    if(sel[0] === sel[1]) {
                        document.getElementById('stog').style.display = 'none';
                        calc();
                    } else {
                        document.getElementById('stog').style.display = 'flex';
                    }
                }
            }
        }

        function resetApp() {
            sel = []; same = null;
            document.getElementById('res').style.display = 'none';
            document.getElementById('stog').style.display = 'none';
            document.getElementById('sT').classList.remove('active');
            document.getElementById('sF').classList.remove('active');
            init(); // Reinicia los botones
        }

        function setS(v) { 
            same = v; 
            document.getElementById('sT').classList.toggle('active', v);
            document.getElementById('sF').classList.toggle('active', !v);
            calc(); 
        }

        function draw(v, blk) { return `<div class="card ${blk?'black':''}">${v}</div>`; }

        function calc() {
            const h1 = sel[0], h2 = sel[1];
            document.getElementById('res').style.display = 'block';
            let b = document.getElementById('banner');
            let isP = h1 === h2;
            let ok = isP || h1==='A' || (h1==='K' && (same || isP));
            
            b.innerText = ok ? "RAISE 🔥" : "FOLD 💀";
            b.style.background = ok ? "#27ae60" : "#c0392b";

            let row1="", row2="", txt1="", txt2="";
            if(isP) {
                row1 = draw(h1, true) + draw('X', false) + draw('X', true);
                txt1 = "MANO 1: SET (TRIO)";
                row2 = draw('2', true) + draw('5', false) + draw('J', true);
                txt2 = "MANO 2: OVERPAIR";
            } else if (sel.includes('A') && sel.includes('Q')) {
                row1 = draw('K', true) + draw('J', false) + draw('T', true);
                txt1 = "MANO 1: ESCALERA";
                row2 = draw('A', false) + draw('Q', true) + draw('5', false);
                txt2 = "MANO 2: TOP PAIR";
            } else {
                row1 = same ? draw('X',true)+draw('X',true)+draw('X',true) : draw(h1,true)+draw(h2,false)+draw('2',true);
                txt1 = same ? "MANO 1: COLOR" : "MANO 1: DOBLES";
                row2 = draw(h1, false) + draw('7', true) + draw('Q', false);
                txt2 = "MANO 2: TOP PAIR";
            }
            document.getElementById('c1').innerHTML = row1;
            document.getElementById('t1').innerText = txt1;
            document.getElementById('c2').innerHTML = row2;
            document.getElementById('t2').innerText = txt2;
        }

        init();
    </script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
