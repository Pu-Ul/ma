import streamlit as st

# Configuración de la interfaz
st.set_page_config(page_title="PauGaR - Radar Inteligente", layout="centered")

# --- ESTILOS DE INTERFAZ ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .main-title { color: #ffcc00; text-align: center; font-size: 2rem; font-weight: 900; margin-bottom: 20px; }
    .decision-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 2.5rem; font-weight: 900; margin: 15px 0; border: 4px solid white; }
    .info-text { font-size: 0.9rem; color: #ffcc00; font-weight: bold; text-align: center; }
    .card-display { font-size: 1.5rem; font-weight: bold; text-align: center; padding: 10px; background: #222; border-radius: 10px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">PAUGAR POKER RADAR</div>', unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO (MEMORIA) ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.mano = []
    st.session_state.suited = None
    st.session_state.flop = []

# --- PASO 1: DECISIÓN PRE-FLOP (CANDADO) ---
if st.session_state.paso == 1:
    st.markdown('<p class="info-text">PASO 1: ELIGE TUS 2 CARTAS</p>', unsafe_allow_html=True)
    
    valores = ['A','K','Q','J','10','9','8','7','6','5','4','3','2']
    cols = st.columns(7)
    for i, v in enumerate(valores):
        if cols[i % 7].button(v, key=f"p1_{v}"):
            if len(st.session_state.mano) < 2:
                st.session_state.mano.append(v)

    if len(st.session_state.mano) > 0:
        st.markdown(f'<div class="card-display">Tus cartas: {" - ".join(st.session_state.mano)}</div>', unsafe_allow_html=True)

    st.markdown('<p class="info-text">¿SON DEL MISMO PALO?</p>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    if col_s1.button("SÍ (Suited)", key="btn_s"): st.session_state.suited = True
    if col_s2.button("NO (Offsuit)", key="btn_o"): st.session_state.suited = False

    # Lógica de decisión con IF
    if len(st.session_state.mano) == 2 and st.session_state.suited is not None:
        c1 = st.session_state.mano[0]
        c2 = st.session_state.mano[1]
        es_suited = st.session_state.suited
        
        # EL CANDADO: Lógica de entrada al juego
        # 1. Parejas (Cualquier par es Raise)
        # 2. Si tienes un AS
        # 3. Si tienes una K y es Suited
        if c1 == c2 or c1 == 'A' or c2 == 'A' or ((c1 == 'K' or c2 == 'K') and es_suited):
            st.markdown('<div class="decision-box" style="background-color: #27ae60;">RAISE</div>', unsafe_allow_html=True)
            if st.button("VER EL FLOP ➡️"):
                st.session_state.paso = 2
                st.rerun()
        else:
            st.markdown('<div class="decision-box" style="background-color: #c0392b;">FOLD</div>', unsafe_allow_html=True)
            if st.button("🔄 OTRA MANO"):
                st.session_state.clear()
                st.rerun()

# --- PASO 2: POST-FLOP (ALIMENTADOR 52 CARTAS) ---
elif st.session_state.paso == 2:
    st.markdown('<p class="info-text">PASO 2: SELECCIONA LAS 3 CARTAS DE LA MESA</p>', unsafe_allow_html=True)
    st.write(f"Mano actual: **{st.session_state.mano[0]} - {st.session_state.mano[1]}**")

    # Matriz completa de 52 cartas
    pintas = [('♠', 'picas'), ('♥', 'coraz'), ('♦', 'diam'), ('♣', 'trebol')]
    ranks = ['A','K','Q','J','10','9','8','7','6','5','4','3','2']

    for simbolo, nombre in pintas:
        cols = st.columns(13)
        for i, r in enumerate(ranks):
            label = f"{r}{simbolo}"
            # Color del texto según la pinta
            if cols[i].button(label, key=f"f_{label}"):
                if len(st.session_state.flop) < 3:
                    st.session_state.flop.append({'r': r, 's': simbolo})

    # Mostrar el Flop elegido
    if st.session_state.flop:
        st.markdown('<p class="info-text">TABLERO ACTUAL</p>', unsafe_allow_html=True)
        cols_f = st.columns(3)
        for idx, card in enumerate(st.session_state.flop):
            color = "red" if card['s'] in ['♥', '♦'] else "white"
            cols_f[idx].markdown(f"<div style='background:white; color:{color}; padding:10px; border-radius:5px; text-align:center; font-size:1.5rem; font-weight:bold;'>{card['r']}{card['s']}</div>", unsafe_allow_html=True)

    # Lógica de Retroalimentación Post-Flop
    if len(st.session_state.flop) == 3:
        st.divider()
        f_ranks = [c['r'] for c in st.session_state.flop]
        f_suits = [c['s'] for c in st.session_state.flop]
        
        # IF de conexión: ¿Alguna de mis cartas está en el flop?
        conectado = any(r in f_ranks for r in st.session_state.mano)
        
        # IF de peligro: ¿Hay 3 del mismo palo?
        color_peligro = any(f_suits.count(s) == 3 for s in set(f_suits))
        
        # IF de mesa doblada
        mesa_doblada = len(set(f_ranks)) < 3

        # Mensajes de Python
        if conectado:
            st.success("✅ **¡CONECTADO!** Tienes juego. Evalúa la fuerza de tu apuesta.")
        else:
            st.warning("❌ **NO CONECTÓ.** La mesa no te favorece. Juega con cautela.")

        if color_peligro:
            st.error("⚠️ **PELIGRO DE COLOR:** La mesa tiene 3 cartas de la misma pinta.")
        
        if mesa_doblada:
            st.error("⚠️ **PELIGRO DE FULL:** La mesa tiene cartas repetidas.")

        if st.button("🔄 FINALIZAR Y VOLVER A EMPEZAR"):
            st.session_state.clear()
            st.rerun()
