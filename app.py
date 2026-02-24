import streamlit as st
from googletrans import Translator
from datetime import datetime, time

# 1. SETUP & BRANDING
st.set_page_config(page_title="RH Modern Building Management", layout="wide")
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("RH EXECUTIVE PANEL")
translator = Translator()
lang_codes = {
    "Bahasa Malaysia": "ms",
    "English": "en",
    "Chinese": "zh-cn",
    "Nepal": "ne",
    "Myanmar": "my",
    "Pakistan": "ur",
    "Tamil": "ta"
}

language_options = [
    "Bahasa Malaysia",
    "English",
    "Chinese",
    "Nepal",
    "Myanmar",
    "Pakistan",
    "Tamil"
]
selected_language = st.sidebar.selectbox("Select Language", language_options, index=1)
st.sidebar.write(f"Selected Language: {selected_language}")
def t(text):
    code = lang_codes.get(selected_language, "en")
    if code == "en":
        return text
    try:
        return translator.translate(text, dest=code).text
    except Exception:
        return text
menu = st.sidebar.radio("Navigation", [
    "🏠 Customer Booking", 
    "🤝 Partner Portal", 
    "📋 Supervisor Portal",
    "⭐ Membership & Points",
    "🛡️ Admin Dashboard"
])

# 2. DATABASE & SEASONAL LOGIC
LOCATIONS = ["Seremban 2", "Garden Homes", "Sendayan", "Nilai", "Putrajaya", "Cyberjaya", "Cheras", "Puchong"]
RATES_RESIDENTIAL = {
    "Sweeping, Vacuuming and Mopping": {"2 bedroom Apartment": 15.0, "3 bedroom Apartment": 18.0, "Single storey 3 room": 20.0, "Single storey 4 room": 25.0, "Double storey 4 room": 35.0},
    "Sweeping, Vacuuming, Mopping and High & Low Dusting": {"2 bedroom Apartment": 20.0, "3 bedroom Apartment": 23.0, "Single storey 3 room": 25.0, "Single storey 4 room": 30.0, "Double storey 4 room": 40.0},
    "Sweeping, Vacuuming, Mopping, High & Low Dusting and Toilet Cleaning": {"2 bedroom Apartment": 25.0, "3 bedroom Apartment": 28.0, "Single storey 3 room": 30.0, "Single storey 4 room": 35.0, "Double storey 4 room": 45.0}
}
IRON_RATES = {"Short sleeve shirt": 2.0, "Long sleeve shirt": 2.5, "Trousers": 2.5, "Blouse": 4.5, "Pants": 4.0, "T-Shirt": 1.5}

# FESTIVAL DISCOUNT SETTINGS
FESTIVAL_NAME = "Ramadan & Raya Special"
FESTIVAL_DISCOUNT = 0.10 # 10% Off

# 3. CUSTOMER BOOKING
if menu == "🏠 Customer Booking":
    st.title(t("✨ RH Cleaning Services"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    col_main, col_summary = st.columns([2, 1])
    
    with col_main:
        st.subheader(t("📍 1. Logistics"))
        c_name = st.text_input(t("Customer Name"))
        c_phone = st.text_input(t("Customer Contact Number"))
        c_address = st.text_area(t("Full House Address"))
        
        st.subheader(t("🧹 2. Service Selection"))
        bundle = st.selectbox(t("Select Service Level"), list(RATES_RESIDENTIAL.keys()))
        prop = st.selectbox(t("Select Property Type"), list(RATES_RESIDENTIAL[bundle].keys()))
        hours = st.number_input(t("Number of Hours"), min_value=1, max_value=12, value=2)
        
        tabs = st.tabs(["Add-ons", "Ironing", "Schedule & Feedback"])
        with tabs[0]:
            fridge = st.radio(t("Fridge Cleaning"), [t("None"), t("Single door (+MYR 75)"), t("Double door (+MYR 145)")], horizontal=True)
        with tabs[1]:
            iron_qty = {item: st.number_input(t(item), min_value=0) for item in IRON_RATES}
        with tabs[2]:
            b_date = st.date_input(t("Date"))
            customer_feedback = st.text_area(t("Special Instructions / Feedback for Previous Service"))

    with col_summary:
        st.subheader(t("💰 Summary"))
        f_map = {t("None"): 0, t("Single door (+MYR 75)"): 75, t("Double door (+MYR 145)"): 145}
        base_price = RATES_RESIDENTIAL[bundle][prop] * hours
        iron_total = sum(iron_qty[item] * IRON_RATES[item] for item in IRON_RATES)
        subtotal = base_price + f_map[fridge] + iron_total
        # Apply Festival Discount
        discount_amount = subtotal * FESTIVAL_DISCOUNT
        grand_total = subtotal - discount_amount
        st.write(f"{t('Subtotal')} ({hours} {t('hour')}{t('s') if hours > 1 else ''}): MYR {subtotal:.2f}")
        st.success(f"🎊 {t(FESTIVAL_NAME)}: -MYR {discount_amount:.2f}")
        st.metric(t("Total Bill"), f"MYR {grand_total:.2f}")
        if st.button(t("Confirm Booking")):
            st.success(t("✅ Booking and Feedback Logged!"))

# 4. PARTNER PORTAL
elif menu == "🤝 Partner Portal":
    st.title(t("🤝 Partner Job Inbox"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    st.write(f"*{t('Customer Name')}:* {c_name if 'c_name' in locals() else 'Siti Aminah'}")
    st.write(f"*{t('Contact')}:* {c_phone if 'c_phone' in locals() else '012-3456789'}")
    st.write(f"*{t('Address')}:* {c_address if 'c_address' in locals() else 'Garden Homes, Seremban'}")
    st.metric(t("Your 90% Payout"), f"MYR {150 * 0.9:.2f}")

# 5. SUPERVISOR PORTAL (REPLY FUNCTION ADDED)
elif menu == "📋 Supervisor Portal":
    st.title(t("📋 Supervisor Control"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    st.metric(t("Daily Commission"), "MYR 1.50")
    st.subheader(t("📬 Customer Feedback & Complaints"))
    with st.expander(t("View Pending Feedback from: En. Ahmad")):
        st.write(f"*{t('Customer Message')}:* '{t('Cleaner missed the kitchen floor.')}'")
        supervisor_reply = st.text_area(t("Type your reply/resolution here:"))
        if st.button(t("Send Reply to Customer")):
            st.success(t("Reply sent to customer email & points notification."))

# 6. MEMBERSHIP & POINTS (RESTORED)
elif menu == "⭐ Membership & Points":
    st.title(t("⭐ RH Gold Membership"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(t("Your Total Points"), "1,250 PTS")
    with col2:
        st.write("### " + t("Rewards Available"))
        st.write(f"- 500 PTS: {t('Free Fridge Cleaning')}")
        st.write(f"- 1000 PTS: {t('MYR 20 Voucher')}")
    st.write("---")
    st.subheader(t("💬 Message from Supervisor"))
    st.info(t("No new replies at this time."))

# 7. ADMIN DASHBOARD
elif menu == "🛡️ Admin Dashboard":
    st.title(t("🛡️ Admin Suite"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    if st.text_input(t("Key"), type="password") == "RH2026":
        st.subheader(t("90/10 Financial Split"))
        st.metric(t("Partner Share"), "MYR 135.00")
        st.metric(t("Company Gross (Before Supervisor Comm)"), "MYR 15.00")
