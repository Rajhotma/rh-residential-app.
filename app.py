import streamlit as st
from datetime import datetime, time
import pandas as pd

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

# 2. DATABASE & LOCATIONS
LOCATIONS = ["Seremban 2", "Garden Homes", "Sendayan", "Nilai", "Enstek", "Putrajaya", "Cyberjaya", "Cheras", "KLCC / Bangsar", "Puchong", "Other"]

# 3. CUSTOMER BOOKING & EMAIL CAPTURE
if menu == "🏠 Customer Booking":
    st.title("✨ RH Cleaning Services")
    col_main, col_summary = st.columns([2, 1])
    with col_main:
        # CUSTOMER DATABASE CAPTURE
        st.subheader("👤 Customer Information")
        c_email = st.text_input("Email Address (for e-Billing & Points)")
        c_phone = st.text_input("Mobile Number")
        
        tabs = st.tabs(["🧹 Residential", "🧼 Deep Clean & Add-ons", "👔 Ironing", "📅 Planner"])
        with tabs[0]:
            # ... (Existing Pricing Logic)
            hours = st.number_input("Basis Work (Hours)", min_value=1, value=2)
            res_total = 25.0 * hours # Simplified for logic display
        with tabs[1]:
            porch = st.checkbox("Car porch cleaning (+MYR 45.00)")
        with tabs[2]:
            st.warning("⚠️ Ironing T&C apply (20x claim limit)")
            iron_agree = st.checkbox("I agree to Ironing Terms")
        with tabs[3]:
            st.date_input("Pick a Date")

    with col_summary:
        st.subheader("💰 Job Summary")
        grand_total = res_total + (45 if porch else 0)
        st.metric("Total Charges", f"MYR {grand_total:.2f}")
        if st.button("Confirm Booking", use_container_width=True):
            if c_email and c_phone:
                st.success(f"Confirmed! Receipt sent to {c_email}")
            else:
                st.error("Please provide Email and Phone for our database.")

# 4. PARTNER PORTAL & CONTACT INFO
elif menu == "🤝 Partner Portal":
    st.title("🤝 Partner Onboarding")
    p_name = st.text_input("Full Name")
    p_phone = st.text_input("WhatsApp Contact Number")
    st.multiselect("Select working areas", LOCATIONS)
    st.file_uploader("Upload IC / Passport", type=['png', 'jpg', 'jpeg'])
    if st.button("Submit Application"):
        st.success("Details saved. Supervisor will contact you at " + p_phone)

# 5. SUPERVISOR PORTAL (COMPLAINT & REVENUE)
elif menu == "📋 Supervisor Portal":
    st.title("📋 Operations Management")
    
    # REVENUE SUMMARY
    m1, m2 = st.columns(2)
    m1.metric("Today's Gross Sales", "MYR 1,250.00")
    m2.metric("Active Complaints", "1")
    
    st.write("---")
    st.subheader("📬 Complaint Resolution Center")
    # Simulation of a complaint entry
    with st.expander("🚨 Complaint #102 - Garden Homes (Toilet Cleaning)"):
        st.write("*Customer:* customer@email.com")
        st.write("*Issue:* Cleaner arrived 15 mins late and missed the guest toilet.")
        reply = st.text_area("Supervisor Reply / Action Taken")
        action = st.selectbox("Resolution", ["Issue Refund", "Schedule Re-clean", "Warning to Cleaner", "Resolved"])
        if st.button("Send Resolution to Customer"):
            st.success("Reply sent to customer email database.")

# 6. MEMBERSHIP & RATING
elif menu == "⭐ Membership & Feedback":
    st.title("⭐ Customer Experience")
    st.subheader("Rate Your Last Service")
    rating = st.slider("Select Rating", 1, 5, 5)
    feedback = st.text_area("How can we improve?")
    if st.button("Submit Feedback"):
        st.success(f"Thank you! You've earned {rating * 10} points.")

# 7. ADMIN DASHBOARD (DATABASE ACCESS)
elif menu == "🛡️ Admin Dashboard":
    st.title("🛡️ Executive Business Analytics")
    if st.text_input("Access Key", type="password") == "RH2026":
        
        tab1, tab2 = st.tabs(["📈 Financials", "🗂️ Databases"])
        
        with tab1:
            st.subheader("Financial Summary")
            st.metric("Total Revenue", "MYR 15,200")
            
        with tab2:
            st.subheader("📧 Customer Email Database")
            # This would display the collected emails
            st.dataframe({"Email": ["cust1@gmail.com", "cust2@yahoo.com"], "Phone": ["012-3456789", "017-9876543"], "Total Spent": [450, 120]})
            
            st.subheader("📞 Cleaner Contact List")
            st.dataframe({"Cleaner Name": ["Siti", "Ah Gao"], "Phone": ["011-2223334", "019-8887776"], "Status": ["On-Job", "Available"]})
