import streamlit as st
# from googletrans import Translator
from datetime import datetime, time

# 1. SETUP & BRANDING
st.set_page_config(page_title="RH Modern Building Management", layout="wide")
st.sidebar.image("logo.png", width='stretch')
st.sidebar.title("RH EXECUTIVE PANEL")

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
    # Translation temporarily disabled
    return text
menu = st.sidebar.radio("Navigation", [
    "🏠 Customer Booking", 
    "🤝 Partner Portal", 
    "📋 Supervisor Portal",
    "⭐ Membership & Points",
    "🛡️ Admin Dashboard"
])

# 2. DATABASE & SEASONAL LOGIC
LOCATIONS = ["Seremban 2", "Garden Homes", "Sendayan", "Nilai", "Putrajaya", "Cyberjaya", "Cheras", "Puchong", "Gaarden Homes", "Seremban 2", "Sendayan", "Suriaman", "Tiara", "Adira", "Bandar Sri Sendayan", "Kota Warisan", "Sepang", "KLIA1", "KLIA2", "Rasah Kemayan", "Port Dickson"]
RATES_RESIDENTIAL = {
    "Sweeping, Vacuuming and Mopping": {"2 bedroom Apartment": 15.0, "3 bedroom Apartment": 18.0, "Single storey 3 room": 20.0, "Single storey 4 room": 25.0, "Double storey 4 room": 35.0},
    "Sweeping, Vacuuming, Mopping and High & Low Dusting": {"2 bedroom Apartment": 20.0, "3 bedroom Apartment": 23.0, "Single storey 3 room": 25.0, "Single storey 4 room": 30.0, "Double storey 4 room": 40.0},
    "Sweeping, Vacuuming, Mopping, High & Low Dusting and Toilet Cleaning": {"2 bedroom Apartment": 25.0, "3 bedroom Apartment": 28.0, "Single storey 3 room": 30.0, "Single storey 4 room": 35.0, "Double storey 4 room": 45.0}
}
IRON_RATES = {"Short sleeve shirt": 2.0, "Long sleeve shirt": 2.5, "Trousers": 2.5, "Blouse": 4.5, "Pants": 4.0, "T-Shirt": 1.5}

# FESTIVAL DISCOUNT SETTINGS
FESTIVAL_NAME = "Ramadan & Raya Special"
FESTIVAL_DISCOUNT = 5.0 # MYR 5.00 Off

