import streamlit as st, itertools, json, os, random, math
from datetime import datetime

st.set_page_config(page_title="Hold'em Pocket Coach", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.block-container{padding-top:.5rem;padding-bottom:.6rem;max-width:560px}
header,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{visibility:hidden;height:0}
div.stButton>button{width:100%;padding:.74rem .85rem;border-radius:16px;font-weight:700}
div[data-baseweb="select"]>div,input,textarea{border-radius:14px!important}
.card{background:rgba(0,0,0,.04);border:1px solid rgba(0,0,0,.08);padding:.72rem .85rem;border-radius:18px;margin-bottom:.55rem}
.small{font-size:.92rem;opacity:.92;line-height:1.28}
.badge{display:inline-block;padding:.14rem .5rem;border-radius:999px;background:rgba(0,0,0,.07);border:1px solid rgba(0,0,0,.08);font-size:.82rem;margin-right:.3rem}
.kpi{display:flex;gap:.4rem;flex-wrap:wrap}
.kpi>div{flex:1;min-width:110px;background:rgba(0,0,0,.03);border:1px solid rgba(0,0,0,.07);border-radius:14px;padding:.45rem .55rem}
.kpi .t{font-size:.75rem;opacity:.7;margin-bottom:.15rem}
.kpi .v{font-size:1.05rem;font-weight:800}
hr{margin:.45rem 0}
</style>
""", unsafe_allow_html=True)

DATA_DIR="data"; HISTORY_PATH=os.path.join(DATA_DIR,"history.json")
RANKS="23456789TJQKA"; SUITS="shdc"; RV={r:i for i,r in enumerate(RANKS,start=2)}
SUIT_SYM={"s":"♠","h":"♥","d":"♦","c":"♣"}

CALM=[
"Decide por proceso: información → rango → pot odds/equity → acción.",
"Si no hay ventaja clara, la jugada más rentable es esperar un spot mejor.",
"Una buena línea no siempre gana hoy, pero gana en el largo plazo.",
"Respira: revisa tamaño del bote, costo y textura. Después elige.",
"Claridad primero. Tu objetivo es consistencia, no adivinar."
]

def ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH,"w",encoding="utf-8") as f: json.dump({"hands":[],"session":{"played":0,"saved":0,"bb_net":0.0}},f,ensure_ascii=False,indent=2)

def load_store():
    ensure_store()
    try:
        with open(HISTORY_PATH,"r",encoding="utf-8") as f: return json.load(f)
    except Exception:
        return {"hands":[],"session":{"played":0,"saved":0,"bb_net":0.0}}

def save_store(store):
    ensure_store()
    with open(HISTORY_PATH,"w",encoding="utf-8") as f: json.dump(store,f,ensure_ascii=False,indent=2)

def cstr(c): return f"{c[0]}{SUIT_SYM[c[1]]}"
def pretty(cs): return " ".join(cstr(x) for x in cs if x)
def deck(): return [r+s for r in RANKS for s in SUITS]
def uniq(cs):
    a=[x for x in cs if x]
    return len(a)==len(set(a))

def card_options():
    o=[""]
    for r in RANKS[::-1]:
        for s in SUITS:
            o.append(r+s)
    return o

def five_rank(cards5):
    rs=sorted([RV[c[0]] for c in cards5], reverse=True)
    ss=[c[1] for c in cards5]
    cnt=sorted(((rs.count(v),v) for v in set(rs)), reverse=True)
    fl=len(set(ss))==1
    def straight_high(vals):
        if set([14,5,4,3,2]).issubset(set(vals)): return 5
        v=sorted(set(vals), reverse=True)
        for i in range(len(v)-4):
            seq=v[i:i+5]
            if seq[0]-seq[4]==4 and len(seq)==5: return seq[0]
        return None
    sh=straight_high(rs)
    if fl and sh: return (8, sh, rs)
    if cnt[0][0]==4:
        q=cnt[0][1]; k=max([v for v in rs if v!=q]); return (7, q, k)
    if cnt[0][0]==3 and cnt[1][0]==2: return (6, cnt[0][1], cnt[1][1])
    if fl: return (5, rs)
    if sh: return (4, sh, rs)
    if cnt[0][0]==3:
        t=cnt[0][1]; ks=sorted([v for v in rs if v!=t], reverse=True); return (3, t, ks)
    if cnt[0][0]==2 and cnt[1][0]==2:
        ph=max(cnt[0][1],cnt[1][1]); pl=min(cnt[0][1],cnt[1][1])
        k=max([v for v in rs if v not in (ph,pl)]); return (2, ph, pl, k)
    if cnt[0][0]==2:
        p=cnt[0][1]; ks=sorted([v for v in rs if v!=p], reverse=True); return (1, p, ks)
    return (0, rs)

def best_rank(cards7):
    best=None; best5=None
    for comb in itertools.combinations(cards7,5):
        r=five_rank(list(comb))
        if best is None or r>best:
            best=r; best5=comb
    return best, best5

def cat_name(rt):
    return {8:"Escalera de color",7:"Póker",6:"Full house",5:"Color",4:"Escalera",3:"Trío",2:"Doble pareja",1:"Pareja",0:"Carta alta"}[rt[0]]

def req_equity(pot_bb, call_bb):
    if call_bb<=0: return 0.0
    return call_bb/(pot_bb+call_bb)

def outs_one_card(hero, board):
    used=set(hero+board)
    d=[c for c in deck() if c not in used]
    cur,_=best_rank(hero+board); curc=cur[0]
    if len(board)>=5: return 0
    imp=0
    for x in d:
        r,_=best_rank(hero+(board+[x]))
        if r[0]>curc: imp+=1
    return imp

def preflop_score(hero):
    r1,r2=hero[0][0],hero[1][0]
    s1,s2=hero[0][1],hero[1][1]
    v1,v2=RV[r1],RV[r2]
    suited=s1==s2; pair=r1==r2
    hi=max(v1,v2); lo=min(v1,v2); gap=hi-lo
    if pair: sc=62+(hi-2)*3.1
    else:
        sc=28+(hi-2)*2.15-gap*2.05
        if suited: sc+=5.6
        if gap==1: sc+=2.2
        if hi>=12 and lo>=10: sc+=2.0
        if hi>=11 and suited and gap<=2: sc+=1.5
        if lo<=5 and suited and gap==1: sc+=1.2
    return max(10,min(95,sc))

def hand_key(c1,c2):
    r1,r2=c1[0],c2[0]
    v1,v2=RV[r1],RV[r2]
    hi,lo=(r1,r2) if v1>=v2 else (r2,r1)
    suited="s" if c1[1]==c2[1] else "o"
    if r1==r2: return hi+lo
    return hi+lo+suited

def pos_group(pos):
    if pos in ("UTG","MP"): return "early"
    if pos in ("CO","BTN"): return "late"
    return "blinds"

def suggest_open_size_bb(stack_bb):
    if stack_bb<=20: return 2.2
    if stack_bb<=40: return 2.4
    return 2.5

def suggest_3bet_size_bb(pos, facing_size_bb):
    if pos in ("SB","BB"): return max(9.0, facing_size_bb*3.7)
    return max(7.0, facing_size_bb*3.0)

def normalize(weights):
    s=sum(weights)
    if s<=0: return None
    return [w/s for w in weights]

def gen_starting_hands():
    cards=[r+s for r in RANKS for s in SUITS]
    hands=[]
    for i in range(len(cards)):
        for j in range(i+1,len(cards)):
            hands.append((cards[i],cards[j]))
    return hands

ALL_START=None

def range_weight(hero_hand, style, pos, facing):
    k=hand_key(hero_hand[0],hero_hand[1])
    base=preflop_score([hero_hand[0],hero_hand[1]])
    if style=="tight":
        thresh=70
    elif style=="loose":
        thresh=50
    else:
        thresh=60
    if facing=="none":
        adj=0
    elif facing=="open":
        adj=6
    else:
        adj=12
    if pos in ("UTG","MP"): adj+=4
    if pos in ("CO","BTN"): adj-=2
    thresh+=adj
    if base>=thresh: return 1.0 + (base-thresh)/25.0
    if base>=thresh-8 and style!="tight": return 0.35
    if base>=thresh-5 and style=="loose": return 0.55
    return 0.0

def sample_opp_hand(excluded, style, pos, facing):
    global ALL_START
    if ALL_START is None: ALL_START=gen_starting_hands()
    candidates=[]; weights=[]
    ex=set(excluded)
    for h in ALL_START:
        if h[0] in ex or h[1] in ex: continue
        w=range_weight(h, style, pos, facing)
        if w>0:
            candidates.append(h); weights.append(w)
    if not candidates:
        d=[c for c in deck() if c not in ex]
        random.shuffle(d)
        return [d[0],d[1]]
    p=normalize(weights)
    idx=random.choices(range(len(candidates)), weights=p, k=1)[0]
    return [candidates[idx][0], candidates[idx][1]]

def equity_mc(hero, board, opps, iters, opp_style, opp_pos, opp_facing):
    used=set(hero+board)
    d0=[c for c in deck() if c not in used]
    need=5-len(board)
    if need<0: return None
    iters=max(900, min(int(iters), 14000))
    w=t=0
    for _ in range(iters):
        d=d0[:]; random.shuffle(d)
        run=board[:] + d[:need]
        used_now=set(hero+run)
        opp_hands=[]
        for _k in range(opps):
            oh=sample_opp_hand(used_now, opp_style, opp_pos, opp_facing)
            used_now.update(oh)
            opp_hands.append(oh)
        hr,_=best_rank(hero+run)
        besto=None
        for oh in opp_hands:
            r,_=best_rank(oh+run)
            if besto is None or r>besto: besto=r
        if hr>besto: w+=1
        elif hr==besto: t+=1
    return (w+0.5*t)/iters

def postflop_advice(equity, req, call_bb, texture_hint, position_adv):
    m=0.05
    if equity is None: return ("Datos incompletos","Completa cartas para calcular.","Equity: probabilidad aproximada de ganar si vas a showdown.")
    if call_bb<=0:
        return ("Plan","Si no hay costo por pagar, decide entre apostar por valor, farolear con sentido o controlar el bote según textura.","Control del bote: mantener el bote manejable con manos medias.")
    if equity>=req+0.10:
        return ("Continuar con intención","Tu equity supera claramente lo requerido por pot odds. Pagar o subir puede ser razonable según acción y textura.","Pot odds: equity mínima para que pagar sea rentable.")
    if equity>=req+m:
        return ("Call razonable","Estás por encima del umbral. Si la textura es peligrosa, prefiere tamaños que controlen el riesgo.","Textura: cómo el board conecta proyectos y manos fuertes.")
    if equity>=req-m:
        return ("Zona fina","Estás cerca del umbral. Si enfrentas apuesta grande y poca posición, foldear es coherente.","Disciplina: evitar pagos negativos protege tu stack.")
    return ("Fold frecuente","Tu equity no cubre pot odds. Esperar spots mejores protege tu BB neto.","Selección de spot: elegir escenarios con ventaja.")

def texture(board):
    if len(board)<3: return "—"
    rs=sorted([RV[c[0]] for c in board], reverse=True)
    ss=[c[1] for c in board]
    paired=len(set([c[0] for c in board]))<len(board)
    suited=max(ss.count(s) for s in set(ss))
    gaps=sorted([abs(rs[i]-rs[i+1]) for i in range(len(rs)-1)])
    wet=False
    if suited>=3: wet=True
    if (len(board)>=3 and min(gaps)<=2): wet=True
    if paired: wet=True
    if wet: return "Conectada/Peligrosa"
    return "Seca/Estable"

def glossary(stage):
    if stage=="preflop":
        return [("Rango","Conjunto de manos que se juegan en una situación."),("Open raise","Primera subida cuando nadie abrió."),("3-bet","Resubida después de una subida.")]
    if stage=="flop":
        return [("Textura","Cómo el board conecta proyectos/pares."),("C-bet","Apuesta del agresor preflop en flop."),("Proyecto","Mano que puede mejorar (draw).")]
    if stage=="turn":
        return [("Outs","Cartas que mejoran tu mano en la próxima calle."),("Pot odds","Costo de pagar vs bote (umbral de equity)."),("Bloqueadores","Cartas que reducen combos fuertes del rival.")]
    return [("Value bet","Apuesta para que te paguen manos peores."),("Bluff","Apuesta para que foldee una mejor."),("Showdown","Revelación final de manos.")]

def calm(): return random.choice(CALM)

def street(stage): return {"preflop":"PREFLOP","flop":"FLOP","turn":"TURN","river":"RIVER"}[stage]

def reset_hand():
    st.session_state.stage="preflop"
    st.session_state.hero=["",""]
    st.session_state.board=[]
    st.session_state.pos="BTN"
    st.session_state.stack_bb=50
    st.session_state.pot_bb=3.0
    st.session_state.call_bb=1.0
    st.session_state.villains=1
    st.session_state.v_style="normal"
    st.session_state.v_pos="CO"
    st.session_state.v_facing="open"
    st.session_state.facing="none"
    st.session_state.facing_size=2.5
    st.session_state.last_eq=None
    st.session_state.last_best=None
    st.session_state.last_note=""

if "stage" not in st.session_state: reset_hand()

store=load_store()
sess=store.get("session",{"played":0,"saved":0,"bb_net":0.0})
hands=store.get("hands",[])

st.markdown(f"""
<div class="card">
  <div><span class="badge">Hold'em</span><span class="badge">Móvil</span><span class="badge">Sin scroll</span><span class="badge">Educativo</span></div>
  <div style="font-size:1.07rem;font-weight:800;margin-top:.18rem;">🃏 {street(st.session_state.stage)}</div>
  <div class="small" style="margin-top:.18rem;"><b>Mano:</b> {pretty(st.session_state.hero) or "—"} &nbsp; | &nbsp; <b>Board:</b> {pretty(st.session_state.board) or "—"}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<div class='card small'>🧭 {calm()}</div>", unsafe_allow_html=True)

top1,top2,top3=st.columns(3,gap="small")
with top1:
    if st.button("🔄 Nueva", use_container_width=True):
        reset_hand(); st.rerun()
with top2:
    if st.button("💾 Guardar", use_container_width=True):
        rec={
            "ts":datetime.now().strftime("%Y-%m-%d %H:%M"),
            "stage":st.session_state.stage,
            "hand":pretty(st.session_state.hero),
            "board":pretty(st.session_state.board),
            "pos":st.session_state.pos,
            "stackBB":int(st.session_state.stack_bb),
            "potBB":float(st.session_state.pot_bb),
            "callBB":float(st.session_state.call_bb),
            "villains":int(st.session_state.villains),
            "v_style":st.session_state.v_style,
            "facing":st.session_state.facing,
            "facing_size":float(st.session_state.facing_size),
            "equity":None if st.session_state.last_eq is None else round(st.session_state.last_eq*100,1),
            "made":None if st.session_state.last_best is None else cat_name(st.session_state.last_best),
            "note":st.session_state.last_note
        }
        hands.insert(0,rec); hands=hands[:30]
        sess["saved"]=sess.get("saved",0)+1
        store["hands"]=hands; store["session"]=sess
        save_store(store)
        st.success("Guardado ✅")
with top3:
    if st.button("🧹 Historial", use_container_width=True):
        st.session_state.show_hist=not st.session_state.get("show_hist",False)

st.markdown("<div class='card'>", unsafe_allow_html=True)
a,b=st.columns(2,gap="small")
with a:
    st.session_state.pos=st.selectbox("📍 Tu posición", ["UTG","MP","CO","BTN","SB","BB"], index=["UTG","MP","CO","BTN","SB","BB"].index(st.session_state.pos))
    st.session_state.stack_bb=st.number_input("💰 Tu stack (BB)", min_value=1, max_value=500, value=int(st.session_state.stack_bb), step=1)
    st.session_state.facing=st.selectbox("⚡ Acción antes de ti", ["none","open","3bet"], index=["none","open","3bet"].index(st.session_state.facing))
    st.session_state.facing_size=st.number_input("📏 Tamaño (BB)", min_value=1.0, max_value=50.0, value=float(st.session_state.facing_size), step=0.5)
with b:
    st.session_state.pot_bb=st.number_input("🪙 Bote (BB)", min_value=0.0, max_value=500.0, value=float(st.session_state.pot_bb), step=0.5)
    st.session_state.call_bb=st.number_input("✅ Costo para pagar (BB)", min_value=0.0, max_value=500.0, value=float(st.session_state.call_bb), step=0.5)
    st.session_state.villains=st.selectbox("👥 Rivales (aprox.)", [1,2,3,4,5], index=[1,2,3,4,5].index(int(st.session_state.villains)))
    st.session_state.v_style=st.selectbox("🎭 Estilo rival", ["tight","normal","loose"], index=["tight","normal","loose"].index(st.session_state.v_style))
st.markdown("</div>", unsafe_allow_html=True)

opts=card_options()
stage=st.session_state.stage

def stage_nav(prev_stage, next_stage, trim_board=None):
    x,y=st.columns(2,gap="small")
    with x:
        if st.button(f"⬅️ {street(prev_stage)}", use_container_width=True):
            st.session_state.stage=prev_stage
            if trim_board is not None: st.session_state.board=st.session_state.board[:trim_board]
            st.rerun()
    with y:
        if st.button(f"➡️ {street(next_stage)}", use_container_width=True):
            st.session_state.stage=next_stage
            st.rerun()

def show_kpis(eq, req, outs, tex, made):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='kpi'>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='t'>Equity</div><div class='v'>{'—' if eq is None else f'{eq*100:.1f}%'}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='t'>Umbral (pot odds)</div><div class='v'>{req*100:.1f}%</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='t'>Outs (1 carta)</div><div class='v'>{outs}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div><div class='t'>Textura</div><div class='v'>{tex}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if made: st.markdown(f"**Lectura:** {made}")
    st.markdown("</div>", unsafe_allow_html=True)

def show_gloss(stage):
    st.markdown("<div class='card small'>", unsafe_allow_html=True)
    st.markdown(f"**📘 Mini-glosario ({street(stage).lower()}):**")
    for k,v in glossary(stage): st.markdown(f"- **{k}:** {v}")
    st.markdown("</div>", unsafe_allow_html=True)

def preflop_plan(hero):
    sc=preflop_score(hero)
    act,reason,term=preflop_action(sc)
    k=hand_key(hero[0],hero[1])
    open_size=suggest_open_size_bb(st.session_state.stack_bb)
    facing=st.session_state.facing
    facing_size=st.session_state.facing_size
    pos=st.session_state.pos
    if facing=="none":
        size_note=f"Tamaño sugerido de open: ~{open_size:.1f} BB."
        line="Si nadie abrió antes, puedes abrir con tamaño estándar y jugar en posición con disciplina."
    elif facing=="open":
        three=suggest_3bet_size_bb(pos, facing_size)
        size_note=f"Si decides 3-bet: ~{three:.1f} BB (ajusta por posición)."
        line="Si hay subida antes, tu decisión depende de tu fuerza, posición y tamaño. A veces call, a veces 3-bet, a veces fold."
    else:
        size_note="Enfrentando 3-bet, ajusta: manos fuertes continúan; marginales suelen foldear."
        line="Ante 3-bet, el rango se estrecha. Evita pagar con manos que no soportan presión postflop."
    return sc,k,act,reason,term,size_note,line

def preflop_action(sc):
    pos=st.session_state.pos
    facing=st.session_state.facing
    stack=st.session_state.stack_bb
    late=pos in ("CO","BTN")
    blinds=pos in ("SB","BB")
    shallow=stack<=20
    if facing=="3bet":
        if sc>=80: return ("4-bet o call según rival","Fuerte para continuar. Elige 4-bet con manos premium o call si el rival farolea poco.","4-bet: resubida después de un 3-bet.")
        if sc>=68: return ("Call o fold según tamaño","Jugable, pero el tamaño manda. Si es grande y fuera de posición, foldea más.","SPR: relación stack/bote que define compromiso.")
        return ("Fold frecuente","Tu mano rara vez compensa el riesgo vs 3-bet.","Selección de spot: evita spots de alta varianza sin ventaja.")
    if facing=="open":
        if sc>=78: return ("3-bet por valor","Sube para capturar valor y tomar iniciativa.","Iniciativa: ser quien presiona define la mano.")
        if sc>=62:
            if late or blinds: return ("Call o 3-bet mixto","Decide por tamaño y posición: call si es pequeño; 3-bet si buscas iniciativa.","Mixto: alternar acciones para ser menos predecible.")
            return ("Call cuidadoso","En posiciones tempranas, prioriza manos que juegan bien postflop.","Posición: actuar después mejora tu EV.")
        if sc>=50 and late and not shallow: return ("Call si el precio es bueno","Busca flops favorables, pero evita pagar tamaños grandes fuera de posición.","Implied odds: ganar más cuando conectas fuerte.")
        return ("Fold","Evita pagar sin ventaja clara.","Disciplina: proteger BB neto.")
    if sc>=78: return ("Open raise","Mano fuerte para abrir y construir bote.","Open raise: primera subida preflop.")
    if sc>=60:
        if late or blinds: return ("Open raise","Buena mano para abrir con posición o ciegas.","Rango: manos que abres según posición.")
        return ("Open o fold según mesa","Si la mesa es agresiva, estrecha; si es pasiva, puedes abrir más.","Adaptación: ajustar al estilo de la mesa.")
    if sc>=48:
        if late and stack>=35: return ("Open ocasional","Mano especulativa; prefiere posición tardía y control.","Control del bote: reducir varianza con manos medias.")
        return ("Fold frecuente","Mano marginal sin ventaja.","Fold equity: valor cuando el rival foldea ante presión.")
    return ("Fold","Mano débil. Espera un spot mejor.","Spot: situación favorable para actuar.")

if stage=="preflop":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="small")
    with c1: st.session_state.hero[0]=st.selectbox("🂡 Tu carta 1", opts, index=opts.index(st.session_state.hero[0]) if st.session_state.hero[0] in opts else 0)
    with c2: st.session_state.hero[1]=st.selectbox("🂡 Tu carta 2", opts, index=opts.index(st.session_state.hero[1]) if st.session_state.hero[1] in opts else 0)
    ok=all(st.session_state.hero) and uniq(st.session_state.hero)
    if not ok and any(st.session_state.hero): st.warning("Las cartas deben ser distintas.")
    if st.button("🎯 Analizar PREFLOP", disabled=not ok, use_container_width=True):
        sc,k,act,reason,term,size_note,line=preflop_plan(st.session_state.hero)
        st.session_state.last_eq=None
        st.session_state.last_best=None
        st.session_state.last_note=f"{act} | {size_note}"
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"**Tu mano (notación):** `{k}`")
        st.markdown(f"**Fuerza preflop (heurística):** `{sc:.0f}/100`")
        st.markdown(f"**Recomendación (condicional):** **{act}**")
        st.markdown(f"- {reason}")
        st.markdown(f"- {line}")
        st.markdown(f"**📏 Tamaños:** {size_note}")
        st.markdown(f"**📘 Término:** *{term}*")
        st.markdown("</div>", unsafe_allow_html=True)
        show_gloss("preflop")
        x,y=st.columns(2,gap="small")
        with x:
            if st.button("➡️ Pasar a FLOP", use_container_width=True):
                st.session_state.stage="flop"; st.session_state.board=[]; st.rerun()
        with y:
            if st.button("✋ Fold / Nueva", use_container_width=True):
                reset_hand(); st.rerun()
    else:
        st.markdown("</div>", unsafe_allow_html=True)

