import streamlit as st
import streamlit.components.v1 as components

# Configuración de la página para móvil
st.set_page_config(page_title="PauGaR - VISIÓN GIGANTE", layout="centered")

# CÓDIGO ÚNICO (HTML + CSS + JS)
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            font-family: 'Arial Black', sans-serif; 
            background: #000; 
            color: #fff; 
            text-align: center; 
            margin: 0; 
            padding: 5px; 
        }

        /* TÍTULO PAUGAR */
        .footer-name { font-size: 1.2rem; color: #444; margin-top: 15px; }
        .footer-name b { color: #00ff00; }

        /* BOTONES DE CARTAS - TAMAÑO GIGANTE */
        .grid { 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 10px; 
            max-width: 100%; 
            margin: 10px auto; 
        }
        .c-btn { 
            padding: 25px 0; 
            font-size: 2.5rem; 
            background: #1a1a1a; 
            color: #fff; 
            border: 3px solid #333; 
            border-radius: 15px; 
            font-weight: bold; 
        }
        .c-btn.active { 
            background: #00ff00 !important; 
            color: #000 !important; 
            border: 5px solid #fff; 
        }
        
        /* BOTONES DE PALO - VISIBLES */
        .suit-box { 
            display: flex; 
            gap: 15px; 
            margin: 20px auto; 
        }
        .s-btn { 
            flex: 1; 
            padding: 35px 10px; 
            font-size: 1.8rem; 
            font-weight: 900; 
            border-radius: 20px; 
            border: 4px solid #333; 
            background: #1a1a1a; 
            color: #fff; 
        }
        .active-s { background: #0055ff !important; border-color: #fff !important; box-shadow: 0 0 20px #0055ff; }
        .active-o { background: #555 !important; border-color: #fff !important; }

        /* RESULTADO TIPO SEMÁFORO (GIGANTE) */
        #res { 
            display: none; 
            margin-top: 20px; 
            padding: 50px 10px; 
            border-radius: 35px; 
        }
        .dec-txt { 
            font-size: 6rem; 
            font-weight: 900; 
            margin: 0; 
            letter-spacing: -2px;
            text-shadow: 2px 2px #000;
        }
        
        /* EL SUEÑO - TEXTO GRANDE */
        .dream-box { 
            margin-top: 25px; 
            background: rgba(0,0,0,0.6); 
            padding: 20px; 
            border-radius: 20px; 
            border: 3px dashed #ffcc00;
        }
        .dream-val { 
            font-size: 2.5rem; 
            color: #ffcc00; 
            font-weight: bold; 
        }

        .btn-reset { 
            width: 100%; 
            padding: 35px; 
            background: #fff; 
            color: #000; 
            font-size: 2.5rem; 
            font-weight: 900; 
            border: none; 
            border-radius: 25px; 
            margin-top: 30px; 
            box-shadow: 0 5px 15px rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>

    <div class="grid" id="g"></div>
    
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setS(true)">MISMO<br>PALO</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">PALO<br>DISTINTO</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        
        <div class="dream-box">
            <span style="font-size: 1.5rem; color: #fff; display:block; margin-bottom:10px;">EL SUEÑO:</span>
            <span id="dream" class="dream-val"></span>
        </div>
        
        <button class="btn-reset" onclick="reset()">OTRA MANO</button>
    </div>

    <div class="footer-name">Developed by <b>PauGaR</b></div>

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
            const d = document.getElementById('dec');
            const dr = document.getElementById('dream');
            
            r.style.display = 'block';

            // --- LÓGICA DE DECISIÓN ---
            if (isP && idx1 <= 7) { 
                d.innerText = "ENTRA"; 
                r.style.backgroundColor = "#27ae60"; // VERDE
            } else if (h1 === 'A' || (h1 === 'K' && (same || idx2 <= 3))) {
                d.innerText = "ENTRA"; 
                r.style.backgroundColor = "#27ae60"; // VERDE
            } else if (same && dist <= 2 && idx1 <= 8) {
                d.innerText = "ENTRA"; 
                r.style.backgroundColor = "#27ae60"; // VERDE
            } else {
                d.innerText = "FUERA"; 
                r.style.backgroundColor = "#c0392b"; // ROJO
            }

            // --- LÓGICA DEL SUEÑO ---
            if (isP) dr.innerText = "TRÍO / PÓKER";
            else if (same) dr.innerText = "COLOR 🎨";
            else if (dist <= 4) dr.innerText = "ESCALERA 📏";
            else dr.innerText = "PAR ALTO 2️⃣";
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

# Renderizado final en la App
components.html(html_code, height=1200, scrolling=True)
