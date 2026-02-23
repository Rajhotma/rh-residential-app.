import streamlit as st
from datetime import datetime, time

# 1. SETUP & BRANDING
st.set_page_config(page_title="RH Modern Building Management", layout="wide")
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("RH EXECUTIVE PANEL")

menu = st.sidebar.radio("Navigation", [
    "🏠 Customer Booking", 
    "🤝 Partner Portal", 
    "📋 Supervisor Portal",
    "⭐ Membership & Feedback",
    "🛡️ Admin Dashboard"
])

# 2. THE COMPLETE DATABASE
LOCATIONS = ["Seremban 2", "Garden Homes", "Sendayan", "Nilai", "Enstek", "Putrajaya", "Cyberjaya", "Cheras", "KLCC / Bangsar", "Puchong", "Other"]

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

IRON_RATES = {
    "Short sleeve shirt": 2.0, "Long sleeve shirt": 2.5, "Trousers": 2.5, 
    "Blouse": 4.5, "Pants": 4.0, "T-Shirt": 1.5
}

DEEP_CLEAN = {"None": 0, "Move in deep cleaning": 300.0, "Move out deep cleaning": 450.0, "Renovation cleaning": 250.0}

# 3. CUSTOMER BOOKING PORTAL
if menu == "🏠 Customer Booking":
    st.title("✨ RH Cleaning Services")
    col_main, col_summary = st.columns([2, 1])
    
    with col_main:
        st.subheader("👤 Customer Information")
        c_name = st.text_input("Full Name")
        c_email = st.text_input("Email Address")
        c_phone = st.text_input("Mobile Number")
        
        tabs = st.tabs(["🧹 Residential", "🧼 Deep Clean & Add-ons", "👔 Ironing", "📅 Planner"])
        
        with tabs[0]:
            st.write("### Residential Service Selection")
            bundle = st.selectbox("Select Service Level", list(RATES_RESIDENTIAL.keys()))
            prop = st.selectbox("Select Property Type", list(RATES_RESIDENTIAL[bundle].keys()))
            hours = st.number_input("Basis Work (Hours)", min_value=2, value=2)
            res_total = RATES_RESIDENTIAL[bundle][prop] * hours

        with tabs[1]:
            st.write("### Specialized Cleaning")
            deep = st.selectbox("Deep Clean Service", list(DEEP_CLEAN.keys()))
            fridge = st.radio("Fridge Cleaning", ["None", "Single door (+MYR 75)", "Double door (+MYR 145)"], horizontal=True)
            porch = st.checkbox("Car porch cleaning (+MYR 45.00)")
            area_select = st.selectbox("Service Area", LOCATIONS)

        with tabs[2]:
            st.write("### Ironing Article Selection")
            iron_qty = {}
            for item, rate in IRON_RATES.items():
                iron_qty[item] = st.number_input(f"{item} (MYR {rate}/pc)", min_value=0, step=1)
            st.warning("⚠️ *Terms & Conditions*")
            iron_agree = st.checkbox("I agree: Claims shall not exceed 20x the ironing charges.")

        with tabs[3]:
            b_date = st.date_input("Booking Date")
            b_time = st.time_input("Booking Time", time(9, 0))

    with col_summary:
        st.subheader("💰 Job Summary")
        f_map = {"None": 0, "Single door (+MYR 75)": 75, "Double door (+MYR 145)": 145}
        iron_total = sum(iron_qty[item] * IRON_RATES[item] for item in IRON_RATES)
        grand_total = res_total + DEEP_CLEAN[deep] + f_map[fridge] + (45 if porch else 0) + iron_total
        
        st.metric("Total Charges", f"MYR {grand_total:.2f}")
        
        if grand_total < 50:
            st.error("❗ Minimum job value is MYR 50.00.")
        else:
            if st.button("Confirm Booking", use_container_width=True):
                st.success("Booking Confirmed!")
                
                # PROFESSIONAL RECEIPT GENERATOR
                st.write("---")
                st.subheader("🧾 Official Receipt")
                receipt_text = f"""
                *RH MODERN BUILDING MANAGEMENT*
                ----------------------------------
                *Customer:* {c_name}
                *Date:* {b_date} | *Time:* {b_time}
                *Area:* {area_select}
                ----------------------------------
                - {bundle} ({prop}): MYR {res_total:.2f}
                - {deep if deep != 'None' else ''}: MYR {DEEP_CLEAN[deep]:.2f}
                - Fridge Cleaning: MYR {f_map[fridge]:.2f}
                - Car Porch: MYR {'45.00' if porch else '0.00'}
                - Ironing Total: MYR {iron_total:.2f}
                ----------------------------------
                *GRAND TOTAL: MYR {grand_total:.2f}*
                ----------------------------------
                Thank you for choosing RH Cleaning!
                """
                st.markdown(receipt_text)
                st.download_button("Download Receipt (.txt)", receipt_text, file_name=f"RH_Receipt_{c_name}.txt")

# 4. PARTNER, SUPERVISOR, & ADMIN PORTALS (RETAINED)
elif menu == "🤝 Partner Portal":
    st.title("🤝 Partner Onboarding")
    st.text_input("WhatsApp Contact Number")
    st.multiselect("Service Coverage Area", LOCATIONS)
    st.file_uploader("Upload IC / Passport", type=['png', 'jpg', 'jpeg'])

elif menu == "📋 Supervisor Portal":
    st.title("📋 Supervisor Dashboard")
    st.metric("Today's Revenue", "MYR 0.00")
    st.subheader("Complaints")
    st.info("No active complaints.")

elif menu == "🛡️ Admin Dashboard":
    st.title("🛡️ Admin Suite")
    if st.text_input("Access Key", type="password") == "RH2026":
        st.subheader("Business Financials")
        st.metric("Monthly Revenue Target", "MYR 20,000", delta="0%")
