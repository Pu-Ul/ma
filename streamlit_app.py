Aquí tienes una versión **realmente usable en celular**, **discreta**, **sin scroll** (pantallas por pasos), **educativa** (te enseña términos en cada calle), te acompaña **de preflop → flop → turn → river**, calcula **equity (probabilidad) por Monte Carlo**, te da **consejos condicionales** (no “sentencias”), toma en cuenta **stack en BB** + **pot y costo a pagar en BB** (para *pot odds*), y guarda **historial acumulativo** en un archivo JSON (ideal para GitHub).

> ✅ Copia/pega tal cual en GitHub como `app.py` y `requirements.txt`.

---

```python
# app.py
# Streamlit Texas Hold'em Advisor (mobile-first, step-by-step, no-scroll UI)
# - Preflop → Flop → Turn → River
# - Monte Carlo equity (vs 1 oponente random por defecto)
# - Pot odds (pot y costo a pagar en BB)
# - Consejos condicionales (no absolutos)
# - Mini-glosario educativo por calle
# - Historial acumulativo (data/history.json)

import itertools
import json
import os
import random
from datetime import datetime

import streamlit as st

# ---------------------------
# Page config + Mobile CSS
# ---------------------------
st.set_page_config(page_title="Hold'em Pocket Coach", layout="centered", initial_sidebar_state="collapsed")

MOBILE_CSS = """
<style>
/* Reduce padding and make it feel like an app */
.block-container { padding-top: .6rem; padding-bottom: .6rem; max-width: 520px; }
header, footer { visibility: hidden; height: 0px; }
[data-testid="stToolbar"] { visibility: hidden; height: 0px; }
[data-testid="stDecoration"] { visibility: hidden; height: 0px; }

/* Try to avoid scroll: keep widgets compact */
div.stButton > button { width: 100%; padding: 0.7rem 0.8rem; border-radius: 14px; }
div.stMetric { padding: 0.2rem 0.3rem; }

/* Compact select boxes */
div[data-baseweb="select"] > div { border-radius: 12px; }
input, textarea { border-radius: 12px !important; }

/* Make dataframe smaller */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }

/* A subtle card look */
.card {
  background: rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.08);
  padding: .7rem .8rem;
  border-radius: 16px;
  margin-bottom: .6rem;
}
.small { font-size: 0.9rem; opacity: 0.9; }
.badge {
  display:inline-block; padding:.12rem .45rem; border-radius: 999px;
  background: rgba(0,0,0,0.07); border: 1px solid rgba(0,0,0,0.08);
  font-size:.8rem; margin-right:.25rem;
}
hr { margin: .5rem 0; }
</style>
"""
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ---------------------------
# Persistence (history)
# ---------------------------
DATA_DIR = "data"
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")

def _ensure_history_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_history():
    _ensure_history_file()
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(items):
    _ensure_history_file()
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

# ---------------------------
# Cards + Evaluator (simple but solid)
# ---------------------------
RANKS = "23456789TJQKA"
SUITS = "shdc"  # spades, hearts, diamonds, clubs
RANK_TO_VAL = {r: i for i, r in enumerate(RANKS, start=2)}

def card_str(card):
    # 'As' -> 'A♠'
    r, s = card[0], card[1]
    sym = {"s":"♠","h":"♥","d":"♦","c":"♣"}[s]
    return f"{r}{sym}"

def make_deck():
    return [r+s for r in RANKS for s in SUITS]

def parse_selected(sel):
    # sel is like "A♠" or "As" depending on option; we store canonical "As"
    # We build options as canonical already, so just return sel
    return sel

def is_valid_unique(cards):
    c = [x for x in cards if x]
    return len(c) == len(set(c))

def five_card_rank(cards5):
    # returns a tuple that can be compared: (category, tiebreakers...)
    # categories: 8 straight-flush, 7 quads, 6 full house, 5 flush, 4 straight, 3 trips, 2 two-pair, 1 pair, 0 high
    ranks = sorted([RANK_TO_VAL[c[0]] for c in cards5], reverse=True)
    suits = [c[1] for c in cards5]
    unique = sorted(set(ranks), reverse=True)
    counts = sorted(((ranks.count(v), v) for v in set(ranks)), reverse=True)  # (count, value)
    is_flush = len(set(suits)) == 1

    # straight (handle wheel A-5)
    def straight_high(vals):
        v = sorted(set(vals), reverse=True)
        if len(v) < 5:
            return None
        # wheel
        if set([14,5,4,3,2]).issubset(set(vals)):
            return 5
        for i in range(len(v)-4):
            seq = v[i:i+5]
            if seq[0]-seq[4] == 4 and len(seq) == 5:
                return seq[0]
        return None

    sh = straight_high(ranks)

    if is_flush and sh:
        return (8, sh, ranks)
    if counts[0][0] == 4:
        quad = counts[0][1]
        kicker = max([v for v in ranks if v != quad])
        return (7, quad, kicker)
    if counts[0][0] == 3 and counts[1][0] == 2:
        trips = counts[0][1]
        pair = counts[1][1]
        return (6, trips, pair)
    if is_flush:
        return (5, ranks)
    if sh:
        return (4, sh, ranks)
    if counts[0][0] == 3:
        trips = counts[0][1]
        kickers = sorted([v for v in ranks if v != trips], reverse=True)
        return (3, trips, kickers)
    if counts[0][0] == 2 and counts[1][0] == 2:
        pair_hi = max(counts[0][1], counts[1][1])
        pair_lo = min(counts[0][1], counts[1][1])
        kicker = max([v for v in ranks if v not in (pair_hi, pair_lo)])
        return (2, pair_hi, pair_lo, kicker)
    if counts[0][0] == 2:
        pair = counts[0][1]
        kickers = sorted([v for v in ranks if v != pair], reverse=True)
        return (1, pair, kickers)
    return (0, ranks)

def best_hand_rank(cards7):
    best = None
    best5 = None
    for comb in itertools.combinations(cards7, 5):
        r = five_card_rank(list(comb))
        if best is None or r > best:
            best = r
            best5 = comb
    return best, best5

def hand_category_name(rank_tuple):
    cat = rank_tuple[0]
    return {
        8: "Escalera de color",
        7: "Póker (4 iguales)",
        6: "Full house",
        5: "Color (flush)",
        4: "Escalera (straight)",
        3: "Trío",
        2: "Doble pareja",
        1: "Pareja",
        0: "Carta alta",
    }[cat]

# ---------------------------
# Equity (Monte Carlo) + Outs
# ---------------------------
def monte_carlo_equity(hero2, board, n_opponents=1, iters=4500, seed=None):
    if seed is not None:
        random.seed(seed)

    deck = make_deck()
    used = set([c for c in hero2 + board if c])
    deck = [c for c in deck if c not in used]

    need_board = 5 - len(board)
    if need_board < 0:
        return None

    wins = ties = total = 0
    # Reduce iters on slower devices if needed
    iters = max(800, min(iters, 12000))

    for _ in range(iters):
        d = deck[:]
        random.shuffle(d)

        # deal opponents
        opp_hands = []
        idx = 0
        for _k in range(n_opponents):
            opp_hands.append([d[idx], d[idx+1]])
            idx += 2

        # complete board
        runout = board[:] + d[idx:idx+need_board]
        idx += need_board

        hero_rank, _ = best_hand_rank(hero2 + runout)

        opp_ranks = []
        for oh in opp_hands:
            r, _ = best_hand_rank(oh + runout)
            opp_ranks.append(r)

        best_opp = max(opp_ranks)
        total += 1
        if hero_rank > best_opp:
            wins += 1
        elif hero_rank == best_opp:
            # tie only if hero equals the top opponent (approx tie handling)
            # if multiple opponents tie, still counts as tie
            ties += 1

    equity = (wins + ties * 0.5) / total
    return equity

def outs_improvement_count(hero2, board):
    # Counts how many remaining single cards improve HERO's category (not vs opponent).
    # Works for flop (2 cards to come) and turn (1 card to come) as a learning tool.
    used = set(hero2 + board)
    deck = [c for c in make_deck() if c not in used]

    current_rank, _ = best_hand_rank(hero2 + board)
    current_cat = current_rank[0]

    # If already river (5 board), no outs
    if len(board) >= 5:
        return 0

    improve = 0
    # We measure immediate improvement with ONE card (next street).
    for c in deck:
        r, _ = best_hand_rank(hero2 + (board + [c]))
        if r[0] > current_cat:
            improve += 1
    return improve

# ---------------------------
# Preflop strength heuristic (educational)
# ---------------------------
def preflop_score(hero2):
    r1, r2 = hero2[0][0], hero2[1][0]
    s1, s2 = hero2[0][1], hero2[1][1]
    v1, v2 = RANK_TO_VAL[r1], RANK_TO_VAL[r2]
    suited = (s1 == s2)
    pair = (r1 == r2)
    high = max(v1, v2)
    low = min(v1, v2)
    gap = high - low

    score = 0
    if pair:
        score = 60 + (high - 2) * 3.0
    else:
        score = 28 + (high - 2) * 2.2 - gap * 2.0
        if suited:
            score += 5.5
        # small connector bonus
        if gap == 1 and high >= 9:
            score += 3
        if high >= 12 and low >= 9:
            score += 3
    return max(10, min(95, score))

def preflop_advice(score, position, stack_bb):
    early = position in ("UTG", "MP")
    late = position in ("CO", "BTN")
    blinds = position in ("SB", "BB")

    # Stack depth heuristic (very simple)
    shallow = stack_bb <= 20
    deep = stack_bb >= 60

    if score >= 78:
        return ("Subir (raise)", "Mano fuerte. En general quieres construir el bote y tomar iniciativa.", "Iniciativa: ser quien apuesta primero suele dar ventaja.")
    if score >= 60:
        if late or blinds:
            return ("Subir (raise)", "Buena mano con ventaja de posición o ciegas: presiona rangos más amplios.", "Rango: conjunto de manos probables del rival.")
        return ("Pagar o subir (call/raise)", "Jugable, pero en posiciones tempranas conviene disciplina y tamaño correcto.", "Posición: actuar después te da información.")
    if score >= 45:
        if late and deep and not shallow:
            return ("Pagar (call) si es barato", "Mano especulativa: puede conectar fuerte en el flop si el costo es razonable.", "Implied odds: ganar más cuando conectas fuerte.")
        if shallow:
            return ("Foldear (fold) con más frecuencia", "Con stack corto, las manos marginales pierden valor.", "Stack BB: profundidad en ciegas grandes.")
        return ("Foldear a menudo", "Mano marginal. Espera spots mejores.", "Disciplina: evitar spots negativos protege tu winrate.")
    return ("Foldear (fold)", "La rentabilidad viene de seleccionar spots. Esta mano rara vez compensa el riesgo.", "Fold equity: valor cuando tu rival foldea ante presión.")

# ---------------------------
# Calm, neutral messages (no “rabia”)
# ---------------------------
CALM_LINES = [
    "Tu decisión es buena si está alineada con la información disponible, no con el resultado.",
    "En póker, una buena línea se mide en el largo plazo. Aquí buscamos consistencia.",
    "El objetivo es elegir spots con ventaja. Si no la hay, retirarse es una jugada profesional.",
    "Respira, revisa pot odds y equity. Luego decide con calma.",
    "Lo importante: proceso claro → decisión clara."
]
def calm_line():
    return random.choice(CALM_LINES)

# ---------------------------
# Session State
# ---------------------------
def reset_hand():
    st.session_state.stage = "preflop"
    st.session_state.hero = ["", ""]
    st.session_state.pos = "BTN"
    st.session_state.stack_bb = 50
    st.session_state.board = []
    st.session_state.pot_bb = 3.0
    st.session_state.call_bb = 1.0
    st.session_state.opps = 1
    st.session_state.last_equity = None
    st.session_state.last_best = None

if "stage" not in st.session_state:
    reset_hand()

# ---------------------------
# UI helpers
# ---------------------------
def card_options():
    # Canonical "As" "Th" etc; show pretty label
    opts = [""]
    for r in RANKS[::-1]:
        for s in SUITS:
            opts.append(r+s)
    return opts

def pretty_cards(cards):
    return " ".join(card_str(c) for c in cards if c)

def street_name(stage):
    return {"preflop":"PREFLOP", "flop":"FLOP", "turn":"TURN", "river":"RIVER"}[stage]

def glossary(stage):
    if stage == "preflop":
        return [
            ("Rango", "Conjunto de manos que juegas según posición y acción previa."),
            ("Open raise", "Primera subida preflop cuando nadie subió antes."),
            ("3-bet", "Resubida: subir después de que alguien ya subió."),
        ]
    if stage == "flop":
        return [
            ("Textura", "Cómo el board conecta (proyectos de escalera/color, pares, etc.)."),
            ("C-bet", "Apuesta de continuación del agresor preflop."),
            ("Proyecto", "Mano que aún no es fuerte, pero puede mejorar (draw)."),
        ]
    if stage == "turn":
        return [
            ("Outs", "Cartas que mejoran tu mano en la siguiente calle."),
            ("Pot odds", "Costo de pagar vs tamaño del bote (equity mínima necesaria)."),
            ("Polarizar", "Apostar fuerte con manos muy buenas o faroles."),
        ]
    return [
        ("Value bet", "Apuesta buscando que te paguen manos peores."),
        ("Bluff", "Apuesta para que el rival foldee una mano mejor."),
        ("Showdown", "Cuando se muestran las manos al final."),
    ]

def required_equity(pot_bb, call_bb):
    if call_bb <= 0:
        return 0.0
    return call_bb / (pot_bb + call_bb)

def advice_postflop(equity, req, stage, stack_bb):
    # Very practical, conditional guidance
    margin = 0.05  # 5% buffer
    if equity is None:
        return ("Datos incompletos", "Completa mano/board para calcular.", "Equity: probabilidad aproximada de ganar en el showdown.")
    if call_bb <= 0:
        return ("Plan", "Si no hay costo por pagar, puedes elegir apostar por valor o controlar el bote según textura.", "Control del bote: mantener el bote manejable con manos medias.")
    if equity >= req + 0.10:
        return ("Seguir con más confianza", f"Tu equity supera claramente la equity mínima (pot odds). Considera pagar o subir según dinámica.", "Pot odds: equity mínima para que pagar sea rentable.")
    if equity >= req + margin:
        return ("Seguir (call) es razonable", f"Tu equity está apenas por encima de la equity mínima. Decide según posición y riesgos del board.", "Posición: actuar último te permite decisiones más precisas.")
    if equity >= req - margin:
        return ("Zona fina", f"Estás cerca del umbral. Si hay presión fuerte o el board empeora tu rango, foldear es válido.", "Umbral: cuando el pago deja de ser rentable por pot odds.")
    return ("Foldear suele ser correcto", f"Tu equity está por debajo de lo requerido por pot odds. Esperar un spot mejor protege tu stack.", "Disciplina: evitar pagos negativos mantiene tu BB/100.")

# ---------------------------
# Header (always visible)
# ---------------------------
st.markdown(
    f"""
<div class="card">
  <div><span class="badge">Hold'em</span><span class="badge">Móvil</span><span class="badge">Paso a paso</span></div>
  <div style="font-size:1.05rem; font-weight:700; margin-top:.2rem;">🃏 {street_name(st.session_state.stage)}</div>
  <div class="small" style="margin-top:.15rem;">
    <b>Mano:</b> {pretty_cards(st.session_state.hero) or "—"} &nbsp; | &nbsp;
    <b>Board:</b> {pretty_cards(st.session_state.board) or "—"}
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# Controls row (compact)
# ---------------------------
colA, colB, colC = st.columns([1,1,1], gap="small")
with colA:
    if st.button("🔄 Nueva mano", use_container_width=True):
        reset_hand()
        st.rerun()
with colB:
    if st.button("💾 Guardar mano", use_container_width=True):
        hist = load_history()
        record = {
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "stage": st.session_state.stage,
            "hand": pretty_cards(st.session_state.hero),
            "board": pretty_cards(st.session_state.board),
            "pos": st.session_state.pos,
            "stackBB": st.session_state.stack_bb,
            "potBB": float(st.session_state.pot_bb),
            "callBB": float(st.session_state.call_bb),
            "opps": int(st.session_state.opps),
            "equity": None if st.session_state.last_equity is None else round(st.session_state.last_equity*100, 1),
        }
        hist.insert(0, record)
        hist = hist[:25]
        save_history(hist)
        st.success("Guardado en historial ✅")
with colC:
    if st.button("🧹 Borrar historial", use_container_width=True):
        save_history([])
        st.success("Historial borrado ✅")

st.markdown(f"<div class='card small'>🧭 {calm_line()}</div>", unsafe_allow_html=True)

# ---------------------------
# Main step screens
# ---------------------------
opts = card_options()

# Shared settings (compact)
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.session_state.pos = st.selectbox("📍 Posición", ["UTG","MP","CO","BTN","SB","BB"], index=["UTG","MP","CO","BTN","SB","BB"].index(st.session_state.pos))
        st.session_state.stack_bb = st.number_input("💰 Stack (BB)", min_value=1, max_value=500, value=int(st.session_state.stack_bb), step=1)
    with c2:
        st.session_state.pot_bb = st.number_input("🪙 Bote actual (BB)", min_value=0.0, max_value=500.0, value=float(st.session_state.pot_bb), step=0.5)
        st.session_state.call_bb = st.number_input("✅ Costo para pagar (BB)", min_value=0.0, max_value=500.0, value=float(st.session_state.call_bb), step=0.5)
    st.session_state.opps = st.selectbox("👤 Oponentes (random)", [1,2,3,4,5], index=[1,2,3,4,5].index(int(st.session_state.opps)))
    st.markdown("</div>", unsafe_allow_html=True)

# Stage: PREFLOP
if st.session_state.stage == "preflop":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    h1, h2 = st.columns(2, gap="small")
    with h1:
        st.session_state.hero[0] = st.selectbox("🂡 Tu carta 1", opts, index=opts.index(st.session_state.hero[0]) if st.session_state.hero[0] in opts else 0)
    with h2:
        st.session_state.hero[1] = st.selectbox("🂡 Tu carta 2", opts, index=opts.index(st.session_state.hero[1]) if st.session_state.hero[1] in opts else 0)

    ok = all(st.session_state.hero) and is_valid_unique(st.session_state.hero)
    if not ok and any(st.session_state.hero):
        st.warning("Las dos cartas deben ser distintas.")

    if st.button("🎯 Analizar preflop", disabled=not ok, use_container_width=True):
        score = preflop_score(st.session_state.hero)
        act, reason, term = preflop_advice(score, st.session_state.pos, st.session_state.stack_bb)
        st.session_state.last_equity = None
        st.session_state.last_best = None

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Fuerza preflop (heurística)", f"{score:.0f}/100")
        st.markdown(f"**Recomendación (condicional):** {act}\n\n- {reason}\n\n**📘 Término:** *{term}*")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card small'>", unsafe_allow_html=True)
        st.markdown("**Mini-glosario (preflop):**")
        for k, v in glossary("preflop"):
            st.markdown(f"- **{k}:** {v}")
        st.markdown("</div>", unsafe_allow_html=True)

        c_next, c_fold = st.columns(2, gap="small")
        with c_next:
            if st.button("➡️ Pasar a FLOP", use_container_width=True):
                st.session_state.stage = "flop"
                st.session_state.board = []
                st.rerun()
        with c_fold:
            if st.button("✋ Foldear / Nueva", use_container_width=True):
                reset_hand()
                st.rerun()

    else:
        st.markdown("</div>", unsafe_allow_html=True)

# Stage: FLOP
elif st.session_state.stage == "flop":
    if not all(st.session_state.hero) or not is_valid_unique(st.session_state.hero):
        st.info("Primero elige tu mano en preflop.")
        if st.button("⬅️ Volver a PREFLOP", use_container_width=True):
            st.session_state.stage = "preflop"
            st.rerun()
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3, gap="small")
        b = st.session_state.board + [""] * (3 - len(st.session_state.board))
        with f1:
            b[0] = st.selectbox("Flop 1", opts, index=opts.index(b[0]) if b[0] in opts else 0)
        with f2:
            b[1] = st.selectbox("Flop 2", opts, index=opts.index(b[1]) if b[1] in opts else 0)
        with f3:
            b[2] = st.selectbox("Flop 3", opts, index=opts.index(b[2]) if b[2] in opts else 0)

        chosen = [x for x in b if x]
        valid = len(chosen) == 3 and is_valid_unique(st.session_state.hero + chosen)

        if len(chosen) == 3 and not valid:
            st.warning("Revisa duplicados (mano/board).")

        if st.button("🔍 Analizar FLOP", disabled=not valid, use_container_width=True):
            st.session_state.board = chosen
            eq = monte_carlo_equity(st.session_state.hero, st.session_state.board, n_opponents=int(st.session_state.opps), iters=4500)
            st.session_state.last_equity = eq

            req = required_equity(float(st.session_state.pot_bb), float(st.session_state.call_bb))
            outs = outs_improvement_count(st.session_state.hero, st.session_state.board)
            act, reason, term = advice_postflop(eq, req, "flop", st.session_state.stack_bb)

            cards7 = st.session_state.hero + st.session_state.board
            best, best5 = best_hand_rank(cards7)
            st.session_state.last_best = (best, best5)

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            cM1, cM2, cM3 = st.columns(3, gap="small")
            with cM1:
                st.metric("Equity (aprox.)", f"{eq*100:.1f}%")
            with cM2:
                st.metric("Equity mínima (pot odds)", f"{req*100:.1f}%")
            with cM3:
                st.metric("Outs (mejora 1 carta)", f"{outs}")
            st.markdown(f"**Lectura de mano:** {hand_category_name(best)}")
            st.markdown(f"**Recomendación (condicional):** {act}\n\n- {reason}\n\n**📘 Término:** *{term}*")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card small'>", unsafe_allow_html=True)
            st.markdown("**Mini-glosario (flop):**")
            for k, v in glossary("flop"):
                st.markdown(f"- **{k}:** {v}")
            st.markdown("</div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2, gap="small")
            with c1:
                if st.button("➡️ Pasar a TURN", use_container_width=True):
                    st.session_state.stage = "turn"
                    st.rerun()
            with c2:
                if st.button("⬅️ Volver a PREFLOP", use_container_width=True):
                    st.session_state.stage = "preflop"
                    st.rerun()
        else:
            st.markdown("</div>", unsafe_allow_html=True)

# Stage: TURN
elif st.session_state.stage == "turn":
    if len(st.session_state.board) != 3:
        st.info("Primero completa el flop.")
        if st.button("⬅️ Volver a FLOP", use_container_width=True):
            st.session_state.stage = "flop"
            st.rerun()
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        turn = st.selectbox("🎴 Carta del TURN", opts, index=0)
        valid = bool(turn) and is_valid_unique(st.session_state.hero + st.session_state.board + [turn])
        if turn and not valid:
            st.warning("Esa carta ya está usada.")
        if st.button("🔍 Analizar TURN", disabled=not valid, use_container_width=True):
            st.session_state.board = st.session_state.board + [turn]
            eq = monte_carlo_equity(st.session_state.hero, st.session_state.board, n_opponents=int(st.session_state.opps), iters=5200)
            st.session_state.last_equity = eq

            req = required_equity(float(st.session_state.pot_bb), float(st.session_state.call_bb))
            outs = outs_improvement_count(st.session_state.hero, st.session_state.board)
            act, reason, term = advice_postflop(eq, req, "turn", st.session_state.stack_bb)

            best, best5 = best_hand_rank(st.session_state.hero + st.session_state.board)
            st.session_state.last_best = (best, best5)

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            cM1, cM2, cM3 = st.columns(3, gap="small")
            with cM1:
                st.metric("Equity (aprox.)", f"{eq*100:.1f}%")
            with cM2:
                st.metric("Equity mínima (pot odds)", f"{req*100:.1f}%")
            with cM3:
                st.metric("Outs (mejora 1 carta)", f"{outs}")
            st.markdown(f"**Lectura de mano:** {hand_category_name(best)}")
            st.markdown(f"**Recomendación (condicional):** {act}\n\n- {reason}\n\n**📘 Término:** *{term}*")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card small'>", unsafe_allow_html=True)
            st.markdown("**Mini-glosario (turn):**")
            for k, v in glossary("turn"):
                st.markdown(f"- **{k}:** {v}")
            st.markdown("</div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2, gap="small")
            with c1:
                if st.button("➡️ Pasar a RIVER", use_container_width=True):
                    st.session_state.stage = "river"
                    st.rerun()
            with c2:
                if st.button("⬅️ Volver a FLOP", use_container_width=True):
                    st.session_state.stage = "flop"
                    # remove turn card
                    st.session_state.board = st.session_state.board[:3]
                    st.rerun()
        else:
            st.markdown("</div>", unsafe_allow_html=True)

# Stage: RIVER
elif st.session_state.stage == "river":
    if len(st.session_state.board) != 4:
        st.info("Primero completa el turn.")
        if st.button("⬅️ Volver a TURN", use_container_width=True):
            st.session_state.stage = "turn"
            st.rerun()
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        river = st.selectbox("🎴 Carta del RIVER", opts, index=0)
        valid = bool(river) and is_valid_unique(st.session_state.hero + st.session_state.board + [river])
        if river and not valid:
            st.warning("Esa carta ya está usada.")
        if st.button("🏁 Análisis final (RIVER)", disabled=not valid, use_container_width=True):
            st.session_state.board = st.session_state.board + [river]
            eq = monte_carlo_equity(st.session_state.hero, st.session_state.board, n_opponents=int(st.session_state.opps), iters=6500)
            st.session_state.last_equity = eq

            req = required_equity(float(st.session_state.pot_bb), float(st.session_state.call_bb))
            # no outs on river
            act, reason, term = advice_postflop(eq, req, "river", st.session_state.stack_bb)

            best, best5 = best_hand_rank(st.session_state.hero + st.session_state.board)
            st.session_state.last_best = (best, best5)

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            cM1, cM2 = st.columns(2, gap="small")
            with cM1:
                st.metric("Equity (aprox.)", f"{eq*100:.1f}%")
            with cM2:
                st.metric("Equity mínima (pot odds)", f"{req*100:.1f}%")
            st.markdown(f"**Lectura de mano final:** {hand_category_name(best)}")
            st.markdown(f"**Recomendación (condicional):** {act}\n\n- {reason}\n\n**📘 Término:** *{term}*")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card small'>", unsafe_allow_html=True)
            st.markdown("**Mini-glosario (river):**")
            for k, v in glossary("river"):
                st.markdown(f"- **{k}:** {v}")
            st.markdown("</div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2, gap="small")
            with c1:
                if st.button("💾 Guardar + Nueva mano", use_container_width=True):
                    hist = load_history()
                    record = {
                        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "stage": "river",
                        "hand": pretty_cards(st.session_state.hero),
                        "board": pretty_cards(st.session_state.board),
                        "pos": st.session_state.pos,
                        "stackBB": st.session_state.stack_bb,
                        "potBB": float(st.session_state.pot_bb),
                        "callBB": float(st.session_state.call_bb),
                        "opps": int(st.session_state.opps),
                        "equity": round(eq*100, 1),
                        "made_hand": hand_category_name(best),
                    }
                    hist.insert(0, record)
                    hist = hist[:25]
                    save_history(hist)
                    reset_hand()
                    st.rerun()
            with c2:
                if st.button("⬅️ Volver a TURN", use_container_width=True):
                    st.session_state.stage = "turn"
                    st.session_state.board = st.session_state.board[:4]
                    st.rerun()
        else:
            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# History (compact)
# ---------------------------
hist = load_history()
if hist:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**📊 Historial (últimas manos)**")
    # Show a compact table-like view without heavy dataframe height
    for i, h in enumerate(hist[:8], start=1):
        eqtxt = "—" if h.get("equity") is None else f"{h.get('equity')}%"
        st.markdown(
            f"<div class='small'><b>{i}.</b> {h.get('ts','')} · {h.get('hand','')} · "
            f"Pos {h.get('pos','')} · {h.get('stackBB','')}BB · Eq {eqtxt}</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='card small'>📌 Historial vacío. Guarda una mano y aparecerá aquí.</div>", unsafe_allow_html=True)
```

