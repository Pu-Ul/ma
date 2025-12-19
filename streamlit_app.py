import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="POKER MTT FAST", layout="centered")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 10px; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; max-width: 400px; margin: 0 auto; }
        button { padding: 15px 0; font-size: 1.4rem; background: #222; color: #fff; border: 1px solid #444; border-radius: 8px; cursor: pointer; }
        button.active { background: #00ff00 !important; color: #000 !important; font-weight: bold; }
        
        .bb-selector { display: flex; justify-content: space-around; margin: 15px auto; max-width: 400px; background: #111; padding: 10px; border-radius: 10px; }
        .bb-btn { flex: 1; margin: 0 5px; font-size: 0.9rem; padding: 10px 0; background: #333; border: 1px solid #555; }
        .bb-btn.active { background: #ffcc00 !important; color: #000 !important; }

        .suit-box { display: none; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px auto; max-width: 400px; }
        .s-btn { padding: 20px; font-size: 1.2rem; font-weight: bold; border-radius: 10px; background: #0055ff; color: #fff; border: none; }
        .s-btn.of { background: #555; }

        #res { display: none; margin-top: 10px; border: 3px solid #00ff00; background: #050505; padding: 20px; border-radius: 15px; }
        .dec { font-size: 2.8rem; font-weight: bold; margin-bottom: 5px; }
        .tier { font-size: 1.2rem; color: #aaa; margin-bottom: 15px; }
        .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .stat-card { background: #1a1a1a; padding: 10px; border-radius: 8px; border: 1px solid #333; }
        .stat-val { font-size: 1.5rem; font-weight: bold; display: block; }
        .btn-clear { width: 100%; padding: 20px; background: #e74c3c; color: #fff; font-size: 1.5rem; font-weight: bold; border: none; border-radius: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="bb-selector">
        <button class="bb-btn" id="bb1" onclick="setBB(10)"> <10 BB </button>
        <button class="bb-btn active" id="bb2" onclick="setBB(30)"> 10-40 BB </button>
        <button class="bb-btn" id="bb3" onclick="setBB(50)"> 40+ BB </button>
    </div>

    <div class="grid" id="g"></div>
    
    <div class="suit-box" id="sb">
        <button class="s-btn" onclick="setS(true)">SUITED (s)</button>
        <button class="s-btn of" onclick="setS(false)">OFFSUIT (o)</button>
    </div>

    <div id="res">
        <div id="dec" class="dec"></div>
        <div id="tier" class="tier"></div>
        <div class="stats">
            <div class="stat-card"><span>EQUITY ITM</span><span class="stat-val" id="itm" style="color:#00ff00"></span></div>
            <div class="stat-card"><span>RANGO</span><span class="stat-val" id="rnk"></span></div>
        </div>
        <button class="btn-clear" onclick="reset()">SIGUIENTE MANO</button>
    </div>

    <script>
        const cards = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];
        let sel = []; let same = null; let bbs = 30;

        function init() {
            const g = document.getElementById('g'); g.innerHTML = "";
            cards.forEach(c => {
                const b = document.createElement('button'); b.innerText = c;
                b.onclick = () => {
                    if(sel.length < 2) {
                        sel.push(c); b.classList.add('active');
                        if(sel.length === 2) {
                            if(sel[0] === sel[1]) { same=false; calc(); }
                            else { document.getElementById('sb').style.display = 'grid'; }
                        }
                    }
                };
                g.appendChild(b);
            });
        }

        function setBB(v) { 
            bbs = v; 
            document.querySelectorAll('.bb-btn').forEach(b => b.classList.remove('active'));
            if(v==10) document.getElementById('bb1').classList.add('active');
            if(v==30) document.getElementById('bb2').classList.add('active');
            if(v==50) document.getElementById('bb3').classList.add('active');
            if(sel.length==2) calc();
        }

        function setS(v) { same = v; calc(); }

        function reset() {
            sel = []; same = null;
            document.getElementById('res').style.display = 'none';
            document.getElementById('sb').style.display = 'none';
            init();
        }

        function calc() {
            document.getElementById('res').style.display = 'block';
            document.getElementById('sb').style.display = 'none';
            const h1 = sel[0], h2 = sel[1];
            const isP = h1 === h2;
            const idx1 = cards.indexOf(h1), idx2 = cards.indexOf(h2);
            
            let d = document.getElementById('dec'), t = document.getElementById('tier');
            let i = document.getElementById('itm'), r = document.getElementById('rnk');

            if (isP && idx1 <= 4) { // AA-TT
                d.innerText = "ALL-IN / RAISE"; d.style.color = "#00ff00";
                t.innerText = "TIER S: PREMIUM PAIR"; i.innerText = "85%"; r.innerText = "#1";
            } else if (h1 === 'A' && (idx2 <= 2 || (same && idx2 <= 9))) { // AK, AQ, AJ o Ax suited
                d.innerText = (bbs < 15) ? "ALL-IN" : "RAISE"; d.style.color = "#00ff00";
                t.innerText = "TIER A: TOP RANGE"; i.innerText = "65%"; r.innerText = "#2";
            } else if (idx1 <= 2 && idx2 <= 3 && same) { // KQs, KJs, QJs
                d.innerText = (bbs < 12) ? "SHOVE" : "OPEN RAISE"; d.style.color = "#ffff00";
                t.innerText = "TIER B: BROADWAY SUITED"; i.innerText = "55%"; r.innerText = "#3";
            } else if (isP && idx1 > 4) { // Small pairs
                d.innerText = (bbs < 20) ? "PUSH/FOLD" : "SET MINING"; d.style.color = "#ffcc00";
                t.innerText = "TIER C: POCKET PAIR"; i.innerText = "48%"; r.innerText = "#4";
            } else {
                d.innerText = "FOLD"; d.style.color = "#ff4444";
                t.innerText = "TIER F: BASURA"; i.innerText = "18%"; r.innerText = "#10";
            }
        }
        init();
    </script>
</body>
</html>
"""
components.html(html_code, height=750)

