import streamlit as st
from datetime import datetime, time
import pandas as pd

# 1. SETUP & BRANDING
st.set_page_config(page_title="RH Modern Building Management", layout="wide")
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("RH EXECUTIVE PANEL")

menu = st.sidebar.radio("Navigation", [
    "🏠 Customer Booking", 
    "🤝 Partner Hub (Cleaner)", 
    "📋 Supervisor Command",
    "⭐ Membership & Loyalty",
    "🛡️ Admin Suite"
])

# 2. MASTER DATABASE
LOCATIONS = ["Seremban 2", "Garden Homes", "Sendayan", "Nilai", "Putrajaya", "Cyberjaya", "Cheras", "Puchong"]
RATES_RESIDENTIAL = {
    "Basic (Vacuum/Mop)": {"Apartment": 15.0, "1-Storey": 20.0, "2-Storey": 35.0},
    "Premium (Dusting)": {"Apartment": 20.0, "1-Storey": 25.0, "2-Storey": 40.0},
    "Elite (Toilet/All)": {"Apartment": 25.0, "1-Storey": 30.0, "2-Storey": 45.0}
}
IRON_RATES = {"Shirt": 2.0, "Trousers": 2.5, "Blouse": 4.5, "T-Shirt": 1.5}

# 3. CUSTOMER BOOKING (FIXED CAR PORCH & DISCLAIMER)
if menu == "🏠 Customer Booking":
    st.title("✨ RH Cleaning Services")
    col_main, col_summary = st.columns([2, 1])
    
    with col_main:
        st.subheader("👤 Client Details")
        c_name = st.text_input("Full Name")
        c_address = st.text_area("Full House Address")
        is_repeat = st.checkbox("Repeat Customer? (Points tracking enabled)")
        
        tabs = st.tabs(["🧹 Cleaning Service", "👔 Ironing & Laundry", "📅 Logistics"])
        with tabs[0]:
            bundle = st.selectbox("Service Tier", list(RATES_RESIDENTIAL.keys()))
            prop = st.selectbox("Property", list(RATES_RESIDENTIAL[bundle].keys()))
            st.markdown("---")
            st.subheader("🏠 Specialized Add-ons")
            # FIXED: Car Porch cleaning explicitly added
            car_porch = st.checkbox("Car Porch Deep Wash (+MYR 45.00)")
            fridge = st.checkbox("Fridge Internal Cleaning (+MYR 75.00)")
            
        with tabs[1]:
            st.write("### Laundry/Ironing")
            iron_qty = {item: st.number_input(f"{item}", min_value=0) for item in IRON_RATES}
            st.info("📜 *Laundry Liability Disclaimer*")
            st.caption("RH Management is committed to high-quality care. However, we accept no liability for shrinkage, color bleeding, or damage to weak fabrics. Claims for damaged articles are strictly capped at 20x the individual ironing fee for said item. By checking below, you agree to these professional terms.")
            iron_agree = st.checkbox("I accept the Laundry Damage Disclaimer")
        with tabs[2]:
            b_date = st.date_input("Date")
            b_time = st.time_input("Time")

    with col_summary:
        st.subheader("💰 Total Summary")
        base = RATES_RESIDENTIAL[bundle][prop] * 2
        addons = (45 if car_porch else 0) + (75 if fridge else 0)
        iron_total = sum(iron_qty[item] * IRON_RATES[item] for item in IRON_RATES)
        grand_total = base + addons + iron_total
        
        st.metric("Amount to Pay", f"MYR {grand_total:.2f}")
        if st.button("Proceed to Assignment"):
            st.success("Booking Assigned! Welcome back!" if is_repeat else "New Customer Logged!")

