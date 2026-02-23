import streamlit as st
from datetime import datetime, time

# 1. SETUP
st.set_page_config(page_title="RH Modern Building Management", layout="wide")
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("RH EXECUTIVE PANEL")

menu = st.sidebar.radio("Navigation", [
    "🏠 Customer Booking", 
    "🤝 Partner Portal", 
    "📋 Supervisor Portal",
    "🛡️ Admin Dashboard"
])

# 2. DATABASE LOGIC (SIMULATED DATA FOR DEMO)
# In a real scenario, these would come from your Google Sheet
DAILY_JOBS_COUNT = 12 
TOTAL_DAILY_REVENUE = 1550.00
SUPERVISOR_RATE = 1.50

# 3. CUSTOMER BOOKING
if menu == "🏠 Customer Booking":
    st.title("✨ RH Cleaning Services")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📍 Booking Details")
        c_name = st.text_input("Customer Name")
        c_address = st.text_area("Full House Address")
        c_area = st.selectbox("Area", ["Seremban 2", "Garden Homes", "Sendayan", "Putrajaya", "Cheras"])
        st.date_input("Date")
    with col2:
        st.subheader("💰 Summary")
        st.metric("Total Bill", "MYR 150.00")
        if st.button("Confirm Booking"):
            st.success("Job Logged & Assigned!")

# 4. PARTNER PORTAL
elif menu == "🤝 Partner Portal":
    st.title("🤝 Partner Job Inbox")
    st.write("---")
    st.write("*Assigned Address:* 123, Jalan Garden Homes, Seremban")
    st.write("*Customer:* En. Ahmad")
    if st.button("Check-in at Site"):
        st.info("Check-in timestamp recorded.")

# 5. SUPERVISOR PORTAL (COMMISSION ADDED)
elif menu == "📋 Supervisor Portal":
    st.title("📋 Supervisor Dashboard")
    
    # Financials for Supervisor
    s1, s2, s3 = st.columns(3)
    s1.metric("Jobs Managed Today", DAILY_JOBS_COUNT)
    s2.metric("Daily Commission", f"MYR {DAILY_JOBS_COUNT * SUPERVISOR_RATE:.2f}", help="Calculated at MYR 1.50 per job")
    s3.metric("Pending Feedbacks", "2")
    
    st.write("---")
    st.subheader("📡 Live Ops Monitoring")
    st.table({
        "Cleaner": ["Siti", "Zul", "Ah Gao"],
        "Status": ["Cleaning", "Traveling", "Arrived"],
        "Address": ["Garden Homes", "Sendayan", "Seremban 2"]
    })

# 6. ADMIN DASHBOARD (90/10 SPLIT ADDED)
elif menu == "🛡️ Admin Dashboard":
    st.title("🛡️ Executive Admin")
    if st.text_input("Access Key", type="password") == "RH2026":
        
        st.subheader("💹 Revenue Breakdown (90/10 Split)")
        
        # Financial Logic
        partner_payout = TOTAL_DAILY_REVENUE * 0.90
        company_gross = TOTAL_DAILY_REVENUE * 0.10
        supervisor_total = DAILY_JOBS_COUNT * SUPERVISOR_RATE
        net_to_hq = company_gross - supervisor_total
        
        a1, a2, a3 = st.columns(3)
        a1.metric("Total Daily Sales", f"MYR {TOTAL_DAILY_REVENUE:.2f}")
        a2.metric("Partner Payout (90%)", f"MYR {partner_payout:.2f}", delta_color="inverse")
        a3.metric("Company Gross (10%)", f"MYR {company_gross:.2f}")

        st.write("---")
        st.subheader("📊 Profitability After Ops Costs")
        p1, p2 = st.columns(2)
        p1.metric("Supervisor Commissions", f"MYR {supervisor_total:.2f}")
        p2.metric("Net Profit (to HQ)", f"MYR {net_to_hq:.2f}")
        
        st.progress(0.10, text="Monthly Revenue Target Progress")
