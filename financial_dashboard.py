"""
╔══════════════════════════════════════════════════════════════════╗
║   INVESTOR INTELLIGENCE PLATFORM  v3.0  — LIVE DATA EDITION     ║
║                                                                  ║
║   Fuentes gratuitas:                                             ║
║     • yfinance      → precios OHLCV + fundamentales             ║
║     • FRED (St. Louis Fed) → macro: VIX, tipos, spreads         ║
║     • Alternative.me → Fear & Greed de Crypto                   ║
║                                                                  ║
║   Instalar dependencias:                                         ║
║     pip install streamlit pandas numpy plotly yfinance requests  ║
║                                                                  ║
║   Ejecutar:                                                      ║
║     streamlit run financial_dashboard.py                         ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import warnings
warnings.filterwarnings("ignore")

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Investor Intelligence Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
#  CSS — Dark luxury terminal aesthetic
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;600&family=Syne:wght@400;600;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace;
    background-color: #0a0d14;
    color: #c8d0e0;
  }
  .main .block-container { padding: 2rem 2.5rem; background: #0a0d14; }

  .dashboard-header {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #1e2535; padding-bottom: 1.2rem; margin-bottom: 2rem;
  }
  .dashboard-title {
    font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800;
    color: #e8eaf0; letter-spacing: -0.5px;
  }
  .dashboard-subtitle { font-size: 0.68rem; color: #4a5568; letter-spacing: 2px; text-transform: uppercase; }
  .live-badge {
    background: rgba(0,255,140,0.1); border: 1px solid rgba(0,255,140,0.3);
    color: #00ff8c; font-size: 0.62rem; padding: 4px 10px; border-radius: 2px;
    letter-spacing: 2px; animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }

  .kpi-card {
    background: #111420; border: 1px solid #1e2535; border-radius: 4px;
    padding: 1.1rem 1.3rem; position: relative; overflow: hidden; transition: border-color 0.2s;
  }
  .kpi-card:hover { border-color: #2a3550; }
  .kpi-card::before { content:''; position:absolute; top:0; left:0; width:3px; height:100%; }
  .kpi-card.green::before  { background:#00ff8c; }
  .kpi-card.red::before    { background:#ff4d6d; }
  .kpi-card.blue::before   { background:#4d9eff; }
  .kpi-card.amber::before  { background:#ffb347; }
  .kpi-card.purple::before { background:#a78bfa; }
  .kpi-card.cyan::before   { background:#67e8f9; }

  .kpi-label  { font-size:0.58rem; letter-spacing:2px; text-transform:uppercase; color:#4a5568; margin-bottom:0.4rem; }
  .kpi-value  { font-family:'Syne',sans-serif; font-size:1.65rem; font-weight:800; color:#e8eaf0; line-height:1; }
  .kpi-delta  { font-size:0.68rem; margin-top:0.35rem; }
  .kpi-delta.pos { color:#00ff8c; }
  .kpi-delta.neg { color:#ff4d6d; }
  .kpi-delta.neu { color:#4a5568; }
  .kpi-sub    { font-size:0.58rem; color:#4a5568; margin-top:0.15rem; }

  .section-header {
    font-family:'Syne',sans-serif; font-size:0.68rem; letter-spacing:3px;
    text-transform:uppercase; color:#4a5568; border-bottom:1px solid #1e2535;
    padding-bottom:0.45rem; margin: 1.8rem 0 1rem 0;
  }

  section[data-testid="stSidebar"] { background:#0d1020; border-right:1px solid #1e2535; }
  section[data-testid="stSidebar"] .block-container { background:#0d1020; padding:1.5rem 1rem; }
  .js-plotly-plot { background:transparent !important; }
  hr { border-color:#1e2535; }

  thead tr th { background:#0d1020 !important; color:#4a5568 !important; font-size:0.62rem !important; letter-spacing:1.5px !important; text-transform:uppercase !important; }
  tbody tr td { color:#c8d0e0 !important; font-size:0.74rem !important; background:#111420 !important; }
  tbody tr:hover td { background:#161b2a !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────
COLORS = {
    "bg": "#0a0d14", "surface": "#111420", "border": "#1e2535",
    "green": "#00ff8c", "red": "#ff4d6d", "blue": "#4d9eff",
    "amber": "#ffb347", "purple": "#a78bfa", "cyan": "#67e8f9",
    "text": "#c8d0e0", "muted": "#4a5568",
}
PALETTE = ["#4d9eff","#00ff8c","#a78bfa","#ffb347","#ff4d6d",
           "#67e8f9","#f472b6","#34d399","#fb923c","#818cf8"]

CHART_LAYOUT = dict(
    paper_bgcolor=COLORS["bg"], plot_bgcolor=COLORS["surface"],
    font=dict(family="IBM Plex Mono", color=COLORS["text"], size=11),
    xaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"],
               tickfont=dict(size=10, color=COLORS["muted"])),
    yaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"],
               tickfont=dict(size=10, color=COLORS["muted"])),
    margin=dict(l=10, r=10, t=35, b=10),
    hoverlabel=dict(bgcolor=COLORS["surface"], bordercolor=COLORS["border"],
                    font_color=COLORS["text"]),
    legend=dict(bgcolor=COLORS["surface"], bordercolor=COLORS["border"],
                borderwidth=1, font=dict(size=10)),
)

DEFAULT_PORTFOLIO = {
    "SPY":     {"shares": 150,  "avg_cost": 440.0,  "sector": "ETF Broad Market"},
    "QQQ":     {"shares": 80,   "avg_cost": 370.0,  "sector": "ETF Technology"},
    "AAPL":    {"shares": 200,  "avg_cost": 165.0,  "sector": "Technology"},
    "MSFT":    {"shares": 120,  "avg_cost": 350.0,  "sector": "Technology"},
    "NVDA":    {"shares": 50,   "avg_cost": 600.0,  "sector": "Semiconductors"},
    "AMZN":    {"shares": 90,   "avg_cost": 155.0,  "sector": "Consumer / Cloud"},
    "META":    {"shares": 60,   "avg_cost": 380.0,  "sector": "Social / Advertising"},
    "GLD":     {"shares": 100,  "avg_cost": 175.0,  "sector": "Commodities"},
    "TLT":     {"shares": 200,  "avg_cost": 105.0,  "sector": "Fixed Income"},
    "BTC-USD": {"shares": 0.5,  "avg_cost": 45000.0,"sector": "Crypto"},
}


# ─────────────────────────────────────────────────────────────────
#  DATA LOADERS — REAL DATA
# ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600, show_spinner=False)
def fetch_price_data(tickers: tuple, period: str = "1y") -> dict:
    result = {}
    if not YF_AVAILABLE:
        return result
    for tk in tickers:
        try:
            df = yf.download(tk, period=period, auto_adjust=True, progress=False)
            if df.empty:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.index = pd.to_datetime(df.index)
            result[tk] = df
        except Exception as e:
            st.warning(f"Error cargando {tk}: {e}")
    return result


@st.cache_data(ttl=600, show_spinner=False)
def fetch_fundamentals(tickers: tuple) -> dict:
    result = {}
    if not YF_AVAILABLE:
        return result
    for tk in tickers:
        try:
            info = yf.Ticker(tk).info
            result[tk] = {
                "trailingPE":       info.get("trailingPE"),
                "forwardPE":        info.get("forwardPE"),
                "priceToBook":      info.get("priceToBook"),
                "priceToSales":     info.get("priceToSalesTrailing12Months"),
                "evToEbitda":       info.get("enterpriseToEbitda"),
                "pegRatio":         info.get("pegRatio"),
                "dividendYield":    info.get("dividendYield"),
                "returnOnEquity":   info.get("returnOnEquity"),
                "returnOnAssets":   info.get("returnOnAssets"),
                "debtToEquity":     info.get("debtToEquity"),
                "currentRatio":     info.get("currentRatio"),
                "grossMargins":     info.get("grossMargins"),
                "operatingMargins": info.get("operatingMargins"),
                "revenueGrowth":    info.get("revenueGrowth"),
                "earningsGrowth":   info.get("earningsGrowth"),
                "marketCap":        info.get("marketCap"),
                "shortName":        info.get("shortName", tk),
                "sector":           info.get("sector", "—"),
            }
        except Exception:
            result[tk] = {}
    return result


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_macro_fred() -> dict:
    BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
    series = {
        "VIX":     "VIXCLS",
        "FEDFUNDS":"FEDFUNDS",
        "T10Y2Y":  "T10Y2YNB",
        "T10YIE":  "T10YIE",
        "UNRATE":  "UNRATE",
        "HY_OAS":  "BAMLH0A0HYM2",
        "IG_OAS":  "BAMLC0A0CM",
        "M2SL":    "M2SL",
    }
    out = {}
    for name, sid in series.items():
        try:
            df = pd.read_csv(f"{BASE}{sid}", parse_dates=["DATE"], na_values=".")
            df = df.dropna().tail(252)
            df.columns = ["Date", "Value"]
            out[name] = df
        except Exception:
            out[name] = pd.DataFrame(columns=["Date","Value"])
    return out


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_crypto_fear_greed() -> dict:
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=30", timeout=6)
        data = r.json()["data"]
        return {
            "current_value": int(data[0]["value"]),
            "current_label": data[0]["value_classification"],
            "history": pd.DataFrame([
                {"date": datetime.fromtimestamp(int(d["timestamp"])),
                 "value": int(d["value"]),
                 "label": d["value_classification"]}
                for d in data
            ])
        }
    except Exception:
        return {"current_value": 50, "current_label": "Neutral", "history": pd.DataFrame()}


@st.cache_data(ttl=600, show_spinner=False)
def fetch_spy_put_call() -> float:
    try:
        spy = yf.Ticker("SPY")
        exp = spy.options[0]
        chain = spy.option_chain(exp)
        pc = chain.puts["volume"].sum() / (chain.calls["volume"].sum() + 1e-10)
        return round(pc, 3)
    except Exception:
        return None


def compute_technicals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["Close"]
    df["SMA20"]  = c.rolling(20).mean()
    df["SMA50"]  = c.rolling(50).mean()
    df["SMA200"] = c.rolling(200).mean()
    df["EMA12"]  = c.ewm(span=12, adjust=False).mean()
    df["EMA26"]  = c.ewm(span=26, adjust=False).mean()
    df["MACD"]   = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["Hist"]   = df["MACD"] - df["Signal"]
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"]    = 100 - 100 / (1 + rs)
    df["BB_mid"] = c.rolling(20).mean()
    std          = c.rolling(20).std()
    df["BB_up"]  = df["BB_mid"] + 2 * std
    df["BB_dn"]  = df["BB_mid"] - 2 * std
    df["Return"] = c.pct_change()
    return df


def valuation_label(pe):
    if pe is None:
        return "N/A", "neu"
    try:
        pe = float(pe)
    except:
        return "N/A", "neu"
    if pe < 0:   return "NEGATIVO", "neg"
    if pe < 15:  return "BARATO",   "pos"
    if pe < 25:  return "JUSTO",    "neu"
    if pe < 40:  return "CARO",     "amber"
    return "MUY CARO", "neg"


# ─────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:1.05rem;font-weight:800;color:#e8eaf0;margin-bottom:1.5rem;">⬡ INVESTOR<br>&nbsp;&nbsp;INTELLIGENCE</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.6rem;letter-spacing:2px;color:#4a5568;text-transform:uppercase;border-bottom:1px solid #1e2535;padding-bottom:0.4rem;margin-bottom:0.8rem;">CARTERA</div>', unsafe_allow_html=True)
    selected_tickers = st.multiselect(
        "Posiciones activas",
        options=list(DEFAULT_PORTFOLIO.keys()),
        default=list(DEFAULT_PORTFOLIO.keys()),
    )

    st.markdown('<div style="font-size:0.6rem;letter-spacing:2px;color:#4a5568;text-transform:uppercase;border-bottom:1px solid #1e2535;padding-bottom:0.4rem;margin:0.8rem 0;">ANÁLISIS</div>', unsafe_allow_html=True)
    primary_ticker = st.selectbox("Activo principal", options=selected_tickers or ["SPY"])
    lookback = st.select_slider("Periodo histórico", options=["1mo","3mo","6mo","1y","2y"], value="1y")
    chart_type = st.radio("Tipo de gráfico", ["Candlestick", "Línea", "Área"], horizontal=True)
    show_sma = st.checkbox("SMA 20/50/200", value=True)
    show_bb  = st.checkbox("Bollinger Bands", value=False)
    show_vol = st.checkbox("Volumen", value=True)

    st.markdown('<div style="font-size:0.6rem;letter-spacing:2px;color:#4a5568;text-transform:uppercase;border-bottom:1px solid #1e2535;padding-bottom:0.4rem;margin:0.8rem 0;">RIESGO</div>', unsafe_allow_html=True)
    risk_free = st.number_input("Tasa libre de riesgo (%)", value=5.25, step=0.05, format="%.2f")
    conf_var  = st.select_slider("Confianza VaR", options=[90, 95, 99], value=95)
    benchmark = st.selectbox("Benchmark", ["SPY", "QQQ", "TLT"])

    st.markdown("---")
    if not YF_AVAILABLE:
        st.error("yfinance no instalado\npip install yfinance")
    st.markdown(f'<div style="font-size:0.58rem;color:#2a3550;letter-spacing:1px;">ACTUALIZADO<br>{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────────────────────────
if not selected_tickers:
    st.warning("Selecciona al menos una posición.")
    st.stop()

with st.spinner("🔄 Cargando datos reales..."):
    tickers_tuple = tuple(selected_tickers)
    all_tickers   = tuple(set(list(tickers_tuple) + [benchmark]))
    raw_prices    = fetch_price_data(all_tickers, period=lookback)
    fundamentals  = fetch_fundamentals(tickers_tuple)
    macro_data    = fetch_macro_fred()
    fg_data       = fetch_crypto_fear_greed()
    pc_ratio      = fetch_spy_put_call()

available = [tk for tk in selected_tickers if tk in raw_prices and not raw_prices[tk].empty]
if not available:
    st.error("No se pudieron cargar datos. Verifica conexión e instalación de yfinance.")
    st.stop()

all_data = {tk: compute_technicals(raw_prices[tk]) for tk in available}


# ─────────────────────────────────────────────────────────────────
#  PORTFOLIO COMPUTATIONS
# ─────────────────────────────────────────────────────────────────

def portfolio_metrics():
    rows = []
    for tk in available:
        pos   = DEFAULT_PORTFOLIO.get(tk, {"shares":1,"avg_cost":100.0,"sector":"—"})
        df    = all_data[tk]
        price = float(df["Close"].iloc[-1])
        prev  = float(df["Close"].iloc[-2]) if len(df)>1 else price
        market_val = price * pos["shares"]
        pnl_pct    = (price - pos["avg_cost"]) / pos["avg_cost"] * 100
        day_chg    = (price - prev) / prev * 100
        ret        = df["Return"].dropna()
        vol_ann    = ret.std() * np.sqrt(252) * 100
        sharpe     = (ret.mean()*252 - risk_free/100) / (ret.std()*np.sqrt(252)+1e-10)
        rsi_val    = float(df["RSI"].iloc[-1])
        rows.append({
            "Ticker": tk, "Sector": pos["sector"],
            "Price": price, "Avg Cost": pos["avg_cost"], "Shares": pos["shares"],
            "Market Value ($)": market_val, "P&L (%)": pnl_pct,
            "Day Chg (%)": day_chg, "Vol (Ann %)": vol_ann,
            "Sharpe": sharpe, "RSI": rsi_val if not np.isnan(rsi_val) else 50.0,
        })
    return pd.DataFrame(rows)


port_df     = portfolio_metrics()
total_value = port_df["Market Value ($)"].sum()
total_cost  = sum(
    DEFAULT_PORTFOLIO.get(tk,{"avg_cost":100,"shares":1})["avg_cost"] *
    DEFAULT_PORTFOLIO.get(tk,{"avg_cost":100,"shares":1})["shares"]
    for tk in available
)
total_pnl     = total_value - total_cost
total_pnl_pct = total_pnl / total_cost * 100

weights = {tk: DEFAULT_PORTFOLIO.get(tk,{"avg_cost":100,"shares":1})["avg_cost"] *
               DEFAULT_PORTFOLIO.get(tk,{"avg_cost":100,"shares":1})["shares"] / total_cost
           for tk in available}

port_returns = pd.concat(
    [all_data[tk]["Return"] * weights[tk] for tk in available], axis=1
).sum(axis=1).dropna()

port_vol   = port_returns.std() * np.sqrt(252) * 100
port_sharp = (port_returns.mean()*252 - risk_free/100) / (port_returns.std()*np.sqrt(252)+1e-10)
var_95     = np.percentile(port_returns, 100-conf_var) * total_value
cum_p      = (1 + port_returns).cumprod()
max_dd     = ((cum_p / cum_p.cummax()) - 1).min() * 100

beta_val = 1.0
if benchmark in all_data:
    br = all_data[benchmark]["Return"].reindex(port_returns.index).dropna()
    shared = port_returns.index.intersection(br.index)
    if len(shared) > 10:
        cv = np.cov(port_returns.loc[shared], br.loc[shared])
        beta_val = cv[0,1] / (np.var(br.loc[shared]) + 1e-10)


# ─────────────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dashboard-header">
  <div>
    <div class="dashboard-title">INVESTOR INTELLIGENCE PLATFORM</div>
    <div class="dashboard-subtitle">Real-time Portfolio &amp; Market Intelligence · {datetime.today().strftime('%B %d, %Y · %H:%M')}</div>
  </div>
  <div class="live-badge">● LIVE · yfinance + FRED + alternative.me</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  ROW 1 — Portfolio KPIs
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">RESUMEN DE CARTERA</div>', unsafe_allow_html=True)

k1,k2,k3,k4,k5,k6 = st.columns(6)
for col, label, value, delta, cclass, dclass in [
    (k1,"TOTAL AUM", f"${total_value:,.0f}", f"Coste: ${total_cost:,.0f}","blue","neu"),
    (k2,"P&L NO REALIZADO", f"${total_pnl:,.0f}",
     f"{'▲' if total_pnl>=0 else '▼'} {total_pnl_pct:.2f}%",
     "green" if total_pnl>=0 else "red","pos" if total_pnl>=0 else "neg"),
    (k3,"VOL. ANUALIZADA", f"{port_vol:.1f}%","Desviación estándar σ","amber","neu"),
    (k4,"SHARPE RATIO", f"{port_sharp:.2f}", f"rf = {risk_free:.2f}%",
     "purple","pos" if port_sharp>1 else "neu"),
    (k5,f"VaR {conf_var}% (1d)", f"${abs(var_95):,.0f}","Pérdida máx. esperada","red","neg"),
    (k6,"MÁXIMO DRAWDOWN", f"{max_dd:.2f}%", f"Beta vs {benchmark}: {beta_val:.2f}","red","neg"),
]:
    with col:
        st.markdown(f"""<div class="kpi-card {cclass}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-delta {dclass}">{delta}</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  ROW 2 — Macro & Sentiment KPIs
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">MACRO · SENTIMIENTO · CRÉDITO</div>', unsafe_allow_html=True)