elif stage=="flop":
    if not all(st.session_state.hero) or not uniq(st.session_state.hero):
        st.info("Primero elige tu mano en preflop.")
        if st.button("⬅️ Volver a PREFLOP", use_container_width=True):
            st.session_state.stage="preflop"; st.rerun()
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        f1,f2,f3=st.columns(3,gap="small")
        b=st.session_state.board + [""]*(3-len(st.session_state.board))
        with f1: b[0]=st.selectbox("Flop 1", opts, index=opts.index(b[0]) if b[0] in opts else 0)
        with f2: b[1]=st.selectbox("Flop 2", opts, index=opts.index(b[1]) if b[1] in opts else 0)
        with f3: b[2]=st.selectbox("Flop 3", opts, index=opts.index(b[2]) if b[2] in opts else 0)
        chosen=[x for x in b if x]
        valid=len(chosen)==3 and uniq(st.session_state.hero+chosen)
        if len(chosen)==3 and not valid: st.warning("Revisa duplicados (mano/board).")
        st.session_state.v_pos=st.selectbox("📍 Posición rival (aprox.)", ["UTG","MP","CO","BTN","SB","BB"], index=["UTG","MP","CO","BTN","SB","BB"].index(st.session_state.v_pos))
        st.session_state.v_facing=st.selectbox("⚡ Rival entró como", ["open","call","3bet"], index=["open","call","3bet"].index(st.session_state.v_facing))
        if st.button("🔍 Analizar FLOP", disabled=not valid, use_container_width=True):
            st.session_state.board=chosen
            tex=texture(st.session_state.board)
            req=req_equity(float(st.session_state.pot_bb), float(st.session_state.call_bb))
            outs=outs_one_card(st.session_state.hero, st.session_state.board)
            eq=equity_mc(st.session_state.hero, st.session_state.board, int(st.session_state.villains), 6500 if int(st.session_state.villains)==1 else 5200, st.session_state.v_style, st.session_state.v_pos, st.session_state.v_facing)
            st.session_state.last_eq=eq
            best,_=best_rank(st.session_state.hero+st.session_state.board)
            st.session_state.last_best=best
            act,reason,term=postflop_advice(eq, req, float(st.session_state.call_bb), tex, True)
            st.session_state.last_note=f"{act} | Textura {tex}"
            st.markdown("</div>", unsafe_allow_html=True)
            show_kpis(eq, req, outs, tex, cat_name(best))
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"**Recomendación (condicional):** **{act}**")
            st.markdown(f"- {reason}")
            if tex=="Conectada/Peligrosa":
                st.markdown("- En boards conectados, prioriza tamaños más pequeños con manos medias y evita pagar apuestas grandes sin margen de equity.")
            else:
                st.markdown("- En boards secos, manos medias ganan valor y los faroles selectivos funcionan mejor.")
            st.markdown(f"**📘 Término:** *{term}*")
            st.markdown("</div>", unsafe_allow_html=True)
            show_gloss("flop")
            x,y=st.columns(2,gap="small")
            with x:
                if st.button("➡️ Pasar a TURN", use_container_width=True):
                    st.session_state.stage="turn"; st.rerun()
            with y:
                if st.button("✋ Fold / Nueva", use_container_width=True):
                    reset_hand(); st.rerun()
        else:
            st.markdown("</div>", unsafe_allow_html=True)

