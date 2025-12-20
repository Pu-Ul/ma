import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="POKER RADAR EDU + CALMA", layout="centered")

html_code = r"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:#000; color:#fff; margin:0; padding:10px; text-align:center; }
    .wrap { max-width: 460px; margin:0 auto; }

    .bb-selector { display:flex; justify-content:space-around; margin-bottom:12px; background:#111; padding:6px; border-radius:12px; }
    .bb-btn { flex:1; margin:0 3px; font-size:.82rem; padding:10px 0; background:#222; border:1px solid #444; color:#aaa; border-radius:10px; }
    .bb-btn.active { background:#ffcc00!important; color:#000!important; font-weight:900; }

    .grid { display:grid; grid-template-columns:repeat(4,1fr); gap:6px; max-width: 440px; margin:0 auto; }
    .c-btn { padding:14px 0; font-size:1.35rem; background:#1a1a1a; color:#fff; border:1px solid #333; border-radius:12px; }
    .c-btn.active { background:#00ff00!important; color:#000!important; font-weight:900; }

    .suit-main { display:flex; gap:8px; margin:12px auto; max-width: 440px; }
    .s-btn { flex:1; padding:14px; font-size:1rem; font-weight:900; border-radius:14px; border:1px solid #333; background:#1a1a1a; color:#666; }
    .s-btn.active-s { background:#0055ff!important; color:#fff!important; }
    .s-btn.active-o { background:#444!important; color:#fff!important; }

    #res { display:none; margin-top:10px; border:2px solid #00ff00; background:#050505; padding:14px; border-radius:16px; }
    .dec { font-size:2.25rem; font-weight:1000; margin-bottom:6px; }
    .sub { color:#bbb; font-size:.92rem; margin-top:4px; }

    .btn-row { display:flex; gap:8px; margin-top:12px; flex-wrap: wrap; }
    .btn { flex:1; min-width: 140px; padding:14px; border:none; border-radius:14px; font-weight:1000; font-size:1rem; cursor:pointer; }
    .btn-new { background:#e74c3c; color:#fff; }
    .btn-round { background:#2ecc71; color:#000; }
    .btn-wipe { background:#444; color:#fff; }
    .btn-calm { background:#aee8ff; color:#000; }

    .panel { margin-top:14px; text-align:left; background:#111; padding:12px; border-radius:14px; border:1px solid #222; }
    .title { color:#ffcc00; font-weight:1000; font-size:.98rem; display:block; margin-bottom:8px; }
    .small { color:#aaa; font-size:.88rem; line-height:1.35; }
    .badge { display:inline-block; padding:3px 9px; border-radius:999px; font-size:.8rem; font-weight:1000; margin-left:6px; }
    .b-pro { background:#00ff00; color:#000; }
    .b-pre { background:#00aaff; color:#000; }
    .b-warn { background:#ffcc00; color:#000; }

    table { width:100%; border-collapse:collapse; font-size:.85rem; }
    th { color:#666; text-align:left; border-bottom:1px solid #333; padding:6px 4px; }
    td { border-bottom:1px solid #222; padding:7px 4px; }
    .pro { color:#00ff00; font-weight:1000; }
    .pre { color:#00aaff; font-weight:1000; }
    .fold { color:#ff4444; font-weight:1000; }
    .raise { color:#ffcc00; font-weight:1000; }

    #motivationBox{
      margin-top:10px;
      padding:10px;
      background:#0b0b0b;
      border:1px solid #222;
      border-radius:12px;
      color:#aee8ff;
      font-size:.95rem;
      transition:opacity .25s;
      opacity: 0.95;
      white-space: pre-line;
    }

    /* Calm overlay */
    #calmOverlay{
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.85);
      display:none;
      align-items:center;
      justify-content:center;
      padding: 18px;
      z-index: 9999;
    }
    #calmCard{
      width: 100%;
      max-width: 420px;
      background:#0b0b0b;
      border:1px solid #222;
      border-radius:16px;
      padding:16px;
      text-align:left;
    }
    #calmTitle{ color:#aee8ff; font-weight:1000; font-size:1.05rem; margin-bottom:8px; }
    #calmText{ color:#fff; font-size:1rem; line-height:1.4; margin-bottom:12px; }
    #calmBar{
      height: 10px;
      border-radius:999px;
      background:#111;
      border:1px solid #222;
      overflow:hidden;
    }
    #calmFill{
      height: 100%;
      width: 0%;
      background:#aee8ff;
      transition: width .2s linear;
    }
    #calmClose{
      margin-top:12px;
      width:100%;
      padding:12px;
      border:none;
      border-radius:12px;
      background:#444;
      color:#fff;
      font-weight:1000;
      cursor:pointer;
    }

    .footer { margin-top:16px; color:#444; font-size:.9rem; }
    .footer b { color:#00ff00; }
  </style>
</head>

<body>
  <div class="wrap">
    <div class="bb-selector">
      <button class="bb-btn" id="bb1" data-bb="10">&lt;10 BB</button>
      <button class="bb-btn active" id="bb2" data-bb="30">10–40 BB</button>
      <button class="bb-btn" id="bb3" data-bb="50">40+ BB</button>
    </div>

    <div class="grid" id="g"></div>

    <div class="suit-main">
      <button class="s-btn" id="btnS">SUITED (s)</button>
      <button class="s-btn" id="btnO">OFFSUIT (o)</button>
    </div>

    <div id="res">
      <div id="dec" class="dec"></div>
      <div class="sub" id="eduHint"></div>
      <div id="motivationBox">Respira. Vamos una mano a la vez.</div>

      <div class="btn-row">
        <button class="btn btn-new" onclick="resetHand()">NUEVA MANO</button>
        <button class="btn btn-round" onclick="newRound()">NUEVA RONDA</button>
        <button class="btn btn-calm" onclick="startCalm10()">CALMA 10s</button>
      </div>
    </div>

    <div class="panel">
      <span class="title">🧠 EDUCACIÓN: PROACTIVA vs PREVENTIVA</span>
      <div class="small" id="eduPanel"></div>
    </div>

    <div class="panel">
      <span class="title">📈 HISTORIAL ACUMULATIVO</span>
      <table>
        <thead>
          <tr><th>Ronda</th><th>Mano</th><th>BB</th><th>Acción</th><th>Tipo</th></tr>
        </thead>
        <tbody id="hBody"></tbody>
      </table>
      <div class="btn-row">
        <button class="btn btn-wipe" onclick="wipeAll()">BORRAR TODO</button>
      </div>
    </div>

    <div class="panel">
      <span class="title">🧾 RESUMEN POR RONDA</span>
      <table>
        <thead><tr><th>Ronda</th><th>Manos</th><th>Pro</th><th>Prev</th><th>% Pro</th></tr></thead>
        <tbody id="rBody"></tbody>
      </table>
    </div>

    <div class="footer">Developed by <b>PauGaR</b></div>
  </div>

  <!-- CALM OVERLAY -->
  <div id="calmOverlay">
    <div id="calmCard">
      <div id="calmTitle">🫧 Calma 10 segundos</div>
      <div id="calmText">Inhala 4… Exhala 6…<br>Una mano a la vez.</div>
      <div id="calmBar"><div id="calmFill"></div></div>
      <button id="calmClose" onclick="closeCalm()">Cerrar</button>
    </div>
  </div>

  <script>
    // ---------------- UI state ----------------
    const cards = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];
    let sel = [];
    let suited = null; // true/false
    let bbs = 30;

    // --------------- LocalStorage keys ----------------
    const K_HIST  = "poker_edu_hist_v3";
    const K_STATS = "poker_edu_stats_v3";
    const K_ROUND = "poker_edu_round_v3";
    const K_RSUM  = "poker_edu_rsum_v3";

    // --------------- Storage helpers ----------------
    function jget(key, fallback){
      try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; }
      catch(e){ return fallback; }
    }
    function jset(key, val){ localStorage.setItem(key, JSON.stringify(val)); }

    function getRound(){ return jget(K_ROUND, 1); }
    function setRound(n){ jset(K_ROUND, n); }

    function getStats(){ return jget(K_STATS, { total:0, proactive:0, preventive:0, streakFold:0 }); }
    function saveStats(s){ jset(K_STATS, s); }

    function getHist(){ return jget(K_HIST, []); }
    function saveHist(h){ jset(K_HIST, h); }

    function getRoundSummary(){ return jget(K_RSUM, {}); }
    function saveRoundSummary(m){ jset(K_RSUM, m); }

    // --------------- Classification ----------------
    function classify(action){
      return (action === "PUSH" || action === "RAISE") ? "PROACTIVA" : "PREVENTIVA";
    }

    // --------------- Calm messages ----------------
    const calmMessages = {
      PROACTIVA: [
        "Respira. Tomaste iniciativa con criterio.",
        "Buena presión. Jugar con intención es progreso.",
        "Confía en el proceso, no en el resultado.",
        "Decidir con claridad también es ganar."
      ],
      PREVENTIVA: [
        "Cuidar fichas es una decisión inteligente.",
        "No entrar también es jugar bien.",
        "Elegiste paciencia. Eso también suma.",
        "Evitar spots malos protege tu juego."
      ],
      AGGRESSIVE: [
        "Pausa breve. No todo spot necesita fuerza.",
        "Calma: el mejor spot no se fuerza, se espera.",
        "Respira 4–4: inhala 4, exhala 4. Vuelve al plan."
      ],
      PASSIVE: [
        "Ojo: quizá estás evitando por tensión. Busca un spot claro.",
        "No necesitas perfección, solo un spot +EV.",
        "Pequeña iniciativa con disciplina también es control."
      ],
      TILT: [
        "La rabia baja si respiras: 4 inhala, 6 exhala.",
        "Un mal resultado no invalida una buena decisión.",
        "No te castigues: ajusta y sigue. Una mano a la vez.",
        "Calma: tu estrategia manda, no la emoción."
      ]
    };
    function pick(arr){ return arr[Math.floor(Math.random()*arr.length)]; }

    function educationMessage(stats){
      if(stats.total < 5){
        return { badge:"b-warn", label:"EN CALENTAMIENTO", text:"📘 Aún recopilando datos (5+ manos para lectura real)." };
      }
      const ratio = stats.proactive / stats.total;
      if(ratio < 0.30){
        return { badge:"b-pre", label:"MUY PREVENTIVA", text:"🔵 Estás foldeando demasiado. Busca spots claros de valor." };
      }
      if(ratio <= 0.60){
        return { badge:"b-pro", label:"EQUILIBRADA", text:"🟢 Buen balance: controlas riesgos y eliges spots." };
      }
      return { badge:"b-warn", label:"MUY PROACTIVA", text:"🟠 Estás presionando mucho. Revisa spots marginales." };
    }

    function motivationalMessage(action, stats){
      let msg = (action === "PUSH" || action === "RAISE") ? pick(calmMessages.PROACTIVA) : pick(calmMessages.PREVENTIVA);
      if(stats.streakFold >= 3) msg = pick(calmMessages.TILT);
      else if(stats.total >= 5){
        const ratio = stats.proactive / stats.total;
        if(ratio > 0.65) msg = pick(calmMessages.AGGRESSIVE);
        if(ratio < 0.30) msg = pick(calmMessages.PASSIVE);
      }
      return msg;
    }

    function showMotivation(text){
      const box = document.getElementById("motivationBox");
      if(!box) return;
      box.innerText = text;
      box.style.opacity = 1;
      setTimeout(()=>{ box.style.opacity = 0.92; }, 1200);
    }

    // --------------- Decision logic (educational placeholder) ----------------
    function decide(h1, h2, suitedFlag, bb){
      const isPair = (h1 === h2);
      const strongPairs = ['A','K','Q','J','T'];
      if(isPair && strongPairs.includes(h1)) return "PUSH";
      if(h1 === 'A' && suitedFlag === true) return "RAISE";
      if(bb <= 10 && h1 === 'A') return "RAISE";
      return "FOLD";
    }

    function actionHint(action){
      if(action === "PUSH") return "Proactiva: tomas la iniciativa y maximizas fold equity.";
      if(action === "RAISE") return "Proactiva: presionas y defines el spot con iniciativa.";
      return "Preventiva: conservas fichas y evitas spots con EV bajo.";
    }

    // --------------- Render ----------------
    function initGrid(){
      const g = document.getElementById('g');
      g.innerHTML = "";
      cards.forEach(c=>{
        const b = document.createElement('button');
        b.innerText = c;
        b.className = "c-btn";
        b.onclick = ()=>pickCard(c,b);
        g.appendChild(b);
      });
    }

    function pickCard(c, btn){
      if(sel.length >= 2) return;
      sel.push(c);
      btn.classList.add('active');

      if(sel.length === 2){
        if(sel[0] === sel[1]){
          suited = false;
          calc();
        } else if(suited !== null){
          calc();
        }
      }
    }

    function setBB(v, clicked){
      bbs = v;
      document.querySelectorAll('.bb-btn').forEach(b=>b.classList.remove('active'));
      clicked.classList.add('active');
    }

    function setSuited(v){
      suited = v;
      document.getElementById('btnS').className = v ? "s-btn active-s" : "s-btn";
      document.getElementById('btnO').className = (!v) ? "s-btn active-o" : "s-btn";
      if(sel.length === 2 && sel[0] !== sel[1]) calc();
    }

    function renderEducation(){
      const stats = getStats();
      const msg = educationMessage(stats);
      const ratio = stats.total ? Math.round((stats.proactive / stats.total) * 100) : 0;

      document.getElementById("eduPanel").innerHTML =
        `Total manos: <b>${stats.total}</b><br>
         Proactivas: <b>${stats.proactive}</b> | Preventivas: <b>${stats.preventive}</b><br>
         Perfil Proactivo: <b>${ratio}%</b>
         <span class="badge ${msg.badge}">${msg.label}</span><br>
         <span class="small">${msg.text}</span>`;
    }

    function renderHistory(){
      const hist = getHist();
      const body = document.getElementById("hBody");
      body.innerHTML = hist.slice(0, 25).map(h=>{
        const aCls = (h.action==="FOLD") ? "fold" : (h.action==="RAISE" ? "raise" : "pro");
        const tCls = (h.type==="PROACTIVA") ? "pro" : "pre";
        return `<tr>
          <td>${h.round}</td>
          <td>${h.hand}</td>
          <td>${h.bb}</td>
          <td class="${aCls}">${h.action}</td>
          <td class="${tCls}">${h.type}</td>
        </tr>`;
      }).join('');
    }

    function renderRounds(){
      const rsum = getRoundSummary();
      const rounds = Object.keys(rsum).map(n=>parseInt(n,10)).sort((a,b)=>b-a);
      const body = document.getElementById("rBody");
      body.innerHTML = rounds.slice(0, 15).map(r=>{
        const s = rsum[String(r)];
        const pct = s.hands ? Math.round((s.pro / s.hands) * 100) : 0;
        return `<tr>
          <td>${r}</td>
          <td>${s.hands}</td>
          <td class="pro">${s.pro}</td>
          <td class="pre">${s.prev}</td>
          <td><b>${pct}%</b></td>
        </tr>`;
      }).join('');
    }

    // --------------- Core: register accumulatively ----------------
    function registerHand(hand, bb, action){
      const round = getRound();
      const type = classify(action);

      const stats = getStats();
      stats.total += 1;
      if(type === "PROACTIVA") stats.proactive += 1;
      else stats.preventive += 1;

      // fold streak for tilt support
      if(action === "FOLD") stats.streakFold += 1;
      else stats.streakFold = 0;

      saveStats(stats);

      const rsum = getRoundSummary();
      if(!rsum[String(round)]) rsum[String(round)] = { hands:0, pro:0, prev:0 };
      rsum[String(round)].hands += 1;
      if(type === "PROACTIVA") rsum[String(round)].pro += 1;
      else rsum[String(round)].prev += 1;
      saveRoundSummary(rsum);

      const hist = getHist();
      hist.unshift({ round, hand, bb, action, type, ts: Date.now() });
      saveHist(hist);

      renderEducation();
      renderHistory();
      renderRounds();

      showMotivation(motivationalMessage(action, stats));
    }

    function calc(){
      if(sel.length < 2) return;
      if(sel[0] !== sel[1] && suited === null) return;

      const h1 = sel[0], h2 = sel[1];
      const handTxt = `${h1}${h2}${(h1===h2)?'':(suited?'s':'o')}`;
      const action = decide(h1, h2, suited, bbs);

      document.getElementById("res").style.display = "block";
      const dec = document.getElementById("dec");
      dec.innerText = action;
      dec.style.color = (action==="FOLD") ? "#ff4444" : (action==="RAISE" ? "#ffcc00" : "#00ff00");
      document.getElementById("eduHint").innerText = actionHint(action);

      registerHand(handTxt, bbs, action);
    }

    function resetHand(){
      sel = [];
      suited = null;
      document.getElementById('res').style.display = 'none';
      document.getElementById('btnS').className = "s-btn";
      document.getElementById('btnO').className = "s-btn";
      initGrid();
    }

    function newRound(){
      const current = getRound();
      setRound(current + 1);
      resetHand();
      renderRounds();
      showMotivation("Nueva ronda. Respira. Tu plan sigue intacto.");
    }

    function wipeAll(){
      localStorage.removeItem(K_HIST);
      localStorage.removeItem(K_STATS);
      localStorage.removeItem(K_RSUM);
      localStorage.removeItem(K_ROUND);
      setRound(1);
      resetHand();
      renderEducation();
      renderHistory();
      renderRounds();
      showMotivation("Reinicio limpio. Sin culpa: claridad y calma.");
    }

    // -------- CALMA 10s (inhala 4 / exhala 6) --------
    let calmTimer = null;
    function startCalm10(){
      const overlay = document.getElementById("calmOverlay");
      const text = document.getElementById("calmText");
      const fill = document.getElementById("calmFill");

      overlay.style.display = "flex";
      fill.style.width = "0%";
      let t = 0;

      if(calmTimer) clearInterval(calmTimer);

      // 10s total: show instructions by second
      calmTimer = setInterval(()=>{
        t += 1;
        fill.style.width = `${(t/10)*100}%`;

        if(t <= 4){
          text.innerText = `Inhala… ${5 - t}\nSuelta hombros y mandíbula.`;
        } else {
          text.innerText = `Exhala… ${11 - t}\nDeja que baje la rabia.`;
        }

        if(t >= 10){
          clearInterval(calmTimer);
          calmTimer = null;
          text.innerText = "Listo. Vuelve al plan.\nUna mano a la vez.";
          setTimeout(()=> closeCalm(), 700);
        }
      }, 1000);
    }

    function closeCalm(){
      const overlay = document.getElementById("calmOverlay");
      overlay.style.display = "none";
    }

    // Bind BB buttons
    document.getElementById('bb1').onclick = (e)=>setBB(10, e.target);
    document.getElementById('bb2').onclick = (e)=>setBB(30, e.target);
    document.getElementById('bb3').onclick = (e)=>setBB(50, e.target);

    // Bind suited buttons
    document.getElementById('btnS').onclick = ()=>setSuited(true);
    document.getElementById('btnO').onclick = ()=>setSuited(false);

    // Init
    initGrid();
    renderEducation();
    renderHistory();
    renderRounds();
    showMotivation("Respira. Vamos una mano a la vez.");
  </script>
</body>
</html>
"""

components.html(html_code, height=1350, scrolling=True)
