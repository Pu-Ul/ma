import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Poker MTT Helper", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; max-width: 380px; margin: 0 auto; padding: 10px; }
        button { padding: 15px; font-size: 1.4rem; background: #222; color: #fff; border: 2px solid #444; border-radius: 8px; cursor: pointer; }
        button.active { background: #00ff00 !important; color: #000 !important; }
        
        .suit-toggle { display: none; gap: 10px; max-width: 380px; margin: 10px auto; padding: 0 10px; }
        .s-btn { flex: 1; padding: 15px; background: #333; color: #fff; border-radius: 8px; border: 2px solid #444; font-size: 1rem; font-weight: bold; }
        .s-btn.active { background: #007bff !important; border-color: #fff; }

        #res { display: none; margin-top: 15px; background: #111; padding: 15px; border-radius: 20px; border: 2px solid #333; }
        .banner { font-size: 2.2rem; margin-bottom: 15px; border-radius: 10px; padding: 10px; font-weight: bold; }
        
        .option { margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #333; }
        .opt-t { color: #ffcc00; font-size: 1rem; display: block; margin-bottom: 10px; text-transform: uppercase; }
        .cards { display: flex; justify-content: center; gap: 8px; margin-bottom: 10px; }
        
        .card { background: #fff; color: #000; width: 55px; height: 80px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; position: relative; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
        .card.red { color: #d32f2f; }
        .card::after { content: '♠'; font-size: 0.8rem; position: absolute; bottom: 3px; right: 5px; color: #000; }
        .card.red::after { content: '♥'; color: #d32f2f; }
        
        .rank-txt { font-size: 1.3rem; font-weight: bold; color: #00ff00; display: block; margin-top: 5px; }
        .type-tag { font-size: 0.9rem; color: #aaa; margin-bottom: 10px; display: block; }
        
        .btn-clear { width: 90%; max-width: 380px; padding: 18px; margin: 20px auto; background: #c0392b; color: white; border: none; border-radius: 12px; font-size: 1.1rem; font-weight: bold; cursor: pointer; display: block; }
    </style>
</head>
<body>
    <div class="grid" id="g"></div>
    
    <div class="suit-toggle" id="stog">
        <button class="s-btn" id="sT" onclick="setS(true)">SUITED (Mismo Palo)</button>
        <button class="s-btn" id="sF" onclick="setS(false)">OFFSUIT (Distinto)</button>
    </div>

    <div id="res">
        <div id="banner" class="banner"></div>
        <div id="type-display" class="type-tag"></div>
        
        <div class="option">
            <span class="opt-t">Mejor Posibilidad (El Sueño)</span>
            <div class="cards" id="c1"></div>
            <div class="rank-txt" id="t1"></div>
        </div>
        
        <div class="option" style="border:none;">
            <span class="opt-t">Segunda Posibilidad</span>
            <div class="cards" id="c2"></div>
            <div class="rank-txt" id="t2"></div>
        </div>

        <button class="btn-clear" onclick="resetApp()">🔄 NUEVA MANO / LIMPIAR</button>
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
                b.onclick = () => {
                    if(sel.length < 2) {
                        sel.push(r);
                        b.classList.add('active');
                        if(sel.length === 2) {
                            if(sel[0] === sel[1]) {
                                same = false; 
                                calc();
                            } else {
                                document.getElementById('stog').style.display = 'flex';
                            }
                        }
                    }
                };
                g.appendChild(b);
            });
        }

        function setS(v) { 
            same = v; 
            document.getElementById('sT').classList.toggle('active', v);
            document.getElementById('sF').classList.toggle('active', !v);
            calc(); 
        }

        function resetApp() {
            sel = []; same = null;
            document.getElementById('res').style.display = 'none';
            document.getElementById('stog').style.display = 'none';
            init();
        }

        function draw(v, red) { return `<div class="card ${red?'red':''}">${v}</div>`; }

        function calc() {
            const h1 = sel[0], h2 = sel[1];
            const isP = h1 === h2;
            document.getElementById('res').style.display = 'block';
            document.getElementById('stog').style.display = isP ? 'none' : 'flex';
            
            const typeDisp = document.getElementById('type-display');
            typeDisp.innerText = isP ? "PAREJA EN MANO" : (same ? "MANO SUITED (s)" : "MANO OFFSUIT (o)");

            let b = document.getElementById('banner');
            let ok = isP || h1 === 'A' || (h1 === 'K' && (same || rs.indexOf(h2) < 5));
            b.innerText = ok ? "RAISE 🔥" : "FOLD 💀";
            b.style.background = ok ? "#27ae60" : "#c0392b";

            let r1="", r2="", t1="", t2="";

            if(isP) {
                r1 = draw(h1, true) + draw(h1, false) + draw('X', true);
                t1 = "SET (TRIO) - 4ta Jerarquía";
                r2 = draw('J', true) + draw('7', false) + draw('2', true);
                t2 = "OVERPAIR - 8va Jerarquía";
            } else if (sel.includes('A') && sel.includes('Q')) {
                r1 = draw('K', true) + draw('J', false) + draw('T', true);
                t1 = "ESCALERA - 6ta Jerarquía";
                r2 = draw('A', false) + draw('Q', true) + draw('5', false);
                t2 = "TOP PAIR - 9na Jerarquía";
            } else if (same) {
                r1 = draw('X', true) + draw('X', true) + draw('X', true);
                t1 = "COLOR (FLUSH) - 5ta Jerarquía";
                r2 = draw(h1, false) + draw('J', true) + draw('4', false);
                t2 = "PROYECTO DE COLOR";
            } else {
                r1 = draw(h1, true) + draw(h2, false) + draw('X', true);
                t1 = "DOBLES PAREJAS - 7ma Jerarquía";
                r2 = draw(h1, true) + draw('9', false) + draw('4', true);
                t2 = "TOP PAIR - 9na Jerarquía";
            }

            document.getElementById('c1').innerHTML = r1;
            document.getElementById('t1').innerText = t1;
            document.getElementById('c2').innerHTML = r2;
            document.getElementById('t2').innerText = t2;
        }

        init();
    </script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=True)
