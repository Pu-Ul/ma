import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar Visual", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 5px; overflow: hidden; }
        
        /* GRID COMPACTO */
        .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 8px; }
        .c-btn { padding: 12px 0; font-size: 1.1rem; background: #1a1a1a; color: #fff; border: 1px solid #444; border-radius: 6px; font-weight: bold; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        /* SELECTOR PALO MINI */
        .suit-box { display: flex; gap: 8px; margin-bottom: 10px; }
        .s-btn { flex: 1; padding: 10px; font-size: 0.9rem; border-radius: 8px; border: 1px solid #333; background: #111; color: #666; }
        .active-s { background: #0055ff !important; color: #fff !important; }
        .active-o { background: #444 !important; color: #fff !important; }

        /* PANEL DE DECISIÓN VISUAL */
        #res { display: none; padding: 15px; border-radius: 12px; margin-top: 5px; }
        .dec-txt { font-size: 2.5rem; font-weight: 900; margin: 0; }
        
        /* ESCUELA VISUAL (SUEÑO) */
        .edu-card { background: rgba(255,255,255,0.1); margin-top: 10px; padding: 10px; border-radius: 10px; text-align: left; border-left: 4px solid #ffcc00; }
        .edu-t { font-size: 0.9rem; color: #ffcc00; font-weight: bold; display: block; }
        .edu-x { font-size: 0.85rem; color: #ddd; line-height: 1.2; }

        .btn-reset { width: 100%; padding: 15px; background: #fff; color: #000; font-size: 1.2rem; font-weight: bold; border-radius: 10px; margin-top: 10px; border: none; }
        .footer { font-size: 0.7rem; color: #333; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="grid" id="g"></div>
    
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setS(true)">MISMO PALO (s)</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">DISTINTO (o)</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        
        <div class="edu-card">
            <span id="eduT" class="edu-t"></span>
            <span id="eduX" class="edu-x"></span>
        </div>
        
        <button class="btn-reset" onclick="reset()">SIGUIENTE</button>
    </div>

    <div class="footer">PauGaR - Guía Pedagógica</div>

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

        function calc() {
            const h1 = sel[0], h2 = sel[1];
            const idx1 = cards.indexOf(h1), idx2 = cards.indexOf(h2);
            const isP = h1 === h2;
            const dist = Math.abs(idx1 - idx2);
            const r = document.getElementById('res');
            r.style.display = 'block';

            // DECISIÓN
            if (isP && idx1 <= 7 || h1 === 'A' || (h1 === 'K' && (same || idx2 <= 3))) { 
                document.getElementById('dec').innerText = "JUEGA"; r.style.backgroundColor = "#27ae60"; 
            } else {
                document.getElementById('dec').innerText = "PASAR"; r.style.backgroundColor = "#c0392b";
            }

            // PEDAGOGÍA
            const et = document.getElementById('eduT'), ex = document.getElementById('eduX');
            if (isP) { et.innerText = "FULL HOUSE"; ex.innerText = "Trío + Pareja. ¡Mano muy fuerte!"; }
            else if (same) { et.innerText = "COLOR (FLUSH)"; ex.innerText = "5 cartas del mismo palo."; }
            else if (dist <= 4) { et.innerText = "ESCALERA"; ex.innerText = "5 números seguidos."; }
            else { et.innerText = "CARTA ALTA"; ex.innerText = "Buscas la pareja más alta."; }
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
components.html(html_code, height=600)