---

```txt
# requirements.txt
streamlit>=1.34
```

---

## Cómo subirlo a GitHub (rápido desde el celular)

1. Crea un repo en GitHub (por ejemplo: `holdem-pocket-coach`).
2. Crea estos archivos en el repo:

   * `app.py` (pega el código completo)
   * `requirements.txt` (pega el contenido)
3. (Opcional) agrega una carpeta vacía `data/` (la app la crea si no existe).
4. En Streamlit Community Cloud: conecta el repo y selecciona `app.py`.

---

## Lo que hace “bien” vs tu ejemplo

* ✅ **No es una sola pantalla larguísima**: va por pasos (preflop/flop/turn/river) → **menos scroll**.
* ✅ **Equity real** por simulación Monte Carlo (no un “% de fuerza” inventado).
* ✅ **Pot odds** (bote + costo a pagar en BB) → decisión más coherente.
* ✅ **Glosario por calle** para aprender terminología sin abrumarte.
* ✅ **Historial acumulativo** (JSON) listo para GitHub.
* ✅ Mensajes de enfoque/claridad **sin hablar de “rabia”** ni emociones explícitas.

---

Si quieres, en la siguiente iteración te lo dejo aún más “tipo app”:

* botones grandes “**Estoy en nueva mano / Ya vi flop / Ya vi turn**”
* selector “**¿hubo subida antes de mí?**” para que el consejo preflop sea más real
* opción “**vs 2–6 jugadores**” (ya está) y “**rango del rival: tight/normal/loose**” para afinar equity.
