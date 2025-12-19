import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PauGaR - Radar Multi-Fase", layout="centered")

# --- LÓGICA DE PROCESAMIENTO (CANDADO DE REGLAS) ---
# Aquí es donde Python decide el destino de la mano
def analizar_mano(r1, r2, suited):
    # Reglas Pre-Flop
    if r1 == r2: return "RAISE / PUSH", "#1b5e20", "SUEÑO: SET / FULL"
    if r1 == 'A' or r2 == 'A': return "RAISE", "#1b5e20", "SUEÑO: TOP PAIR"
    if (r1 == 'K' or r2 == 'K') and suited: return "RAISE", "#1b5e20", "SUEÑO: COLOR"
    return "FOLD", "#b71c1c", "SUEÑO: ESCALERA (DIFÍCIL)"

# --- COMPONENTE VISUAL INTEGRADO ---
# Usamos un solo bloque HTML para garantizar que la matriz de 52 cartas sea horizontal (13 col)
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: 'Arial Black', sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 2px; }
        .label { font-size: 0.65rem; color: #ffcc00; text-transform: uppercase; margin: 8px 0; display: block; }
        
        /* MATRIZ HORIZONTAL FORZADA (13 Columnas) */
        .poker-grid { 
            display: grid; 
            grid-template-columns: repeat(13, 1fr); 
            gap: 2px; 
            width: 98vw; 
            margin: 0 auto;
        }
        
        .c-btn { 
            padding: 10px 0; font-size: 0.65rem; background: #1a1a1a; color: #fff; 
            border: 1px solid #333; border-radius: 4px; font-weight: bold; cursor: pointer;
        }
        .c-btn.active { background: #fff !important; color: #000 !important; border: 1px solid #00ff00; }
        
        /* PINTAS */
        .p-s { border-bottom: 2px solid #555; }
        .p-h { border-bottom: 2px solid #ff4444; color: #ff8888; }
        .p-d { border-bottom: 2px solid #ff4444; color: #ff8888; }
        .p-t { border-bottom: 2px solid #00ff00; color: #88ff88; }

        /* ZONAS DE RESULTADO */
        #box-p1 { display: none; margin-top: 10px; padding: 15px; border-radius: 12px; border: 2px solid #fff; }
        .dec-txt { font-size: 2.2rem; font-weight: 900; margin: 0; }
        
        #box-p2 { display: none; margin-top: 15px; background: #111; padding: 10px; border-radius: 10px; border: 1px solid #00ff00; }
        .flop-display { display: flex; justify-content: center; gap: 6px; margin: 10px 0; }
        .mini-card { width: 40px; height: 55px; background: #fff; color: #000; border-radius: 5px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 0.9rem; font-weight: bold; }
        
        .ana-box { background: #000; padding: 8px; border-radius: 6px; font-size: 0.75rem; text-align: left; margin-top: 10px; border-left: 3px solid #ffcc00; }
        .btn-reset { width: 100%; padding: 18px; background: #fff; color: #000; font-size: 1.3rem; font-weight: 900; border-radius: 10px; margin-top: 15px; border: none; }
    </style>
</head>
<body>

    <span class="label">1. TUS 2 CARTAS (MATRIZ 13x4)</span>
    <div class="poker-grid" id="main-grid"></div>

    <div id="box-p1">
        <p id="dec-val" class="dec-txt"></p>
        <p id="dream-val" style="font-size: 0.7rem; color: #ffcc00; margin: 5px 0;"></p>
        
        <div id="box-p2">
            <span class="label" style="color:#00ff00">2. EL FLOP (TOCA 3 MÁS ABAJO)</span>
            <div id="flop-view" class="flop-display"></div>
            <div id="ana-result" class="ana-box" style="display:none;"></div>
        </div>

        <button class="btn-reset" onclick="window.location.reload()">NUEVA MANO</button>
    </div>

    <script>
        const ranks = ['A','K','Q','J','10','9','8','7','6','5','4','3','2'];
        const suits = [{s:'♠', c:'p-s'}, {s:'♥', c:'p-h'}, {s:'♦', c:'p-d'}, {s:'♣', c:'p-t'}];
        let myHand = []; let flopHand = [];

        // Generar Matriz 52 Cartas
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
            if (myHand.length < 2 && !btn.classList.contains('active')) {
                myHand.push({r, s});
                btn.classList.add('active');
                if (myHand.length === 2) procesarPaso1();
            } else if (myHand.length === 2 && flopHand.length < 3 && !btn.classList.contains('active')) {
                flopHand.push({r, s});
                btn.classList.add('active');
                actualizarFlop();
            }
        }

        function procesarPaso1() {
            const box = document.getElementById('box-p1');
            const dec = document.getElementById('dec-val');
            const dream = document.getElementById('dream-val');
            box.style.display = 'block';
            
            const r1 = myHand[0].r, r2 = myHand[1].r;
            const sameSuit = myHand[0].s === myHand[1].s;
            
            // LÓGICA IF INTEGRADA
            let action = "FOLD"; let color = "#b71c1c"; let suneo = "SUEÑO: ESCALERA";
            
            if (r1 === r2 || r1 === 'A' || r2 === 'A' || ((r1 === 'K' || r2 === 'K') && sameSuit)) {
                action = "RAISE"; color = "#1b5e20";
                suneo = (r1 === r2) ? "SUEÑO: SET / FULL" : "SUEÑO: TOP PAIR";
                document.getElementById('box-p2').style.display = 'block';
            }
            
            dec.innerText = action;
            box.style.backgroundColor = color;
            dream.innerText = suneo;
        }

        function actualizarFlop() {
            const view = document.getElementById('flop-view');
            view.innerHTML = flopHand.map(c => `
                <div class="mini-card" style="color:${(c.s=='♥'||c.s=='♦')?'red':'black'}">
                    <span>${c.r}</span><span>${c.s}</span>
                </div>`).join('');
            
            if (flopHand.length === 3) {
                const ana = document.getElementById('ana-result');
                ana.style.display = 'block';
                
                const connected = flopHand.some(f => f.r === myHand[0].r || f.r === myHand[1].r);
                const mesaRanks = flopHand.map(f => f.r);
                const mesaDoblada = new Set(mesaRanks).size < 3;
                const mesaSuits = flopHand.map(f => f.s);
                const peligroColor = mesaSuits.every(s => s === mesaSuits[0]);

                ana.innerHTML = `
                    <b>ESTADO:</b> ${connected ? "✅ CONECTASTE" : "❌ NO CONECTÓ"}<br>
                    ${mesaDoblada ? "⚠️ <b>PELIGRO:</b> MESA DOBLADA (FULL)<br>" : ""}
                    ${peligroColor ? "⚠️ <b>PELIGRO:</b> COLOR EN MESA" : "✅ MESA LIMPIA"}
                `;
            }
        }
    </script>
</body>
</html>
"""

components.html(html_code, height=950, scrolling=False)
