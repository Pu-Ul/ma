import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR Radar Elite", layout="centered")

# Estilo para ocultar elementos innecesarios de Streamlit y maximizar espacio
st.markdown("""
    <style>
    .block-container { padding: 0.5rem 1rem; }
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 2px; overflow-x: hidden; }
        
        /* CABECERA JERÁRQUICA */
        .top-bar { display: flex; justify-content: space-between; background: #111; padding: 10px; border-radius: 10px; border: 1px solid #222; margin-bottom: 8px; }
        .h-label { font-size: 0.55rem; color: #ffcc00; font-weight: bold; text-transform: uppercase; display: block; }
        .h-val { font-size: 0.75rem; color: #fff; font-weight: bold; }

        /* PASO 1: TECLADO COMPACTO (13 BOTONES) */
        .p1-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 8px; }
        .p1-btn { padding: 12px 0; font-size: 1rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 8px; font-weight: bold; transition: 0.2s; }
        .p1-btn.active { background: #00ff00 !important; color: #000 !important; border: 2px solid #fff; }
        
        .suit-box { display: flex; gap: 6px; margin-bottom: 12px; }
        .s-btn { flex: 1; padding: 15px; font-size: 0.85rem; border-radius: 10px; border: 1px solid #333; background: #111; color: #888; font-weight: bold; }
        .active-s { background: #0055ff !important; color: #fff !important; box-shadow: 0 0 10px #0055ff; }
        .active-o { background: #444 !important; color: #fff !important; }

        /* PANEL DE DECISIÓN INTELIGENTE */
        #res-box { display: none; padding: 18px 10px; border-radius: 20px; margin-top: 8px; border: 4px solid #fff; transition: 0.3s; }
        .dec-txt { font-size: 3rem; font-weight: 900; margin: 0; text-shadow: 2px 2px #000; }
        .dream-lbl { font-size: 0.7rem; color: #ffcc00; font-weight: bold; margin-top: 8px; text-transform: uppercase; display: block; }

        /* PASO 2: MATRIZ HORIZONTAL 52 (CERO SCROLL) */
        #paso2 { display: none; margin-top: 20px; border-top: 2px dashed #444; padding-top: 15px; }
        .matrix-52 { display: grid; grid-template-columns: repeat(13, 1fr); gap: 1px; width: 100vw; margin-left: -2px; }
        .m-card { padding: 10px 0; font-size: 0.55rem; background: #111; color: #fff; border: 1px solid #222; font-weight: bold; }
        .m-card.active { background: #fff !important; color: #000 !important; border: 1px solid #00ff00; }
        .p-h, .p-d { color: #ff8888; border-bottom: 2px solid #ff4444; }
        .p-s { border-bottom: 2px solid #555; }
        .p-t { color: #88ff88; border-bottom: 2px solid #00ff00; }

        .f-display { display: flex; justify-content: center; gap: 8px; margin: 15px 0; }
        .ui-card { width: 42px; height: 60px; background: #fff; color: #000; border-radius: 6px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 1rem; font-weight: 900; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .ana-box { background: #111; padding: 10px; border-radius: 10px; font-size: 0.8rem; text-align: left; border-left: 5px solid #ffcc00; margin-top: 10px; line-height: 1.4; }

        /* HISTORIAL Y EXPORTACIÓN */
        .hist-container { margin-top: 20px; background: #0a0a0a; padding: 12px; border-radius: 12px; border: 1px solid #222; }
        .h-row { display: flex; justify-content: space-between; border-bottom: 1px solid #222; padding: 6px 0; font-size: 0.7rem; color: #bbb; }
        .v-input { background: #222; border: 1px solid #444; color: #ffcc00; padding: 4px; width: 75px; border-radius: 5px; font-weight: bold; text-align: center; }
        .btn-exp { width: 100%; padding: 14px; background: #27ae60; color: #fff; border: none; border-radius: 10px; font-weight: bold; margin-top: 10px; cursor: pointer; }

        .btn-reset { width: 100%; padding: 25px; background: #fff; color: #000; font-size: 1.8rem; font-weight: 900; border-radius: 18px; margin-top: 25px; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="h-unit"><span class="h-label">STACK</span><span class="h-val">30 BB (Promedio)</span></div>
        <div class="h-unit"><span class="h-label">POSICIÓN</span><span class="h-val">LATE / BTN</span></div>
    </div>

    <div class="p1-grid" id="grid1"></div>
    <div class="suit-box">
        <button class="s-btn" id="btnS" onclick="setSuited(true)">SUITED (s)</button>
        <button class="s-btn" id="btnO" onclick="setSuited(false)">OFFSUIT (o)</button>
    </div>

    <div id="res-box">
        <p id="decision" class="dec-txt"></p>
        <span id="dream" class="dream-lbl"></span>
        
        <div id="paso2">
            <span class="h-label" style="color:#00ff00">ALIMENTAR FLOP (PINTAS)</span>
            <div class="matrix-52" id="matrix52"></div>
            <div id="f-view" class="f-display"></div>
            <div id="analysis" class="ana-box" style="display:none;"></div>
        </div>

        <div class="hist-container">
            <span class="h-label">HISTORIAL DE SESIÓN</span>
            <div id="hList"></div>
            <button class="btn-exp" onclick="exportData()">📤 COPIAR REPORTE PARA ANÁLISIS</button>
        </div>

        <button class="btn-reset" onclick="window.location.reload()">SIGUIENTE MANO</button>
    </div>

    <script>
        const ranks = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        const suits = [{s:'♠',c:'p-s'},{s:'♥',c:'p-h'},{s:'♦',c:'p-d'},{s:'♣',c:'p-t'}];
        let hand = []; let isSuited = null; let flop = [];
        let history = JSON.parse(localStorage.getItem('paugar_final_data')) || [];

        function init() {
            const g1 = document.getElementById('grid1');
            ranks.forEach(r => {
                const b = document.createElement('button'); b.innerText = r; b.className = "p1-btn";
                b.onclick = () => { if(hand.length < 2) { hand.push(r); b.classList.add('active'); if(hand.length==2 && isSuited!==null) calcPre(); } };
                g1.appendChild(b);
            });
            const g52 = document.getElementById('matrix52');
            suits.forEach(s => {
                ranks.forEach(r => {
                    const b = document.createElement('button'); b.innerText = r+s.s; b.className = `m-card ${s.c}`;
                    b.onclick = () => { if(flop.length < 3 && !b.classList.contains('active')) { flop.push({r,s:s.s}); b.classList.add('active'); renderFlop(); } };
                    g52.appendChild(b);
                });
            });
            updateHistory();
        }

        function setSuited(v) { isSuited = v; if(hand.length == 2) calcPre(); }

        function calcPre() {
            const box = document.getElementById('res-box'); const dec = document.getElementById('decision');
            const dream = document.getElementById('dream');
            box.style.display = 'block';
            
            const r1 = hand[0], r2 = hand[1];
            // LÓGICA INTELIGENTE: Parejas, Ases, o K-Suited entran.
            const isOk = (r1 === r2 || r1 === 'A' || r2 === 'A' || (r1 === 'K' && isSuited) || (r2 === 'K' && isSuited));
            
            dec.innerText = isOk ? "RAISE" : "FOLD";
            box.style.backgroundColor = isOk ? "#1b5e20" : "#b71c1c";
            dream.innerText = (r1 === r2) ? "SUEÑO: SET / FULL HOUSE" : (isSuited ? "SUEÑO: FLUSH (COLOR)" : "SUEÑO: TOP PAIR");

            saveLog(hand.join("")+(isSuited?'s':'o'), dec.innerText);
            if(isOk) document.getElementById('paso2').style.display = 'block';
        }

        function renderFlop() {
            const view = document.getElementById('f-view');
            view.innerHTML = flop.map(c => `<div class="ui-card" style="color:${(c.s=='♥'||c.s=='♦')?'red':'black'}"><span>${c.r}</span><span>${c.s}</span></div>`).join('');
            if(flop.length === 3) {
                const ana = document.getElementById('analysis'); ana.style.display = 'block';
                const connect = flop.some(f => hand.includes(f.r));
                const paired = new Set(flop.map(f => f.r)).size < 3;
                ana.innerHTML = `<b>ESTADO:</b> ${connect ? "✅ IMPACTO DIRECTO" : "❌ MESA SECA / FALLO"}<br><b>RIESGO:</b> ${paired ? "⚠️ MESA DOBLADA (Peligro de Full)" : "✅ MESA LIMPIA"}`;
            }
        }

        function saveLog(m, a) {
            history.unshift({ t: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}), m, a, v: '' });
            if(history.length > 5) history.pop();
            localStorage.setItem('paugar_final_data', JSON.stringify(history));
            updateHistory();
        }

        function updateHistory() {
            document.getElementById('hList').innerHTML = history.map((x, i) => `
                <div class="h-row">
                    <span>${x.t} | <b>${x.m}</b> | ${x.a}</span>
                    <input class="v-input" placeholder="Ganó con:" onchange="saveV(${i}, this.value)" value="${x.v}">
                </div>`).join('');
        }

        function saveV(i, val) { history[i].v = val; localStorage.setItem('paugar_final_data', JSON.stringify(history)); }

        function exportData() {
            const txt = "REPORTE PAUGAR RADAR:\\n" + history.map(x => `${x.t} - Mano: ${x.m} - Yo: ${x.a} - Villano: ${x.v}`).join("\\n");
            navigator.clipboard.writeText(txt).then(() => alert("✅ Reporte copiado al portapapeles."));
        }

        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=1150, scrolling=True)
