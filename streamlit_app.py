import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="POKER RADAR + HISTORIAL", layout="centered")

html_code = r"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <style>
    body { font-family: sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 10px; }
    .bb-selector { display: flex; justify-content: space-around; margin-bottom: 12px; background: #111; padding: 5px; border-radius: 8px; }
    .bb-btn { flex: 1; margin: 0 3px; font-size: 0.75rem; padding: 10px 0; background: #222; border: 1px solid #444; color: #888; border-radius: 5px; }
    .bb-btn.active { background: #ffcc00 !important; color: #000 !important; font-weight: bold; }

    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; max-width: 400px; margin: 0 auto; }
    .c-btn { padding: 15px 0; font-size: 1.4rem; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 6px; }
    .c-btn.active { background: #00ff00 !important; color: #000 !important; font-weight: bold; }

    .suit-main { display: flex; gap: 8px; margin: 12px auto; max-width: 400px; }
    .s-btn { flex: 1; padding: 15px; font-size: 1rem; font-weight: bold; border-radius: 8px; border: 1px solid #333; background: #1a1a1a; color: #555; }
    .s-btn.active-s { background: #0055ff !important; color: #fff !important; }
    .s-btn.active-o { background: #444 !important; color: #fff !important; }

    #res { display: none; margin-top: 10px; border: 2px solid #00ff00; background: #050505; padding: 15px; border-radius: 12px; }
    .dec { font-size: 2.2rem; font-weight: bold; margin-bottom: 2px; }
    .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .stat-card { background: #111; padding: 10px; border-radius: 8px; }

    .btn-clear { width: 100%; padding: 18px; background: #e74c3c; color: #fff; font-size: 1.3rem; font-weight: bold; border: none; border-radius: 10px; margin-top: 12px; }

    /* HISTORIAL */
    .history-section { margin-top: 20px; text-align: left; background: #111; padding: 15px; border-radius: 10px; border: 1px solid #222; max-width: 420px; margin-left: auto; margin-right: auto; }
    .history-title { color: #ffcc00; font-size: 0.9rem; margin-bottom: 10px; display: block; font-weight: bold; }
    .small { font-size: 0.8rem; color: #aaa; }
    table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    th { border-bottom: 1px solid #333; padding: 6px 5px; color: #666; text-align: left; }
    td { padding: 8px 5px; border-bottom: 1px solid #222; }
    .h-push { color: #00ff00; font-weight: bold; }
    .h-fold { color: #ff4444; font-weight: bold; }
    .h-raise { color: #ffcc00; font-weight: bold; }

    .btn-del { background: none; border: 1px solid #444; color: #aaa; font-size: 0.8rem; padding: 10px; border-radius: 6px; cursor: pointer; width: 100%; margin-top: 10px; }
    .footer { margin-top: 20px; padding: 15px; font-size: 0.9rem; color: #444; }
    .footer b { color: #00ff00; }
  </style>
</head>

<body>
  <div class="bb-selector">
    <button class="bb-btn" id="bb1" data-bb="10">&lt;10 BB</button>
    <button class="bb-btn active" id="bb2" data-bb="30">10-40 BB</button>
    <button class="bb-btn" id="bb3" data-bb="50">40+ BB</button>
  </div>

  <div class="grid" id="g"></div>

  <div class="suit-main">
    <button class="s-btn" id="btnS">SUITED (s)</button>
    <button class="s-btn" id="btnO">OFFSUIT (o)</button>
  </div>

  <div id="res">
    <div id="dec" class="dec"></div>
    <div class="stats">
      <div class="stat-card"><span>EQUITY</span><br><span id="itm" style="color:#00ff00; font-size: 1.4rem;"></span></div>
      <div class="stat-card"><span>RANGO</span><br><span id="rnk" style="font-size: 1.4rem;"></span></div>
    </div>
    <button class="btn-clear" onclick="resetHand()">NUEVA MANO</button>
  </div>

  <div class="history-section">
    <span class="history-title">📈 TENDENCIAS RECIENTES (PauGaR)</span>

    <div class="small" id="vppLine">VPP: 0% (0/0 jugadas)</div>

    <table>
      <thead><tr><th>MANO</th><th>BB</th><th>ACCIÓN</th></tr></thead>
      <tbody id="hBody"></tbody>
    </table>

    <button onclick="clearHistory()" class="btn-del">BORRAR HISTORIAL COMPLETO</button>
  </div>

  <div class="footer">Developed by <b>PauGaR</b></div>

  <script>
    const cards = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];

    let sel = [];
    let suited = null;   // true = suited, false = offsuit
    let bbs = 30;

    function initGrid() {
      const g = document.getElementById('g');
      g.innerHTML = "";
      cards.forEach(c => {
        const b = document.createElement('button');
        b.innerText = c;
        b.className = "c-btn";
        b.onclick = () => pickCard(c, b);
        g.appendChild(b);
      });
    }

    function pickCard(c, btn) {
      if (sel.length >= 2) return;
      sel.push(c);
      btn.classList.add('active');

      if (sel.length === 2) {
        // parejas no necesitan suited/offsuit
        if (sel[0] === sel[1]) {
          suited = false;
          calc();
        } else if (suited !== null) {
          calc();
        }
      }
    }

    function setBB(v, clickedBtn) {
      bbs = v;
      document.querySelectorAll('.bb-btn').forEach(b => b.classList.remove('active'));
      clickedBtn.classList.add('active');
      // si ya hay 2 cartas y suited definido, recalcula
      if (sel.length === 2 && (sel[0] === sel[1] || suited !== null)) calc();
    }

    function setSuited(v) {
      suited = v;
      document.getElementById('btnS').className = v ? "s-btn active-s" : "s-btn";
      document.getElementById('btnO').className = (!v) ? "s-btn active-o" : "s-btn";
      if (sel.length === 2 && sel[0] !== sel[1]) calc();
    }

    function decisionLogic(h1, h2, isPair, idx1, idx2, suitedFlag) {
      // Lógica ejemplo (la tuya real puede ser más completa)
      // Devuelve {action, equity, rank, cls, color}
      if (isPair && idx1 <= 4) {
        return { action: "PUSH", equity: "85%", rank: "#1", cls: "h-push", color: "#00ff00" };
      } else if (h1 === 'A' && (idx2 <= 2 || suitedFlag === true)) {
        return { action: "RAISE", equity: "65%", rank: "#2", cls: "h-raise", color: "#ffcc00" };
      } else {
        return { action: "FOLD", equity: "18%", rank: "#10", cls: "h-fold", color: "#ff4444" };
      }
    }

    function calc() {
      if (sel.length < 2) return;
      if (sel[0] !== sel[1] && suited === null) return;

      const h1 = sel[0], h2 = sel[1];
      const idx1 = cards.indexOf(h1), idx2 = cards.indexOf(h2);
      const isP = h1 === h2;

      const res = decisionLogic(h1, h2, isP, idx1, idx2, suited);
      document.getElementById('res').style.display = 'block';

      const d = document.getElementById('dec');
      const i = document.getElementById('itm');
      const r = document.getElementById('rnk');

      d.innerText = res.action;
      d.style.color = res.color;
      i.innerText = res.equity;
      r.innerText = res.rank;

      const handTxt = `${h1}${h2}${isP ? '' : (suited ? 's' : 'o')}`;
      saveToHistory(handTxt, bbs, res.action, res.cls);
    }

    function getHistory() {
      try {
        return JSON.parse(localStorage.getItem('poker_hist')) || [];
      } catch (e) {
        return [];
      }
    }

    function setHistory(history) {
      localStorage.setItem('poker_hist', JSON.stringify(history));
    }

    function saveToHistory(mano, bb, acc, cls) {
      let history = getHistory();
      history.unshift({ mano, bb, acc, cls, ts: Date.now() });
      if (history.length > 10) history.pop();
      setHistory(history);
      updateHistoryTable();
    }

    function updateVPP(history) {
      const total = history.length;
      const played = history.filter(h => (h.acc === "PUSH" || h.acc === "RAISE")).length;
      const vpp = total === 0 ? 0 : Math.round((played / total) * 100);
      document.getElementById('vppLine').innerText = `VPP: ${vpp}% (${played}/${total} jugadas)`;
    }

    function updateHistoryTable() {
      const history = getHistory();
      const body = document.getElementById('hBody');
      body.innerHTML = history.map(h =>
        `<tr>
          <td>${h.mano}</td>
          <td>${h.bb}BB</td>
          <td class="${h.cls}">${h.acc}</td>
        </tr>`
      ).join('');
      updateVPP(history);
    }

    function clearHistory() {
      localStorage.removeItem('poker_hist');
      updateHistoryTable();
    }

    function resetHand() {
      sel = [];
      suited = null;
      document.getElementById('res').style.display = 'none';
      document.getElementById('btnS').className = "s-btn";
      document.getElementById('btnO').className = "s-btn";
      initGrid();
    }

    // Bind buttons
    document.getElementById('bb1').onclick = (e) => setBB(10, e.target);
    document.getElementById('bb2').onclick = (e) => setBB(30, e.target);
    document.getElementById('bb3').onclick = (e) => setBB(50, e.target);
    document.getElementById('btnS').onclick = () => setSuited(true);
    document.getElementById('btnO').onclick = () => setSuited(false);

    // Init
    initGrid();
    updateHistoryTable();
  </script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=True)
