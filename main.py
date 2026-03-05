import ccxt, time, pandas as pd, pandas_ta as ta, requests, json
from datetime import datetime, timedelta

# --- [ إعدادات الاتصال ] ---
MY_TOKEN = '8681138761:AAEUVPSzkPzrwLMGcwotBbISQ3D1b-QZds8'
MY_ID = '5809146953'
# روابط الجداول (يمكنك توحيدهما أو فصلهما)
SHEET_SPOT = 'رابط_جدول_السبوت'
SHEET_FUTURES = 'رابط_جدول_الفيوتشرز'

# إعدادات المنصة
spot_ex = ccxt.bitget({'options': {'defaultType': 'spot'}})
fut_ex = ccxt.bitget({'options': {'defaultType': 'swap'}})

def send_telegram(msg):
    try: requests.get(f"https://api.telegram.org/bot{MY_TOKEN}/sendMessage?chat_id={MY_ID}&text={msg}&parse_mode=Markdown")
    except: pass

def get_signals(ex, symbol, is_futures=False):
    try:
        bars = ex.fetch_ohlcv(symbol, timeframe='15m', limit=200)
        df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        df['EMA200'] = ta.ema(df['c'], length=200)
        st = ta.supertrend(df['h'], df['l'], df['c'], 10, 3)['SUPERTd_10_3.0']
        df['RSI'] = ta.rsi(df['c'], length=14)
        
        c, ema, s, r = df['c'].iloc[-1], df['EMA200'].iloc[-1], st.iloc[-1], df['RSI'].iloc[-1]
        
        # إشارة صعود (تصلح للسبوت والفيوتشرز)
        if c > ema and s == 1 and 45 < r < 70: return "LONG", c
        # إشارة هبوط (للفيوتشرز فقط)
        if is_futures and c < ema and s == -1 and 30 < r < 55: return "SHORT", c
    except: return None, 0
    return None, 0

print("🚀 Integrated Sniper Bot Started on Render!")
send_telegram("🛰️ *تم تشغيل النظام الموحد (سبوت + فيوتشرز)*\nالنظام الآن يعمل بشكل مستقل 24/7.")

while True:
    try:
        # 1. فحص السبوت (أعلى 20 عملة)
        spot_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'AVAX/USDT', 'XRP/USDT'] # يمكنك زيادتها
        for s in spot_symbols:
            sig, p = get_signals(spot_ex, s)
            if sig == "LONG":
                send_telegram(f"💎 *فرصة سبوت:* `{s}` بسعر `{p}`")
                # كود الإرسال للجدول هنا...

        # 2. فحص الفيوتشرز (أعلى 20 عملة)
        fut_symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'SOL/USDT:USDT', 'NEAR/USDT:USDT']
        for s in fut_symbols:
            sig, p = get_signals(fut_ex, s, is_futures=True)
            if sig:
                send_telegram(f"⚡ *إشارة فيوتشرز {sig}:* `{s}` بسعر `{p}`")
                # كود الإرسال للجدول هنا...

        time.sleep(60) # فحص كل دقيقة
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(30)