# 3. CUSTOMER BOOKING
if menu == "🏠 Customer Booking":
    st.title(t("✨ RH Cleaning Services"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    col_main, col_summary = st.columns([2, 1])
    
    with col_main:
        st.subheader(t("📍 1. Logistics"))
        greeting = st.selectbox(t("Greeting"), ["Mr", "Mrs", "Puan", "Sir", "Dr", "Tan Sri", "Dato", "Madam"])
        c_name = st.text_input(t("Customer Name"))
        c_phone = st.text_input(t("Customer Contact Number"))
        c_dob = st.date_input(t("Date of Birth"))
        c_address = st.text_area(t("Full House Address"))
        c_postcode = st.text_input(t("Postcode"))
        
        st.subheader(t("🧹 2. Service Selection"))
        bundle = st.selectbox(t("Select Service Level"), list(RATES_RESIDENTIAL.keys()))
        prop = st.selectbox(t("Select Property Type"), list(RATES_RESIDENTIAL[bundle].keys()))
        min_hours = {"Sweeping, Vacuuming and Mopping": 2, "Sweeping, Vacuuming, Mopping and High & Low Dusting": 3, "Sweeping, Vacuuming, Mopping, High & Low Dusting and Toilet Cleaning": 4}[bundle]
        hours = st.number_input(t("Number of Hours"), min_value=min_hours, max_value=12, value=max(2, min_hours))
        
        tabs = st.tabs(["Add-ons", "Ironing", "Schedule & Feedback"])
        with tabs[0]:
            fridge = st.radio(t("Fridge Cleaning"), [t("None"), t("Single door (+MYR 75)"), t("Double door (+MYR 145)")], horizontal=True)
            car_porch = st.checkbox(t("Car Porch Cleaning (+MYR 55)"))
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
        car_porch_cost = 55 if car_porch else 0
        subtotal = base_price + f_map[fridge] + iron_total + car_porch_cost
        # Apply Festival Discount
        discount_amount = FESTIVAL_DISCOUNT
        grand_total = subtotal - discount_amount
        st.write(f"{t('Subtotal')} ({hours} {t('hour')}{t('s') if hours > 1 else ''}): MYR {subtotal:.2f}")
        st.success(f"🎊 {t(FESTIVAL_NAME)}: -MYR {discount_amount:.2f}")
        st.metric(t("Total Bill"), f"MYR {grand_total:.2f}")
        st.write(t("Laundry damaged linen disclaimer: shall not exceed 20 times of the cleaning charges"))
        if st.button(t("Confirm Booking")):
            st.success(t("✅ Booking and Feedback Logged!"))
            st.session_state['booking_confirmed'] = True
        
        if 'booking_confirmed' in st.session_state and st.session_state['booking_confirmed']:
            rating = st.slider(t("Rate the service (1-5 stars)"), 1, 5, 5)
            st.write(f"{t('Thank you for your rating:')} {rating} ⭐")

# 4. PARTNER PORTAL
elif menu == "🤝 Partner Portal":
    st.title(t("🤝 Partner Job Inbox"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    
    # Registration Section
    st.subheader(t("Registration"))
    with st.expander(t("Complete Registration")):
        nric_passport = st.file_uploader(t("Upload NRIC or Passport"))
        gender = st.selectbox(t("Gender"), ["Male", "Female"])
        p_dob = st.date_input(t("Date of Birth"))
        p_contact = st.text_input(t("Contact Number"))
        next_kin_name = st.text_input(t("Next of Kin Name"))
        next_kin_contact = st.text_input(t("Next of Kin Contact"))
        banking_details = st.text_input(t("Banking Details for Withdrawal"))
        if st.button(t("Register")):
            st.success(t("Registration Complete!"))
    
    # Job Details
    st.subheader(t("Upcoming Job"))
    st.write(f"*{t('Service Type')}:* Sweeping, Vacuuming and Mopping")
    st.write(f"*{t('Distance to Site')}:* 5 KM (30 mins)")
    st.write(f"*{t('Customer Name')}:* {c_name if 'c_name' in locals() else 'Siti Aminah'}")
    st.write(f"*{t('Contact')}:* {c_phone if 'c_phone' in locals() else '012-3456789'}")
    st.write(f"*{t('Address')}:* {c_address if 'c_address' in locals() else 'Garden Homes, Seremban'}")
    
    # Earnings
    st.subheader(t("Earnings"))
    st.metric(t("Daily Earnings"), "MYR 135.00")
    st.metric(t("Weekly Earnings"), "MYR 945.00")
    st.metric(t("Monthly Earnings"), "MYR 3780.00")
    st.metric(t("Your 90% Payout"), f"MYR {135 * 0.9:.2f}")
    
    # Status
    online_status = st.radio(t("Status"), ["Online", "Offline"], index=0)
    st.write(f"Current Status: {online_status}")

# 5. SUPERVISOR PORTAL (REPLY FUNCTION ADDED)
elif menu == "📋 Supervisor Portal":
    st.title(t("📋 Supervisor Control"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    
    # Banking Details
    st.subheader(t("Banking Details"))
    s_banking = st.text_input(t("Banking Details for Withdrawal"))
    
    # Earnings
    st.subheader(t("Earnings"))
    st.metric(t("Daily Commission"), "MYR 1.50")
    st.metric(t("Weekly Commission"), "MYR 10.50")
    st.metric(t("Monthly Commission"), "MYR 42.00")
    
    # Cleaner Movements
    st.subheader(t("Cleaner Movements"))
    st.write("**Cleaner 1:** In Progress - Garden Homes")
    st.write("**Cleaner 2:** Pending - Sendayan")
    st.write("**Cleaner 3:** Traveling - 2 KM away")
    st.write("**Cleaner 4:** Online - Available")
    st.write("**Cleaner 5:** Offline")
    
    st.subheader(t("📬 Customer Feedback & Complaints"))
    with st.expander(t("View Pending Feedback from: En. Ahmad")):
        st.write(f"*{t('Customer Message')}:* '{t('Cleaner missed the kitchen floor.')}'")
        reply_options = st.selectbox(t("Resolution"), ["Future Discount Coupon - MYR 10", "Cleaner to Redo", "Sincerely Apologize Notes for this One Off Incident"])
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
        st.subheader(t("Earnings (Minus Partners & Supervisor)"))
        st.metric(t("Daily Earnings"), "MYR 13.50")
        st.metric(t("Weekly Earnings"), "MYR 94.50")
        st.metric(t("Monthly Earnings"), "MYR 378.00")
        
        st.subheader(t("90/10 Financial Split"))
        st.metric(t("Partner Share"), "MYR 135.00")
        st.metric(t("Company Gross (Before Supervisor Comm)"), "MYR 15.00")
        
        st.subheader(t("Area Demand"))
        st.write("**Most Demanded Areas:**")
        st.write("- Seremban 2: 45 bookings")
        st.write("- Garden Homes: 38 bookings")
        st.write("- Putrajaya: 32 bookings")