elif stage=="turn":
    if len(st.session_state.board)!=3:
        st.info("Primero completa el flop.")
        if st.button("⬅️ Volver a FLOP", use_container_width=True):
            st.session_state.stage="flop"; st.rerun()
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        t=st.selectbox("🎴 Carta del TURN", opts, index=0)
        valid=bool(t) and uniq(st.session_state.hero+st.session_state.board+[t])
        if t and not valid: st.warning("Esa carta ya está usada.")
        if st.button("🔍 Analizar TURN", disabled=not valid, use_container_width=True):
            st.session_state.board=st.session_state.board+[t]
            tex=texture(st.session_state.board)
            req=req_equity(float(st.session_state.pot_bb), float(st.session_state.call_bb))
            outs=outs_one_card(st.session_state.hero, st.session_state.board)
            eq=equity_mc(st.session_state.hero, st.session_state.board, int(st.session_state.villains), 8200 if int(st.session_state.villains)==1 else 6000, st.session_state.v_style, st.session_state.v_pos, st.session_state.v_facing)
            st.session_state.last_eq=eq
            best,_=best_rank(st.session_state.hero+st.session_state.board)
            st.session_state.last_best=best
            act,reason,term=postflop_advice(eq, req, float(st.session_state.call_bb), tex, True)
            st.session_state.last_note=f"{act} | Turn"
            st.markdown("</div>", unsafe_allow_html=True)
            show_kpis(eq, req, outs, tex, cat_name(best))
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"**Recomendación (condicional):** **{act}**")
            st.markdown(f"- {reason}")
            st.markdown("- En turn, el tamaño de apuesta del rival pesa más: si el costo sube, el umbral de equity también.")
            st.markdown(f"**📘 Término:** *{term}*")
            st.markdown("</div>", unsafe_allow_html=True)
            show_gloss("turn")
            x,y=st.columns(2,gap="small")
            with x:
                if st.button("➡️ Pasar a RIVER", use_container_width=True):
                    st.session_state.stage="river"; st.rerun()
            with y:
                if st.button("⬅️ Volver a FLOP", use_container_width=True):
                    st.session_state.stage="flop"; st.session_state.board=st.session_state.board[:3]; st.rerun()
        else:
            st.markdown("</div>", unsafe_allow_html=True)

