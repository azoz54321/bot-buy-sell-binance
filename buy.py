import streamlit as st
import pandas as pd
from binance.helpers import round_step_size
from binance.client import Client

# st.sidebar.title("🔐 معلومات الدخول")

# api_key = st.sidebar.text_input("API Key")
# api_secret = st.sidebar.text_input("API Secret", type="password")

# if api_key and api_secret:
#     client = Client(api_key=api_key, api_secret=api_secret)
#     try:
#         # اختبار بسيط للتأكد من أن المفاتيح صحيحة
#         client.get_account()
#         st.success("✅ تم التحقق من API بنجاح!")
#     except Exception as e:
#         st.error("❌ فشل التحقق من API - تأكد من صحة المفاتيح!")
#         st.stop()
# else:
#     st.warning("🛑 الرجاء إدخال مفاتيح API للاستمرار.")
#     st.stop()

Pkey = '4KEsUb2zuZcGHbT9wYSHcBQtCLqxBQJWmaSAphujUH5ycdCMjY7YN13RYqwMcI0G' 
Skey = '0MI1Vuz0r6AitKyn9Rm6MQ11oCK8RubuVJci3Ps9AwcbHWDxHj57zD09B266eT5M'
client = Client(api_key=Pkey, api_secret=Skey) 

# دالة تنسيق الرمز
def format_symbol(symbol):
    symbol = symbol.upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    return symbol

def pairPriceinfo(symbol):
    info = client.get_symbol_info(symbol)
    minPrice = pd.to_numeric(info['filters'][0]['minPrice'])
    return minPrice

def pairQtyinfo(symbol):
    info = client.get_symbol_info(symbol)
    minQty = pd.to_numeric(info['filters'][1]['minQty'])
    return minQty

def market_buy_order(symbol, freebusd):
    minPrice = pairPriceinfo(symbol)
    freebusd = round_step_size(freebusd, minPrice)

    order = client.order_market_buy(
        symbol=symbol,
        quoteOrderQty=freebusd
    )
    # نحصل سعر الشراء من الصفقة
    price = float(order['fills'][0]['price'])
    return price

def oco_sell_order(symbol, limit_percent, stop_percent, price):
    asset = symbol[:-4].upper()
    assetBalance = client.get_asset_balance(asset=asset)
    assetBalance = float(assetBalance['free'])
    if assetBalance == 0:
        return "لا يوجد رصيد من الأصل للبيع."

    minQty = pairQtyinfo(symbol)
    assetBalance = round_step_size(assetBalance, minQty)

    minPrice = pairPriceinfo(symbol)
    LimitPrice = float(price) * (1 + limit_percent / 100)
    LimitPrice = round_step_size(LimitPrice, minPrice)
    StopPrice = float(price) * (1 - stop_percent / 100)
    StopPrice = round_step_size(StopPrice, minPrice)

    orderoco = client.create_oco_order(
        symbol=symbol,
        side='SELL',
        quantity=assetBalance,
        price=LimitPrice,
        stopPrice=StopPrice
    )
    return f'✅ أمر بيع OCO تم بنجاح: هدف {LimitPrice} وقف خسارة {StopPrice}'

# --- واجهة Streamlit ---
st.title("🤖 بوت تداول العملات الرقمية")

raw_symbol = st.text_input("ادخل رمز العملة (مثال: BNB):")
symbol = format_symbol(raw_symbol)

busd_amount = st.number_input("ادخل مبلغ الشراء (BUSD):", min_value=1.0)

take_profit = st.number_input("ادخل نسبة جني الربح %:", min_value=0.1, value=10.0)
stop_loss = st.number_input("ادخل نسبة وقف الخسارة %:", min_value=0.1, value=5.0)

if st.button("✅ تنفيذ شراء + إعداد بيع OCO تلقائي"):
    try:
        buy_price = market_buy_order(symbol, busd_amount)
        st.success(f"تم الشراء بسعر {buy_price}")
        sell_result = oco_sell_order(symbol, take_profit, stop_loss, buy_price)
        st.success(sell_result)
    except Exception as e:
        st.error(f"حدث خطأ: {e}")



# لتشغيل الكود خش على المجلد وبعدها حط هاذا الامر streamlit run calcoletor.py

