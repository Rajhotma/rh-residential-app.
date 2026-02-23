import streamlit as st
from datetime import datetime, time

# 1. SETUP & BRANDING
st.set_page_config(page_title="RH Modern Building Management", layout="wide")
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("RH EXECUTIVE PANEL")

# UPDATED NAVIGATION (Supervisor Added Back)
menu = st.sidebar.radio("Navigation", [
    "🏠 Customer Booking", 
    "🤝 Partner Portal", 
    "📋 Supervisor Portal",
    "⭐ Membership & Points",
    "🛡️ Admin Dashboard"
])

# 2. THE PRICING DATABASE
RATES_RESIDENTIAL = {
    "Sweeping, Vacuuming and Mopping": {
        "2 bedroom Apartment": 15.0, "3 bedroom Apartment": 18.0, "Single storey 3 room": 20.0, "Single storey 4 room": 25.0, "Double storey 4 room": 35.0
    },
    "Sweeping, Vacuuming, Mopping and High & Low Dusting": {
        "2 bedroom Apartment": 20.0, "3 bedroom Apartment": 23.0, "Single storey 3 room": 25.0, "Single storey 4 room": 30.0, "Double storey 4 room": 40.0
    },
    "Sweeping, Vacuuming, Mopping, High & Low Dusting and Toilet Cleaning": {
        "2 bedroom Apartment": 25.0, "3 bedroom Apartment": 28.0, "Single storey 3 room": 30.0, "Single storey 4 room": 35.0, "Double storey 4 room": 45.0
    }
}
DEEP_CLEAN = {"None": 0, "Move in cleaning deep cleaning": 300.0, "Move out deep cleaning": 450.0, "Renovation cleaning": 250.0}
FRIDGE_RATES = {"None": 0, "Single door fridge cleaning": 75.0, "Double door fridge cleaning": 145.0}
IRON_RATES = {"Short sleeve shirt": 2.0, "Long sleeve shirt": 2.5, "Trousers": 2.5, "Blouse": 4.5, "Pants": 4.0, "T-Shirt": 1.5}

# 3. CUSTOMER BOOKING PORTAL
if menu == "🏠 Customer Booking":
    st.title("✨ RH Cleaning Services")
    st.info("🕒 Support: 9am-8pm Daily | 📄 e-Billing | 📍 Nearest Cleaner Auto-Assign")
    col_main, col_summary = st.columns([2, 1])
    with col_main:
        tabs = st.tabs(["🧹 Residential", "🧼 Deep Clean & Add-ons", "👔 Ironing", "📅 Planner"])
        with tabs[0]:
            bundle = st.selectbox("Select Service Bundle", list(RATES_RESIDENTIAL.keys()))
            prop = st.selectbox("Property Type", list(RATES_RESIDENTIAL[bundle].keys()))
            hours = st.number_input("Basis Work (Hours)", min_value=1, value=2)
            res_total = RATES_RESIDENTIAL[bundle][prop] * hours
        with tabs[1]:
            deep = st.selectbox("Select Deep Clean", list(DEEP_CLEAN.keys()))
            fridge = st.radio("Fridge Cleaning", list(FRIDGE_RATES.keys()), horizontal=True)
            porch = st.checkbox("Car porch cleaning (+MYR 45.00)")
            standby = st.number_input("Cleaner standby onsite (MYR 10.00 per hour/pax)", min_value=0, value=0)
        with tabs[2]:
            iron_qty = {item: st.number_input(f"{item} (MYR {rate})", min_value=0) for item, rate in IRON_RATES.items()}
            st.warning("⚠️ *Terms & Conditions*")
            iron_agree = st.checkbox("I agree: If garments are damaged, claims shall not exceed 20 times the ironing charges.")
        with tabs[3]:
            st.date_input("Pick a Date", min_value=datetime.now())
            st.time_input("Pick a Time", time(9, 0))
    with col_summary:
        st.subheader("💰 Job Summary")
        iron_total = sum(iron_qty[item] * IRON_RATES[item] for item in IRON_RATES)
        grand_total = res_total + DEEP_CLEAN[deep] + FRIDGE_RATES[fridge] + (45 if porch else 0) + (standby * 10) + iron_total
        st.metric("Total Charges", f"MYR {grand_total:.2f}")
        if grand_total < 50:
            st.error("❗ Minimum job value is MYR 50.00.")
        elif iron_total > 0 and not iron_agree:
            st.warning("❗ Please accept Ironing T&C.")
        else:
            if st.button("Confirm Booking", use_container_width=True):
                st.success("Booking Assigned!")

# 4. PARTNER PORTAL
elif menu == "🤝 Partner Portal":
    st.title("🤝 Partner Onboarding")
    st.subheader("🛡️ Identity Verification")
    id_type = st.selectbox("Document Type", ["Malaysian IC (Blue)", "International Passport", "Work Permit"])
    col1, col2 = st.columns(2)
    with col1: st.file_uploader(f"Upload Front of {id_type}", type=['png', 'jpg', 'jpeg'])
    with col2: st.file_uploader(f"Upload Back of {id_type}", type=['png', 'jpg', 'jpeg'])
    st.multiselect("Coverage Areas", ["Seremban", "Nilai", "Cyberjaya", "Puchong", "KLCC"])
    if st.button("Submit Application"):
        st.success("Application Sent!")

# 5. SUPERVISOR PORTAL (THE MISSING PIECE)
elif menu == "📋 Supervisor Portal":
    st.title("📋 Supervisor Dashboard")
    st.subheader("Live Operations Management")
    col1, col2, col3 = st.columns(3)
    col1.metric("Pending Partners", "0")
    col2.metric("Active Jobs", "0")
    col3.metric("Complaints", "0")
    st.write("---")
    st.write("### New Partner Applications")
    st.info("No new applications to verify at this moment.")

# 6. MEMBERSHIP & ADMIN
elif menu == "⭐ Membership & Points":
    st.title("⭐ RH Membership")
    st.metric("Your Points", "150")
elif menu == "🛡️ Admin Dashboard":
    st.title("🛡️ Admin Suite")
    if st.text_input("Access Key", type="password") == "RH2026":
        st.progress(0.15, text="Salary Replacement: 15%")