def get_last(key):
    df = macro_data.get(key, pd.DataFrame(columns=["Date","Value"]))
    if df.empty: return None, None
    return float(df["Value"].iloc[-1]), float(df["Value"].iloc[-1]) - float(df["Value"].iloc[-2]) if len(df)>1 else 0.0

vix_val,  vix_d  = get_last("VIX")
yc_val,   yc_d   = get_last("T10Y2Y")
infl_val, infl_d = get_last("T10YIE")
hy_val,   hy_d   = get_last("HY_OAS")
ff_val,   ff_d   = get_last("FEDFUNDS")
unemp_v,  unemp_d= get_last("UNRATE")
fg_val  = fg_data.get("current_value", 50)
fg_lbl  = fg_data.get("current_label", "Neutral")

def fmtv(v, dec=2, suffix=""):
    return f"{v:.{dec}f}{suffix}" if v is not None else "N/A"

def d_html(d, inv=False):
    if d is None or d == 0: return '<span class="kpi-delta neu">—</span>'
    up = d > 0
    sign = "▲" if up else "▼"
    css = ("neg" if up else "pos") if inv else ("pos" if up else "neg")
    return f'<span class="kpi-delta {css}">{sign} {abs(d):.3f}</span>'

# Amplitud de mercado
above_sma50 = sum(1 for tk in available
                  if not np.isnan(float(all_data[tk]["SMA50"].iloc[-1])) and
                  float(all_data[tk]["Close"].iloc[-1]) > float(all_data[tk]["SMA50"].iloc[-1]))
