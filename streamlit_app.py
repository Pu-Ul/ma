import streamlit as st
import streamlit.components.v1 as components

# Configuración para que se vea perfecto en el celular
st.set_page_config(page_title="PauGaR - SISTEMA FINAL", layout="centered")

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

        /* TABLERO DE CARTAS GIGANTE */
        .grid { 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 10px; 
            margin: 10px auto; 
        }
        .c-btn { 
            padding: 25px 0; 
            font-size: 2.5rem; 
            background: #1a1a1a; 
            color: #fff; 
            border: 3px solid #444; 
            border-radius: 15px; 
        }
        .c-btn.active { 
            background: #00ff00 !important; 
            color: #000 !important; 
            border: 5px solid #fff; 
        }
        
        /* BOTONES DE PALO GIGANTES */
        .suit-box { 
            display: flex; 
            gap: 15px; 
            margin: 20px auto; 
        }
        .s-btn { 
            flex: 1; 
            padding: 30px 10px; 
            font-size: 1.6rem; 
            font-weight: 900; 
            border-radius: 20px; 
            border: 4px solid #333; 
            background: #1a1a1a; 
            color: #fff; 
        }
        .active-s { background: #0055ff !important; border-color: #fff !important; }
        .active-o { background: #555 !important; border-color: #fff !important; }

        /* RESULTADO (SEMÁFORO) */
        #res { 
            display: none; 
            margin-top: 20px; 
            padding: 40px 10px; 
            border-radius: 30px; 
        }
        .dec-txt { 
            font-size: 5rem; 
            font-weight: 900; 
            margin: 0; 
        }
        
        /* CUADRO DE APRENDIZAJE (EL SUEÑO) */
        .edu-box { 
            margin-top: 20px; 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 20px; 
            border-left: 8px solid #ffcc00;
            text-align: left;
        }
        .edu-title { 
            color: #ffcc00; 
            font-size: 1.5rem; 
            font-weight: bold; 
            display: block; 
            margin-bottom: 8px; 
        }
        .edu-text { 
            font-size: 1.2rem; 
            color: #fff; 
            font-family: sans-serif;
            line-height: 1.4;
        }

        .btn-reset { 
            width: 100%; 
            padding: 30px; 
            background: #fff; 
            color: #000; 
            font-size: 2.2rem; 
            font-weight: 900; 
            border-radius: 25px; 
            margin-top: 30px; 
        }

        .footer { font-size: 1.2rem; color: #444; margin: 20px 0; }
        .footer b { color: #00ff00; }
    </style>
</head>
<body>

    <div class="grid" id="g"></div>
    
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setS(true)">MISMO<br>PALO</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">DISTINTO<br>PALO</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        
        <div class="edu-box">
            <span id="eduT" class="edu-title"></span>
            <span id="eduX" class="edu-text"></span>
        </div>
        
        <button class="btn-reset" onclick="reset()">OTRA MANO</button>
    </div>

    <div class="footer">Developed by <b>PauGaR</b></div>

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
            const et = document.getElementById('eduT');
            const ex = document.getElementById('eduX');
            
            r.style.display = 'block';

            // DECISIÓN SEMÁFORO
            if (isP && idx1 <= 7) { 
                d.innerText = "ENTRA"; r.style.backgroundColor = "#27ae60"; 
            } else if (h1 === 'A' || (h1 === 'K' && (same || idx2 <= 3))) {
                d.innerText = "ENTRA"; r.style.backgroundColor = "#27ae60";
            } else if (same && dist <= 2 && idx1 <= 8) {
                d.innerText = "ENTRA"; r.style.backgroundColor = "#27ae60";
            } else {
                d.innerText = "FUERA"; r.style.backgroundColor = "#c0392b";
            }

            // EDUCACIÓN Y CULTURA DE POKER
            if (isP) {
                et.innerText = "SUEÑO: FULL HOUSE";
                ex.innerText = "Tienes una pareja inicial. Buscas un TRÍO (3 iguales) para armar un Full House (un trío y una pareja). ¡Es una mano ganadora!";
            } else if (same) {
                et.innerText = "SUEÑO: COLOR (FLUSH)";
                ex.innerText = "Tus cartas son del mismo palo. Buscas que salgan 3 más en la mesa para completar 5 del mismo palo.";
            } else if (dist <= 4) {
                et.innerText = "SUEÑO: ESCALERA";
                ex.innerText = "Tus cartas están cerca en número. Buscas completar 5 seguidas (ej: 7-8-9-10-J).";
            } else {
                et.innerText = "SUEÑO: PAREJA ALTA";
                ex.innerText = "Tus cartas están lejos. Solo buscas que salga una igual en la mesa para tener la pareja más fuerte.";
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
components.html(html_code, height=1200, scrolling=True)
