import json
import time
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Poker Radar PRO (Edu + Historial)", layout="centered")

# -----------------------------
# Persistencia (archivo local)
# -----------------------------
DATA_PATH = Path("poker_history.json")

def load_data():
    if DATA_PATH.exists():
        try:
            return json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"round": 1, "hands": []}
    return {"round": 1, "hands": []}

def save_data(data):
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# -----------------------------
# Modelo PRO (simple pero serio)
# Ajusta aquí tus rangos reales.
# La clave es que ahora NO es "demo": es tabla editable.
# -----------------------------
# Formato: (hand, suited_flag) -> action
# hand normalizado: "AK", "QJ", "TT" etc.
# suited_flag: True/False/None (None = pares)
RANGES = {
    "LT10": {
        ("AA", None): "PUSH", ("KK", None): "PUSH", ("QQ", None): "PUSH", ("JJ", None): "PUSH", ("TT", None): "PUSH",
        ("99", None): "PUSH", ("88", None): "PUSH",
        ("AK", True): "PUSH", ("AQ", True): "PUSH", ("AJ", True): "PUSH",
        ("AK", False): "PUSH", ("AQ", False): "PUSH",
        ("KQ", True): "RAISE",
        ("AT", True): "RAISE", ("KJ", True): "RAISE", ("QJ", True): "RAISE",
    },
    "10_40": {
        ("AA", None): "RAISE", ("KK", None): "RAISE", ("QQ", None): "RAISE", ("JJ", None): "RAISE", ("TT", None): "RAISE",
        ("99", None): "RAISE", ("88", None): "RAISE", ("77", None): "RAISE",
        ("AK", True): "RAISE", ("AQ", True): "RAISE", ("AJ", True): "RAISE",
        ("AK", False): "RAISE", ("AQ", False): "RAISE",
        ("KQ", True): "RAISE", ("KJ", True): "RAISE", ("QJ", True): "RAISE",
        ("AT", True): "RAISE", ("A9", True): "RAISE",
    },
    "40P": {
        ("AA", None): "RAISE", ("KK", None): "RAISE", ("QQ", None): "RAISE", ("JJ", None): "RAISE", ("TT", None): "RAISE",
        ("AK", True): "RAISE", ("AQ", True): "RAISE",
        ("AK", False): "RAISE",
        ("KQ", True): "RAISE",
    }
}

def bb_bucket(bb: int) -> str:
    if bb < 10:
        return "LT10"
    if 10 <= bb <= 40:
        return "10_40"
    return "40P"

def normalize_hand(c1: str, c2: str):
    order = "AKQJT98765432"
    # ordenar por fuerza
    if order.index(c1) <= order.index(c2):
        hi, lo = c1, c2
    else:
        hi, lo = c2, c1
    pair = (hi == lo)
    return (hi + lo, pair)

def decide_action(bb: int, c1: str, c2: str, suited: bool | None):
    hand, is_pair = normalize_hand(c1, c2)
    bucket = bb_bucket(bb)
    table = RANGES[bucket]
    key = (hand, None) if is_pair else (hand, suited)
    return table.get(key, "FOLD")

def classify(action: str) -> str:
    return "PROACTIVA" if action in ("PUSH", "RAISE") else "PREVENTIVA"

def coach_message(stats, last_action=None):
    # stats: dict total/proactive/preventive/fold_streak
    total = stats["total"]
    if total == 0:
        return "Respira. Empieza con calma: hoy entrenas decisiones, no resultados."
    ratio = stats["proactive"] / total if total else 0

    if stats["fold_streak"] >= 3:
        return "🫧 Tilt check: 3+ folds seguidos. Haz CALMA 10s, vuelve al plan. Una mano a la vez."

    if last_action == "FOLD":
        if ratio < 0.30:
            return "🔵 Muy preventiva hoy: revisa si estás foldeando por tensión. Busca un spot claro, no perfecto."
        return "✅ Buen fold: conservar fichas también es jugar bien. Respira y sigue."
    if last_action in ("RAISE", "PUSH"):
        if ratio > 0.65:
            return "🟠 Muy proactiva hoy: excelente iniciativa, pero cuida spots marginales. Disciplina > impulso."
        return "🟢 Buena iniciativa: presión con criterio. Confía en el proceso."
    return "Mantén el plan."

# -----------------------------
# State
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data = load_data()

if "sel" not in st.session_state:
    st.session_state.sel = []

if "suited" not in st.session_state:
    st.session_state.suited = None  # True/False/None

# -----------------------------
# UI
# -----------------------------
st.title("Poker Radar PRO 🧠")
st.caption("Educativo, acumulativo, con historial persistente y coach anti-tilt.")

# Selector BB
bb = st.segmented_control(
    "Stack (BB)",
    options=[8, 20, 35, 50],
    default=20,
    help="Elige un BB aproximado. Puedes ajustar a tu necesidad."
)

# Ronda
colA, colB, colC = st.columns([1,1,1])
with colA:
    st.metric("Ronda", st.session_state.data.get("round", 1))
with colB:
    if st.button("➕ Nueva ronda", use_container_width=True):
        st.session_state.data["round"] = int(st.session_state.data.get("round", 1)) + 1
        save_data(st.session_state.data)
        st.toast("Ronda nueva creada ✅")