breadth_pct = above_sma50 / len(available) * 100

# Put/Call label
pc_label = "N/A"
pc_css   = "blue"
if pc_ratio is not None:
    pc_label = "BEARISH" if pc_ratio>1.0 else "BULLISH" if pc_ratio<0.7 else "NEUTRAL"
    pc_css   = "red" if pc_ratio>1.0 else "green" if pc_ratio<0.7 else "blue"

fg_css = "green" if fg_val>60 else "red" if fg_val<35 else "amber"

m1,m2,m3,m4,m5,m6,m7,m8 = st.columns(8)
macro_cards = [
    (m1,"VIX", fmtv(vix_val), d_html(vix_d,inv=True),
     "PÁNICO" if (vix_val or 0)>30 else "ALERTA" if (vix_val or 0)>20 else "CALMA",
     "red" if (vix_val or 0)>30 else "amber" if (vix_val or 0)>20 else "green"),
    (m2,"CURVA 10Y-2Y", fmtv(yc_val)+"%", d_html(yc_d),
     "INVERTIDA ⚠️" if (yc_val or 0)<0 else "POSITIVA ✓",
     "red" if (yc_val or 0)<0 else "green"),
    (m3,"BREAKEVEN INFL.", fmtv(infl_val)+"%", d_html(infl_d),
     "Inflación implícita 10Y","blue"),
    (m4,"HY SPREAD", fmtv(hy_val,0)+"bp", d_html(hy_d,inv=True),
     "ESTRÉS" if (hy_val or 0)>600 else "ELEVADO" if (hy_val or 0)>450 else "NORMAL",
     "red" if (hy_val or 0)>600 else "amber" if (hy_val or 0)>450 else "green"),
    (m5,"FED FUNDS", fmtv(ff_val)+"%", d_html(ff_d,inv=True),
     "Política monetaria","purple"),
    (m6,"DESEMPLEO US", fmtv(unemp_v)+"%", d_html(unemp_d,inv=True),
     "NAIRU ≈ 4.5%","green" if (unemp_v or 5)<5 else "amber"),
    (m7,"FEAR & GREED", str(fg_val), "",
     fg_lbl.upper(), fg_css),
    (m8,"PUT/CALL SPY", fmtv(pc_ratio,3) if pc_ratio else "N/A", "",
     pc_label, pc_css),
]
for col, label, value, delta_h, sub, cclass in macro_cards:
    with col:
        st.markdown(f"""<div class="kpi-card {cclass}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          {delta_h}
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# Amplitud
acol1, acol2 = st.columns([1,7])
with acol1:
    b_css = "green" if breadth_pct>60 else "red" if breadth_pct<40 else "amber"
    st.markdown(f"""<div class="kpi-card {b_css}" style="margin-top:0.8rem">
      <div class="kpi-label">AMPLITUD MERCADO</div>
      <div class="kpi-value">{breadth_pct:.0f}%</div>
      <div class="kpi-delta {b_css}">{'ALCISTA' if breadth_pct>60 else 'BAJISTA' if breadth_pct<40 else 'MIXTO'}</div>
      <div class="kpi-sub">% posiciones sobre SMA50</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  MACRO CHARTS
# ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    df_v = macro_data.get("VIX", pd.DataFrame())
    if not df_v.empty:
        fig = go.Figure(go.Scatter(
            x=df_v["Date"], y=df_v["Value"],
            fill="tozeroy", fillcolor="rgba(255,179,71,0.07)",
            line=dict(color=COLORS["amber"],width=1.5)
        ))
        fig.add_hline(y=20, line_dash="dot", line_color=COLORS["amber"], opacity=0.5,
                      annotation_text="20·Alerta", annotation_font=dict(size=8))
        fig.add_hline(y=30, line_dash="dot", line_color=COLORS["red"], opacity=0.5,
                      annotation_text="30·Pánico", annotation_font=dict(size=8))
        fig.update_layout(**CHART_LAYOUT, height=220,
                          title=dict(text="VIX — Volatilidad CBOE",
                                     font=dict(size=11, color=COLORS["muted"])))
        st.plotly_chart(fig, use_container_width=True)

with c2:
    df_yc = macro_data.get("T10Y2Y", pd.DataFrame())
    if not df_yc.empty:
        yc_clrs = [COLORS["red"] if v<0 else COLORS["green"] for v in df_yc["Value"]]
        fig = go.Figure(go.Bar(
            x=df_yc["Date"], y=df_yc["Value"], marker_color=yc_clrs, opacity=0.8
        ))
        fig.add_hline(y=0, line_color=COLORS["border"])
        fig.update_layout(**CHART_LAYOUT, height=220,
                          title=dict(text="Curva de Tipos 10Y−2Y",
                                     font=dict(size=11, color=COLORS["muted"])))
        st.plotly_chart(fig, use_container_width=True)

with c3:
    fg_hist = fg_data.get("history", pd.DataFrame())
    if not fg_hist.empty:
        def fg_color(v):
            if v<=25: return COLORS["red"]
            if v<=45: return COLORS["amber"]
            if v<=55: return COLORS["blue"]
            if v<=75: return COLORS["green"]
            return COLORS["red"]
        clrs = [fg_color(v) for v in fg_hist["value"]]
        fig = go.Figure(go.Bar(
            x=fg_hist["date"], y=fg_hist["value"],
            marker_color=clrs, opacity=0.85,
            text=fg_hist["value"], textposition="outside", textfont=dict(size=8)
        ))
        fig.add_hline(y=25, line_dash="dot", line_color=COLORS["red"], opacity=0.5)
        fig.add_hline(y=75, line_dash="dot", line_color=COLORS["green"], opacity=0.5)
        fig.update_layout(**CHART_LAYOUT, height=220,
                          title=dict(text=f"Crypto Fear & Greed · {fg_val} ({fg_lbl})",
                                     font=dict(size=11, color=COLORS["muted"])),
                          yaxis=dict(range=[0,100]))
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
#  TECHNICAL CHART
# ─────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-header">ANÁLISIS TÉCNICO · {primary_ticker}</div>', unsafe_allow_html=True)

col_chart, col_pie = st.columns([3,1])

with col_chart:
    df_p = all_data[primary_ticker]
    nsub = 3 if show_vol else 2
    rh   = [0.55,0.25,0.20] if show_vol else [0.65,0.35]
    fig  = make_subplots(rows=nsub, cols=1, shared_xaxes=True,
                         row_heights=rh, vertical_spacing=0.03,
                         specs=[[{}]]*nsub)

    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df_p.index, open=df_p["Open"], high=df_p["High"],
            low=df_p["Low"], close=df_p["Close"],
            increasing_fillcolor=COLORS["green"], decreasing_fillcolor=COLORS["red"],
            increasing_line_color=COLORS["green"], decreasing_line_color=COLORS["red"],
            name=primary_ticker, showlegend=False
        ), row=1, col=1)
    elif chart_type == "Línea":
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["Close"],
            line=dict(color=COLORS["blue"],width=1.5), name=primary_ticker
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df_p.index, y=df_p["Close"], fill="tozeroy",
            fillcolor="rgba(77,158,255,0.07)",
            line=dict(color=COLORS["blue"],width=1.5), name=primary_ticker
        ), row=1, col=1)

    if show_sma:
        for cn, cl, d in [("SMA20",COLORS["amber"],"solid"),
                           ("SMA50",COLORS["purple"],"dash"),
                           ("SMA200",COLORS["red"],"dot")]:
            fig.add_trace(go.Scatter(
                x=df_p.index, y=df_p[cn],
                line=dict(color=cl,width=1,dash=d), name=cn, opacity=0.85
            ), row=1, col=1)

    if show_bb:
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p["BB_up"],
                                  line=dict(color=COLORS["muted"],width=0.8,dash="dot"),
                                  showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_p.index, y=df_p["BB_dn"],
                                  fill="tonexty", fillcolor="rgba(74,85,104,0.08)",
                                  line=dict(color=COLORS["muted"],width=0.8,dash="dot"),
                                  showlegend=False), row=1, col=1)

    hclrs = [COLORS["green"] if v>=0 else COLORS["red"] for v in df_p["Hist"]]
    fig.add_trace(go.Bar(x=df_p.index, y=df_p["Hist"], marker_color=hclrs,
                          showlegend=False, opacity=0.7), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p["MACD"],
                              line=dict(color=COLORS["blue"],width=1), name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_p.index, y=df_p["Signal"],
                              line=dict(color=COLORS["amber"],width=1), name="Signal"), row=2, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color=COLORS["border"], row=2, col=1)

    if show_vol and "Volume" in df_p.columns:
        vc = [COLORS["green"] if df_p["Close"].iloc[i]>=df_p["Open"].iloc[i]
              else COLORS["red"] for i in range(len(df_p))]
        fig.add_trace(go.Bar(x=df_p.index, y=df_p["Volume"],
                              marker_color=vc, showlegend=False, opacity=0.6), row=3, col=1)

    lp  = float(df_p["Close"].iloc[-1])
    lrs = float(df_p["RSI"].iloc[-1])
    fig.update_layout(**CHART_LAYOUT, height=490,
                      title=dict(text=f"{primary_ticker} · ${lp:,.2f} · RSI {lrs:.1f}",
                                 font=dict(size=12, color=COLORS["muted"])))
    fig.update_xaxes(showgrid=False, rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with col_pie:
    st.markdown('<div style="font-size:0.58rem;letter-spacing:2px;color:#4a5568;text-transform:uppercase;margin-bottom:0.5rem;">ASIGNACIÓN</div>', unsafe_allow_html=True)
    fig_pie = go.Figure(go.Pie(
        labels=port_df["Ticker"], values=port_df["Market Value ($)"],
        hole=0.55, marker=dict(colors=PALETTE[:len(port_df)]),
        textfont=dict(size=9), hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig_pie.update_layout(**CHART_LAYOUT, height=200, showlegend=True,
                           legend=dict(font=dict(size=8)),
                           annotations=[dict(text=f"${total_value/1e6:.2f}M", x=0.5, y=0.5,
                                             showarrow=False,
                                             font=dict(size=13,color=COLORS["text"],family="Syne"))])
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div style="font-size:0.58rem;letter-spacing:2px;color:#4a5568;text-transform:uppercase;margin:0.5rem 0 0.3rem 0;">SECTOR</div>', unsafe_allow_html=True)
    sec_df = port_df.groupby("Sector")["Market Value ($)"].sum().reset_index()
    sec_df["W%"] = sec_df["Market Value ($)"] / total_value * 100
    fig_sec = go.Figure(go.Bar(
        y=sec_df["Sector"].str.split(" ").str[-1], x=sec_df["W%"], orientation="h",
        marker=dict(color=COLORS["blue"],opacity=0.7),
        text=[f"{v:.1f}%" for v in sec_df["W%"]], textfont=dict(size=8), textposition="auto"
    ))
    fig_sec.update_layout(**CHART_LAYOUT, height=200, showlegend=False,
                           xaxis_title=None, yaxis=dict(tickfont=dict(size=8)))
    st.plotly_chart(fig_sec, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
#  POSITIONS TABLE
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">MONITOR DE POSICIONES</div>', unsafe_allow_html=True)

def color_pnl(val):
    if isinstance(val,(int,float)):
        c = "#00ff8c" if val>0 else "#ff4d6d" if val<0 else "#4a5568"
        return f"color:{c};font-weight:600"
    return ""

def color_rsi(val):
    if isinstance(val,(int,float)):
        if val>70: return "color:#ff4d6d"
        if val<30: return "color:#00ff8c"
    return "color:#c8d0e0"

st.dataframe(
    port_df.style
    .format({"Price":"${:,.2f}","Avg Cost":"${:,.2f}","Market Value ($)":"${:,.0f}",
             "P&L (%)":"{:+.2f}%","Day Chg (%)":"{:+.2f}%","Vol (Ann %)":"{:.1f}%",
             "Sharpe":"{:.2f}","RSI":"{:.1f}","Shares":"{:.4g}"})
    .applymap(color_pnl, subset=["P&L (%)","Day Chg (%)"])
    .applymap(color_rsi, subset=["RSI"]),
    use_container_width=True, hide_index=True
)


# ─────────────────────────────────────────────────────────────────
#  VALUATION RATIOS  ← DATOS REALES
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">RATIOS DE VALORACIÓN · FUNDAMENTALES REALES</div>', unsafe_allow_html=True)

val_rows = []
for tk in available:
    f = fundamentals.get(tk, {})
    def fv(key, mult=1, dec=2, suf=""):
        v = f.get(key)
        if v is None: return "—"
        try: return f"{float(v)*mult:.{dec}f}{suf}"
        except: return "—"

    pe  = f.get("trailingPE")
    lbl, _ = valuation_label(pe)
    mc  = f.get("marketCap", 0)
    val_rows.append({
        "Ticker":        tk,
        "Cap. Mercado":  f"${mc/1e9:.1f}B" if mc else "—",
        "P/E Trailing":  fv("trailingPE"),
        "P/E Forward":   fv("forwardPE"),
        "P/B":           fv("priceToBook"),
        "P/S":           fv("priceToSales"),
        "EV/EBITDA":     fv("evToEbitda"),
        "PEG":           fv("pegRatio"),
        "Div. Yield":    fv("dividendYield", mult=100, suf="%"),
        "ROE":           fv("returnOnEquity", mult=100, dec=1, suf="%"),
        "ROA":           fv("returnOnAssets", mult=100, dec=1, suf="%"),
        "D/E":           fv("debtToEquity"),
        "Gross Margin":  fv("grossMargins", mult=100, dec=1, suf="%"),
        "Op. Margin":    fv("operatingMargins", mult=100, dec=1, suf="%"),
        "Rev. Growth":   fv("revenueGrowth", mult=100, dec=1, suf="%"),
        "EPS Growth":    fv("earningsGrowth", mult=100, dec=1, suf="%"),
        "Valoración":    lbl,
    })

st.dataframe(pd.DataFrame(val_rows), use_container_width=True, hide_index=True)

# Visual valuation charts
vc1, vc2, vc3 = st.columns(3)

def simple_bar(tks, vals, title, color, unit="x"):
    pairs = [(t,v) for t,v in zip(tks,vals)
             if v is not None and str(v)!="—"]
    if not pairs: return None
    ls, vs = zip(*pairs)
    try: vs = [float(v) for v in vs]
    except: return None
    fig = go.Figure(go.Bar(
        x=list(ls), y=vs, marker=dict(color=color, opacity=0.75),
        text=[f"{v:.1f}{unit}" for v in vs], textposition="outside", textfont=dict(size=9)
    ))
    fig.update_layout(**CHART_LAYOUT, height=230,
                      title=dict(text=title, font=dict(size=11,color=COLORS["muted"])),
                      showlegend=False, yaxis_ticksuffix=unit)
    return fig

with vc1:
    pe_vals = [fundamentals.get(tk,{}).get("trailingPE") for tk in available]
    f = simple_bar(available, pe_vals, "P/E Trailing por activo", COLORS["blue"])
    if f: st.plotly_chart(f, use_container_width=True)

with vc2:
    pb_vals = [fundamentals.get(tk,{}).get("priceToBook") for tk in available]
    f = simple_bar(available, pb_vals, "Price / Book", COLORS["purple"])
    if f: st.plotly_chart(f, use_container_width=True)

with vc3:
    ev_vals = [fundamentals.get(tk,{}).get("evToEbitda") for tk in available]
    f = simple_bar(available, ev_vals, "EV / EBITDA", COLORS["amber"])
    if f: st.plotly_chart(f, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
#  QUALITY & GROWTH
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">RENTABILIDAD · MÁRGENES · CRECIMIENTO</div>', unsafe_allow_html=True)
qc1, qc2, qc3 = st.columns(3)

with qc1:
    roe_vals = [fundamentals.get(tk,{}).get("returnOnEquity") for tk in available]
    f = simple_bar(available, [v*100 if v else None for v in roe_vals],
                   "Return on Equity (%)", COLORS["green"], "%")
    if f: st.plotly_chart(f, use_container_width=True)

with qc2:
    gm_vals = [fundamentals.get(tk,{}).get("grossMargins") for tk in available]
    f = simple_bar(available, [v*100 if v else None for v in gm_vals],
                   "Gross Margin (%)", COLORS["cyan"], "%")
    if f: st.plotly_chart(f, use_container_width=True)

with qc3:
    eg_vals = [fundamentals.get(tk,{}).get("earningsGrowth") for tk in available]
    eg_pct  = [v*100 if v else None for v in eg_vals]
    clean   = [(t,v) for t,v in zip(available,eg_pct) if v is not None]
    if clean:
        ls, vs = zip(*clean)
        fig_eg = go.Figure(go.Bar(
            x=list(ls), y=list(vs),
            marker_color=[COLORS["green"] if v>=0 else COLORS["red"] for v in vs],
            opacity=0.8,
            text=[f"{v:+.1f}%" for v in vs], textposition="outside", textfont=dict(size=9)
        ))
        fig_eg.add_hline(y=0, line_color=COLORS["border"])
        fig_eg.update_layout(**CHART_LAYOUT, height=230,
                              title=dict(text="Crecimiento EPS YoY (%)",
                                         font=dict(size=11,color=COLORS["muted"])),
                              showlegend=False, yaxis_ticksuffix="%")
        st.plotly_chart(fig_eg, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
#  RETURNS + CORRELATION
# ─────────────────────────────────────────────────────────────────
col_ret, col_corr = st.columns([3,2])

with col_ret:
    st.markdown('<div class="section-header">RETORNOS ACUMULADOS</div>', unsafe_allow_html=True)
    fig_ret = go.Figure()
    for i, tk in enumerate(available):
        cum = (1+all_data[tk]["Return"]).cumprod()-1
        fig_ret.add_trace(go.Scatter(
            x=cum.index, y=cum*100, name=tk,
            line=dict(color=PALETTE[i%len(PALETTE)],width=1.5)
        ))
    fig_ret.update_layout(**CHART_LAYOUT, height=280,
                           yaxis_title="Retorno (%)",
                           title=dict(text="Retorno acumulado del período",
                                      font=dict(size=11,color=COLORS["muted"])))
    st.plotly_chart(fig_ret, use_container_width=True)

with col_corr:
    st.markdown('<div class="section-header">MATRIZ DE CORRELACIÓN</div>', unsafe_allow_html=True)
    ret_mat = pd.concat({tk: all_data[tk]["Return"] for tk in available}, axis=1).dropna()
    corr    = ret_mat.corr()
    mask    = np.triu(np.ones_like(corr,dtype=bool), k=1)
    corr_d  = corr.copy(); corr_d[mask] = np.nan
    fig_corr = go.Figure(go.Heatmap(
        z=corr_d.values, x=corr.columns.tolist(), y=corr.index.tolist(),
        colorscale=[[0,COLORS["red"]],[0.5,COLORS["surface"]],[1,COLORS["green"]]],
        zmid=0, zmin=-1, zmax=1,
        text=np.where(np.isnan(corr_d.values),"",np.round(corr_d.values,2).astype(str)),
        texttemplate="%{text}", textfont=dict(size=8),
        showscale=True, colorbar=dict(thickness=8,len=0.8,tickfont=dict(size=9,color=COLORS["muted"]))
    ))
    fig_corr.update_layout(**CHART_LAYOUT, height=280)
    fig_corr.update_xaxes(tickangle=-45, tickfont=dict(size=9))
    st.plotly_chart(fig_corr, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
#  RISK ANALYTICS
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">ANALYTICS DE RIESGO</div>', unsafe_allow_html=True)
r1,r2,r3 = st.columns(3)

with r1:
    rc = port_returns.dropna()*100
    vl = np.percentile(rc, 100-conf_var)
    fig = go.Figure(go.Histogram(x=rc, nbinsx=40, marker_color=COLORS["blue"], opacity=0.7))
    fig.add_vline(x=vl, line_color=COLORS["red"], line_dash="dash",
                  annotation_text=f"VaR {conf_var}%: {vl:.2f}%",
                  annotation_font=dict(size=8,color=COLORS["red"]), annotation_position="top left")
    fig.update_layout(**CHART_LAYOUT, height=260,
                      title=dict(text="Distribución de Retornos",
                                 font=dict(size=11,color=COLORS["muted"])),
                      showlegend=False, bargap=0.02)
    st.plotly_chart(fig, use_container_width=True)

with r2:
    dd = (cum_p/cum_p.cummax()-1)*100
    fig = go.Figure(go.Scatter(
        x=dd.index, y=dd, fill="tozeroy", fillcolor="rgba(255,77,109,0.1)",
        line=dict(color=COLORS["red"],width=1)
    ))
    fig.update_layout(**CHART_LAYOUT, height=260,
                      title=dict(text="Underwater Chart (Drawdown %)",
                                 font=dict(size=11,color=COLORS["muted"])),
                      yaxis_ticksuffix="%", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with r3:
    rsh = (port_returns.rolling(21).mean()*252)/(port_returns.rolling(21).std()*np.sqrt(252))
    rc2 = [COLORS["green"] if v>=1 else COLORS["amber"] if v>=0 else COLORS["red"]
           for v in rsh.fillna(0)]
    fig = go.Figure(go.Bar(x=rsh.index, y=rsh, marker_color=rc2, opacity=0.8))
    fig.add_hline(y=1, line_dash="dot", line_color=COLORS["green"], opacity=0.5)
    fig.add_hline(y=0, line_color=COLORS["border"])
    fig.update_layout(**CHART_LAYOUT, height=260,
                      title=dict(text="Sharpe Ratio Rolling 21d",
                                 font=dict(size=11,color=COLORS["muted"])),
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
#  RSI SCANNER + RISK/RETURN
# ─────────────────────────────────────────────────────────────────
s1, s2 = st.columns([1,2])

with s1:
    st.markdown('<div class="section-header">RSI SCANNER</div>', unsafe_allow_html=True)
    rsi_s = port_df[["Ticker","RSI"]].sort_values("RSI")
    rc3 = [COLORS["red"] if v>70 else COLORS["green"] if v<30 else COLORS["blue"]
           for v in rsi_s["RSI"]]
    fig = go.Figure(go.Bar(
        x=rsi_s["RSI"], y=rsi_s["Ticker"], orientation="h",
        marker=dict(color=rc3),
        text=[f"{v:.1f}" for v in rsi_s["RSI"]],
        textposition="auto", textfont=dict(size=9)
    ))
    fig.add_vline(x=70, line_dash="dot", line_color=COLORS["red"], opacity=0.6,
                  annotation_text="Sobrecompra", annotation_font=dict(size=8,color=COLORS["red"]))
    fig.add_vline(x=30, line_dash="dot", line_color=COLORS["green"], opacity=0.6,
                  annotation_text="Sobreventa", annotation_font=dict(size=8,color=COLORS["green"]))
    fig.update_layout(**CHART_LAYOUT, height=300, xaxis=dict(range=[0,100]), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with s2:
    st.markdown('<div class="section-header">RIESGO / RETORNO</div>', unsafe_allow_html=True)
    sdata = []
    for tk in available:
        r = all_data[tk]["Return"].dropna()
        sdata.append({
            "tk": tk,
            "ret": r.mean()*252*100,
            "vol": r.std()*np.sqrt(252)*100,
            "sh":  (r.mean()*252-risk_free/100)/(r.std()*np.sqrt(252)+1e-10),
            "mv":  DEFAULT_PORTFOLIO.get(tk,{"avg_cost":100,"shares":1})["avg_cost"] *
                   DEFAULT_PORTFOLIO.get(tk,{"avg_cost":100,"shares":1})["shares"],
        })
    fig_sc = go.Figure()
    for s in sdata:
        fig_sc.add_trace(go.Scatter(
            x=[s["vol"]], y=[s["ret"]], mode="markers+text",
            marker=dict(
                size=max(12,min(38,s["mv"]/2500)),
                color=COLORS["green"] if s["sh"]>1 else COLORS["amber"] if s["sh"]>0 else COLORS["red"],
                opacity=0.85, line=dict(color=COLORS["border"],width=1)
            ),
            text=[s["tk"]], textposition="top center",
            textfont=dict(size=9,color=COLORS["text"]), name=s["tk"],
            hovertemplate=f"<b>{s['tk']}</b><br>Ret: {s['ret']:.2f}%<br>Vol: {s['vol']:.2f}%<br>Sharpe: {s['sh']:.2f}<extra></extra>"
        ))
    fig_sc.add_hline(y=0, line_color=COLORS["border"])
    fig_sc.update_layout(**CHART_LAYOUT, height=300,
                          xaxis_title="Volatilidad Anualizada (%)",
                          yaxis_title="Retorno Anualizado (%)", showlegend=False)
    st.plotly_chart(fig_sc, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
#  CRÉDITO Y LIQUIDEZ
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">CRÉDITO · LIQUIDEZ · M2</div>', unsafe_allow_html=True)
lc1, lc2 = st.columns(2)

with lc1:
    df_hy = macro_data.get("HY_OAS", pd.DataFrame())
    if not df_hy.empty:
        fig = go.Figure(go.Scatter(
            x=df_hy["Date"], y=df_hy["Value"],
            fill="tozeroy", fillcolor="rgba(255,77,109,0.07)",
            line=dict(color=COLORS["red"],width=1.5)
        ))
        fig.add_hline(y=400, line_dash="dot", line_color=COLORS["amber"],
                      annotation_text="400bp·Neutral", annotation_font=dict(size=8))
        fig.add_hline(y=600, line_dash="dot", line_color=COLORS["red"],
                      annotation_text="600bp·Estrés", annotation_font=dict(size=8))
        fig.update_layout(**CHART_LAYOUT, height=230,
                          title=dict(text="US High Yield OAS Spread (bp)",
                                     font=dict(size=11,color=COLORS["muted"])))
        st.plotly_chart(fig, use_container_width=True)

with lc2:
    df_m2 = macro_data.get("M2SL", pd.DataFrame())
    if not df_m2.empty and len(df_m2) > 12:
        df_m2["YoY"] = df_m2["Value"].pct_change(12)*100
        yoy = df_m2.dropna(subset=["YoY"])
        m2c = [COLORS["green"] if v>=0 else COLORS["red"] for v in yoy["YoY"]]
        fig = go.Figure(go.Bar(x=yoy["Date"], y=yoy["YoY"], marker_color=m2c, opacity=0.8))
        fig.add_hline(y=0, line_color=COLORS["border"])
        fig.update_layout(**CHART_LAYOUT, height=230,
                          title=dict(text="M2 Money Supply — Variación Anual (%)",
                                     font=dict(size=11,color=COLORS["muted"])),
                          yaxis_ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
#  STATISTICAL SUMMARY
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">RESUMEN ESTADÍSTICO COMPLETO</div>', unsafe_allow_html=True)

stats = []
for tk in available:
    r = all_data[tk]["Return"].dropna()
    ann_r = r.mean()*252*100
    ann_v = r.std()*np.sqrt(252)*100
    cp    = (1+r).cumprod()
    md    = ((cp/cp.cummax())-1).min()*100
    stats.append({
        "Ticker":       tk,
        "Ret. Anual":   f"{ann_r:+.2f}%",
        "Vol. Anual":   f"{ann_v:.2f}%",
        "Sharpe":       f"{(r.mean()*252-risk_free/100)/(r.std()*np.sqrt(252)+1e-10):.2f}",
        "Sortino":      f"{(r.mean()*252-risk_free/100)/(r[r<0].std()*np.sqrt(252)+1e-10):.2f}",
        "Calmar":       f"{ann_r/abs(md+1e-10):.2f}",
        "Skewness":     f"{r.skew():.3f}",
        "Kurtosis":     f"{r.kurt():.3f}",
        f"VaR{conf_var}%": f"{np.percentile(r,100-conf_var)*100:.3f}%",
        "CVaR":         f"{r[r<=np.percentile(r,(100-conf_var)/100)].mean()*100:.3f}%",
        "Max DD":       f"{md:.2f}%",
        "Win Rate":     f"{(r>0).mean()*100:.1f}%",
    })

st.dataframe(pd.DataFrame(stats), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;padding:0.4rem 0;">
  <div style="font-size:0.58rem;color:#2a3550;letter-spacing:1px;">INVESTOR INTELLIGENCE PLATFORM v3.0 · {datetime.today().year}</div>
  <div style="font-size:0.58rem;color:#2a3550;letter-spacing:1px;">⚠️ NO ES ASESORAMIENTO FINANCIERO · SOLO EDUCATIVO</div>
  <div style="font-size:0.58rem;color:#2a3550;letter-spacing:1px;">yfinance · FRED (St. Louis Fed) · alternative.me</div>
</div>
""", unsafe_allow_html=True)
