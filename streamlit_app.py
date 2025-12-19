import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR Poker Radar", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Helvetica', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 10px; overflow: hidden; }
        
        /* TECLADO DE CARTAS COMPACTO */
        .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 12px; }
        .c-btn { padding: 12px 0; font-size: 1.1rem; background: #1a1a1a; color: #fff; border: 1px solid #444; border-radius: 6px; font-weight: bold; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        /* SELECTORES TÉCNICOS */
        .suit-box { display: flex; gap: 8px; margin-bottom: 15px; }
        .s-btn { flex: 1; padding: 12px; font-size: 0.9rem; border-radius: 8px; border: 1px solid #333; background: #111; color: #777; font-weight: bold; }
        .active-s { background: #0055ff !important; color: #fff !important; border-color: #fff !important; }
        .active-o { background: #444 !important; color: #fff !important; border-color: #fff !important; }

        /* RESULTADO SEMÁFORO PROFESIONAL */
        #res { display: none; padding: 15px; border-radius: 12px; margin-top: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
        .dec-txt { font-size: 2.8rem; font-weight: 900; margin: 0; text-transform: uppercase; }
        
        /* SECCIÓN EL SUEÑO (JERARQUÍA REAL) */
        .dream-card { background: rgba(0,0,0,0.6); margin-top: 10px; padding: 12px; border-radius: 10px; text-align: left; border-left: 5px solid #ffcc00; }
        .dream-t { font-size: 0.75rem; color: #ffcc00; font-weight: bold; text-transform: uppercase; display: block; }
        .dream-val { font-size: 1.2rem; color: #fff; font-weight: bold; display: block; margin: 2px 0; }
        .dream-info { font-size: 0.8rem; color: #bbb; line-height: 1.2; display: block; }

        .btn-reset { width: 100%; padding: 18px; background: #fff; color: #000; font-size: 1.3rem; font-weight: 900; border-radius: 10px; margin-top: 12px; border: none; }
        .footer { font-size: 0.8rem; color: #333; margin-top: 15px; border-top: 1px solid #111; padding-top: 5px; }
    </style>
</head>
<body>
    <div class="grid" id="g"></div>
    
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setS(true)">SUITED (Mismo palo)</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">OFFSUIT (Distintos)</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        
        <div class="dream-card">
            <span class="dream-t">EL SUEÑO (Potencial)</span>
            <span id="dream" class="dream-val"></span>
            <span id="info" class="dream-info"></span>
        </div>
        
        <button class="btn-reset" onclick="reset()">SIGUIENTE MANO</button>
    </div>

    <div class="footer">TERMINOLOGÍA PROFESIONAL • PAUGAR</div>

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
            const h1 = sel[0], h2 = sel[1], idx1 = cards.indexOf(h1), idx2 = cards.indexOf(h2);
            const isP = h1 === h2, dist = Math.abs(idx1 - idx2);
            const r = document.getElementById('res');
            r.style.display = 'block';

            // DECISIÓN: PUSH (ENTRAR) O FOLD (RETIRARSE)
            if (isP && idx1 <= 7 || h1 === 'A' || (h1 === 'K' && (same || idx2 <= 3))) { 
                document.getElementById('dec').innerText = "PUSH"; r.style.backgroundColor = "#27ae60"; 
            } else {
                document.getElementById('dec').innerText = "FOLD"; r.style.backgroundColor = "#c0392b";
            }

            // EL SUEÑO: TERMINOLOGÍA TÉCNICA
            const dV = document.getElementById('dream'), dI = document.getElementById('info');
            if (isP) { 
                dV.innerText = "FULL HOUSE / QUADS"; 
                dI.innerText = "Buscas el 'Set' (trío) para completar un Full (3+2) o un Póker (4)."; 
            } else if (same) { 
                dV.innerText = "FLUSH (COLOR)"; 
                dI.innerText = "Buscas 5 cartas del mismo palo. Es el 'Nut' (la mejor) si tienes el As."; 
            } else if (dist <= 4) { 
                dV.innerText = "STRAIGHT (ESCALERA)"; 
                dI.innerText = "Buscas 5 cartas en orden numérico. Muy fuerte si es a las cartas altas."; 
            } else { 
                dV.innerText = "TOP PAIR"; 
                dI.innerText = "Buscas conectar la pareja más alta de la mesa para ganar por fuerza."; 
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
components.html(html_code, height=650)
