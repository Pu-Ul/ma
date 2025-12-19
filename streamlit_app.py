import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar Total Auditado", layout="centered")

# Lógica de Python integrada en el componente visual para máxima velocidad
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 5px; }
        .label { font-size: 0.65rem; color: #ffcc00; font-weight: bold; display: block; margin: 8px 0; text-transform: uppercase; }
        
        /* MATRIZ DE 52 CARTAS - DISEÑO HORIZONTAL (13 COL) */
        .poker-grid { 
            display: grid; 
            grid-template-columns: repeat(13, 1fr); 
            gap: 2px; 
            width: 100%; 
            margin: 0 auto;
        }
        
        .c-btn { 
            padding: 10px 0; font-size: 0.6rem; background: #1a1a1a; color: #fff; 
            border: 1px solid #333; border-radius: 4px; font-weight: bold; cursor: pointer;
        }
        .c-btn.active { background: #fff !important; color: #000 !important; border: 1px solid #00ff00; }
        
        /* PINTAS VISUALES */
        .p-s { border-bottom: 3px solid #555; }
        .p-h { border-bottom: 3px solid #ff4444; color: #ff8888; }
        .p-d { border-bottom: 3px solid #ff4444; color: #ff8888; }
        .p-t { border-bottom: 3px solid #00ff00; color: #88ff88; }

        /* RESULTADOS Y SEMÁFORO */
        #box-res { display: none; padding: 15px; border-radius: 15px; margin-top: 10px; border: 3px solid #fff; }
        .dec-txt { font-size: 3rem; font-weight: 900; margin: 0; text-shadow: 2px 2px #000; }
        
        /* MÓDULO POST-FLOP */
        #box-post { display: none; margin-top: 20px; background: #111; padding: 12px; border-radius: 15px; border: 1px solid #00ff00; }
        .flop-display { display: flex; justify-content: center; gap: 6px; margin: 10px 0; }
        .card-ui { width: 45px; height: 65px; background: #fff; color: #000; border-radius: 6px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 1rem; font-weight: bold; }
        
        .ana-box { background: #000; padding: 10px; border-radius: 8px; font-size: 0.8rem; text-align: left; margin-top: 10px; border-left: 4px solid #ffcc00; line-height: 1.3; }
        
        /* HISTORIAL */
        .hist-box { margin-top: 25px; text-align: left; background: #0a0a0a; padding: 10px; border-radius: 12px; border: 1px solid #222; }
        .v-input { background: #222; border: 1px solid #444; color: #ffcc00; padding: 5px; border-radius: 5px; width: 80px; font-weight: bold; font-size: 0.7rem; }

        .btn-reset { width: 100%; padding: 22px; background: #fff; color: #000; font-size: 1.6rem; font-weight: 900; border-radius: 15px; margin-top: 20px; border: none; }
    </style>
</head>
<body>

    <span class="label">Paso 1: Matriz de 52 (Selecciona tus 2 cartas)</span>
    <div class="poker-grid" id="main-grid"></div>

    <div id="box-res">
        <p id="dec-val" class="dec-txt"></p>
        
        <div id="box-post">
            <span class="label" style="color:#00ff00">Paso 2: Alimentar Flop (Selecciona 3 más arriba)</span>
            <div id="flop-view" class="flop-display"></div>
            <div id="ana-res" class="ana-box" style="display:none;"></div>
        </div>

        <div class="hist-box">
            <span style="color:#ffcc00; font-size:0.75rem;">REPORTE: YO | ACCIÓN | VILLANO GANÓ CON:</span>
            <div id="hList" style="margin-top:8px; font-size:0.8rem;"></div>
        </div>

        <button class="btn-reset" onclick="window.location.reload()">SIGUIENTE MANO</button>
    </div>

    <script>
        const ranks = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        const suits = [{s:'♠', c:'p-s'}, {s:'♥', c:'p-h'}, {s:'♦', c:'p-d'}, {s:'♣', c:'p-t'}];
        let myH = []; let flopH = [];

        // Generar Matriz
        const grid = document.getElementById('main-grid');
        suits.forEach(suit => {
            ranks.forEach(rank => {
                const b = document.createElement('button');
                b.innerText = rank + suit.s;
                b.className = `c-btn ${suit.c}`;
                b.onclick = () => handleInput(rank, suit.s, b);
                grid.appendChild(b);
            });
        });

        function handleInput(r, s, btn) {
            if (myH.length < 2 && !btn.classList.contains('active')) {
                myH.push({r, s}); btn.classList.add('active');
                if (myH.length === 2) procesarPre();
            } else if (myH.length === 2 && flopH.length < 3 && !btn.classList.contains('active')) {
                flopH.push({r, s}); btn.classList.add('active');
                renderFlop();
            }
        }

        function procesarPre() {
            const box = document.getElementById('box-res');
            const dec = document.getElementById('dec-val');
            box.style.display = 'block';
            
            const r1 = myH[0].r, r2 = myH[1].r;
            const suited = myH[0].s === myH[1].s;
            
            // LÓGICA DE DECISIÓN (IF)
            let ok = (r1 === r2 || r1 === 'A' || r2 === 'A' || ((r1 === 'K' || r2 === 'K') && suited));
            
            dec.innerText = ok ? "RAISE" : "FOLD";
            box.style.backgroundColor = ok ? "#1b5e20" : "#b71c1c";
            
            if (ok) document.getElementById('box-post').style.display = 'block';
            
            addHist(myH[0].r + myH[1].r + (suited?'s':'o'), dec.innerText);
        }

        function renderFlop() {
            const view = document.getElementById('flop-view');
            view.innerHTML = flopH.map(c => `
                <div class="card-ui" style="color:${(c.s=='♥'||c.s=='♦')?'red':'black'}">
                    <span>${c.r}</span><span>${c.s}</span>
                </div>`).join('');
            
            if (flopH.length === 3) {
                const ana = document.getElementById('ana-res');
                ana.style.display = 'block';
                const connect = flopH.some(f => f.r === myH[0].r || f.r === myH[1].r);
                const mesaD = new Set(flopH.map(f => f.r)).size < 3;
                const mesaS = flopH.every(f => f.s === flopH[0].s);

                ana.innerHTML = `<b>CONEXIÓN:</b> ${connect ? "✅ IMPACTO" : "❌ FALLO"}<br>` +
                                `<b>PELIGRO:</b> ${mesaD ? "⚠️ MESA DOBLADA (FULL)" : (mesaS ? "⚠️ COLOR EN MESA" : "✅ MESA SECA")}`;
            }
        }

        function addHist(mano, accion) {
            const h = document.getElementById('hList');
            h.innerHTML = `<div style="margin-bottom:5px;">${mano} | <b>${accion}</b> | <input class="v-input" placeholder="p.ej. Q♠Q♦"></div>` + h.innerHTML;
        }
    </script>
</body>
</html>
"""

components.html(html_code, height=1050, scrolling=True)
