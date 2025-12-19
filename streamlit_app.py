import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - RADAR DEFINITIVO", layout="centered")

# Lógica blindada: Paso 1 Simple + Paso 2 Evolutivo
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 5px; }
        .label { font-size: 0.75rem; color: #ffcc00; font-weight: bold; display: block; margin: 12px 0; text-transform: uppercase; }
        
        /* --- PASO 1: TECLADO SIMPLE (CANDADO) --- */
        .grid-p1 { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 10px; }
        .btn-p1 { padding: 15px 0; font-size: 1.2rem; background: #1a1a1a; color: #fff; border: 1px solid #444; border-radius: 8px; font-weight: bold; }
        .btn-p1.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        .suit-box { display: flex; gap: 8px; margin-bottom: 15px; }
        .s-btn { flex: 1; padding: 18px; font-size: 1rem; border-radius: 12px; border: 2px solid #333; background: #111; color: #888; font-weight: bold; }
        .active-s { background: #0055ff !important; color: #fff !important; border-color: #fff !important; }
        .active-o { background: #444 !important; color: #fff !important; border-color: #fff !important; }

        /* --- RESULTADO SEMÁFORO --- */
        #res-p1 { display: none; padding: 25px 10px; border-radius: 20px; margin-top: 10px; border: 4px solid #fff; }
        .dec-txt { font-size: 3.5rem; font-weight: 900; margin: 0; text-shadow: 2px 2px #000; }
        .dream-lbl { font-size: 0.8rem; color: #ffcc00; font-weight: bold; margin-top: 10px; display: block; }

        /* --- PASO 2: MATRIZ 52 PARA EL FLOP --- */
        #paso2 { display: none; margin-top: 25px; border-top: 3px dashed #444; padding-top: 20px; }
        .poker-grid { display: grid; grid-template-columns: repeat(13, 1fr); gap: 2px; margin-bottom: 10px; width: 100%; }
        .c-btn { padding: 10px 0; font-size: 0.6rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 4px; font-weight: bold; }
        .c-btn.active { background: #fff !important; color: #000 !important; border: 1px solid #00ff00 !important; }
        
        /* PINTAS EN MATRIZ */
        .p-s { border-bottom: 3px solid #555; }
        .p-h { border-bottom: 3px solid #ff4444; color: #ff8888; }
        .p-d { border-bottom: 2px solid #ff4444; color: #ff8888; }
        .p-t { border-bottom: 3px solid #00ff00; color: #88ff88; }

        .flop-display { display: flex; justify-content: center; gap: 8px; margin: 15px 0; }
        .card-ui { width: 50px; height: 75px; background: #fff; color: #000; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 1.1rem; font-weight: 900; box-shadow: 0 4px 8px rgba(0,255,0,0.3); }
        
        .ana-card { background: #111; padding: 15px; border-radius: 12px; border-left: 5px solid #00ff00; text-align: left; margin-top: 10px; font-size: 0.85rem; line-height: 1.4; }
        
        /* HISTORIAL */
        .hist-box { margin-top: 25px; text-align: left; background: #0a0a0a; padding: 12px; border-radius: 12px; border: 1px solid #222; font-size: 0.75rem; }
        .v-input { background: #222; border: 1px solid #444; color: #ffcc00; padding: 5px; width: 80px; border-radius: 5px; font-weight: bold; }

        .btn-reset { width: 100%; padding: 25px; background: #fff; color: #000; font-size: 2rem; font-weight: 900; border-radius: 15px; margin-top: 30px; border: none; }
    </style>
</head>
<body>

    <span class="label">Paso 1: Tu Mano Inicial (Candado)</span>
    <div class="grid-p1" id="g1"></div>
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setS(true)">SUITED (s)</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">OFFSUIT (o)</button>
    </div>

    <div id="res-p1">
        <p id="dec" class="dec-txt"></p>
        <span class="dream-lbl" id="dream-txt"></span>
        
        <div id="paso2">
            <span class="label" style="color:#00ff00">Paso 2: Alimentar Flop (Matriz 52)</span>
            <div class="poker-grid" id="g52"></div>
            <div class="flop-display" id="flop-view"></div>
            <div id="analysis-box" class="ana-card" style="display:none;"></div>
        </div>

        <div class="hist-box">
            <span style="color:#ffcc00; font-weight:bold;">HISTORIAL: YO | ACCIÓN | VILLANO GANÓ CON:</span>
            <div id="hList" style="margin-top:10px;"></div>
        </div>

        <button class="btn-reset" onclick="window.location.reload()">SIGUIENTE MANO</button>
    </div>

    <script>
        const ranks = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        const suits = [{s:'♠',c:'p-s'},{s:'♥',c:'p-h'},{s:'♦',c:'p-d'},{s:'♣',c:'p-t'}];
        let myHand = []; let same = null; let flopHand = [];

        function init() {
            // Cargar Teclado Paso 1
            const g1 = document.getElementById('g1');
            ranks.forEach(r => {
                const b = document.createElement('button'); b.innerText = r; b.className = "btn-p1";
                b.onclick = () => { if(myHand.length < 2) { myHand.push(r); b.classList.add('active'); if(myHand.length==2 && same!==null) procesarP1(); } };
                g1.appendChild(b);
            });
            // Cargar Matriz Paso 2
            const g52 = document.getElementById('g52');
            suits.forEach(s => {
                ranks.forEach(r => {
                    const b = document.createElement('button'); b.innerText = r+s.s; b.className = `c-btn ${s.c}`;
                    b.onclick = () => { if(flopHand.length < 3 && !b.classList.contains('active')) { flopHand.push({r,s:s.s}); b.classList.add('active'); renderFlop(); } };
                    g52.appendChild(b);
                });
            });
        }

        function setS(v) { same = v; if(myHand.length == 2) procesarP1(); }

        function procesarP1() {
            const res = document.getElementById('res-p1'); const dec = document.getElementById('dec');
            const dream = document.getElementById('dream-txt');
            res.style.display = 'block';
            
            const r1 = myHand[0], r2 = myHand[1];
            const esRaise = (r1 === r2 || r1 === 'A' || r2 === 'A' || ((r1 === 'K' || r2 === 'K') && same));
            
            dec.innerText = esRaise ? "RAISE" : "FOLD";
            res.style.backgroundColor = esRaise ? "#1b5e20" : "#b71c1c";
            dream.innerText = (r1 === r2) ? "SUEÑO: SET / FULL HOUSE" : (same ? "SUEÑO: FLUSH (COLOR)" : "SUEÑO: STRAIGHT (ESCALERA)");
            
            if(esRaise) document.getElementById('paso2').style.display = 'block';
            addHist(myHand.join("")+(same?'s':'o'), dec.innerText);
        }

        function renderFlop() {
            const view = document.getElementById('flop-display');
            view.innerHTML = flopHand.map(c => `<div class="card-ui" style="color:${(c.s=='♥'||c.s=='♦')?'red':'black'}"><span>${c.r}</span><span>${c.s}</span></div>`).join('');
            if(flopHand.length === 3) analyzeMesa();
        }

        function analyzeMesa() {
            const ana = document.getElementById('analysis-box');
            ana.style.display = 'block';
            const conn = flopHand.some(f => myHand.includes(f.r));
            const paired = new Set(flopHand.map(f => f.r)).size < 3;
            const flush = flopHand.every(f => f.s === flopHand[0].s);

            ana.innerHTML = `<b>ESTADO:</b> ${conn ? "✅ CONECTADO" : "❌ FALLO"}<br>` +
                            `<b>ALERTAS:</b> ${paired ? "⚠️ MESA DOBLADA (FULL)" : (flush ? "⚠️ PELIGRO COLOR" : "✅ MESA SECA")}`;
        }

        function addHist(mano, accion) {
            const h = document.getElementById('hList');
            h.innerHTML = `<div style="padding:5px 0; border-bottom:1px solid #222;">${mano} | <b>${accion}</b> | <input class="v-input" placeholder="ej: KK"></div>` + h.innerHTML;
        }

        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=1200, scrolling=True)