# 4. PARTNER HUB (ENHANCED EARNINGS & RATINGS)
elif menu == "🤝 Partner Hub (Cleaner)":
    st.title("🤝 Partner Professional Hub")
    
    # ONLINE/OFFLINE TOGGLE
    status = st.toggle("Duty Status (Online/Offline)", value=True)
    st.write(f"Status: {'🟢 Active' if status else '🔴 Inactive'}")
    
    # JOB DETAILS & ACHIEVEMENTS
    c1, c2, c3 = st.columns(3)
    c1.metric("Lifetime Rating", "⭐ 4.9/5.0")
    c2.metric("Total Jobs Done", "124")
    c3.metric("Achievement", "🎖️ Top Tier")
    
    # EARNINGS WALLET
    st.subheader("💰 Earnings Wallet (90% Payout)")
    w1, w2, w3 = st.columns(3)
    w1.metric("Daily Salary", "MYR 135.00")
    w2.metric("Weekly Salary", "MYR 945.00")
    w3.metric("Monthly Salary", "MYR 3,780.00")
    
    st.write("---")
    st.subheader("📬 Current Assigned Job")
    st.info("Customer: En. Ahmad | Address: Garden Homes, S2 | Time: 10:00 AM")
    if st.button("Confirm Check-In (Notify Supervisor)"):
        st.success("Live Location Shared with Supervisor Command.")

# 5. SUPERVISOR COMMAND (LOCATION & ADD CLEANER)
elif menu == "📋 Supervisor Command":
    st.title("📋 Operations Command Center")
    
    # ADD CLEANERS FUNCTION
    with st.sidebar.expander("➕ Register New Cleaner"):
        new_name = st.text_input("Cleaner Full Name")
        new_phone = st.text_input("Cleaner WhatsApp")
        if st.button("Add to Fleet"):
            st.success(f"Cleaner {new_name} added to Database!")

    # MULTI-SUPERVISOR COMMISSION TRACKING
    st.subheader("📈 Multi-Supervisor Commissions")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Sup. 1 (Daily)", "MYR 15.00")
    sc2.metric("Sup. 1 (Weekly)", "MYR 105.00")
    sc3.metric("Sup. 1 (Monthly)", "MYR 450.00")
    
    # LIVE LOCATION TRACKING
    st.write("---")
    st.subheader("🛰️ Live Fleet Tracking")
    # Simulated GPS Table
    tracking_df = pd.DataFrame({
        "Cleaner": ["Siti", "Zul", "Ah Gao"],
        "Live Location": ["Garden Homes (On-Site)", "S2 Highway (Moving)", "Sendayan (Arriving)"],
        "Battery": ["85%", "40%", "92%"],
        "Current Task": ["Living Room", "Traveling", "Wait Check-in"]
    })
    st.table(tracking_df)

# 6. MEMBERSHIP & LOYALTY (SIMPLIFIED)
elif menu == "⭐ Membership & Loyalty":
    st.title("⭐ RH Gold Rewards")
    st.subheader("How it works:")
    st.markdown("""
    1. *Earn 1 Point for every MYR 1 spent.*
    2. *Silver Tier:* 0 - 500 Points (5% discount)
    3. *Gold Tier:* 501 - 2000 Points (10% discount)
    4. *Platinum Tier:* 2000+ Points (Free Deep Clean vouchers)
    """)
    st.progress(0.65, text="Your Progress to Platinum: 1300/2000 Points")

# 7. ADMIN SUITE (TRANSACTIONS)
elif menu == "🛡️ Admin Suite":
    st.title("🛡️ Executive Analytics")
    if st.text_input("Key", type="password") == "RH2026":
        st.subheader("📝 Daily Transaction Ledger")
        # Transaction History Table
        ledger = pd.DataFrame({
            "Time": ["09:00", "10:30", "12:00"],
            "Customer": ["Siti", "Tan", "Arun"],
            "Amount": ["MYR 150", "MYR 45", "MYR 230"],
            "90% Partner": ["MYR 135", "MYR 40.5", "MYR 207"],
            "10% HQ": ["MYR 15", "MYR 4.5", "MYR 23"]
        })
        st.dataframe(ledger, use_container_width=True)
