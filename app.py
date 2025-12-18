import streamlit as st
import yfinance as yf
import pandas as pd

# 1. பக்கத்தின் தலைப்பு மற்றும் அமைப்பு
st.set_page_config(page_title="My Paper Trading App", layout="wide")
st.title("📈 என் சொந்த டிரேடிங் தளம் (Paper Trading)")

# 2. ஆரம்ப செட்டிங்ஸ் (Session State)
# இது உங்கள் போர்ட்ஃபோலியோ மற்றும் பணத்தை நினைவில் வைத்துக்கொள்ள உதவும்
if 'balance' not in st.session_state:
    st.session_state.balance = 1000000.0  # ஆரம்ப மூலதனம் ₹10 லட்சம்
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}  # வாங்கிய பங்குகள்
if 'history' not in st.session_state:
    st.session_state.history = []    # டிரேடிங் வரலாறு

# --- Sidebar (பங்குகளைத் தேட) ---
st.sidebar.header("பங்கைத் தேடுங்கள்")
symbol = st.sidebar.text_input("Symbol (e.g., RELIANCE.NS)", "RELIANCE.NS").upper()

# லைவ் விலையை எடுத்தல்
try:
    stock = yf.Ticker(symbol)
    info = stock.history(period="1d")
    
    if not info.empty:
        current_price = info['Close'].iloc[-1]
        
        # --- Main Screen (முதன்மைத் திரை) ---
        col1, col2, col3 = st.columns(3)
        col1.metric("பங்கு பெயர்", symbol)
        col2.metric("தற்போதைய விலை", f"₹{current_price:.2f}")
        col3.metric("கையிருப்பு பணம்", f"₹{st.session_state.balance:,.2f}")
        
        # சார்ட் வரைதல்
        st.subheader("விலை வரைபடம் (1 Month)")
        hist_data = stock.history(period="1mo")
        st.line_chart(hist_data['Close'])
        
        # --- Buy / Sell ஆப்ஷன் ---
        st.markdown("---")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Buy Stock")
            qty_buy = st.number_input("எத்தனை பங்குகள் வாங்க வேண்டும்?", min_value=1, value=10)
            cost = qty_buy * current_price
            
            if st.button("🟢 BUY (வாங்கு)"):
                if st.session_state.balance >= cost:
                    st.session_state.balance -= cost
                    # போர்ட்ஃபோலியோவில் சேர்த்தல்
                    if symbol in st.session_state.portfolio:
                        st.session_state.portfolio[symbol] += qty_buy
                    else:
                        st.session_state.portfolio[symbol] = qty_buy
                    
                    st.session_state.history.append(f"BOUGHT {qty_buy} of {symbol} at ₹{current_price:.2f}")
                    st.success(f"வெற்றி! {symbol} வாங்கப்பட்டது.")
                    st.rerun() # திரையைப் புதுப்பிக்க
                else:
                    st.error("பணம் போதவில்லை!")

        with c2:
            st.subheader("Sell Stock")
            # நம்மிடம் அந்தப் பங்கு இருக்கிறதா எனப் பார்த்தல்
            current_qty = st.session_state.portfolio.get(symbol, 0)
            st.info(f"உங்களிடம் உள்ள பங்குகள்: {current_qty}")
            
            qty_sell = st.number_input("எத்தனை விற்க வேண்டும்?", min_value=1, max_value=current_qty if current_qty > 0 else 1, value=1)
            
            if st.button("🔴 SELL (விற்றுவிடு)"):
                if current_qty >= qty_sell:
                    sale_value = qty_sell * current_price
                    st.session_state.balance += sale_value
                    st.session_state.portfolio[symbol] -= qty_sell
                    
                    # பங்கு 0 ஆனால் லிஸ்டில் இருந்து நீக்கு
                    if st.session_state.portfolio[symbol] == 0:
                        del st.session_state.portfolio[symbol]
                        
                    st.session_state.history.append(f"SOLD {qty_sell} of {symbol} at ₹{current_price:.2f}")
                    st.success(f"வெற்றி! {symbol} விற்கப்பட்டது.")
                    st.rerun()
                else:
                    st.error("விற்கப் போதுமான பங்குகள் இல்லை!")

    else:
        st.error("தவறான Symbol. சரியான பெயரை டைப் செய்யவும் (எ.கா: TATASTEEL.NS)")

except Exception as e:
    st.error(f"பிழை: {e}")

# --- Portfolio Section (கீழே காட்டுவது) ---
st.markdown("---")
st.header("📋 உங்கள் போர்ட்ஃபோலியோ")

# போர்ட்ஃபோலியோவை அட்டவணைப்படுத்துதல்
if st.session_state.portfolio:
    portfolio_data = []
    total_value = 0
    
    for s, q in st.session_state.portfolio.items():
        # ஒவ்வொரு பங்கின் தற்போதைய விலையை எடுத்து மதிப்பிடுதல்
        ltp = yf.Ticker(s).history(period="1d")['Close'].iloc[-1]
        val = ltp * q
        portfolio_data.append({"Symbol": s, "Qty": q, "Current Price": ltp, "Total Value": val})
        total_value += val
        
    df_port = pd.DataFrame(portfolio_data)
    st.dataframe(df_port, use_container_width=True)
    
    total_assets = st.session_state.balance + total_value
    pnl = total_assets - 1000000
    
    st.metric("மொத்தச் சொத்து மதிப்பு (Net Worth)", f"₹{total_assets:,.2f}", delta=f"{pnl:,.2f}")
else:
    st.write("இன்னும் எந்தப் பங்கும் வாங்கவில்லை.")

# வரலாறு
with st.expander("வர்த்தக வரலாறு (Transaction History)"):
    for item in reversed(st.session_state.history):
        st.write(item)
