import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar Elite Final", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 2px; }
        
        /* CABECERA TÉCNICA */
        .header { display: flex; justify-content: space-between; background: #111; padding: 5px; border-radius: 8px; border: 1px solid #222; margin-bottom: 5px; }
        .h-item { flex: 1; }
        .lbl { font-size: 0.5rem; color: #ffcc00; font-weight: bold; display: block; }
        .val { font-size: 0.65rem; color: #fff; font-weight: bold; }

        /* PASO 1: CANDADO (13 BOTONES) */
        .grid-p1 { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; margin: 5px auto; width: 98%; }
        .btn-p1 { padding: 12px 0; font-size: 1rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 6px; font-weight: bold; }
        .btn-p1.active { background: #00ff00 !important; color: #000 !important; border: 1px solid #fff; }
        
        .suit-box { display: flex; gap: 5px; margin: 5px auto; width: 98%; }
        .s-btn { flex: 1; padding: 12px; font-size: 0.8rem; border-radius: 8px; border: 1px solid #333; background: #111; color: #888; font-weight: bold; }
        .active-s { background: #0055ff !important; color: #fff !important; }
        .active-o { background: #444 !important; color: #fff !important; }

        /* RESULTADO Y SUEÑO */
        #res-panel { display: none; padding: 15px 5px; border-radius: 12px; margin-top: 5px; border: 2px solid #fff; }
        .dec-big { font-size: 2.5rem; font-weight: 900; margin: 0; line-height: 1; }
        .dream-txt { font-size: 0.6rem; color: #ffcc00; font-weight: bold; margin-top: 5px; text-transform: uppercase; display: block; }

        /* PASO 2: MATRIZ 52 HORIZONTAL */
        #paso2 { display: none; margin-top: 15px; border-top: 1px dashed #444; padding-top: 10px; }
        .matrix { display: grid; grid-template-columns: repeat(13, 1fr); gap: 1px; width: 100%; }
        .m-card { padding: 8px 0; font-size: 0.5rem; background: #111; color: #fff; border: 1px solid #222; }
        .m-card.active { background: #fff !important; color: #000 !important; }
        .p-h, .p-d { color: #ff8888; border-bottom: 2px solid #ff4444; }
        .p-s { border-bottom: 2px solid #555; }
        .p-t { color: #88ff88; border-bottom: 2px solid #00ff00; }

        .flop-view { display: flex; justify-content: center; gap: 5px; margin: 10px 0; }
        .card-ui { width: 38px; height: 55px; background: #fff; color: #000; border-radius: 5px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 0.9rem; font-weight: bold; }

        /* HISTORIAL Y EXPORTACIÓN */
        .hist-box { margin-top: 15px; background: #0a0a0a; padding: 8px; border-radius: 8px; text-align: left; }
        .h-item { display: flex; justify-content: space-between; border-bottom: 1px solid #222; padding: 4px 0; font-size: 0.65rem; color: #bbb; }
        .v-in { background: #222; border: 1px solid #444; color: #ffcc00; padding: 3px; width: 60px; border-radius: 4px; font-weight: bold; }
        .btn-export { width: 100%; padding: 12px; background: #27ae60; color: #fff; border: none; border-radius: 8px; font-weight: bold; margin-top: 10px; cursor: pointer; }

        .btn-reset { width: 100%; padding: 18px; background: #fff; color: #000; font-size: 1.5rem; font-weight: 900; border-radius: 12px; margin-top: 15px; border: none; }
    </style>
</head>
<body>

    <div class="header">
        <div class="h-item"><span class="lbl">STACK</span><span class="val">15-40 BB</span></div>
        <div class="h-item"><span class="lbl">POSICIÓN</span><span class="val">MID/LATE</span></div>
    </div>

    <div class="grid-p1" id="g1"></div>
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setS(true)">SUITED (s)</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">OFFSUIT (o)</button>
    </div>

    <div id="res-panel">
        <p id="dec" class="dec-big"></p>
        <span id="dream" class="dream-txt"></span>
        
        <div id="paso2">
            <span class="lbl" style="color:#00ff00; margin-bottom:5px;">ALIMENTAR FLOP (PINTAS)</span>
            <div class="matrix" id="g52"></div>
            <div id="f-view" class="flop-view"></div>
            <div id="ana" style="font-size:0.7rem; color:#ffcc00; text-align:left; border-left:3px solid #ffcc00; padding-left:5px;"></div>
        </div>

        <div class="hist-box">
            <span class="lbl">HISTORIAL: MANO | ACCIÓN | VILLANO</span>
            <div id="hList"></div>
            <button class="btn-export" onclick="doExport()">📤 COPIAR REPORTE COMPLETO</button>
        </div>

        <button class="btn-reset" onclick="window.location.reload()">SIGUIENTE MANO</button>
    </div>

    <script>
        const ranks = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        const suits = [{s:'♠',c:'p-s'},{s:'♥',c:'p-h'},{s:'♦',c:'p-d'},{s:'♣',c:'p-t'}];
        let myH = []; let same = null; let flopH = [];
        let log = JSON.parse(localStorage.getItem('paugar_final')) || [];

        function init() {
            const g1 = document.getElementById('g1');
            ranks.forEach(r => {
                const b = document.createElement('button'); b.innerText = r; b.className = "btn-p1";
                b.onclick = () => { if(myH.length < 2) { myH.push(r); b.classList.add('active'); if(myH.length==2 && same!==null) calc(); } };
                g1.appendChild(b);
            });
            const g52 = document.getElementById('g52');
            suits.forEach(s => {
                ranks.forEach(r => {
                    const b = document.createElement('button'); b.innerText = r+s.s; b.className = `m-card ${s.c}`;
                    b.onclick = () => { if(flopH.length < 3 && !b.classList.contains('active')) { flopH.push({r,s:s.s}); b.classList.add('active'); renderF(); } };
                    g52.appendChild(b);
                });
            });
            updateH();
        }

        function setS(v) { same = v; if(myH.length == 2) calc(); }

        function calc() {
            const res = document.getElementById('res-panel');
            res.style.display = 'block';
            const r1 = myH[0], r2 = myH[1];
            const ok = (r1 === r2 || r1 === 'A' || r2 === 'A' || (r1 === 'K' && same));
            
            const action = ok ? "RAISE" : "FOLD";
            document.getElementById('dec').innerText = action;
            res.style.backgroundColor = ok ? "#1b5e20" : "#b71c1c";
            
            let dTxt = (r1 === r2) ? "SUEÑO: SET / FULL" : (same ? "SUEÑO: COLOR" : "SUEÑO: TOP PAIR");
            document.getElementById('dream').innerText = dTxt;

            saveLog(myH.join("")+(same?'s':'o'), action);
            if(ok) document.getElementById('paso2').style.display = 'block';
        }

        function renderF() {
            const view = document.getElementById('f-view');
            view.innerHTML = flopH.map(c => `<div class="card-ui" style="color:${(c.s=='♥'||c.s=='♦')?'red':'black'}"><span>${c.r}</span><span>${c.s}</span></div>`).join('');
            if(flopH.length === 3) {
                const ana = document.getElementById('ana');
                const conn = flopH.some(f => myH.includes(f.r));
                const pair = new Set(flopH.map(f => f.r)).size < 3;
                ana.innerHTML = (conn ? "✅ IMPACTO DIRECTO" : "❌ FALLO") + (pair ? " <br>⚠️ MESA DOBLADA (FULL?)" : "");
            }
        }

        function saveLog(m, a) {
            log.unshift({ t: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}), m, a, v: '' });
            if(log.length > 8) log.pop();
            localStorage.setItem('paugar_final', JSON.stringify(log));
            updateH();
        }

        function updateH() {
            document.getElementById('hList').innerHTML = log.map((x, i) => `
                <div class="h-item">
                    <span>${x.t} | <b>${x.m}</b> | ${x.a}</span>
                    <input class="v-in" placeholder="Ganó:" onchange="updateV(${i}, this.value)" value="${x.v}">
                </div>`).join('');
        }

        function updateV(i, val) { log[i].v = val; localStorage.setItem('paugar_final', JSON.stringify(log)); }

        function doExport() {
            const txt = "REPORTE PauGaR:\\n" + log.map(x => `${x.t} Mano:${x.m} Yo:${x.a} Villano:${x.v}`).join("\\n");
            navigator.clipboard.writeText(txt).then(() => alert("Copiado al portapapeles"));
        }
        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=1100, scrolling=True)
