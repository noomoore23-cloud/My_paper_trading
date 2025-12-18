import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go  # வரைபடத்திற்கான புதிய லைப்ரரி

# 1. பக்கத்தின் தலைப்பு மற்றும் அமைப்பு
st.set_page_config(page_title="My Pro Trading App", layout="wide")
st.title("📈 என் சொந்த டிரேடிங் தளம் (Pro Version)")

# 2. ஆரம்ப செட்டிங்ஸ்
if 'balance' not in st.session_state:
    st.session_state.balance = 1000000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Sidebar ---
st.sidebar.header("பங்கைத் தேடுங்கள்")
symbol = st.sidebar.text_input("Symbol", "RELIANCE.NS").upper()

# --- Time Frame தேர்வு (புதிய வசதி) ---
# இன்ட்ராடே செய்வோருக்கு 5 நிமிடம், முதலீட்டாளருக்கு 1 நாள்
time_frame = st.sidebar.selectbox("கால அளவு (Time Frame)", ["1d", "5d", "1mo", "3mo", "1y"])
interval_map = {"1d": "5m", "5d": "15m", "1mo": "1d", "3mo": "1d", "1y": "1wk"}
interval = interval_map[time_frame]

try:
    stock = yf.Ticker(symbol)
    # இன்ட்ராடே சார்ட் பார்க்க interval கொடுக்கிறோம்
    hist_data = stock.history(period=time_frame, interval=interval)
    
    if not hist_data.empty:
        current_price = hist_data['Close'].iloc[-1]
        
        # --- Main Screen ---
        col1, col2, col3 = st.columns(3)
        col1.metric("பங்கு பெயர்", symbol)
        col2.metric("தற்போதைய விலை", f"₹{current_price:.2f}")
        col3.metric("கையிருப்பு பணம்", f"₹{st.session_state.balance:,.2f}")
        
        # --- CANDLESTICK CHART (முக்கிய மாற்றம்) ---
        st.subheader(f"🕯️ மெழுகுவர்த்தி வரைபடம் ({symbol})")
        
        fig = go.Figure(data=[go.Candlestick(
            x=hist_data.index,
            open=hist_data['Open'],
            high=hist_data['High'],
            low=hist_data['Low'],
            close=hist_data['Close'],
            name=symbol
        )])
        
        # சார்ட் டிசைன்
        fig.update_layout(
            xaxis_rangeslider_visible=False, # கீழே உள்ள ஸ்லைடரை மறைக்க
            height=500,
            title=f"{symbol} Price Movement ({time_frame})",
            template="plotly_dark" # இருண்ட பின்னணி (Dark Mode)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # --- Buy / Sell ஆப்ஷன் ---
        st.markdown("---")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Buy (Long)")
            qty_buy = st.number_input("வாங்கும் அளவு", min_value=1, value=10)
            cost = qty_buy * current_price
            
            if st.button("🟢 BUY"):
                if st.session_state.balance >= cost:
                    st.session_state.balance -= cost
                    if symbol in st.session_state.portfolio:
                        st.session_state.portfolio[symbol] += qty_buy
                    else:
                        st.session_state.portfolio[symbol] = qty_buy
                    
                    st.session_state.history.append(f"BOUGHT {qty_buy} {symbol} @ ₹{current_price:.2f}")
                    st.success(f"வெற்றி! {symbol} வாங்கப்பட்டது.")
                    st.rerun()
                else:
                    st.error("பணம் போதவில்லை!")

        with c2:
            st.subheader("Sell (Short/Exit)")
            current_qty = st.session_state.portfolio.get(symbol, 0)
            st.info(f"கையிருப்பு: {current_qty}")
            
            qty_sell = st.number_input("விற்கும் அளவு", min_value=1, max_value=current_qty if current_qty > 0 else 1, value=1)
            
            if st.button("🔴 SELL"):
                if current_qty >= qty_sell:
                    sale_value = qty_sell * current_price
                    st.session_state.balance += sale_value
                    st.session_state.portfolio[symbol] -= qty_sell
                    
                    if st.session_state.portfolio[symbol] == 0:
                        del st.session_state.portfolio[symbol]
                        
                    st.session_state.history.append(f"SOLD {qty_sell} {symbol} @ ₹{current_price:.2f}")
                    st.success(f"வெற்றி! {symbol} விற்கப்பட்டது.")
                    st.rerun()
                else:
                    st.error("விற்கப் போதுமான பங்குகள் இல்லை!")

    else:
        st.error("தகவல் கிடைக்கவில்லை.")

except Exception as e:
    st.error(f"பிழை: {e}")

# --- Portfolio & P&L ---
st.markdown("---")
st.header("📋 உங்கள் இன்ட்ராடே நிலவரம்")

if st.button("🔄 Refresh P&L"):
    st.rerun()

if st.session_state.portfolio:
    portfolio_data = []
    current_portfolio_value = 0
    
    for s, q in st.session_state.portfolio.items():
        try:
            live_data = yf.Ticker(s).history(period="1d")
            if not live_data.empty:
                ltp = live_data['Close'].iloc[-1]
                val = ltp * q
                portfolio_data.append({"Symbol": s, "Qty": q, "LTP": round(ltp, 2), "Value": round(val, 2)})
                current_portfolio_value += val
        except:
            pass
        
    df_port = pd.DataFrame(portfolio_data)
    st.dataframe(df_port, use_container_width=True)
    
    net_worth = st.session_state.balance + current_portfolio_value
    pnl = net_worth - 1000000
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Cash Balance", f"₹{st.session_state.balance:,.2f}")
    c2.metric("Portfolio Value", f"₹{current_portfolio_value:,.2f}")
    c3.metric("Total Profit/Loss", f"₹{pnl:,.2f}", delta=f"{pnl:,.2f}")

    if st.button("🚨 CLOSE ALL POSITIONS"):
        st.session_state.balance += current_portfolio_value
        st.session_state.portfolio = {} 
        st.session_state.history.append(f"CLOSED ALL POSITIONS. Final P&L: ₹{pnl:.2f}")
        st.success("All Sold!")
        st.rerun()
else:
    st.info("No open positions.")
