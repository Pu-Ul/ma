import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="POKER RADAR PRO", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 10px; overflow-x: hidden; }
        
        /* SELECTOR DE CIEGAS SUPERIOR */
        .bb-selector { display: flex; justify-content: space-around; margin-bottom: 15px; background: #111; padding: 8px; border-radius: 10px; border: 1px solid #333; }
        .bb-btn { flex: 1; margin: 0 4px; font-size: 0.8rem; padding: 12px 0; background: #222; border: 1px solid #444; color: #888; border-radius: 6px; }
        .bb-btn.active { background: #ffcc00 !important; color: #000 !important; font-weight: bold; border-color: #fff; }

        /* GRID DE CARTAS */
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; max-width: 400px; margin: 0 auto; }
        .c-btn { padding: 18px 0; font-size: 1.5rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 8px; cursor: pointer; }
        .c-btn.active { background: #00ff00 !important; color: #000 !important; font-weight: bold; }
        
        /* SELECTOR SUITED/OFFSUIT SIEMPRE VISIBLE */
        .suit-main { display: flex; gap: 10px; margin: 15px auto; max-width: 400px; }
        .s-btn { flex: 1; padding: 20px; font-size: 1.1rem; font-weight: bold; border-radius: 10px; border: 2px solid #333; background: #1a1a1a; color: #666; cursor: pointer; }
        .s-btn.active-s { background: #0055ff !important; color: #fff !important; border-color: #fff; }
        .s-btn.active-o { background: #444 !important; color: #fff !important; border-color: #bbb; }

        /* PANEL DE RESULTADOS */
        #res { display: none; margin-top: 10px; border: 3px solid #00ff00; background: #050505; padding: 20px; border-radius: 15px; box-shadow: 0 0 20px rgba(0,255,0,0.2); }
        .dec { font-size: 2.5rem; font-weight: bold; margin-bottom: 5px; line-height: 1.1; }
        .tier { font-size: 1rem; color: #aaa; margin-bottom: 15px; letter-spacing: 1px; }
        .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .stat-card { background: #111; padding: 12px; border-radius: 10px; border: 1px solid #222; }
        .stat-label { font-size: 0.7rem; color: #777; display: block; margin-bottom: 5px; }
        .stat-val { font-size: 1.6rem; font-weight: bold; }

        .btn-clear { width: 100%; padding: 22px; background: #e74c3c; color: #fff; font-size: 1.4rem; font-weight: bold; border: none; border-radius: 12px; margin-top: 15px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="bb-selector">
        <button class="bb-btn" id="bb1" onclick="setBB(10)"> <10 BB </button>
        <button class="bb-btn active" id="bb2" onclick="setBB(30)"> 10-40 BB </button>
        <button class="bb-btn" id="bb3" onclick="setBB(50)"> 40+ BB </button>
    </div>

    <div class="grid" id="g"></div>
    
    <div class="suit-main" id="sm">
        <button class="s-btn" id="btnS" onclick="setS(true)">SUITED (s)</button>
        <button class="s-btn" id="btnO" onclick="setS(false)">OFFSUIT (o)</button>
    </div>

    <div id="res">
        <div id="dec" class="dec"></div>
        <div id="tier" class="tier"></div>
        <div class="stats">
            <div class="stat-card"><span class="stat-label">EQUITY ITM</span><span class="stat-val" id="itm" style="color:#00ff00"></span></div>
            <div class="stat-card"><span class="stat-label">RANGO #</span><span class="stat-val" id="rnk"></span></div>
        </div>
        <button class="btn-clear" onclick="reset()">NUEVA MANO</button>
    </div>

    <script>
        const cards = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null; let bbs = 30;

        function init() {
            const g = document.getElementById('g'); g.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button');
                b.innerText = c; b.className = "c-btn";
                b.onclick = () => {
                    if(sel.length < 2) {
                        sel.push(c); b.classList.add('active');
                        checkAutoCalc();
                    }
                };
                g.appendChild(b);
            });
        }

        function setBB(v) { 
            bbs = v; 
            document.querySelectorAll('.bb-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            if(sel.length==2) calc();
        }

        function setS(v) { 
            if(sel[0] === sel[1]) return; // Ignorar si es pareja
            same = v; 
            document.getElementById('btnS').className = v ? "s-btn active-s" : "s-btn";
            document.getElementById('btnO').className = !v ? "s-btn active-o" : "s-btn";
            if(sel.length == 2)