elif stage=="river":
    if len(st.session_state.board)!=4:
        st.info("Primero completa el turn.")
        if st.button("⬅️ Volver a TURN", use_container_width=True):
            st.session_state.stage="turn"; st.rerun()
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        r=st.selectbox("🎴 Carta del RIVER", opts, index=0)
        valid=bool(r) and uniq(st.session_state.hero+st.session_state.board+[r])
        if r and not valid: st.warning("Esa carta ya está usada.")
        if st.button("🏁 Analizar RIVER", disabled=not valid, use_container_width=True):
            st.session_state.board=st.session_state.board+[r]
            tex=texture(st.session_state.board)
            req=req_equity(float(st.session_state.pot_bb), float(st.session_state.call_bb))
            eq=equity_mc(st.session_state.hero, st.session_state.board, int(st.session_state.villains), 11000 if int(st.session_state.villains)==1 else 7500, st.session_state.v_style, st.session_state.v_pos, st.session_state.v_facing)
            st.session_state.last_eq=eq
            best,_=best_rank(st.session_state.hero+st.session_state.board)
            st.session_state.last_best=best
            act,reason,term=postflop_advice(eq, req, float(st.session_state.call_bb), tex, True)
            st.session_state.last_note=f"{act} | River"
            st.markdown("</div>", unsafe_allow_html=True)
            show_kpis(eq, req, 0, tex, cat_name(best))
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"**Recomendación (condicional):** **{act}**")
            st.markdown(f"- {reason}")
            st.markdown("- En river ya no hay outs: decide por fuerza final, rangos y tamaño del bote.")
            st.markdown(f"**📘 Término:** *{term}*")
            st.markdown("</div>", unsafe_allow_html=True)
            show_gloss("river")
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            bb_net=st.number_input("📈 Resultado de la mano (BB neto, +ganaste / -perdiste)", min_value=-500.0, max_value=500.0, value=0.0, step=0.5)
            if st.button("✅ Cerrar mano (guardar y reiniciar)", use_container_width=True):
                rec={
                    "ts":datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "stage":"river",
                    "hand":pretty(st.session_state.hero),
                    "board":pretty(st.session_state.board),
                    "pos":st.session_state.pos,
                    "stackBB":int(st.session_state.stack_bb),
                    "potBB":float(st.session_state.pot_bb),
                    "callBB":float(st.session_state.call_bb),
                    "villains":int(st.session_state.villains),
                    "v_style":st.session_state.v_style,
                    "v_pos":st.session_state.v_pos,
                    "v_facing":st.session_state.v_facing,
                    "facing":st.session_state.facing,
                    "facing_size":float(st.session_state.facing_size),
                    "equity":round(eq*100,1),
                    "made":cat_name(best),
                    "bb_net":float(bb_net),
                    "note":st.session_state.last_note
                }
                hands.insert(0,rec); hands=hands[:30]
                sess["played"]=sess.get("played",0)+1
                sess["saved"]=sess.get("saved",0)+1
                sess["bb_net"]=float(sess.get("bb_net",0.0))+float(bb_net)
                store["hands"]=hands; store["session"]=sess
                save_store(store)
                reset_hand()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.get("show_hist",False):
    store=load_store()
    sess=store.get("session",{"played":0,"saved":0,"bb_net":0.0})
    hands=store.get("hands",[])
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**📊 Sesión**")
    st.markdown(f"<div class='kpi'><div><div class='t'>Manos cerradas</div><div class='v'>{int(sess.get('played',0))}</div></div><div><div class='t'>BB neto</div><div class='v'>{float(sess.get('bb_net',0.0)):.1f}</div></div><div><div class='t'>Guardadas</div><div class='v'>{int(sess.get('saved',0))}</div></div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if hands:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**🗂️ Últimas manos**")
        for i,h in enumerate(hands[:10], start=1):
            eq="—" if h.get("equity") is None else f"{h.get('equity')}%"
            made=h.get("made","—")
            bn=h.get("bb_net",None)
            bn_txt="" if bn is None else f" · BB {float(bn):+.1f}"
            st.markdown(f"<div class='small'><b>{i}.</b> {h.get('ts','')} · {h.get('hand','')} · {h.get('board','—')} · Pos {h.get('pos','')} · Eq {eq} · {made}{bn_txt}</div>", unsafe_allow_html=True)
        if st.button("🧨 Borrar TODO el historial", use_container_width=True):
            save_store({"hands":[],"session":{"played":0,"saved":0,"bb_net":0.0}})
            reset_hand()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='card small'>Historial vacío.</div>", unsafe_allow_html=True)
