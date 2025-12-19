import streamlit as st

# Configuración ultra-compacta para móvil
st.set_page_config(page_title="PauGaR Radar", layout="centered")

# CSS para forzar la cuadrícula y eliminar espacios muertos
st.markdown("""
    <style>
    /* Eliminar espacios superiores */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    
    /* Botones pequeños y en línea */
    div.stButton > button {
        width: 100%;
        padding: 5px 2px !important;
        font-size: 14px !important;
        height: 40px !important;
        border-radius: 5px;
    }
    
    /* Contenedor de decisión compacto */
    .dec-box {
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: 900;
        font-size: 24px;
        margin: 10px 0;
    }
    
    /* Ajuste para que las columnas no se amontonen */
    [data-testid="column"] {
        padding: 0 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MEMORIA DEL SISTEMA ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.mano = []
    st.session_state.suited = None
    st.session_state.flop = []
    st.session_state.historial = []

# --- PASO 1: RADAR (CANDADO) ---
if st.session_state.paso == 1:
    st.write("### 🃏 PASO 1: TUS 2 CARTAS")
    
    valores = ['A','K','Q','J','10','9','8','7','6','5','4','3','2']
    
    # Primera fila de cartas
    cols1 = st.columns(7)
    for i in range(7):
        if cols1[i].button(valores[i], key=f"p1_{valores[i]}"):
            if len(st.session_state.mano) < 2: st.session_state.mano.append(valores[i])
            
    # Segunda fila de cartas
    cols2 = st.columns(6)
    for i in range(6):
        idx = i + 7
        if cols2[i].button(valores[idx], key=f"p1_{valores[idx]}"):
            if len(st.session_state.mano) < 2: st.session_state.mano.append(valores[idx])

    if st.session_state.mano:
        st.info(f"Selección: {' - '.join(st.session_state.mano)}")

    st.write("¿Mismo palo?")
    c_s1, c_s2 = st.columns(2)
    if c_s1.button("SÍ (s)"): st.session_state.suited = True
    if c_s2.button("NO (o)"): st.session_state.suited = False

    # Lógica de decisión
    if len(st.session_state.mano) == 2 and st.session_state.suited is not None:
        c1, c2 = st.session_state.mano
        # Lógica IF Python
        if c1 == c2 or c1 == 'A' or c2 == 'A' or ((c1 == 'K' or c2 == 'K') and st.session_state.suited):
            st.markdown('<div class="dec-box" style="background:#27ae60;">RAISE</div>', unsafe_allow_html=True)
            if st.button("INGRESAR FLOP ➡️"):
                st.session_state.paso = 2
                st.rerun()
        else:
            st.markdown('<div class="dec-box" style="background:#c0392b;">FOLD</div>', unsafe_allow_html=True)
            if st.button("OTRA MANO"):
                st.session_state.clear()
                st.rerun()

# --- PASO 2: POST-FLOP (MESA) ---
elif st.session_state.paso == 2:
    st.write(f"### 🏟️ MESA ({st.session_state.mano[0]}{st.session_state.mano[1]})")
    
    pintas = ['♠', '♥', '♦', '♣']
    v_flop = ['A','K','Q','J','10','9','8','7','6','5','4','3','2']
    
    # Matriz de 52 cartas compacta
    for p in pintas:
        cols = st.columns(7) # Dividido en bloques para móvil
        for i in range(7):
            label = f"{v_flop[i]}{p}"
            if cols[i].button(label, key=f"f_{label}"):
                if len(st.session_state.flop) < 3: st.session_state.flop.append(label)
        
        cols2 = st.columns(6)
        for i in range(6):
            idx = i + 7
            label = f"{v_flop[idx]}{p}"
            if cols2[i].button(label, key=f"f_{label}"):
                if len(st.session_state.flop) < 3: st.session_state.flop.append(label)

    if st.session_state.flop:
        st.warning(f"Mesa: {' '.join(st.session_state.flop)}")

    if len(st.session_state.flop) == 3:
        # Lógica de alertas básica
        st.success("Análisis: Evalúa conexión con tu mano.")
        if st.button("FINALIZAR SESIÓN"):
            st.session_state.clear()
            st.rerun()
