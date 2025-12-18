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
    # உங்களுக்கு பிடித்த பங்குகளை இங்கே சேர்க்கலாம்
    watchlist = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "TATAMOTORS.NS", "SBIN.NS", "INFY.NS", "ITC.NS"]
    
    st.write("Favorites:")
    for stock in watchlist:
        # Fetch minimal live data for color
        try:
            data = yf.Ticker(stock).history(period="1d")
            if not data.empty:
                price = data['Close'].iloc[-1]
                open_p = data['Open'].iloc[-1]
                change = price - open_p
                
                # கலர் லாஜிக் (பச்சை/சிவப்பு)
                color = "green" if change >= 0 else "red"
                
                # பட்டன் மூலம் பங்கைத் தேர்ந்தெடுத்தல்
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
        # Intraday 5-minute data (வேகமாக வர)
        hist_data = ticker.history(period="1d", interval="5m") 
        
        if not hist_data.empty:
            current_price = hist_data['Close'].iloc[-1]
            prev_close = hist_data['Open'].iloc[0] 
            chg = current_price - prev_close
            chg_pct = (chg / prev_close) * 100
            color_code = "green" if chg >= 0 else "red"
            
            # --- TOP INFO BAR (பெரிய எழுத்துக்கள்) ---
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
                    # Interactive Candlestick Chart (Plotly)
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
                        template="plotly_white",
                        title=f"{symbol} Intraday Chart"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_controls:
                    st.markdown("#### Place Order")
                    
                    # BUY / SELL FORM
                    qty = st.number_input("Qty", min_value=1, value=10)
                    req_margin = qty * current_price
                    st.write(f"Margin Req: ₹{req_margin:,.2f}")
                    
                    b1, b2 = st.columns(2)
                    
                    # --- BUY BUTTON logic ---
                    if b1.button("🔵 BUY", use_container_width=True):
                        if st.session_state.balance >= req_margin:
                            st.session_state.balance -= req_margin
                            st.session_state.portfolio[symbol] = st.session_state.portfolio.get(symbol, 0) + qty
                            
                            # History Update (பிழை வராத முறை)
                            trade_data = {
                                "Time": datetime.datetime.now().strftime("%H:%M"),
                                "Type": "BUY",
                                "Symbol": symbol,
                                "Qty": qty,
                                "Price": current_price
                            }
                            st.session_state.history.append(trade_data)
                            
                            st.success("Order Executed!")
                            st.rerun()
                        else:
                            st.error("Insufficient Funds")
                            
                    # --- SELL BUTTON logic ---
                    if b2.button("🔴 SELL", use_container_width=True):
                        current_qty = st.session_state.portfolio.get(symbol, 0)
                        if current_qty >= qty:
                            st.session_state.balance += req_margin
                            st.session_state.portfolio[symbol] -= qty
                            
                            if st.session_state.portfolio[symbol] == 0:
                                del st.session_state.portfolio[symbol]
                            
                            # History Update
                            trade_data = {
                                "Time": datetime.datetime.now().strftime("%H:%M"),
                                "Type": "SELL",
                                "Symbol": symbol,
                                "Qty": qty,
                                "Price": current_price
                            }
                            st.session_state.history.append(trade_data)
                            
                            st.success("Order Executed!")
                            st.rerun()
                        else:
                            st.error("Insufficient Holdings")
            
            # ----------- TAB 2: DASHBOARD (HOLDINGS) -----------
            with tab_holdings:
                st.subheader("Live Positions")
                
                if st.session_state.portfolio:
                    data_list = []
                    total_pnl = 0
                    current_val_total = 0
                    
                    for s, q in st.session_state.portfolio.items():
                        # Get live price for P&L
                        try:
                            lp = yf.Ticker(s).history(period="1d")['Close'].iloc[-1]
                            val = lp * q
                            
                            data_list.append({
                                "Symbol": s,
                                "Qty": q,
                                "LTP": round(lp, 2),
                                "Current Value": round(val, 2)
                            })
                            current_val_total += val
                        except:
                            pass
                    
                    # Show Table
                    df = pd.DataFrame(data_list)
                    st.dataframe(df, use_container_width=True)
                    
                    # Net Worth Calculation
                    net_worth = st.session_state.balance + current_val_total
                    pnl = net_worth - 1000000
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Cash Balance", f"₹{st.session_state.balance:,.2f}")
                    m2.metric("Portfolio Value", f"₹{current_val_total:,.2f}")
                    m3.metric("Total P&L", f"₹{pnl:,.2f}", delta=f"{pnl:.2f}")
                    
                    # Panic Button
                    st.markdown("---")
                    if st.button("🚨 Square Off All Positions (Exit All)"):
                        st.session_state.balance += current_val_total
                        st.session_state.portfolio = {}
                        
                        exit_data = {
                            "Time": "SYSTEM",
                            "Type": "SQUARE OFF",
                            "Symbol": "ALL",
                            "Qty": 0,
                            "Price": 0
                        }
                        st.session_state.history.append(exit_data)
                        
                        st.success("All positions closed.")
                        st.rerun()
                else:
                    st.info("No open positions. Start trading from the Chart tab.")

            # ----------- TAB 3: ORDER BOOK -----------
            with tab_orders:
                st.subheader("Trade History")
                if st.session_state.history:
                    df_hist = pd.DataFrame(st.session_state.history)
                    # Show latest first
                    st.dataframe(df_hist.iloc[::-1], use_container_width=True)
                else:
                    st.write("No trades yet.")
        
        else:
            st.error("Market Data not available currently. (Check Symbol or Market Time)")
            
    except Exception as e:
        st.error(f"Error: {e}")
import yfinance as yf
import pandas as pd
import time
import datetime

# எந்தப் பங்கு?
symbol = "RELIANCE.NS"

print(f"🤖 {symbol} அல்கோ ரோபோ தயார்...")
print("சந்தையைக் கண்காணிக்கிறது (Press Ctrl+C to stop)...\n")

def get_signal():
    # 1. கடைசி 1 நாள் டேட்டாவை 1 நிமிட இடைவெளியில் எடு
    data = yf.Ticker(symbol).history(period="1d", interval="1m")
    
    if len(data) > 5:
        # 2. கடைசி விலை (LTP)
        current_price = data['Close'].iloc[-1]
        
        # 3. தொழில்நுட்பக் குறியீடு: 5 நிமிட சராசரி (SMA 5)
        # கடைசி 5 நிமிடங்களின் சராசரி விலை
        sma_5 = data['Close'].tail(5).mean()
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        print(f"[{timestamp}] விலை: {current_price:.2f} | சராசரி (SMA): {sma_5:.2f}")
        
        # 4. முடிவு எடுக்கும் மூளை (The Logic)
        if current_price > sma_5:
            return "🟢 BUY SIGNAL (விலை சராசரியை விட அதிகம்)"
        elif current_price < sma_5:
            return "🔴 SELL SIGNAL (விலை சராசரியை விட குறைவு)"
        else:
            return "⚪ NEUTRAL (காத்திரு)"
    else:
        return "Not enough data"

# 5. ரோபோவை ஓட விடுதல் (Loop)
try:
    while True:
        signal = get_signal()
        
        # சிக்னல் வந்தால் மட்டும் பெரிய எழுத்தில் காட்டு
        if "BUY" in signal or "SELL" in signal:
            print(f"👉 {signal}")
            print("-" * 30)
        
        # 1 நிமிடம் காத்திரு (அடுத்த கேண்டிலுக்காக)
        time.sleep(60)

except KeyboardInterrupt:
    print("\n🛑 ரோபோ நிறுத்தப்பட்டது.")
