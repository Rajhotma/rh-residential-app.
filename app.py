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
    st.title("✨ RH Cleaning Services")
    col_main, col_summary = st.columns([2, 1])
    
    with col_main:
        st.subheader("📍 1. Logistics")
        c_name = st.text_input("Customer Name")
        c_phone = st.text_input("Customer Contact Number")
        c_address = st.text_area("Full House Address")
        
        st.subheader("🧹 2. Service Selection")
        bundle = st.selectbox("Select Service Level", list(RATES_RESIDENTIAL.keys()))
        prop = st.selectbox("Select Property Type", list(RATES_RESIDENTIAL[bundle].keys()))
        hours = st.number_input("Number of Hours", min_value=1, max_value=12, value=2)
        
        tabs = st.tabs(["Add-ons", "Ironing", "Schedule & Feedback"])
        with tabs[0]:
            fridge = st.radio("Fridge Cleaning", ["None", "Single door (+MYR 75)", "Double door (+MYR 145)"], horizontal=True)
        with tabs[1]:
            iron_qty = {item: st.number_input(f"{item}", min_value=0) for item in IRON_RATES}
        with tabs[2]:
            b_date = st.date_input("Date")
            customer_feedback = st.text_area("Special Instructions / Feedback for Previous Service")

    with col_summary:
        st.subheader("💰 Summary")
        f_map = {"None": 0, "Single door (+MYR 75)": 75, "Double door (+MYR 145)": 145}
        base_price = RATES_RESIDENTIAL[bundle][prop] * hours
        iron_total = sum(iron_qty[item] * IRON_RATES[item] for item in IRON_RATES)
        subtotal = base_price + f_map[fridge] + iron_total
        
        # Apply Festival Discount
        discount_amount = subtotal * FESTIVAL_DISCOUNT
        grand_total = subtotal - discount_amount
        
        st.write(f"Subtotal ({hours} hour{'s' if hours > 1 else ''}): MYR {subtotal:.2f}")
        st.success(f"🎊 {FESTIVAL_NAME}: -MYR {discount_amount:.2f}")
        st.metric("Total Bill", f"MYR {grand_total:.2f}")
        
        if st.button("Confirm Booking"):
            st.success("✅ Booking and Feedback Logged!")

# 4. PARTNER PORTAL
elif menu == "🤝 Partner Portal":
    st.title("🤝 Partner Job Inbox")
    st.write(f"*Customer Name:* {c_name if 'c_name' in locals() else 'Siti Aminah'}")
    st.write(f"*Contact:* {c_phone if 'c_phone' in locals() else '012-3456789'}")
    st.write(f"*Address:* {c_address if 'c_address' in locals() else 'Garden Homes, Seremban'}")
    st.metric("Your 90% Payout", f"MYR {150 * 0.9:.2f}")

# 5. SUPERVISOR PORTAL (REPLY FUNCTION ADDED)
elif menu == "📋 Supervisor Portal":
    st.title("📋 Supervisor Control")
    st.metric("Daily Commission", "MYR 1.50")
    
    st.subheader("📬 Customer Feedback & Complaints")
    with st.expander("View Pending Feedback from: En. Ahmad"):
        st.write("*Customer Message:* 'Cleaner missed the kitchen floor.'")
        supervisor_reply = st.text_area("Type your reply/resolution here:")
        if st.button("Send Reply to Customer"):
            st.success("Reply sent to customer email & points notification.")

# 6. MEMBERSHIP & POINTS (RESTORED)
elif menu == "⭐ Membership & Points":
    st.title("⭐ RH Gold Membership")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Your Total Points", "1,250 PTS")
    with col2:
        st.write("### Rewards Available")
        st.write("- 500 PTS: Free Fridge Cleaning")
        st.write("- 1000 PTS: MYR 20 Voucher")
    
    st.write("---")
    st.subheader("💬 Message from Supervisor")
    st.info("No new replies at this time.")

# 7. ADMIN DASHBOARD
elif menu == "🛡️ Admin Dashboard":
    st.title("🛡️ Admin Suite")
    if st.text_input("Key", type="password") == "RH2026":
        st.subheader("90/10 Financial Split")
        st.metric("Partner Share", "MYR 135.00")
        st.metric("Company Gross (Before Supervisor Comm)", "MYR 15.00")

