import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import datetime

# 1. Page Config & CSS (Zerodha Style)
st.set_page_config(page_title="Kite Clone - Paper Trading", layout="wide", page_icon="🪁")

# Custom CSS for Zerodha Look
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 20px;
        color: #444;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 4px;
        font-weight: 500;
        width: 100%;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: white;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State Initialization (Logic)
if 'balance' not in st.session_state:
    st.session_state.balance = 1000000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'history' not in st.session_state:
    st.session_state.history = []
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = "RELIANCE.NS" # Default

# --- HEADER ---
c1, c2 = st.columns([1, 10])
with c1:
    st.markdown("### 🪁 Kite")
with c2:
    st.markdown(f"**Funds Available: ₹{st.session_state.balance:,.2f}**")
st.markdown("---")

# --- MAIN LAYOUT ---
left_panel, right_panel = st.columns([3, 9])

# ================= LEFT PANEL: WATCHLIST & SEARCH =================
with left_panel:
    st.subheader("Watchlist")
    
    # Stock Search
    search_symbol = st.text_input("Search (e.g., INFY.NS)", value=st.session_state.selected_stock).upper()
    if st.button("Load Stock"):
        st.session_state.selected_stock = search_symbol
        st.rerun()

    st.markdown("---")
    
    # Pre-defined Watchlist (Clickable)
    watchlist = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "TATAMOTORS.NS", "SBIN.NS"]
    st.write("Favorites:")
    for stock in watchlist:
        # Fetch minimal live data for color
        try:
            data = yf.Ticker(stock).history(period="1d")
            if not data.empty:
                price = data['Close'].iloc[-1]
                open_p = data['Open'].iloc[-1]
                change = price - open_p
                color = "green" if change >= 0 else "red"
                
                # Simple display
                if st.button(f"{stock}  |  ₹{price:.1f}", key=stock):
                    st.session_state.selected_stock = stock
                    st.rerun()
        except:
            st.write(stock)

# ================= RIGHT PANEL: TABS =================
with right_panel:
    # Selected Stock Logic
    symbol = st.session_state.selected_stock
    
    # Fetch Data
    try:
        ticker = yf.Ticker(symbol)
        # Intraday 1-minute data for chart accuracy
        hist_data = ticker.history(period="1d", interval="5m") 
        
        if not hist_data.empty:
            current_price = hist_data['Close'].iloc[-1]
            prev_close = hist_data['Open'].iloc[0] 
            chg = current_price - prev_close
            chg_pct = (chg / prev_close) * 100
            color_code = "green" if chg >= 0 else "red"
            
            # --- TOP INFO BAR ---
            st.markdown(f"""
            ## {symbol} 
            <span style='font-size:24px; color:{color_code}'>₹{current_price:.2f}</span> 
            <small style='color:{color_code}'>({chg:.2f} / {chg_pct:.2f}%)</small>
            """, unsafe_allow_html=True)
            
            # --- TABS ---
            tab_chart, tab_holdings, tab_orders = st.tabs(["📈 Chart & Trade", "📊 Dashboard (P&L)", "📋 Order Book"])
            
            # ----------- TAB 1: CHART & TRADE -----------
            with tab_chart:
                col_graph, col_controls = st.columns([3, 1])
                
                with col_graph:
                    # Interactive Candlestick Chart
                    fig = go.Figure(data=[go.Candlestick(
                        x=hist_data.index,
                        open=hist_data['Open'],
                        high=hist_data['High'],
                        low=hist_data['Low'],
                        close=hist_data['Close'],
                        name=symbol
                    )])
                    fig.update_layout(
                        height=500, 
                        margin=dict(l=20, r=20, t=20, b=20),
                        xaxis_rangeslider_visible=False,
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_controls:
                    st.markdown("#### Place Order")
                    
                    # BUY / SELL FORM
                    qty = st.number_input("Qty", min_value=1, value=10)
                    req_margin = qty * current_price
                    st.write(f"Margin Req: ₹{req_margin:,.2f}")
                    
                    b1, b2 = st.columns(2)
                    {
    "Time": ...,
    "Type": "BUY",
    ...
}
                    
