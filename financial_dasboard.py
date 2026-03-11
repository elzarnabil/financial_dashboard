import streamlit as st
import anthropic
from datetime import datetime

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  :root {
    --bg: #080c10; --bg2: #0d1219; --bg3: #111820;
    --border: #1e2d3d; --accent: #00d4ff; --accent2: #00ff88;
    --red: #ff3b5c; --yellow: #ffd166; --green: #00ff88;
    --muted: #4a6278; --text: #c8dce8; --text2: #8aa4b8; --white: #e8f4fc;
  }

  html, body, [class*="css"], .stApp {
    background-color: #080c10 !important;
    color: #c8dce8 !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* Hide Streamlit default elements */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 1.5rem 2rem 4rem 2rem !important; max-width: 1400px; }

  /* HEADER BANNER */
  .mcc-header {
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid #1e2d3d; padding-bottom: 16px; margin-bottom: 24px;
    flex-wrap: wrap; gap: 12px;
  }
  .mcc-logo {
    font-family: 'Space Mono', monospace; font-size: 24px; letter-spacing: 4px;
    color: #00d4ff; text-shadow: 0 0 30px rgba(0,212,255,0.4);
  }
  .mcc-logo span { color: #e8f4fc; }
  .regime-badge {
    font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700;
    letter-spacing: 2px; padding: 6px 14px; border-radius: 2px;
    color: #ffd166; border: 1px solid #ffd166;
    background: rgba(255,209,102,0.08); box-shadow: 0 0 15px rgba(255,209,102,0.2);
  }

  /* SECTION HEADERS */
  .section-hdr {
    display: flex; align-items: baseline; gap: 14px;
    border-bottom: 1px solid #1e2d3d; padding-bottom: 8px; margin: 28px 0 16px 0;
  }
  .sec-num { font-family: 'Space Mono', monospace; font-size: 28px; color: #1e2d3d; line-height:1; }
  .sec-title { font-family: 'Space Mono', monospace; font-size: 14px; letter-spacing: 3px; color: #8aa4b8; }
  .sec-sub { font-family: 'Space Mono', monospace; font-size: 10px; color: #4a6278; margin-left: auto; }

  /* CARDS */
  .card {
    background: #0d1219; border: 1px solid #1e2d3d; border-radius: 4px;
    padding: 18px; position: relative; overflow: hidden; height: 100%;
  }
  .card-top-cyan { border-top: 2px solid #00d4ff; }
  .card-top-green { border-top: 2px solid #00ff88; }
  .card-top-red { border-top: 2px solid #ff3b5c; }
  .card-top-yellow { border-top: 2px solid #ffd166; }

  .card-label {
    font-family: 'Space Mono', monospace; font-size: 9px; letter-spacing: 2px;
    color: #4a6278; text-transform: uppercase; margin-bottom: 8px;
  }
  .card-value { font-family: 'Space Mono', monospace; font-size: 32px; color: #e8f4fc; line-height: 1; margin-bottom: 6px; }
  .card-value-sm { font-size: 22px !important; }

  /* TAGS */
  .tag { font-family: 'Space Mono', monospace; font-size: 9px; padding: 2px 8px;
         border-radius: 2px; font-weight: 700; letter-spacing: 1px; display: inline-block; }
  .tag-red    { background: rgba(255,59,92,0.15);  color: #ff3b5c; border: 1px solid rgba(255,59,92,0.3); }
  .tag-green  { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
  .tag-yellow { background: rgba(255,209,102,0.15); color: #ffd166; border: 1px solid rgba(255,209,102,0.3); }
  .tag-cyan   { background: rgba(0,212,255,0.15); color: #00d4ff; border: 1px solid rgba(0,212,255,0.3); }

  /* SEMAPHORE */
  .sema-item {
    background: #0d1219; border: 1px solid #1e2d3d; border-radius: 4px;
    padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; gap: 12px;
  }
  .sema-name { font-size: 12px; font-weight: 600; color: #c8dce8; }
  .sema-val  { font-family: 'Space Mono', monospace; font-size: 13px; font-weight: 700; margin-top: 2px; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; display: inline-block; }
  .dot-green  { background: #00ff88; box-shadow: 0 0 8px #00ff88; }
  .dot-yellow { background: #ffd166; box-shadow: 0 0 8px #ffd166; }
  .dot-red    { background: #ff3b5c; box-shadow: 0 0 8px #ff3b5c; }

  /* NOTES */
  .note-blue { background: rgba(0,212,255,0.04); border: 1px solid rgba(0,212,255,0.15);
               border-left: 3px solid #00d4ff; border-radius: 2px; padding: 14px 18px;
               font-size: 13px; color: #8aa4b8; line-height: 1.6; margin-top: 12px; }
  .note-warn { background: rgba(255,209,102,0.04); border: 1px solid rgba(255,209,102,0.15);
               border-left: 3px solid #ffd166; border-radius: 2px; padding: 14px 18px;
               font-size: 13px; color: #8aa4b8; line-height: 1.6; margin-top: 12px; }

  /* SIGNAL BADGES */
  .sig { font-family:'Space Mono',monospace; font-size:10px; font-weight:700;
         padding:6px 10px; border-radius:2px; letter-spacing:1px; display:inline-block; }
  .sig-over    { background:rgba(0,255,136,0.12);  color:#00ff88; border:1px solid rgba(0,255,136,0.25); }
  .sig-neutral { background:rgba(255,209,102,0.12);color:#ffd166; border:1px solid rgba(255,209,102,0.25); }
  .sig-under   { background:rgba(255,59,92,0.12);  color:#ff3b5c; border:1px solid rgba(255,59,92,0.25); }
  .sig-avoid   { background:rgba(255,59,92,0.2);   color:#ff3b5c; border:1px solid rgba(255,59,92,0.4); }
  .sig-watch   { background:rgba(0,212,255,0.12);  color:#00d4ff; border:1px solid rgba(0,212,255,0.25); }

  /* INDEX CARD */
  .idx-card {
    background: #0d1219; border: 1px solid #1e2d3d; border-radius: 4px; padding: 16px;
  }
  .idx-name  { font-family:'Space Mono',monospace; font-size:9px; letter-spacing:2px; color:#4a6278; margin-bottom:4px; }
  .idx-value { font-family:'Space Mono',monospace; font-size:26px; color:#e8f4fc; line-height:1; }
  .ma-above { background:rgba(0,255,136,0.1);  color:#00ff88; border:1px solid rgba(0,255,136,0.25);
              font-family:'Space Mono',monospace; font-size:9px; padding:3px 8px; border-radius:2px; display:inline-block; margin:3px 2px 0 0; }
  .ma-below { background:rgba(255,59,92,0.1);  color:#ff3b5c; border:1px solid rgba(255,59,92,0.25);
              font-family:'Space Mono',monospace; font-size:9px; padding:3px 8px; border-radius:2px; display:inline-block; margin:3px 2px 0 0; }

  /* GAUGE BAR */
  .gauge-track { height:4px; background:#111820; border-radius:2px; overflow:hidden; margin-top:6px; }
  .gauge-fill  { height:100%; border-radius:2px; }

  /* AI PANEL */
  .ai-panel { background:#080c10; border:1px solid #1e2d3d; border-radius:4px; overflow:hidden; }
  .ai-header {
    background:#0d1219; border-bottom:1px solid #1e2d3d; padding:10px 18px;
    display:flex; align-items:center; gap:10px;
    font-family:'Space Mono',monospace; font-size:9px; color:#4a6278; letter-spacing:2px;
  }
  .ai-dot { width:6px; height:6px; border-radius:50%; background:#00ff88; box-shadow:0 0 8px #00ff88; display:inline-block; }
  .ai-body { padding:22px; font-size:13px; line-height:1.75; color:#c8dce8; white-space:pre-wrap; min-height:180px; }

  /* EVENT LIST */
  .event-item {
    background:#0d1219; border:1px solid #1e2d3d; border-radius:4px;
    padding:10px 14px; display:flex; align-items:center; gap:14px; margin-bottom:8px;
  }
  .event-date { font-family:'Space Mono',monospace; font-size:11px; color:#00d4ff; min-width:80px; }
  .event-name { font-size:13px; font-weight:500; color:#c8dce8; }
  .impact-high { margin-left:auto; font-family:'Space Mono',monospace; font-size:8px; padding:3px 7px;
                 border-radius:2px; background:rgba(255,59,92,0.15); color:#ff3b5c; border:1px solid rgba(255,59,92,0.3); }

  /* TABLES */
  .mcc-table { width:100%; border-collapse:collapse; font-size:12px; }
  .mcc-table th { font-family:'Space Mono',monospace; font-size:8px; letter-spacing:2px; color:#4a6278;
                  padding:8px 12px; text-align:left; border-bottom:1px solid #1e2d3d; background:#080c10; }
  .mcc-table td { padding:10px 12px; border-bottom:1px solid rgba(30,45,61,0.5); color:#c8dce8; }
  .mcc-table tr:hover td { background:rgba(0,212,255,0.03); }

  /* POSITION ROW */
  .pos-row {
    display:flex; align-items:center; gap:12px; padding:10px 0;
    border-bottom:1px solid rgba(30,45,61,0.5);
  }
  .pos-asset  { flex:1; font-weight:500; font-size:13px; }
  .pos-detail { font-size:11px; color:#8aa4b8; margin-top:2px; }

  /* STATUS BAR */
  .status-bar {
    background:#0d1219; border-top:1px solid #1e2d3d; padding:8px 16px;
    font-family:'Space Mono',monospace; font-size:9px; color:#4a6278;
    letter-spacing:1px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;
    margin-top:40px;
  }

  /* Streamlit button override */
  .stButton > button {
    background:transparent !important; border:1px solid #00d4ff !important;
    color:#00d4ff !important; font-family:'Space Mono',monospace !important;
    font-size:11px !important; letter-spacing:1px !important;
    border-radius:2px !important; padding:8px 18px !important;
    transition:all 0.2s !important;
  }
  .stButton > button:hover { background:rgba(0,212,255,0.1) !important; }

  /* Streamlit text_area */
  .stTextArea textarea {
    background:#080c10 !important; color:#c8dce8 !important;
    border:1px solid #1e2d3d !important; font-family:'Space Mono',monospace !important;
    font-size:12px !important;
  }
  .stTextInput input {
    background:#080c10 !important; color:#c8dce8 !important;
    border:1px solid #1e2d3d !important; font-family:'Space Mono',monospace !important;
  }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def section(num: str, title: str, sub: str = ""):
    sub_html = f'<span class="sec-sub">{sub}</span>' if sub else ""
    st.markdown(
        f'<div class="section-hdr"><span class="sec-num">{num}</span>'
        f'<span class="sec-title">{title}</span>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def sema_item(name, value, dot_color):
    return f"""
    <div class="sema-item">
      <div><div class="sema-name">{name}</div>
           <div class="sema-val" style="color:{'#ffd166' if dot_color=='yellow' else ('#ff3b5c' if dot_color=='red' else '#00ff88')}">{value}</div>
      </div>
      <span class="dot dot-{dot_color}"></span>
    </div>"""


# ── HEADER ────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%A %d %B %Y · %H:%M").upper()

st.markdown(f"""
<div class="mcc-header">
  <div class="mcc-logo">MARKET <span>COMMAND CENTER</span></div>
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
    <span style="font-family:'Space Mono',monospace;font-size:10px;color:#4a6278">
      ÚLTIMA ACT: <strong style="color:#00d4ff">{now_str}</strong>
    </span>
    <span class="regime-badge">⚠ STAGFLATION SUAVE</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── 01 SEMÁFORO MACRO ─────────────────────────────────────────────────────────
section("01", "SEMÁFORO MACRO", "RÉGIMEN DE MERCADO")

sema_data = [
    ("UST 10Y Yield",        "4.08%",        "yellow"),
    ("UST 2Y Yield",         "3.48%",        "green"),
    ("Spread 2s10s",         "+0.60%",       "green"),
    ("CPI Headline (ene'26)","2.4% YoY",     "yellow"),
    ("Core CPI (ene'26)",    "2.5% YoY",     "yellow"),
    ("Core PCE (dic'25)",    "~3.0% YoY",    "red"),
    ("PIB Q4 2025 (anualiz.)","1.4%",        "red"),
    ("Fed Funds Rate",       "4.25–4.50%",   "yellow"),
]

cols = st.columns(4)
for i, (name, value, dot) in enumerate(sema_data):
    with cols[i % 4]:
        st.markdown(sema_item(name, value, dot), unsafe_allow_html=True)

st.markdown("""
<div class="note-warn">
  <strong style="color:#ffd166">⚠ Diagnóstico de Régimen: ESTANFLACIÓN SUAVE ("Stagflite")</strong><br>
  PIB Q4 al 1.4% (estimado consenso 3.0%) + Core PCE al ~3.0% (sobre objetivo Fed) = sin espacio para
  recortes agresivos. La normalización de la curva 2s10s desde inversión histórica es estadísticamente el
  período de mayor riesgo de recesión (re-steepening pre-recesivo). Próximo CPI:
  <strong style="color:#ffd166">11 de marzo 2026</strong>.
</div>
""", unsafe_allow_html=True)


# ── 02 VALORACIÓN ─────────────────────────────────────────────────────────────
section("02", "INDICADORES DE VALORACIÓN", "S&P 500 | MÚLTIPLOS Y RIESGO")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("""
    <div class="card card-top-red">
      <div class="card-label">Forward P/E S&P 500</div>
      <div class="card-value">21.5x</div>
      <div><span class="tag tag-red">CARO</span>&nbsp;<span style="font-size:11px;color:#8aa4b8">Media 10a: 18.8x</span></div>
      <div class="gauge-track" style="margin-top:14px">
        <div class="gauge-fill" style="width:72%;background:linear-gradient(90deg,#00ff88,#ffd166,#ff3b5c)"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-family:'Space Mono',monospace;font-size:8px;color:#4a6278;margin-top:3px">
        <span>BARATO</span><span>PERCENTIL 72</span><span>BURBUJA</span>
      </div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card card-top-yellow">
      <div class="card-label">Equity Risk Premium</div>
      <div class="card-value card-value-sm">~0.57%</div>
      <div><span class="tag tag-red">MÍNIMO</span>&nbsp;<span style="font-size:11px;color:#8aa4b8">Hist. ~3.5%</span></div>
      <div class="note-blue" style="font-size:10px;padding:7px 9px;margin-top:10px">
        Earnings Yield (4.65%) − UST10Y (4.08%) = renta fija compite con bolsa
      </div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="card card-top-cyan">
      <div class="card-label">EPS Growth Estimado CY26</div>
      <div class="card-value" style="color:#00ff88">+14.4%</div>
      <div><span class="tag tag-green">POSITIVO</span>&nbsp;<span style="font-size:11px;color:#8aa4b8">EPS 2026E: ~$304</span></div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="card card-top-yellow">
      <div class="card-label">Media P/E 10 años</div>
      <div class="card-value card-value-sm">18.8x</div>
      <div><span class="tag tag-yellow">REFERENCIA</span>&nbsp;<span style="font-size:11px;color:#8aa4b8">+2.7x sobre media</span></div>
    </div>""", unsafe_allow_html=True)

st.markdown("""
<div class="note-blue">
  <strong style="color:#e8f4fc">Lectura crítica:</strong> El mercado cotiza en el percentil 72 de valoración
  (10 años). Con ERP en mínimos (~0.57% ajustado), la renta fija corta al 4.5%+ compite directamente con la
  bolsa por primera vez en 15 años. La única justificación de estas valoraciones es el crecimiento de
  beneficios del +14.4%. Si el ciclo de earnings decepciona, el riesgo de compresión de múltiplos es real.
</div>
""", unsafe_allow_html=True)


# ── 03 SENTIMIENTO ────────────────────────────────────────────────────────────
section("03", "PULSO DE SENTIMIENTO", "FEAR & GREED | VIX | CRIPTO")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="card card-top-yellow">
      <div class="card-label">CNN Fear &amp; Greed (Equities)</div>
      <div style="text-align:center;padding:8px 0">
        <div style="font-family:'Space Mono',monospace;font-size:56px;color:#ffd166;line-height:1">35</div>
        <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;color:#ffd166;margin-bottom:12px">FEAR</div>
      </div>
      <div class="gauge-track">
        <div class="gauge-fill" style="width:35%;background:linear-gradient(90deg,#00ff88,#ffd166,#ff3b5c)"></div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:4px">
        <span style="font-family:'Space Mono',monospace;font-size:8px;color:#00ff88">0 FEAR</span>
        <span style="font-family:'Space Mono',monospace;font-size:8px;color:#ff3b5c">100 GREED</span>
      </div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card card-top-cyan">
      <div class="card-label">VIX (Volatility Index)</div>
      <div style="text-align:center;padding:8px 0">
        <div style="font-family:'Space Mono',monospace;font-size:56px;color:#00d4ff;line-height:1">19.09</div>
        <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;color:#00d4ff;margin-bottom:12px">MODERADO / EN ALZA</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
        <div style="font-size:10px;color:#4a6278">52W High <span style="color:#ff3b5c;font-family:'Space Mono',monospace">60.13</span></div>
        <div style="font-size:10px;color:#4a6278">52W Low <span style="color:#00ff88;font-family:'Space Mono',monospace">13.38</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="card card-top-red">
      <div class="card-label">Crypto Fear &amp; Greed (BTC)</div>
      <div style="text-align:center;padding:8px 0">
        <div style="font-family:'Space Mono',monospace;font-size:56px;color:#ff3b5c;line-height:1">5</div>
        <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;color:#ff3b5c;margin-bottom:12px">EXTREME FEAR</div>
      </div>
      <div class="gauge-track">
        <div class="gauge-fill" style="width:5%;background:#ff3b5c"></div>
      </div>
      <div style="margin-top:10px;font-family:'Space Mono',monospace;font-size:9px;color:#4a6278">
        BTC: <span style="color:#ff3b5c">~$65,000</span> · –49% del ATH ($126K)
      </div>
    </div>""", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="card" style="margin-top:12px">
      <div class="card-label">Sentimiento Tech (Post-DeepSeek)</div>
      <div style="margin-top:8px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span style="font-size:12px">IA / Semiconductores</span><span class="tag tag-yellow">CAUTELOSO</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span style="font-size:12px">Megacaps IA (NVDA, META)</span><span class="tag tag-yellow">MIXTO</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-size:12px">ROI capex IA en debate</span><span class="tag tag-red">NEGATIVO</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card" style="margin-top:12px">
      <div class="card-label">BTC On-Chain &amp; Derivados</div>
      <div style="margin-top:8px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span style="font-size:12px">Open Interest Futuros BTC</span>
          <span style="font-family:'Space Mono',monospace;font-size:12px;color:#ff3b5c">$19.5B ↓</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span style="font-size:12px">Caída 30 días</span>
          <span style="font-family:'Space Mono',monospace;font-size:12px;color:#ff3b5c">-27%</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-size:12px">Put/Call Ratio BTC</span><span class="tag tag-red">ELEVADO (BEARISH)</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


# ── 04 MOMENTUM ───────────────────────────────────────────────────────────────
section("04", "FLUJOS Y MOMENTUM", "MEDIAS MÓVILES 50D / 200D")

indices = [
    ("S&P 500",     "6,881",  "color:#e8f4fc",
     '<span class="ma-below">MM50: 6,895 ↓</span><span class="ma-above">MM200: 6,517 ↑</span>',
     "-0.2% vs MM50 | +5.6% vs MM200"),
    ("NASDAQ 100",  "~21,400","color:#e8f4fc",
     '<span class="ma-below">MM50: ~21,700 ↓</span><span class="ma-above">MM200: ~20,100 ↑</span>',
     "Consolidación post-DeepSeek"),
    ("IBEX 35 ⭐",  "18,186", "color:#00ff88",
     '<span class="ma-above">MM50: 13,840 ↑</span><span class="ma-above">MM200: 12,890 ↑</span>',
     "+31.5% YTD · Outperformer global"),
    ("STOXX 600",   "~560",   "color:#e8f4fc",
     '<span class="ma-above">MM50: ↑</span><span class="ma-above">MM200: ↑</span>',
     "Defensiva europea en alza"),
]

cols = st.columns(4)
for col, (name, value, vstyle, ma_html, note) in zip(cols, indices):
    with col:
        border = "border-color:rgba(0,255,136,0.3)" if "⭐" in name else ""
        st.markdown(f"""
        <div class="idx-card" style="{border}">
          <div class="idx-name" style="{'color:#00ff88' if '⭐' in name else ''}">{name}</div>
          <div class="idx-value" style="{vstyle}">{value}</div>
          <div style="margin-top:8px">{ma_html}</div>
          <div style="margin-top:8px;font-size:10px;color:#4a6278">{note}</div>
        </div>""", unsafe_allow_html=True)


# ── 05 POSICIONAMIENTO ────────────────────────────────────────────────────────
section("05", "POSICIONAMIENTO SUGERIDO", "ASSET ALLOCATION | SEÑALES")

positions_left = [
    ("💵 Liquidez / Money Market", "USD, EUR · Remunerado 4.5%+", "sig-over",  "SOBREPONDERAR"),
    ("📊 Renta Fija Corta (< 2Y)", "T-Bills, Letras Tesoro",      "sig-over",  "SOBREPONDERAR"),
    ("🇪🇸 IBEX 35 / Europa",       "Momentum + valoración rel.",  "sig-over",  "ACUMULAR"),
    ("🌍 S&P 500 (Diversificado)", "Blue chips, no concentrado",  "sig-neutral","MANTENER"),
]
positions_right = [
    ("📉 Nasdaq 100 / Growth Tech","Alta volatilidad macro",      "sig-under",  "INFRAPONDERAR"),
    ("₿ Cripto (BTC/ETH)",         "Capitulación en curso",       "sig-avoid",  "EVITAR"),
    ("🥇 Oro (XAU/USD)",           "Hedge inflación / USD",       "sig-watch",  "VIGILAR"),
    ("🛢️ Petróleo / Commodities",  "Incertidumbre geopolítica",  "sig-neutral","NEUTRO"),
]

c1, c2 = st.columns(2)
for col, positions in [(c1, positions_left), (c2, positions_right)]:
    with col:
        for asset, detail, sig_class, sig_label in positions:
            st.markdown(f"""
            <div class="pos-row">
              <div style="flex:1">
                <div class="pos-asset">{asset}</div>
                <div class="pos-detail">{detail}</div>
              </div>
              <span class="sig {sig_class}">{sig_label}</span>
            </div>""", unsafe_allow_html=True)


# ── 06 OTROS INDICADORES ──────────────────────────────────────────────────────
section("06", "RADAR DE OTROS INDICADORES", "MACRO ADICIONAL | CALENDARIO")

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <table class="mcc-table" style="background:#0d1219;border:1px solid #1e2d3d;border-radius:4px">
      <thead><tr><th>INDICADOR</th><th>VALOR / ESTADO</th><th>SEÑAL</th></tr></thead>
      <tbody>
        <tr><td>DXY (Dólar Index)</td><td style="font-family:'Space Mono',monospace;font-size:11px">Semana alcista</td><td><span class="tag tag-yellow">VIGILAR</span></td></tr>
        <tr><td>Oro (XAU/USD)</td><td style="font-family:'Space Mono',monospace;font-size:11px">Cerca ATH</td><td><span class="tag tag-green">HEDGE ACTIVO</span></td></tr>
        <tr><td>Petróleo (WTI)</td><td style="font-family:'Space Mono',monospace;font-size:11px">~$70</td><td><span class="tag tag-yellow">NEUTRO</span></td></tr>
        <tr><td>High Yield Spreads</td><td style="font-family:'Space Mono',monospace;font-size:11px">~3.0%</td><td><span class="tag tag-green">TRANQUILO</span></td></tr>
        <tr><td>Curva 10Y-3M</td><td style="font-family:'Space Mono',monospace;font-size:11px">~0 (limbo)</td><td><span class="tag tag-red">RECESIÓN WATCH</span></td></tr>
        <tr><td>AAII Sentiment</td><td style="font-family:'Space Mono',monospace;font-size:11px">Bajista (retail)</td><td><span class="tag tag-cyan">CONTRARIAN BUY?</span></td></tr>
        <tr><td>Earnings Revision</td><td style="font-family:'Space Mono',monospace;font-size:11px">Ligeramente neg.</td><td><span class="tag tag-yellow">VIGILAR</span></td></tr>
        <tr><td>Trade Deficit USA dic'25</td><td style="font-family:'Space Mono',monospace;font-size:11px">$70.3B (récord)</td><td><span class="tag tag-red">RIESGO USD L/P</span></td></tr>
      </tbody>
    </table>""", unsafe_allow_html=True)

with c2:
    events = [
        ("28 FEB",   "PCE Core (enero 2026)"),
        ("11 MAR",   "CPI Febrero 2026"),
        ("18-19 MAR","FOMC Meeting (Fed)"),
        ("28 MAR",   "PCE Core (febrero 2026)"),
        ("ABR 2026", "Q1 Earnings Season"),
        ("ONGOING",  "Decisión aranceles Trump (15% global)"),
    ]
    st.markdown('<div class="card-label" style="font-family:\'Space Mono\',monospace;font-size:9px;letter-spacing:2px;color:#4a6278;margin-bottom:10px">PRÓXIMOS CATALIZADORES CLAVE</div>', unsafe_allow_html=True)
    for date, name in events:
        st.markdown(f"""
        <div class="event-item">
          <span class="event-date">{date}</span>
          <span class="event-name">{name}</span>
          <span class="impact-high">ALTO IMPACTO</span>
        </div>""", unsafe_allow_html=True)


# ── 07 ANÁLISIS IA ────────────────────────────────────────────────────────────
section("07", "ANÁLISIS IA EN TIEMPO REAL", "GENERADO POR CLAUDE · ACTUALIZABLE")

DEFAULT_ANALYSIS = """El mercado en este momento es un campo de minas con aspecto de césped. La superficie (S&P 500 a -1% del ATH, curva positiva, inflación bajando) parece relativamente benigna. Pero debajo: aranceles inflacionarios, Fed sin margen, valoraciones ajustadas, cripto en capitulación y crecimiento estancado.

No es momento de aumentar agresivamente riesgo. La liquidez remunerada al 4.5% y la renta fija corta son opciones respetables mientras se espera mayor claridad macro. El IBEX 35 es la excepción positiva por momentum y valoración relativa.

▸ SEMÁFORO FINAL DE DECISIÓN:
  ❌ ¿Aumentar Riesgo Agresivo (Nasdaq, Cripto)? → NO
  🟡 ¿Mantener Renta Variable Diversificada? → NEUTRAL
  ✅ ¿Sobreponderar Liquidez + RF Corta? → SÍ
  ✅ ¿Acumular IBEX / Europa en correcciones? → SÍ

Pulsa "↻ ACTUALIZAR CON IA" para obtener el análisis más reciente."""

if "ai_analysis" not in st.session_state:
    st.session_state.ai_analysis = DEFAULT_ANALYSIS
if "ai_timestamp" not in st.session_state:
    st.session_state.ai_timestamp = "Cargado: " + datetime.now().strftime("%d/%m/%Y %H:%M")

ts = st.session_state.ai_timestamp
st.markdown(f"""
<div class="ai-panel">
  <div class="ai-header">
    <span class="ai-dot"></span>
    <span>CLAUDE MARKET ANALYST</span>
    <span style="margin-left:auto">{ts}</span>
  </div>
  <div class="ai-body">{st.session_state.ai_analysis}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

if st.button("↻ ACTUALIZAR CON IA"):
    today = datetime.now().strftime("%A %d %B %Y")
    prompt = f"""Eres un Senior Investment Strategist. Hoy es {today}.

Proporciona un análisis de mercado CONCISO y ACTUALIZADO en español con los siguientes datos clave:

1. **RÉGIMEN MACRO** (1-2 frases): ¿Expansión, Estanflación o Recesión?

2. **VALORACIÓN S&P 500** (1-2 frases): Forward P/E, ERP y si las valoraciones justifican el riesgo.

3. **SENTIMIENTO** (1-2 frases): Señales de Fear & Greed, VIX y comportamiento cripto.

4. **MOMENTUM** (1-2 frases): Estado técnico S&P 500, Nasdaq e IBEX 35 respecto a sus medias móviles.

5. **VEREDICTO FINAL** (3-5 frases directas y críticas): ¿Debe el inversor aumentar exposición al riesgo, mantenerse neutral o refugiarse en liquidez/renta fija?

Formato: texto fluido, profesional y directo. Máximo 300 palabras. Termina con:
"▸ SEÑAL: [RISK-ON / NEUTRO / RISK-OFF] — [razón de 10 palabras]" """

    with st.spinner("⠋ ANALIZANDO CONDICIONES DE MERCADO..."):
        try:
            client = anthropic.Anthropic()
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            st.session_state.ai_analysis = message.content[0].text
            st.session_state.ai_timestamp = "Actualizado: " + datetime.now().strftime("%d/%m/%Y %H:%M")
            st.rerun()
        except Exception as e:
            st.error(f"⚠ Error al conectar con la API: {e}")


# ── STATUS BAR ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="status-bar">
  <div style="display:flex;gap:20px;flex-wrap:wrap">
    <span>🟢 DASHBOARD ACTIVO</span>
    <span>🟡 DATOS: ÚLTIMA SESIÓN DISPONIBLE (11-MAR-2026)</span>
  </div>
  <span>MARKET COMMAND CENTER · INVERSOR PARTICULAR · DATOS NO CONSTITUYEN ASESORAMIENTO FINANCIERO</span>
</div>
""", unsafe_allow_html=True)
