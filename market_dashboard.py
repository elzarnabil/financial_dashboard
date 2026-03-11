"""
Market Command Center — Streamlit Edition
Fuentes de datos gratuitas:
  · Yahoo Finance (yfinance)   → Índices, VIX, oro, petróleo, BTC, yields
  · FRED (CSV público)         → CPI, PCE, GDP, Fed Funds, Spreads, HY
  · alternative.me API         → Crypto Fear & Greed Index
  · CNN Fear & Greed API       → Equity Fear & Greed
"""

import streamlit as st
import anthropic
import requests
from datetime import datetime

try:
    import yfinance as yf
    YF_OK = True
except ImportError:
    YF_OK = False

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
  html, body, [class*="css"], .stApp {
    background-color: #080c10 !important; color: #c8dce8 !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 1.5rem 2rem 4rem 2rem !important; max-width: 1400px; }

  .mcc-header { display:flex; align-items:center; justify-content:space-between;
    border-bottom:1px solid #1e2d3d; padding-bottom:16px; margin-bottom:24px; flex-wrap:wrap; gap:12px; }
  .mcc-logo { font-family:'Space Mono',monospace; font-size:24px; letter-spacing:4px;
    color:#00d4ff; text-shadow:0 0 30px rgba(0,212,255,0.4); }
  .mcc-logo span { color:#e8f4fc; }
  .regime-badge { font-family:'Space Mono',monospace; font-size:11px; font-weight:700;
    letter-spacing:2px; padding:6px 14px; border-radius:2px; color:#ffd166;
    border:1px solid #ffd166; background:rgba(255,209,102,0.08); box-shadow:0 0 15px rgba(255,209,102,0.2); }

  .section-hdr { display:flex; align-items:baseline; gap:14px;
    border-bottom:1px solid #1e2d3d; padding-bottom:8px; margin:28px 0 16px 0; }
  .sec-num { font-family:'Space Mono',monospace; font-size:28px; color:#1e2d3d; line-height:1; }
  .sec-title { font-family:'Space Mono',monospace; font-size:14px; letter-spacing:3px; color:#8aa4b8; }
  .sec-sub { font-family:'Space Mono',monospace; font-size:10px; color:#4a6278; margin-left:auto; }

  .card { background:#0d1219; border:1px solid #1e2d3d; border-radius:4px; padding:18px; }
  .card-top-cyan   { border-top:2px solid #00d4ff; }
  .card-top-green  { border-top:2px solid #00ff88; }
  .card-top-red    { border-top:2px solid #ff3b5c; }
  .card-top-yellow { border-top:2px solid #ffd166; }
  .card-label { font-family:'Space Mono',monospace; font-size:9px; letter-spacing:2px;
    color:#4a6278; text-transform:uppercase; margin-bottom:8px; }
  .card-value { font-family:'Space Mono',monospace; font-size:32px; color:#e8f4fc; line-height:1; margin-bottom:6px; }
  .card-value-sm { font-size:22px !important; }

  .tag { font-family:'Space Mono',monospace; font-size:9px; padding:2px 8px;
    border-radius:2px; font-weight:700; letter-spacing:1px; display:inline-block; }
  .tag-red    { background:rgba(255,59,92,0.15);   color:#ff3b5c; border:1px solid rgba(255,59,92,0.3); }
  .tag-green  { background:rgba(0,255,136,0.15);  color:#00ff88; border:1px solid rgba(0,255,136,0.3); }
  .tag-yellow { background:rgba(255,209,102,0.15);color:#ffd166; border:1px solid rgba(255,209,102,0.3); }
  .tag-cyan   { background:rgba(0,212,255,0.15);  color:#00d4ff; border:1px solid rgba(0,212,255,0.3); }

  .sema-item { background:#0d1219; border:1px solid #1e2d3d; border-radius:4px;
    padding:12px 16px; display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:8px; }
  .sema-name { font-size:12px; font-weight:600; color:#c8dce8; }
  .sema-val  { font-family:'Space Mono',monospace; font-size:13px; font-weight:700; margin-top:2px; }
  .dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; display:inline-block; }
  .dot-green  { background:#00ff88; box-shadow:0 0 8px #00ff88; }
  .dot-yellow { background:#ffd166; box-shadow:0 0 8px #ffd166; }
  .dot-red    { background:#ff3b5c; box-shadow:0 0 8px #ff3b5c; }

  .note-blue { background:rgba(0,212,255,0.04); border:1px solid rgba(0,212,255,0.15);
    border-left:3px solid #00d4ff; border-radius:2px; padding:14px 18px;
    font-size:13px; color:#8aa4b8; line-height:1.6; margin-top:12px; }
  .note-warn { background:rgba(255,209,102,0.04); border:1px solid rgba(255,209,102,0.15);
    border-left:3px solid #ffd166; border-radius:2px; padding:14px 18px;
    font-size:13px; color:#8aa4b8; line-height:1.6; margin-top:12px; }

  .sig { font-family:'Space Mono',monospace; font-size:10px; font-weight:700;
    padding:6px 10px; border-radius:2px; letter-spacing:1px; display:inline-block; }
  .sig-over    { background:rgba(0,255,136,0.12);  color:#00ff88; border:1px solid rgba(0,255,136,0.25); }
  .sig-neutral { background:rgba(255,209,102,0.12);color:#ffd166; border:1px solid rgba(255,209,102,0.25); }
  .sig-under   { background:rgba(255,59,92,0.12);  color:#ff3b5c; border:1px solid rgba(255,59,92,0.25); }
  .sig-avoid   { background:rgba(255,59,92,0.2);   color:#ff3b5c; border:1px solid rgba(255,59,92,0.4); }
  .sig-watch   { background:rgba(0,212,255,0.12);  color:#00d4ff; border:1px solid rgba(0,212,255,0.25); }

  .idx-card { background:#0d1219; border:1px solid #1e2d3d; border-radius:4px; padding:16px; }
  .idx-name  { font-family:'Space Mono',monospace; font-size:9px; letter-spacing:2px; color:#4a6278; margin-bottom:4px; }
  .idx-value { font-family:'Space Mono',monospace; font-size:26px; color:#e8f4fc; line-height:1; }
  .ma-above { background:rgba(0,255,136,0.1); color:#00ff88; border:1px solid rgba(0,255,136,0.25);
    font-family:'Space Mono',monospace; font-size:9px; padding:3px 8px; border-radius:2px; display:inline-block; margin:3px 2px 0 0; }
  .ma-below { background:rgba(255,59,92,0.1); color:#ff3b5c; border:1px solid rgba(255,59,92,0.25);
    font-family:'Space Mono',monospace; font-size:9px; padding:3px 8px; border-radius:2px; display:inline-block; margin:3px 2px 0 0; }

  .gauge-track { height:4px; background:#111820; border-radius:2px; overflow:hidden; margin-top:6px; }
  .gauge-fill  { height:100%; border-radius:2px; }

  .ai-panel { background:#080c10; border:1px solid #1e2d3d; border-radius:4px; overflow:hidden; }
  .ai-header { background:#0d1219; border-bottom:1px solid #1e2d3d; padding:10px 18px;
    display:flex; align-items:center; gap:10px; font-family:'Space Mono',monospace; font-size:9px; color:#4a6278; letter-spacing:2px; }
  .ai-dot { width:6px; height:6px; border-radius:50%; background:#00ff88; box-shadow:0 0 8px #00ff88; display:inline-block; }
  .ai-body { padding:22px; font-size:13px; line-height:1.75; color:#c8dce8; white-space:pre-wrap; min-height:180px; }

  .event-item { background:#0d1219; border:1px solid #1e2d3d; border-radius:4px;
    padding:10px 14px; display:flex; align-items:center; gap:14px; margin-bottom:8px; }
  .event-date { font-family:'Space Mono',monospace; font-size:11px; color:#00d4ff; min-width:80px; }
  .event-name { font-size:13px; font-weight:500; color:#c8dce8; }
  .impact-high { margin-left:auto; font-family:'Space Mono',monospace; font-size:8px; padding:3px 7px;
    border-radius:2px; background:rgba(255,59,92,0.15); color:#ff3b5c; border:1px solid rgba(255,59,92,0.3); }

  .mcc-table { width:100%; border-collapse:collapse; font-size:12px; }
  .mcc-table th { font-family:'Space Mono',monospace; font-size:8px; letter-spacing:2px; color:#4a6278;
    padding:8px 12px; text-align:left; border-bottom:1px solid #1e2d3d; background:#080c10; }
  .mcc-table td { padding:10px 12px; border-bottom:1px solid rgba(30,45,61,0.5); color:#c8dce8; }

  .pos-row { display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid rgba(30,45,61,0.5); }
  .pos-asset  { flex:1; font-weight:500; font-size:13px; }
  .pos-detail { font-size:11px; color:#8aa4b8; margin-top:2px; }

  .src { font-family:'Space Mono',monospace; font-size:8px; padding:1px 5px; border-radius:2px;
    background:rgba(0,212,255,0.08); color:#00d4ff; border:1px solid rgba(0,212,255,0.2); display:inline-block; margin-left:5px; }

  .status-bar { background:#0d1219; border-top:1px solid #1e2d3d; padding:8px 16px;
    font-family:'Space Mono',monospace; font-size:9px; color:#4a6278;
    display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-top:40px; }

  .stButton > button { background:transparent !important; border:1px solid #00d4ff !important;
    color:#00d4ff !important; font-family:'Space Mono',monospace !important; font-size:11px !important;
    letter-spacing:1px !important; border-radius:2px !important; padding:8px 18px !important; }
  .stButton > button:hover { background:rgba(0,212,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  FUENTES DE DATOS GRATUITAS
# ═══════════════════════════════════════════════════════════════════════════════

def fmt(val, dec=2, prefix="", suffix=""):
    if val is None: return "—"
    try: return f"{prefix}{val:,.{dec}f}{suffix}"
    except: return "—"

def pcolor(v):
    if v is None: return "#8aa4b8"
    return "#00ff88" if v >= 0 else "#ff3b5c"

def dot_col(v, lo, hi, inv=False):
    if v is None: return "yellow"
    if not inv:
        return "red" if v >= hi else ("yellow" if v >= lo else "green")
    else:
        return "red" if v <= lo else ("yellow" if v <= hi else "green")


# ── Yahoo Finance ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_yf():
    if not YF_OK:
        return {}
    syms = {
        "SP500":"^GSPC","NDX":"^NDX","IBEX":"^IBEX","STOXX":"^STOXX",
        "VIX":"^VIX","TNX":"^TNX","IRX":"^IRX",
        "GOLD":"GC=F","OIL":"CL=F","DXY":"DX-Y.NYB","BTC":"BTC-USD",
    }
    out = {}
    try:
        raw = yf.download(list(syms.values()), period="5d", interval="1d",
                          progress=False, auto_adjust=True)
        closes = raw["Close"] if "Close" in raw.columns else raw.xs("Close", axis=1, level=0)
        for k, s in syms.items():
            try:
                sr = closes[s].dropna()
                if len(sr) >= 2:
                    out[k] = {"price": float(sr.iloc[-1]), "prev": float(sr.iloc[-2]),
                              "pct": float((sr.iloc[-1]/sr.iloc[-2]-1)*100)}
                elif len(sr) == 1:
                    out[k] = {"price": float(sr.iloc[-1]), "prev": None, "pct": None}
            except: pass

        # Moving averages (1 year)
        hist = yf.download(["^GSPC","^NDX","^IBEX","^STOXX"], period="1y",
                           interval="1d", progress=False, auto_adjust=True)
        hc = hist["Close"] if "Close" in hist.columns else hist.xs("Close", axis=1, level=0)
        for k, s in [("SP500","^GSPC"),("NDX","^NDX"),("IBEX","^IBEX"),("STOXX","^STOXX")]:
            try:
                sr = hc[s].dropna()
                if k in out:
                    out[k]["ma50"]  = float(sr.tail(50).mean())  if len(sr) >= 50  else None
                    out[k]["ma200"] = float(sr.tail(200).mean()) if len(sr) >= 200 else None
            except: pass
    except Exception as e:
        out["_err"] = str(e)
    return out


# ── FRED (CSV gratuito, sin API key) ─────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fred():
    """FRED public CSV endpoint — no API key required."""
    BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"
    sids = ["FEDFUNDS","CPILFESL","PCEPILFE","GDP","T10Y2Y","T10Y3M",
            "DGS10","DGS2","BAMLH0A0HYM2","CPIAUCSL","PCEPI"]
    out = {}
    for sid in sids:
        try:
            r = requests.get(f"{BASE}?id={sid}", timeout=10,
                             headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                for line in reversed(r.text.strip().split("\n")[1:]):
                    p = line.split(",")
                    if len(p) == 2 and p[1].strip() not in (".", ""):
                        out[sid] = {"value": float(p[1].strip()), "date": p[0].strip()}
                        break
        except: pass
    return out


# ── Crypto Fear & Greed (alternative.me) ─────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_cfg():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
        if r.status_code == 200:
            d = r.json()["data"][0]
            return {"value": int(d["value"]), "label": d["value_classification"]}
    except: pass
    return {"value": None, "label": "N/A"}


# ── CNN Fear & Greed ──────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_cnn():
    try:
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
                         timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            d = r.json()
            return {"value": round(d["fear_and_greed"]["score"]),
                    "label": d["fear_and_greed"]["rating"].upper()}
    except: pass
    return {"value": None, "label": "N/A"}


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'Space Mono\',monospace;font-size:11px;color:#00d4ff;letter-spacing:2px;margin-bottom:16px">⚙ PANEL DE CONTROL</div>', unsafe_allow_html=True)
    if st.button("🔄 Refrescar todos los datos"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("""
    <div style="font-family:'Space Mono',monospace;font-size:9px;color:#4a6278;margin-top:20px;line-height:2">
    <strong style="color:#8aa4b8">FUENTES GRATUITAS</strong><br>
    📈 <strong style="color:#c8dce8">Yahoo Finance</strong><br>
    &nbsp;&nbsp;Índices · VIX · Oro · BTC · DXY<br>
    🏦 <strong style="color:#c8dce8">FRED (St. Louis Fed)</strong><br>
    &nbsp;&nbsp;CPI · PCE · GDP · Fed Funds<br>
    &nbsp;&nbsp;Yields · HY Spreads · Curva<br>
    😱 <strong style="color:#c8dce8">alternative.me</strong><br>
    &nbsp;&nbsp;Crypto Fear &amp; Greed<br>
    📺 <strong style="color:#c8dce8">CNN API</strong><br>
    &nbsp;&nbsp;Equity Fear &amp; Greed<br><br>
    <strong style="color:#8aa4b8">CACHE</strong><br>
    5 min · Precios de mercado<br>
    60 min · Datos macro FRED
    </div>
    """, unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("⠋ CARGANDO DATOS DE MERCADO EN TIEMPO REAL..."):
    yfd    = fetch_yf()
    fred   = fetch_fred()
    cfg    = fetch_cfg()
    cnn_fg = fetch_cnn()

# ── Helper getters ────────────────────────────────────────────────────────────
def fv(sid):
    return fred.get(sid, {}).get("value")

def fd(sid):
    return fred.get(sid, {}).get("date", "")

def yp(k):
    return yfd.get(k, {}).get("price")

def ypct(k):
    return yfd.get(k, {}).get("pct")

def yma(k, n):
    return yfd.get(k, {}).get(f"ma{n}")

# Key values
ust10       = fv("DGS10")
ust2        = fv("DGS2")
spread_2s10 = fv("T10Y2Y")
spread_10_3 = fv("T10Y3M")
fed_rate    = fv("FEDFUNDS")
cpi_hl      = fv("CPIAUCSL")
core_cpi    = fv("CPILFESL")
core_pce    = fv("PCEPILFE")
gdp         = fv("GDP")
hy_sprd     = fv("BAMLH0A0HYM2")

vix   = yp("VIX")
gold  = yp("GOLD")
oil   = yp("OIL")
dxy   = yp("DXY")
btc   = yp("BTC")

sp5_p    = yp("SP500");   sp5_pct  = ypct("SP500")
ndx_p    = yp("NDX");     ndx_pct  = ypct("NDX")
ibex_p   = yp("IBEX");    ibex_pct = ypct("IBEX")
stoxx_p  = yp("STOXX");   stoxx_pct= ypct("STOXX")

cfg_val  = cfg.get("value");   cfg_lbl  = cfg.get("label", "N/A")
cnn_val  = cnn_fg.get("value");cnn_lbl  = cnn_fg.get("label", "N/A")

# Regime heuristic
if gdp and gdp < 2.0 and core_pce and core_pce > 2.5:
    regime = "⚠ STAGFLATION"
elif spread_10_3 and spread_10_3 < -0.3:
    regime = "🔴 RIESGO RECESIÓN"
elif gdp and gdp >= 2.5 and core_pce and core_pce <= 2.3:
    regime = "✅ EXPANSIÓN"
else:
    regime = "🟡 TRANSICIÓN MACRO"

# Source status
yf_ok   = bool(yfd and "_err" not in yfd)
fred_ok = bool(fred)
cfg_ok  = cfg_val is not None
cnn_ok  = cnn_val is not None

now_str = datetime.now().strftime("%A %d %B %Y · %H:%M").upper()

# ── UI HELPERS ────────────────────────────────────────────────────────────────
def sec(num, title, sub=""):
    s = f'<span class="sec-sub">{sub}</span>' if sub else ""
    st.markdown(f'<div class="section-hdr"><span class="sec-num">{num}</span><span class="sec-title">{title}</span>{s}</div>',
                unsafe_allow_html=True)

def src(name):
    return f'<span class="src">{name}</span>'

def sema(name, val, dc, source=""):
    cm = {"green":"#00ff88","yellow":"#ffd166","red":"#ff3b5c"}
    vc = cm.get(dc, "#8aa4b8")
    s = src(source) if source else ""
    return f"""<div class="sema-item">
      <div><div class="sema-name">{name}{s}</div>
           <div class="sema-val" style="color:{vc}">{val}</div></div>
      <span class="dot dot-{dc}"></span></div>"""

def ma_badge(price, ma, label):
    if not price or not ma:
        return f'<span style="font-family:\'Space Mono\',monospace;font-size:9px;color:#4a6278">{label}:—</span>'
    cls = "ma-above" if price > ma else "ma-below"
    arr = "↑" if price > ma else "↓"
    return f'<span class="{cls}">{label}:{fmt(ma,0)}{arr}</span>'

def fg_color(v):
    if v is None: return "#8aa4b8"
    if v <= 25: return "#ff3b5c"
    if v <= 45: return "#ffd166"
    if v <= 65: return "#e8f4fc"
    return "#00ff88"


# ═══════════════════════════════════════════════════════════════════════════════
#  RENDER
# ═══════════════════════════════════════════════════════════════════════════════

# HEADER
st.markdown(f"""
<div class="mcc-header">
  <div class="mcc-logo">MARKET <span>COMMAND CENTER</span></div>
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
    <span style="font-family:'Space Mono',monospace;font-size:10px;color:#4a6278">
      ACTUALIZADO: <strong style="color:#00d4ff">{now_str}</strong>
    </span>
    <span class="regime-badge">{regime}</span>
  </div>
</div>""", unsafe_allow_html=True)

# SOURCE STATUS STRIP
cs = st.columns(4)
for col, (name, ok, desc) in zip(cs, [
    ("Yahoo Finance", yf_ok,   "Índices · VIX · Oro · BTC"),
    ("FRED",          fred_ok, "CPI · PCE · GDP · Yields"),
    ("Crypto F&G",    cfg_ok,  "alternative.me API"),
    ("CNN F&G",       cnn_ok,  "CNN Fear & Greed"),
]):
    with col:
        st.markdown(f"""
        <div style="background:#0d1219;border:1px solid #1e2d3d;border-radius:4px;padding:10px 14px;margin-bottom:8px">
          <div style="font-family:'Space Mono',monospace;font-size:9px;color:#4a6278">
            {'🟢' if ok else '🔴'} {name}</div>
          <div style="font-size:11px;color:#8aa4b8;margin-top:3px">{desc}</div>
        </div>""", unsafe_allow_html=True)


# ── 01 SEMÁFORO MACRO ─────────────────────────────────────────────────────────
sec("01", "SEMÁFORO MACRO", "RÉGIMEN DE MERCADO · FRED + YAHOO")

rows = [
    ("UST 10Y Yield",   f"{fmt(ust10)}%",       dot_col(ust10, 3.5, 4.5, inv=True),  "FRED"),
    ("UST 2Y Yield",    f"{fmt(ust2)}%",         dot_col(ust2, 3.0, 4.0, inv=True),   "FRED"),
    ("Spread 2s10s",    f"{fmt(spread_2s10):+}%" if spread_2s10 else "—",
                        "green" if spread_2s10 and spread_2s10 > 0 else "red",        "FRED"),
    ("CPI Headline",    f"{fmt(cpi_hl)}% YoY",   dot_col(cpi_hl,2.0,3.0,inv=True) if cpi_hl else "yellow", "FRED"),
    ("Core CPI",        f"{fmt(core_cpi)}% YoY", dot_col(core_cpi,2.0,3.0,inv=True) if core_cpi else "yellow","FRED"),
    ("Core PCE",        f"{fmt(core_pce)}% YoY", dot_col(core_pce,2.0,3.0,inv=True) if core_pce else "yellow","FRED"),
    ("GDP (último)",    f"{fmt(gdp)}%",           dot_col(gdp,1.5,2.5,inv=True) if gdp else "yellow", "FRED"),
    ("Fed Funds Rate",  f"{fmt(fed_rate)}%",      "yellow" if fed_rate and fed_rate > 4 else "green",  "FRED"),
]
cols = st.columns(4)
for i, (n, v, dc, s) in enumerate(rows):
    with cols[i % 4]:
        st.markdown(sema(n, v, dc, s), unsafe_allow_html=True)

st.markdown(f"""
<div class="note-warn">
  <strong style="color:#ffd166">⚠ {regime}</strong>&nbsp;&nbsp;
  GDP: <strong style="color:#ffd166">{fmt(gdp)}%</strong> ·
  Core PCE: <strong style="color:#ffd166">{fmt(core_pce)}%</strong> (obj. Fed 2%) ·
  Spread 2s10s: <strong style="color:#ffd166">{fmt(spread_2s10):+}%</strong> ·
  Curva 10Y-3M: <strong style="color:#ffd166">{fmt(spread_10_3):+}%</strong>
  <br><span style="font-size:10px;color:#4a6278">Fuente: FRED (Federal Reserve Bank of St. Louis) · {fd("DGS10")}</span>
</div>""", unsafe_allow_html=True)


# ── 02 VALORACIÓN ─────────────────────────────────────────────────────────────
sec("02", "INDICADORES DE VALORACIÓN", "S&P 500 | MÚLTIPLOS · FRED+CALC")

fwd_pe = 21.5  # No hay fuente pública gratis para forward PE; se actualiza manualmente
ey = (1 / fwd_pe) * 100
erp = ey - (ust10 or 4.08)
erp_c = "#ff3b5c" if erp < 1.0 else ("#ffd166" if erp < 2.5 else "#00ff88")
erp_t = "tag-red" if erp < 1.0 else ("tag-yellow" if erp < 2.5 else "tag-green")
hy_c  = "#00ff88" if hy_sprd and hy_sprd < 4.0 else ("#ffd166" if hy_sprd and hy_sprd < 5.5 else "#ff3b5c")
hy_t  = "tag-green" if hy_sprd and hy_sprd < 4.0 else "tag-yellow"
vix_c = "#ff3b5c" if vix and vix > 25 else ("#ffd166" if vix and vix > 18 else "#00ff88")
vix_t = "tag-red" if vix and vix > 25 else "tag-yellow"

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="card card-top-red">
      <div class="card-label">Forward P/E S&P 500 {src("MANUAL")}</div>
      <div class="card-value">{fwd_pe}x</div>
      <div><span class="tag tag-red">CARO</span>&nbsp;<span style="font-size:11px;color:#8aa4b8">Media 10a: 18.8x</span></div>
      <div class="gauge-track" style="margin-top:12px">
        <div class="gauge-fill" style="width:72%;background:linear-gradient(90deg,#00ff88,#ffd166,#ff3b5c)"></div>
      </div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="card card-top-yellow">
      <div class="card-label">Equity Risk Premium {src("FRED+CALC")}</div>
      <div class="card-value card-value-sm" style="color:{erp_c}">{fmt(erp)}%</div>
      <div><span class="tag {erp_t}">ERP</span>&nbsp;<span style="font-size:11px;color:#8aa4b8">Hist. ~3.5%</span></div>
      <div class="note-blue" style="font-size:10px;padding:7px 9px;margin-top:10px">
        EY({fmt(ey)}%) − UST10Y({fmt(ust10)}%) = {fmt(erp)}%
      </div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="card card-top-cyan">
      <div class="card-label">High Yield Spread {src("FRED")}</div>
      <div class="card-value card-value-sm" style="color:{hy_c}">{fmt(hy_sprd)}%</div>
      <div><span class="tag {hy_t}">HY OAS</span>&nbsp;<span style="font-size:11px;color:#8aa4b8">Estrés &gt;5%</span></div>
      <div style="margin-top:8px;font-size:10px;color:#4a6278">{fd("BAMLH0A0HYM2")}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="card card-top-yellow">
      <div class="card-label">VIX {src("YAHOO")}</div>
      <div class="card-value card-value-sm" style="color:{vix_c}">{fmt(vix, 2)}</div>
      <div><span class="tag {vix_t}">{'PÁNICO' if vix and vix>25 else 'MODERADO'}</span>&nbsp;<span style="font-size:11px;color:#8aa4b8">Pánico &gt;30</span></div>
    </div>""", unsafe_allow_html=True)


# ── 03 SENTIMIENTO ────────────────────────────────────────────────────────────
sec("03", "PULSO DE SENTIMIENTO", "FEAR & GREED EN TIEMPO REAL")

c1, c2, c3 = st.columns(3)

with c1:
    cv = cnn_val or 0
    cc = fg_color(cnn_val)
    st.markdown(f"""
    <div class="card card-top-{'red' if cv<35 else ('yellow' if cv<55 else 'green')}">
      <div class="card-label">CNN Fear &amp; Greed {src("CNN API")}</div>
      <div style="text-align:center;padding:8px 0">
        <div style="font-family:'Space Mono',monospace;font-size:56px;color:{cc};line-height:1">{cnn_val or '—'}</div>
        <div style="font-family:'Space Mono',monospace;font-size:10px;color:{cc};letter-spacing:2px;margin-bottom:12px">{cnn_lbl}</div>
      </div>
      <div class="gauge-track"><div class="gauge-fill" style="width:{cv}%;background:linear-gradient(90deg,#00ff88,#ffd166,#ff3b5c)"></div></div>
      <div style="display:flex;justify-content:space-between;margin-top:4px">
        <span style="font-family:'Space Mono',monospace;font-size:8px;color:#00ff88">0 FEAR</span>
        <span style="font-family:'Space Mono',monospace;font-size:8px;color:#ff3b5c">100 GREED</span>
      </div>
    </div>""", unsafe_allow_html=True)

with c2:
    vc2 = "#ff3b5c" if vix and vix>25 else ("#ffd166" if vix and vix>18 else "#00d4ff")
    vlbl = "PÁNICO" if vix and vix>30 else ("ELEVADO" if vix and vix>20 else "MODERADO")
    st.markdown(f"""
    <div class="card card-top-cyan">
      <div class="card-label">VIX Volatility Index {src("YAHOO")}</div>
      <div style="text-align:center;padding:8px 0">
        <div style="font-family:'Space Mono',monospace;font-size:56px;color:{vc2};line-height:1">{fmt(vix,2)}</div>
        <div style="font-family:'Space Mono',monospace;font-size:10px;color:{vc2};letter-spacing:2px">{vlbl}</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:12px">
        <div style="font-size:10px;color:#4a6278">BTC <span style="color:{'#ff3b5c' if btc and btc<80000 else '#00ff88'};font-family:'Space Mono',monospace">${fmt(btc,0)}</span></div>
        <div style="font-size:10px;color:#4a6278">DXY <span style="color:#c8dce8;font-family:'Space Mono',monospace">{fmt(dxy)}</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

with c3:
    cfv = cfg_val or 0
    cfc = fg_color(cfg_val)
    st.markdown(f"""
    <div class="card card-top-{'red' if cfv<35 else 'yellow'}">
      <div class="card-label">Crypto Fear &amp; Greed {src("ALTERNATIVE.ME")}</div>
      <div style="text-align:center;padding:8px 0">
        <div style="font-family:'Space Mono',monospace;font-size:56px;color:{cfc};line-height:1">{cfg_val or '—'}</div>
        <div style="font-family:'Space Mono',monospace;font-size:10px;color:{cfc};letter-spacing:2px;margin-bottom:12px">{cfg_lbl}</div>
      </div>
      <div class="gauge-track"><div class="gauge-fill" style="width:{cfv}%;background:linear-gradient(90deg,#00ff88,#ffd166,#ff3b5c)"></div></div>
    </div>""", unsafe_allow_html=True)


# ── 04 MOMENTUM ───────────────────────────────────────────────────────────────
sec("04", "FLUJOS Y MOMENTUM", "MEDIAS MÓVILES 50D / 200D · YAHOO FINANCE")

idxs = [
    ("S&P 500",    sp5_p,   sp5_pct,   yma("SP500","50"),  yma("SP500","200"),  False),
    ("NASDAQ 100", ndx_p,   ndx_pct,   yma("NDX","50"),    yma("NDX","200"),    False),
    ("IBEX 35 ⭐", ibex_p,  ibex_pct,  yma("IBEX","50"),   yma("IBEX","200"),   True),
    ("STOXX 600",  stoxx_p, stoxx_pct, yma("STOXX","50"),  yma("STOXX","200"),  False),
]
cols = st.columns(4)
for col, (name, price, pct, ma50, ma200, star) in zip(cols, idxs):
    with col:
        brd = "border-color:rgba(0,255,136,0.3)" if star else ""
        nc  = "color:#00ff88" if star else "color:#e8f4fc"
        pct_s = f' <span style="color:{pcolor(pct)};font-size:11px">({fmt(pct,2):+}%)</span>' if pct else ""
        st.markdown(f"""
        <div class="idx-card" style="{brd}">
          <div class="idx-name" style="{'color:#00ff88' if star else ''}">{name}</div>
          <div class="idx-value" style="{nc}">{fmt(price,0) if price else '—'}{pct_s}</div>
          <div style="margin-top:8px">
            {ma_badge(price, ma50, "MM50")}
            {ma_badge(price, ma200, "MM200")}
          </div>
        </div>""", unsafe_allow_html=True)


# ── 05 POSICIONAMIENTO ────────────────────────────────────────────────────────
sec("05", "POSICIONAMIENTO SUGERIDO", "ASSET ALLOCATION | SEÑALES")

pos_l = [
    ("💵 Liquidez / Money Market", f"Remunerado ~{fmt(fed_rate)}%",   "sig-over",    "SOBREPONDERAR"),
    ("📊 Renta Fija Corta (< 2Y)", f"UST 2Y: {fmt(ust2)}%",          "sig-over",    "SOBREPONDERAR"),
    ("🇪🇸 IBEX 35 / Europa",       f"IBEX: {fmt(ibex_p,0)}",          "sig-over",    "ACUMULAR"),
    ("🌍 S&P 500",                 f"S&P: {fmt(sp5_p,0)}",            "sig-neutral", "MANTENER"),
]
pos_r = [
    ("📉 Nasdaq 100 / Growth",     f"NDX: {fmt(ndx_p,0)}",            "sig-under",  "INFRAPONDERAR"),
    ("₿ Cripto (BTC/ETH)",         f"BTC: ${fmt(btc,0)}",             "sig-avoid",  "EVITAR"),
    ("🥇 Oro (XAU/USD)",           f"${fmt(gold,0)}/oz",              "sig-watch",  "VIGILAR"),
    ("🛢️ Petróleo WTI",            f"${fmt(oil,2)}/barril",           "sig-neutral","NEUTRO"),
]
c1, c2 = st.columns(2)
for col, positions in [(c1, pos_l), (c2, pos_r)]:
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


# ── 06 RADAR MACRO ────────────────────────────────────────────────────────────
sec("06", "RADAR DE OTROS INDICADORES", "MACRO ADICIONAL · FRED + YAHOO")

c1, c2 = st.columns(2)
with c1:
    rows_t = [
        ("DXY", src("YAHOO"), fmt(dxy), "tag-yellow" if dxy and dxy>104 else "tag-green", "VIGILAR" if dxy and dxy>104 else "NEUTRO"),
        ("Oro XAU/USD", src("YAHOO"), f"${fmt(gold,0)}", "tag-green" if gold and gold>2500 else "tag-yellow", "HEDGE ACTIVO" if gold and gold>2500 else "NEUTRO"),
        ("Petróleo WTI", src("YAHOO"), f"${fmt(oil,2)}", "tag-yellow", "NEUTRO"),
        ("BTC", src("YAHOO"), f"${fmt(btc,0)}", "tag-red" if btc and btc<80000 else "tag-green", "BEARISH" if btc and btc<80000 else "BULLISH"),
        ("High Yield Spread", src("FRED"), f"{fmt(hy_sprd)}%", "tag-green" if hy_sprd and hy_sprd<4 else "tag-red", "TRANQUILO" if hy_sprd and hy_sprd<4 else "ESTRÉS"),
        ("Curva 10Y-3M", src("FRED"), f"{fmt(spread_10_3):+}%", "tag-red" if spread_10_3 and spread_10_3<0 else "tag-green", "RECESIÓN WATCH" if spread_10_3 and spread_10_3<0 else "NORMAL"),
        ("CNN F&G", src("CNN"), f"{cnn_val}/100", "tag-red" if cnn_val and cnn_val<30 else "tag-yellow", cnn_lbl),
        ("Crypto F&G", src("ALT.ME"), f"{cfg_val}/100", "tag-red" if cfg_val and cfg_val<30 else "tag-yellow", cfg_lbl),
    ]
    rows_html = "".join(f"<tr><td>{n}{s}</td><td style=\"font-family:'Space Mono',monospace;font-size:11px\">{v}</td><td><span class=\"tag {tc}\">{tl}</span></td></tr>"
                        for n, s, v, tc, tl in rows_t)
    st.markdown(f"""
    <table class="mcc-table" style="background:#0d1219;border:1px solid #1e2d3d;border-radius:4px">
      <thead><tr><th>INDICADOR</th><th>VALOR</th><th>SEÑAL</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card-label" style="font-family:\'Space Mono\',monospace;font-size:9px;letter-spacing:2px;color:#4a6278;margin-bottom:10px">PRÓXIMOS CATALIZADORES CLAVE</div>', unsafe_allow_html=True)
    for date, name in [
        ("18-19 MAR","FOMC Meeting (Fed)"),
        ("28 MAR",   "PCE Core (febrero 2026)"),
        ("ABR 2026", "Q1 Earnings Season"),
        ("ONGOING",  "Aranceles Trump (15% global)"),
        ("ONGOING",  "Geopolítica / Ucrania / Taiwan"),
    ]:
        st.markdown(f"""
        <div class="event-item">
          <span class="event-date">{date}</span>
          <span class="event-name">{name}</span>
          <span class="impact-high">ALTO IMPACTO</span>
        </div>""", unsafe_allow_html=True)


# ── 07 ANÁLISIS IA ────────────────────────────────────────────────────────────
sec("07", "ANÁLISIS IA EN TIEMPO REAL", "CLAUDE · ALIMENTADO CON DATOS REALES")

if "ai_text" not in st.session_state:
    st.session_state.ai_text = "Pulsa '↻ ANALIZAR CON IA' para generar un análisis con los datos reales cargados."
if "ai_ts" not in st.session_state:
    st.session_state.ai_ts = "—"

st.markdown(f"""
<div class="ai-panel">
  <div class="ai-header">
    <span class="ai-dot"></span>
    <span>CLAUDE MARKET ANALYST · DATOS REALES</span>
    <span style="margin-left:auto">{st.session_state.ai_ts}</span>
  </div>
  <div class="ai-body">{st.session_state.ai_text}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

if st.button("↻ ANALIZAR CON IA (datos reales)"):
    today = datetime.now().strftime("%A %d de %B de %Y")
    prompt = f"""Eres un Senior Investment Strategist. Hoy es {today}.
Datos REALES de mercado obtenidos en tiempo real:

MACRO (FRED — St. Louis Fed):
- UST 10Y: {fmt(ust10)}% | UST 2Y: {fmt(ust2)}%
- Spread 2s10s: {fmt(spread_2s10):+}% | Curva 10Y-3M: {fmt(spread_10_3):+}%
- Core CPI: {fmt(core_cpi)}% YoY | Core PCE: {fmt(core_pce)}% YoY | CPI Hl: {fmt(cpi_hl)}%
- GDP (último dato): {fmt(gdp)}% anualizado
- Fed Funds Rate: {fmt(fed_rate)}%
- High Yield Spread: {fmt(hy_sprd)}%

MERCADOS (Yahoo Finance):
- S&P 500: {fmt(sp5_p,0)} ({fmt(sp5_pct,2):+}%) | Nasdaq 100: {fmt(ndx_p,0)} ({fmt(ndx_pct,2):+}%)
- IBEX 35: {fmt(ibex_p,0)} ({fmt(ibex_pct,2):+}%) | STOXX 600: {fmt(stoxx_p,2)}
- VIX: {fmt(vix,2)} | Oro: ${fmt(gold,0)} | Petróleo WTI: ${fmt(oil,2)}
- DXY: {fmt(dxy)} | BTC: ${fmt(btc,0)}

SENTIMIENTO:
- CNN Fear & Greed: {cnn_val}/100 — {cnn_lbl}
- Crypto Fear & Greed: {cfg_val}/100 — {cfg_lbl}

Con ESTOS datos reales proporciona análisis en español (máx. 350 palabras):
1. RÉGIMEN MACRO (2 frases)
2. VALORACIÓN (2 frases)
3. SENTIMIENTO Y VOLATILIDAD (2 frases)
4. MOMENTUM TÉCNICO (2 frases)
5. VEREDICTO FINAL (4-5 frases)
Termina: "▸ SEÑAL: [RISK-ON / NEUTRO / RISK-OFF] — [razón 10 palabras]"
"""
    with st.spinner("⠋ PROCESANDO DATOS Y GENERANDO ANÁLISIS..."):
        try:
            client = anthropic.Anthropic()
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            st.session_state.ai_text = msg.content[0].text
            st.session_state.ai_ts   = "Actualizado: " + datetime.now().strftime("%d/%m/%Y %H:%M")
            st.rerun()
        except Exception as e:
            st.error(f"⚠ Error API: {e}")


# STATUS BAR
ok_count = sum([yf_ok, fred_ok, cfg_ok, cnn_ok])
st.markdown(f"""
<div class="status-bar">
  <div style="display:flex;gap:20px;flex-wrap:wrap">
    <span>🟢 DASHBOARD ACTIVO</span>
    <span>{'🟢' if ok_count==4 else '🟡'} FUENTES: {ok_count}/4 OPERATIVAS</span>
    <span>🕒 CACHE PRECIOS: 5 MIN | FRED: 60 MIN</span>
  </div>
  <span>MARKET COMMAND CENTER · DATOS NO CONSTITUYEN ASESORAMIENTO FINANCIERO</span>
</div>""", unsafe_allow_html=True)