with colC:
    if st.button("🧹 Borrar todo", use_container_width=True):
        st.session_state.data = {"round": 1, "hands": []}
        st.session_state.sel = []
        st.session_state.suited = None
        save_data(st.session_state.data)
        st.toast("Todo borrado ✅")

st.divider()

# Selección cartas
cards = list("AKQJT98765432")
st.subheader("Selecciona 2 cartas")
grid_cols = st.columns(7)
for i, c in enumerate(cards):
    with grid_cols[i % 7]:
        if st.button(c, use_container_width=True):
            if len(st.session_state.sel) < 2:
                st.session_state.sel.append(c)

# suited / offsuit
c1, c2 = st.columns(2)
with c1:
    suited_btn = st.button("Suited (s)", use_container_width=True)
with c2:
    offsuit_btn = st.button("Offsuit (o)", use_container_width=True)

if suited_btn:
    st.session_state.suited = True
if offsuit_btn:
    st.session_state.suited = False

# Mostrar selección actual
sel = st.session_state.sel
suited = st.session_state.suited

sel_txt = " ".join(sel) if sel else "—"
flag_txt = "pair" if (len(sel)==2 and sel[0]==sel[1]) else ("suited" if suited is True else ("offsuit" if suited is False else "—"))
st.info(f"Selección: **{sel_txt}** | Tipo: **{flag_txt}**", icon="🃏")

# Acción
action = None
can_calc = False
if len(sel) == 2:
    if sel[0] == sel[1]:
        can_calc = True
        suited_needed = False
    else:
        suited_needed = True
        can_calc = suited in (True, False)

if st.button("📌 Calcular decisión", type="primary", use_container_width=True, disabled=not can_calc):
    c1, c2 = sel[0], sel[1]
    action = decide_action(bb, c1, c2, suited if c1 != c2 else None)

    # Guardar
    rec = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "round": int(st.session_state.data.get("round", 1)),
        "bb": int(bb),
        "hand": f"{c1}{c2}" + ("" if c1==c2 else ("s" if suited else "o")),
        "action": action,
        "type": classify(action)
    }
    st.session_state.data["hands"].insert(0, rec)
    save_data(st.session_state.data)

    # reset selección para siguiente mano
    st.session_state.sel = []
    st.session_state.suited = None

    st.toast("Guardado ✅")

# Mostrar resultado si último existe
hands = st.session_state.data.get("hands", [])
last = hands[0] if hands else None

if last:
    st.subheader("Resultado")
    color = {"PUSH":"🟢", "RAISE":"🟡", "FOLD":"🔴"}.get(last["action"], "⚪")
    st.markdown(f"### {color} **{last['action']}**  \n**Mano:** `{last['hand']}` | **BB:** `{last['bb']}` | **Tipo:** `{last['type']}`")

# Stats + coach
total = len(hands)
proactive = sum(1 for h in hands if h["type"] == "PROACTIVA")
preventive = total - proactive

# fold streak
fold_streak = 0
for h in hands[:10]:
    if h["action"] == "FOLD":
        fold_streak += 1
    else:
        break

stats = {"total": total, "proactive": proactive, "preventive": preventive, "fold_streak": fold_streak}
ratio = round((proactive/total)*100) if total else 0

st.divider()
st.subheader("Perfil de hoy (acumulativo)")
m1, m2, m3 = st.columns(3)
m1.metric("Total manos", total)
m2.metric("Proactivas", proactive)
m3.metric("% Proactiva", f"{ratio}%")

st.success(coach_message(stats, last_action=(last["action"] if last else None)), icon="💙")

# Botón CALMA 10s (real, sin HTML)
if st.button("🫧 CALMA 10s (Inhala 4 / Exhala 6)", use_container_width=True):
    box = st.empty()
    for t in range(1, 11):
        if t <= 4:
            box.info(f"Inhala… **{5-t}**  \nSuelta hombros y mandíbula.", icon="🌬️")
        else:
            box.info(f"Exhala… **{11-t}**  \nDeja que baje la rabia.", icon="🫧")
        time.sleep(1)
    box.success("Listo. Vuelve al plan. Una mano a la vez.", icon="✅")

# Historial + resumen por ronda
st.divider()
st.subheader("Historial (últimas 50)")
df = pd.DataFrame(hands[:50])
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Resumen por ronda")
if hands:
    rdf = pd.DataFrame(hands)
    piv = (rdf.groupby(["round", "type"]).size()
           .unstack(fill_value=0)
           .reset_index()
           .sort_values("round", ascending=False))
    if "PROACTIVA" not in piv.columns: piv["PROACTIVA"] = 0
    if "PREVENTIVA" not in piv.columns: piv["PREVENTIVA"] = 0
    piv["Manos"] = piv["PROACTIVA"] + piv["PREVENTIVA"]
    piv["% Pro"] = (piv["PROACTIVA"] / piv["Manos"]).fillna(0).round(2)
    piv = piv[["round", "Manos", "PROACTIVA", "PREVENTIVA", "% Pro"]]
    st.dataframe(piv, use_container_width=True, hide_index=True)

    # Export CSV
    csv = pd.DataFrame(hands).to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar historial CSV", data=csv, file_name="poker_history.csv", mime="text/csv", use_container_width=True)
else:
    st.caption("Aún no hay manos guardadas.")
