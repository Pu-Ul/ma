import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar Inteligente", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 5px; }
        .row-label { font-size: 0.7rem; color: #ffcc00; font-weight: bold; display: block; margin: 10px 0 5px 0; text-transform: uppercase; }
        
        /* BOTONES SUPERIORES */
        .btn-group { display: flex; justify-content: space-around; gap: 5px; margin-bottom: 10px; }
        .mini-btn { flex: 1; font-size: 0.7rem; padding: 12px 0; background: #222; border: 1px solid #444; color: #888; border-radius: 8px; font-weight: bold; }
        .mini-btn.active { background: #ffcc00 !important; color: #000 !important; border-color: #fff; }

        /* GRID DE CARTAS */
        .grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 10px; }
        .c-btn { padding: 12px 0; font-size: 1.1rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 8px; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        /* RESULTADO */
        #res { display: none; padding: 20px; border-radius: 20px; margin-top: 10px; }
        .dec-txt { font-size: 3.5rem; font-weight: 900; margin: 0; }

        /* SECCIÓN FLOP */
        #flop-section { display: none; background: #111; padding: 15px; border-radius: 20px; border: 2px solid #00ff00; margin-top: 15px; }
        .flop-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
        .f-btn { padding: 10px 0; font-size: 0.9rem; background: #222; border: 1px solid #444; color: #fff; border-radius: 6px; }
        .f-btn.active { background: #00ff00 !important; color: #000 !important; }

        /* HISTORIAL CON REGISTRO DE VILLANO */
        .hist-box { margin-top: 25px; text-align: left; background: #0a0a0a; padding: 15px; border-radius: 12px; border: 1px solid #222; }
        .h-item { font-size: 0.75rem; padding: 8px 0; border-bottom: 1px solid #222; color: #bbb; }
        .v-input { background: #222; border: 1px solid #444; color: #ffcc00; padding: 5px; border-radius: 4px; width: 60px; font-weight: bold; }

        .btn-action { width: 100%; padding: 20px; font-size: 1.5rem; font-weight: 900; border-radius: 15px; margin-top: 15px; border: none; }
    </style>
</head>
<body>
    <div class="btn-group">
        <button class="mini-btn active" onclick="setBB(30)">10-40 BB</button>
        <button class="mini-btn" onclick="setPos('LATE')">LATE POS</button>
    </div>

    <span class="row-label">TUS CARTAS (Mano Inicial)</span>
    <div class="grid" id="g"></div>
    <div class="btn-group">
        <button class="mini-btn" id="btnS" onclick="setS(true)">MISMO PALO</button>
        <button class="mini-btn" id="btnO" onclick="setS(false)">DISTINTO</button>
    </div>

    <div id="res">
        <p id="dec" class="dec-txt"></p>
        <button class="btn-action" style="background:#00ff00; color:#000;" onclick="showFlop()">VER FLOP (MESA)</button>
        <button class="btn-action" style="background:#fff; color:#000;" onclick="reset()">OTRA MANO</button>
    </div>

    <div id="flop-section">
        <span class="row-label">CARTAS EN MESA (FLOP)</span>
        <div class="flop-grid" id="fg"></div>
        <div id="analysis" style="margin-top:10px; font-size:0.9rem; color:#ffcc00;"></div>
    </div>

    <div class="hist-box">
        <span style="color:#ffcc00; font-size:0.8rem; display:block; margin-bottom:10px;">HISTORIAL Y REGISTRO DE VILLANOS</span>
        <div id="hList"></div>
        <button onclick="exportH()" class="mini-btn" style="width:100%; margin-top:10px; background:#27ae60; color:#fff;">EXPORTAR REPORTE</button>
    </div>

    <script>
        const cards = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null; let flopSel = [];

        function init() {
            const g = document.getElementById('g'); g.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button'); b.innerText = c; b.className = "c-btn";
                b.onclick = () => { if(sel.length < 2) { sel.push(c); b.classList.add('active'); if(sel.length==2 && same!==null) calc(); } };
                g.appendChild(b);
            });
            const fg = document.getElementById('fg'); fg.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button'); b.innerText = c; b.className = "f-btn";
                b.onclick = () => { if(flopSel.length < 3) { flopSel.push(c); b.classList.add('active'); if(flopSel.length==3) anaFlop(); } };
                fg.appendChild(b);
            });
            updateH();
        }

        function setS(v) { same = v; if(sel.length == 2) calc(); }

        function calc() {
            const h1 = sel[0], h2 = sel[1];
            const isGood = (h1==='A' || (h1==='K' && same) || h1===h2);
            const r = document.getElementById('res'); r.style.display = 'block';
            const d = document.getElementById('dec');
            d.innerText = isGood ? "PUSH" : "FOLD";
            r.style.backgroundColor = isGood ? "#27ae60" : "#c0392b";
            saveH(sel.join("")+(same?'s':'o'), d.innerText);
        }

        function showFlop() { document.getElementById('flop-section').style.display = 'block'; }

        function anaFlop() {
            const ana = document.getElementById('analysis');
            const paired = new Set(flopSel).size !== 3;
            ana.innerHTML = paired ? "⚠️ PELIGRO: MESA DOBLADA (Posible Full House)" : "✅ MESA LIMPIA";
        }

        function saveH(m, a) {
            let h = JSON.parse(localStorage.getItem('ph')) || [];
            h.unshift({m, a, v: '', t: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})});
            if(h.length > 10) h.pop();
            localStorage.setItem('ph', JSON.stringify(h));
            updateH();
        }

        function updateH() {
            let h = JSON.parse(localStorage.getItem('ph')) || [];
            document.getElementById('hList').innerHTML = h.map((x, i) => `
                <div class="h-item">
                    ${x.t} | MIA: <b>${x.m}</b> | ACCIÓN: <b>${x.a}</b> | 
                    GANÓ CON: <input class="v-input" placeholder="ej. KK" onchange="updateV(${i}, this.value)" value="${x.v}">
                </div>`).join('');
        }

        function updateV(i, val) {
            let h = JSON.parse(localStorage.getItem('ph'));
            h[i].v = val.toUpperCase();
            localStorage.setItem('ph', JSON.stringify(h));
        }

        function exportH() {
            let h = JSON.parse(localStorage.getItem('ph')) || [];
            let txt = h.map(x => `${x.t} Mano:${x.m} Yo:${x.a} Villano:${x.v}`).join("\\n");
            navigator.clipboard.writeText(txt).then(() => alert("Copiado"));
        }

        function reset() {
            sel = []; same = null; flopSel = [];
            document.getElementById('res').style.display = 'none';
            document.getElementById('flop-section').style.display = 'none';
            init();
        }
        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=1200, scrolling=True)
