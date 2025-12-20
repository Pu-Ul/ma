html_code = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
      color: #fff;
      padding: 15px;
      min-height: 100vh;
    }
    .container { max-width: 420px; margin: 0 auto; }
    .header { text-align: center; margin-bottom: 20px; }
    .header h1 { font-size: 1.8rem; margin-bottom: 5px; }
    .header p { color: #a0d8f1; font-size: 0.9rem; }
    
    .card { background: rgba(0,0,0,0.4); backdrop-filter: blur(10px); border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); }
    
    .input-group { margin-bottom: 12px; }
    .input-group label { display: block; font-size: 0.85rem; color: #a0d8f1; margin-bottom: 6px; font-weight: 600; }
    
    .card-select-container { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    select, input { 
      width: 100%; 
      padding: 14px; 
      background: #1a3a4a; 
      border: 2px solid #2c5364; 
      border-radius: 8px; 
      color: #fff; 
      font-size: 1rem;
      font-weight: bold;
    }
    select:focus, input:focus { outline: none; border-color: #4a90e2; }
    
    .flop-container, .single-card { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
    .single-card { grid-template-columns: 1fr; }
    
    .btn { 
      width: 100%; 
      padding: 16px; 
      font-size: 1.05rem; 
      font-weight: bold; 
      border: none; 
      border-radius: 10px; 
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn:active { transform: scale(0.98); }
    .btn-primary { background: #4a90e2; color: #fff; }
    .btn-primary:hover { background: #357abd; }
    .btn-primary:disabled { background: #555; cursor: not-allowed; opacity: 0.5; }
    .btn-success { background: #27ae60; color: #fff; }
    .btn-success:hover { background: #229954; }
    .btn-danger { background: #e74c3c; color: #fff; }
    .btn-danger:hover { background: #c0392b; }
    .btn-secondary { background: #555; color: #fff; }
    .btn-secondary:hover { background: #444; }
    
    .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
    
    .hand-display { text-align: center; padding: 15px; }
    .hand-cards { font-size: 2.5rem; font-weight: bold; letter-spacing: 8px; margin-bottom: 8px; }
    .hand-name { color: #4a90e2; font-size: 1.1rem; margin-bottom: 5px; }
    .hand-meta { color: #888; font-size: 0.9rem; }
    
    .strength-bar { margin: 15px 0; }
    .strength-label { display: flex; justify-content: space-between; margin-bottom: 8px; }
    .strength-label span:last-child { font-size: 1.4rem; font-weight: bold; color: #f39c12; }
    .bar-bg { width: 100%; height: 8px; background: #333; border-radius: 4px; overflow: hidden; }
    .bar-fill { height: 100%; background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%); transition: width 0.3s; }
    
    .advice-box { 
      background: rgba(74, 144, 226, 0.15); 
      border-left: 4px solid #4a90e2; 
      padding: 15px; 
      border-radius: 8px; 
      margin: 15px 0;
    }
    .advice-action { font-size: 1.3rem; font-weight: bold; color: #f39c12; margin-bottom: 8px; }
    .advice-reason { font-size: 0.95rem; line-height: 1.5; margin-bottom: 10px; }
    .advice-term { font-size: 0.85rem; color: #4a90e2; font-style: italic; }
    
    .board-display { text-align: center; margin: 15px 0; }
    .board-label { font-size: 0.85rem; color: #888; margin-bottom: 8px; }
    .board-cards { font-size: 1.8rem; font-weight: bold; letter-spacing: 6px; }
    
    .history { max-height: 300px; overflow-y: auto; }
    .history-title { font-size: 1rem; font-weight: bold; margin-bottom: 12px; color: #f39c12; }
    .history-item { 
      background: rgba(0,0,0,0.3); 
      padding: 12px; 
      border-radius: 8px; 
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .history-hand { font-weight: bold; font-size: 1rem; }
    .history-position { color: #888; font-size: 0.85rem; margin-left: 8px; }
    .history-stats { text-align: right; }
    .history-strength { color: #f39c12; font-weight: bold; }
    .history-bb { font-size: 0.8rem; color: #888; }
    
    .hidden { display: none; }
    
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
    ::-webkit-scrollbar-thumb { background: #4a90e2; border-radius: 3px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🎴 Poker Advisor Pro</h1>
      <p>Asistente Inteligente de Texas Hold'em</p>
    </div>

    <!-- PANTALLA INICIAL -->
    <div id="screenStart">
      <div class="card">
        <div class="input-group">
          <label>🂡 Tu Mano (2 cartas)</label>
          <div class="card-select-container">
            <select id="card1">
              <option value="">Carta 1</option>
            </select>
            <select id="card2">
              <option value="">Carta 2</option>
            </select>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-select-container">
          <div class="input-group">
            <label>📍 Posición</label>
            <select id="position">
              <option value="">Selecciona</option>
              <option value="UTG">UTG (Early)</option>
              <option value="MP">MP (Middle)</option>
              <option value="CO">CO (Cutoff)</option>
              <option value="BTN">BTN (Button)</option>
              <option value="SB">SB (Small Blind)</option>
              <option value="BB">BB (Big Blind)</option>
            </select>
          </div>
          <div class="input-group">
            <label>💰 Stack (BB)</label>
            <input type="number" id="stackBB" placeholder="100" min="1">
          </div>
        </div>
      </div>

      <button class="btn btn-primary" onclick="analyzePreflop()">🎯 Analizar Preflop</button>
    </div>

    <!-- PANTALLA PREFLOP -->
    <div id="screenPreflop" class="hidden">
      <div class="card">
        <div class="hand-display">
          <div class="hand-cards" id="displayHand"></div>
          <div class="hand-name" id="displayHandName"></div>
          <div class="hand-meta" id="displayMeta"></div>
        </div>
        
        <div class="strength-bar">
          <div class="strength-label">
            <span>Fuerza de Mano</span>
            <span id="strengthValue"></span>
          </div>
          <div class="bar-bg">
            <div class="bar-fill" id="strengthBar"></div>
          </div>
        </div>

        <div class="advice-box">
          <div class="advice-action" id="adviceAction"></div>
          <div class="advice-reason" id="adviceReason"></div>
          <div class="advice-term">📚 <span id="adviceTerm"></span></div>
        </div>
      </div>

      <div class="btn-grid">
        <button class="btn btn-success" onclick="goToFlop()">Ver Flop →</button>
        <button class="btn btn-danger" onclick="foldHand()">Fold / Nueva</button>
      </div>
    </div>

    <!-- PANTALLA FLOP -->
    <div id="screenFlop" class="hidden">
      <div class="card">
        <div class="board-display">
          <div class="board-label">Tu mano: <span id="flopYourHand"></span></div>
          <div class="board-label" style="margin-top: 10px; font-size: 1.1rem; color: #f39c12;">FLOP</div>
        </div>
        
        <div class="input-group">
          <label>🃏 Cartas del Flop</label>
          <div class="flop-container">
            <select id="flopC1"><option value="">C1</option></select>
            <select id="flopC2"><option value="">C2</option></select>
            <select id="flopC3"><option value="">C3</option></select>
          </div>
        </div>

        <div class="advice-box">
          <div class="advice-reason">Ingresa las 3 cartas del flop para analizar tu situación.</div>
          <div class="advice-term">📚 Textura: Cómo las cartas comunitarias se conectan entre sí.</div>
        </div>
      </div>

      <div class="btn-grid">
        <button class="btn btn-primary" onclick="analyzeFlop()">🔍 Analizar Flop</button>
        <button class="btn btn-danger" onclick="foldHand()">Fold / Nueva</button>
      </div>
    </div>

    <!-- PANTALLA POST-FLOP -->
    <div id="screenPostFlop" class="hidden">
      <div class="card">
        <div class="board-display">
          <div class="board-label">Mano: <span id="postFlopHand"></span></div>
          <div class="board-label">Flop: <span id="postFlopBoard" class="board-cards"></span></div>
        </div>

        <div class="advice-box">
          <div class="advice-action" id="flopAdviceAction"></div>
          <div class="advice-reason" id="flopAdviceReason"></div>
          <div class="advice-term">📚 <span id="flopAdviceTerm"></span></div>
        </div>
      </div>

      <div class="btn-grid">
        <button class="btn btn-success" onclick="goToTurn()">Ver Turn →</button>
        <button class="btn btn-danger" onclick="foldHand()">Fold / Nueva</button>
      </div>
    </div>

    <!-- PANTALLA TURN -->
    <div id="screenTurn" class="hidden">
      <div class="card">
        <div class="board-display">
          <div class="board-label">Mano: <span id="turnYourHand"></span></div>
          <div class="board-label">Flop: <span id="turnFlopBoard"></span></div>
          <div class="board-label" style="margin-top: 10px; font-size: 1.1rem; color: #f39c12;">TURN</div>
        </div>
        
        <div class="input-group">
          <label>🎴 Carta del Turn</label>
          <div class="single-card">
            <select id="turnCard"><option value="">Selecciona</option></select>
          </div>
        </div>

        <div class="advice-box">
          <div class="advice-reason">La cuarta carta cambia dinámicas. Evalúa si mejoraste o hay nuevos peligros.</div>
          <div class="advice-term">📚 Outs: Cartas que mejorarían tu mano a ganadora.</div>
        </div>
      </div>

      <div class="btn-grid">
        <button class="btn btn-primary" onclick="analyzeTurn()">🔍 Analizar Turn</button>
        <button class="btn btn-danger" onclick="foldHand()">Fold / Nueva</button>
      </div>
    </div>

    <!-- PANTALLA POST-TURN -->
    <div id="screenPostTurn" class="hidden">
      <div class="card">
        <div class="board-display">
          <div class="board-label">Mano: <span id="postTurnHand"></span></div>
          <div class="board-label">Board: <span id="postTurnBoard" class="board-cards"></span></div>
        </div>

        <div class="advice-box">
          <div class="advice-action">DECISIÓN CRÍTICA</div>
          <div class="advice-reason">Con 4 cartas visibles, tienes información sólida. El bote crece, cada decisión pesa más.</div>
          <div class="advice-term">📚 Pot Odds: Relación entre costo de call y tamaño del bote.</div>
        </div>
      </div>

      <div class="btn-grid">
        <button class="btn btn-success" onclick="goToRiver()">Ver River →</button>
        <button class="btn btn-danger" onclick="foldHand()">Fold / Nueva</button>
      </div>
    </div>

    <!-- PANTALLA RIVER -->
    <div id="screenRiver" class="hidden">
      <div class="card">
        <div class="board-display">
          <div class="board-label">Mano: <span id="riverYourHand"></span></div>
          <div class="board-label">Board: <span id="riverTurnBoard"></span></div>
          <div class="board-label" style="margin-top: 10px; font-size: 1.1rem; color: #f39c12;">RIVER</div>
        </div>
        
        <div class="input-group">
          <label>🎴 Carta del River</label>
          <div class="single-card">
            <select id="riverCard"><option value="">Selecciona</option></select>
          </div>
        </div>

        <div class="advice-box">
          <div class="advice-reason">Última carta. Todas las cartas están a la vista. Momento de decisión final.</div>
          <div class="advice-term">📚 Value Bet: Apuesta buscando que te paguen manos peores.</div>
        </div>
      </div>

      <div class="btn-grid">
        <button class="btn btn-primary" onclick="analyzeRiver()">🏁 Análisis Final</button>
        <button class="btn btn-danger" onclick="foldHand()">Fold / Nueva</button>
      </div>
    </div>

    <!-- PANTALLA FINAL RIVER -->
    <div id="screenFinalRiver" class="hidden">
      <div class="card">
        <div class="board-display">
          <div class="board-label">Mano: <span id="finalHand"></span></div>
          <div class="board-label">Board completo: <span id="finalBoard" class="board-cards"></span></div>
        </div>

        <div class="advice-box">
          <div class="advice-action">SHOWDOWN</div>
          <div class="advice-reason">Decisión final. Si llegaste hasta aquí con fuerza, confía en tu lectura. Evalúa el tamaño del bote vs tu mano.</div>
          <div class="advice-term">📚 Showdown: Momento donde se revelan las manos.</div>
        </div>
      </div>

      <button class="btn btn-success" style="margin-bottom: 10px;" onclick="saveAndNew()">💾 Guardar Mano</button>
      <button class="btn btn-secondary" onclick="newHand()">🔄 Nueva Mano</button>
    </div>

    <!-- HISTORIAL -->
    <div id="historySection" class="card hidden">
      <div class="history-title">📊 Historial (últimas 10 manos)</div>
      <div class="history" id="historyList"></div>
      <button class="btn btn-secondary" style="margin-top: 10px; font-size: 0.9rem; padding: 12px;" onclick="clearHistory()">🗑️ Borrar Historial</button>
    </div>
  </div>

  <script>
    const ranks = ['2','3','4','5','6','7','8','9','T','J','Q','K','A'];
    const suits = ['♠','♥','♦','♣'];
    
    let gameData = {
      hand: { c1: '', c2: '' },
      position: '',
      bb: 0,
      flop: { c1: '', c2: '', c3: '' },
      turn: '',
      river: '',
      strength: 0
    };

    function initCardSelects() {
      const selects = ['card1', 'card2', 'flopC1', 'flopC2', 'flopC3', 'turnCard', 'riverCard'];
      selects.forEach(id => {
        const sel = document.getElementById(id);
        ranks.forEach(r => {
          suits.forEach(s => {
            const opt = document.createElement('option');
            opt.value = r + s;
            opt.textContent = r + s;
            sel.appendChild(opt);
          });
        });
      });
    }

    function showScreen(screenId) {
      document.querySelectorAll('[id^="screen"]').forEach(s => s.classList.add('hidden'));
      document.getElementById(screenId).classList.remove('hidden');
    }

    function calculateStrength(c1, c2) {
      const r1 = c1[0], r2 = c2[0];
      const suited = c1[1] === c2[1];
      const isPair = r1 === r2;
      
      const v1 = ranks.indexOf(r1);
      const v2 = ranks.indexOf(r2);
      
      let str = 0;
      
      if (isPair) {
        str = 60 + (v1 * 3);
      } else {
        const high = Math.max(v1, v2);
        const gap = Math.abs(v1 - v2);
        str = 30 + (high * 2) - (gap * 2);
        if (suited) str += 5;
      }
      
      return Math.min(95, Math.max(15, str));
    }

    function getHandName(c1, c2) {
      const r1 = c1[0], r2 = c2[0];
      const suited = c1[1] === c2[1] ? 's' : 'o';
      
      if (r1 === r2) return `Pareja de ${r1}${r1}`;
      
      const v1 = ranks.indexOf(r1);
      const v2 = ranks.indexOf(r2);
      const high = v1 > v2 ? r1 : r2;
      const low = v1 < v2 ? r1 : r2;
      
      return `${high}${low}${suited}`;
    }

    function getAdvice(strength, position) {
      const early = ['UTG', 'MP'].includes(position);
      const late = ['CO', 'BTN'].includes(position);
      
      if (strength >= 75) {
        return {
          action: 'RAISE',
          reason: 'Mano premium. Tu rango es fuerte desde cualquier posición. Construye el bote.',
          term: '3-Bet: Subir después de que alguien ya subió (re-raise).'
        };
      } else if (strength >= 55) {
        if (late) {
          return {
            action: 'RAISE',
            reason: 'Mano sólida en posición tardía. Aprovecha tu ventaja posicional para controlar la mano.',
            term: 'Posición: Actuar después te da información valiosa sobre tus rivales.'
          };
        } else {
          return {
            action: 'CALL o RAISE',
            reason: 'Mano jugable pero con cautela en posición temprana. Observa la acción.',
            term: 'Rango: Conjunto de manos que juegas en cada situación específica.'
          };
        }
      } else if (strength >= 35) {
        if (late && gameData.bb <= 20) {
          return {
            action: 'CALL (condicional)',
            reason: 'Mano especulativa. En posición tardía y con stack adecuado puedes ver flop barato.',
            term: 'Implied Odds: Potencial de ganar mucho si conectas tu mano.'
          };
        } else {
          return {
            action: 'FOLD',
            reason: 'Mano marginal. Protege tus ciegas para mejores oportunidades.',
            term: 'Spot: Situación favorable para aplicar una jugada específica.'
          };
        }
      } else {
        return {
          action: 'FOLD',
          reason: 'Mano débil. La paciencia y disciplina son rentables a largo plazo.',
          term: 'Fold Equity: Valor generado al hacer que rivales abandonen la mano.'
        };
      }
    }

    function analyzePreflop() {
      const c1 = document.getElementById('card1').value;
      const c2 = document.getElementById('card2').value;
      const pos = document.getElementById('position').value;
      const bb = parseInt(document.getElementById('stackBB').value);
      
      if (!c1 || !c2 || !pos || !bb) {
        alert('Por favor completa todos los campos');
        return;
      }
      
      gameData.hand = { c1, c2 };
      gameData.position = pos;
      gameData.bb = bb;
      gameData.strength = calculateStrength(c1, c2);
      
      const advice = getAdvice(gameData.strength, pos);
      
      document.getElementById('displayHand').textContent = `${c1} ${c2}`;
      document.getElementById('displayHandName').textContent = getHandName(c1, c2);
      document.getElementById('displayMeta').textContent = `${pos} • ${bb} BB`;
      document.getElementById('strengthValue').textContent = `${gameData.strength}%`;
      document.getElementById('strengthBar').style.width = `${gameData.strength}%`;
      document.getElementById('adviceAction').textContent = `Recomendación: ${advice.action}`;
      document.getElementById('adviceReason').textContent = advice.reason;
      document.getElementById('adviceTerm').textContent = advice.term;
      
      showScreen('screenPreflop');
    }

    function goToFlop() {
      document.getElementById('flopYourHand').textContent = `${gameData.hand.c1} ${gameData.hand.c2}`;
      showScreen('screenFlop');
    }

    function analyzeFlop() {
      const c1 = document.getElementById('flopC1').value;
      const c2 = document.getElementById('flopC2').value;
      const c3 = document.getElementById('flopC3').value;
      
      if (!c1 || !c2 || !c3) {
        alert('Selecciona las 3 cartas del flop');
        return;
      }
      
      gameData.flop = { c1, c2, c3 };
      
      document.getElementById('postFlopHand').textContent = `${gameData.hand.c1} ${gameData.hand.c2}`;
      document.getElementById('postFlopBoard').textContent = `${c1} ${c2} ${c3}`;
      document.getElementById('flopAdviceAction').textContent = 'C-BET o CHECK';
      document.getElementById('flopAdviceReason').textContent = 'Si fuiste el agresor preflop, considera apostar por continuación. Si no conectaste pero tienes posición, puedes controlar el bote con check.';
      document.getElementById('flopAdviceTerm').textContent = 'C-Bet: Apuesta de continuación tras ser agresor preflop.';
      
      showScreen('screenPostFlop');
    }

    function goToTurn() {
      document.getElementById('turnYourHand').textContent = `${gameData.hand.c1} ${gameData.hand.c2}`;
      document.getElementById('turnFlopBoard').textContent = `${gameData.flop.c1} ${gameData.flop.c2} ${gameData.flop.c3}`;
      showScreen('screenTurn');
    }

    function analyzeTurn() {
      const turn = document.getElementById('turnCard').value;
      if (!turn) {
        alert('Selecciona la carta del turn');
        return;
      }
      
      gameData.turn = turn;
      
      document.getElementById('postTurnHand').textContent = `${gameData.hand.c1} ${gameData.hand.c2}`;
      document.getElementById('postTurnBoard').textContent = `${gameData.flop.c1} ${gameData.flop.c2} ${gameData.flop.c3} ${turn}`;
      
      showScreen('screenPostTurn');
    }

    function goToRiver() {
      document.getElementById('riverYourHand').textContent = `${gameData.hand.c1} ${gameData.hand.c2}`;
      document.getElementById('riverTurnBoard').textContent = `${gameData.flop.c1} ${gameData.flop.c2} ${gameData.flop.c3} ${gameData.turn}`;
      showScreen('screenRiver');
    }

    function analyzeRiver() {
      const river = document.getElementById('riverCard').value;
      if (!river) {
        alert('Selecciona la carta del river');
        return;
      }
      
      gameData.river = river;
      
      document.getElementById('finalHand').textContent = `${gameData.hand.c1} ${gameData.hand.c2}`;
      document.getElementById('finalBoard').textContent = `${gameData.flop.c1} ${gameData.flop.c2} ${gameData.flop.c3} ${gameData.turn} ${river}`;
      
      showScreen('screenFinalRiver');
    }

    function saveAndNew() {
      saveToHistory();
      newHand();
    }

    function foldHand() {
      saveToHistory();
      newHand();
    }

    function saveToHistory() {
      let history = JSON.parse(localStorage.getItem('pokerHistory') || '[]');
      
      const record = {
        hand: `${gameData.hand.c1} ${gameData.hand.c2}`,
        position: gameData.position,
        bb: gameData.bb,
        strength: gameData.strength,
        timestamp: new Date().toLocaleString('es-CO', { 
          day: '2-digit', 
          month: '2-digit', 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      };
      
      history.unshift(record);
      if (history.length > 10) history = history.slice(0, 10);
      
      localStorage.setItem('pokerHistory', JSON.stringify(history));
      updateHistoryDisplay();
    }

    function updateHistoryDisplay() {
      const history = JSON.parse(localStorage.getItem('pokerHistory') || '[]');
      
      if (history.length > 0) {
        document.getElementById('historySection').classList.remove('hidden');
        
        const html = history.map(h => `
          <div class="history-item">
            <div>
              <span class="history-hand">${h.hand}</span>
              <span class="history-position">${h.position}</span>
            </div>
            <div class="history-stats">
              <div class="history-strength">${h.strength}%</div>
              <div class="history-bb">${h.bb} BB</div>
            </div>
          </div>
        `).join('');
        
        document.getElementById('historyList').innerHTML = html;
      }
    }

    function clearHistory() {
      if (confirm('¿Borrar todo el historial?')) {
        localStorage.removeItem('pokerHistory');
        document.getElementById('historySection').classList.add('hidden');
      }
    }

    function newHand() {
      gameData = {
        hand: { c1: '', c2: '' },
        position: '',
        bb: 0,
        flop: { c1: '', c2: '', c3: '' },
        turn: '',
        river: '',
        strength: 0
      };
      
      document.getElementById('card1').value = '';
      document.getElementById('card2').value = '';
      document.getElementById('position').value = '';
      document.getElementById('stackBB').value = '';
      
      showScreen('screenStart');
    }

    initCardSelects
();
updateHistoryDisplay();
</script>
</body>
</html>
"""
components.html(html_code, height=900, scrolling=False)