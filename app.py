import streamlit as st
# from googletrans import Translator
from datetime import datetime, time
import random
import math
import sqlite3
import json
import os

# Try to import Google Sheets integration
try:
    from google_sheets_integration import GoogleSheetsManager, init_google_sheets
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

# 1. SETUP & BRANDING
try:
    import qrcode
    from io import BytesIO
    from PIL import Image
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    st.error("QR code module not available. Please refresh the page or contact support.")
try:
    params = st.query_params
    role = params.get("role", None)
except AttributeError:
    # Fallback for older Streamlit versions
    params = st.experimental_get_query_params()
    role = params.get("role", [None])[0]

# Define menu options for each role
MENU_OPTIONS = {
    "customer": ["🏠 Customer Booking"],
    "partner": ["🤝 Partner Portal"],
    "supervisor": ["🤝 Partner Portal", "📋 Supervisor Portal", "⭐ Membership & Points"],
    None: [
        "🏠 Customer Booking", 
        "🤝 Partner Portal", 
        "📋 Supervisor Portal",
        "⭐ Membership & Points",
        "🛡️ Admin Dashboard"
    ]
}
st.set_page_config(page_title="AXIS Modern Building Management", layout="wide")

# Custom CSS for white background and dark text
st.markdown("""
    <style>
        .stApp {
            background-color: white;
        }
        [data-testid="stAppViewContainer"] {
            background-color: white;
        }
        body {
            color: #1f1f1f;
        }
        .stMarkdown, .stWrite, .stText, p {
            color: #1f1f1f !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1f1f1f !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.image("logo.png", width=250)
st.sidebar.title("AXIS EXECUTIVE PANEL")

# QR code sharing for customer and partner portal
st.sidebar.markdown("---")
st.sidebar.subheader("Quick Access QR Codes")
base_url = st.secrets["base_url"] if "base_url" in st.secrets else "https://your-app-url"  # Set your deployment URL here
customer_url = f"{base_url}/?role=customer"
partner_url = f"{base_url}/?role=partner"

def qr_img(url):
    if not QRCODE_AVAILABLE:
        return None
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

st.sidebar.markdown("**Customer Booking**")
if QRCODE_AVAILABLE:
    st.sidebar.image(qr_img(customer_url), caption="Scan to Book (Customer)", use_column_width=True)
st.sidebar.markdown(f"[Open Booking Page]({customer_url})")

st.sidebar.markdown("**Partner Portal**")
if QRCODE_AVAILABLE:
    st.sidebar.image(qr_img(partner_url), caption="Scan for Partner Portal", use_column_width=True)
st.sidebar.markdown(f"[Open Partner Portal]({partner_url})")

# --- DATABASE SETUP ---
DB_FILE = "axis_database.db"

def _init_db():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Bookings table
    c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id TEXT PRIMARY KEY,
        created_at TEXT,
        service_date TEXT,
        amount REAL,
        payment_method TEXT,
        customer_name TEXT,
        location_lat REAL,
        location_lon REAL,
        customer_address TEXT,
        assigned_to TEXT,
        assigned_at TEXT
    )
    ''')
    
    # Cleaners table
    c.execute('''
    CREATE TABLE IF NOT EXISTS cleaners (
        name TEXT PRIMARY KEY,
        lat REAL,
        lon REAL,
        status TEXT,
        last_update TEXT,
        on_site_since TEXT,
        expected_minutes INTEGER,
        email TEXT,
        assigned_job TEXT,
        next_kin_name TEXT,
        next_kin_contact TEXT,
        bank_name TEXT,
        account_number TEXT
    )
    ''')
    
    # Supervisors table
    c.execute('''
    CREATE TABLE IF NOT EXISTS supervisors (
        id TEXT PRIMARY KEY,
        name TEXT,
        employee_number TEXT UNIQUE,
        email TEXT,
        phone TEXT,
        nric TEXT,
        bank_name TEXT,
        account_number TEXT,
        personal_details TEXT,
        created_at TEXT,
        status TEXT
    )
    ''')
    
    # Auto transactions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS auto_transactions (
        id TEXT PRIMARY KEY,
        supervisor_id TEXT,
        amount REAL,
        scheduled_time TEXT,
        last_transaction TEXT,
        status TEXT,
        FOREIGN KEY(supervisor_id) REFERENCES supervisors(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def _load_bookings_from_db():
    """Load all bookings from database."""
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM bookings')
    rows = c.fetchall()
    conn.close()
    
    bookings = []
    for row in rows:
        booking = {
            'id': row[0],
            'created_at': datetime.fromisoformat(row[1]) if row[1] else None,
            'service_date': datetime.fromisoformat(row[2]).date() if row[2] else None,
            'amount': row[3],
            'payment_method': row[4],
            'customer_name': row[5],
            'location_lat': row[6],
            'location_lon': row[7],
            'customer_address': row[8],
            'assigned_to': row[9],
            'assigned_at': datetime.fromisoformat(row[10]) if row[10] else None,
        }
        bookings.append(booking)
    return bookings

def _load_cleaners_from_db():
    """Load all cleaners from database."""
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM cleaners')
    rows = c.fetchall()
    conn.close()
    
    cleaners = []
    for row in rows:
        cleaner = {
            'name': row[0],
            'lat': row[1],
            'lon': row[2],
            'status': row[3],
            'last_update': datetime.fromisoformat(row[4]) if row[4] else None,
            'on_site_since': datetime.fromisoformat(row[5]) if row[5] else None,
            'expected_minutes': row[6],
            'email': row[7],
            'assigned_job': row[8],
            'next_kin_name': row[9],
            'next_kin_contact': row[10],
            'bank_name': row[11],
            'account_number': row[12],
        }
        cleaners.append(cleaner)
    return cleaners

def _save_booking_to_db(booking):
    """Save a single booking to database."""
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    INSERT OR REPLACE INTO bookings 
    (id, created_at, service_date, amount, payment_method, customer_name, location_lat, location_lon, customer_address, assigned_to, assigned_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        booking['id'],
        booking['created_at'].isoformat() if booking.get('created_at') else None,
        booking['service_date'].isoformat() if booking.get('service_date') else None,
        booking['amount'],
        booking['payment_method'],
        booking['customer_name'],
        booking['location_lat'],
        booking['location_lon'],
        booking['customer_address'],
        booking['assigned_to'],
        booking['assigned_at'].isoformat() if booking.get('assigned_at') else None,
    ))
    conn.commit()
    conn.close()

def _save_cleaner_to_db(cleaner):
    """Save a single cleaner to database."""
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    INSERT OR REPLACE INTO cleaners 
    (name, lat, lon, status, last_update, on_site_since, expected_minutes, email, assigned_job, next_kin_name, next_kin_contact, bank_name, account_number)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        cleaner['name'],
        cleaner['lat'],
        cleaner['lon'],
        cleaner['status'],
        cleaner['last_update'].isoformat() if cleaner.get('last_update') else None,
        cleaner['on_site_since'].isoformat() if cleaner.get('on_site_since') else None,
        cleaner['expected_minutes'],
        cleaner['email'],
        cleaner['assigned_job'],
        cleaner.get('next_kin_name'),
        cleaner.get('next_kin_contact'),
        cleaner.get('bank_name'),
        cleaner.get('account_number'),
    ))
    conn.commit()
    conn.close()

def _load_supervisors_from_db():
    """Load all supervisors from database."""
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM supervisors')
    rows = c.fetchall()
    conn.close()
    
    supervisors = []
    for row in rows:
        supervisor = {
            'id': row[0],
            'name': row[1],
            'employee_number': row[2],
            'email': row[3],
            'phone': row[4],
            'nric': row[5],
            'bank_name': row[6],
            'account_number': row[7],
            'personal_details': row[8],
            'created_at': datetime.fromisoformat(row[9]) if row[9] else None,
            'status': row[10],
        }
        supervisors.append(supervisor)
    return supervisors

def _save_supervisor_to_db(supervisor):
    """Save a single supervisor to database."""
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    INSERT OR REPLACE INTO supervisors 
    (id, name, employee_number, email, phone, nric, bank_name, account_number, personal_details, created_at, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        supervisor['id'],
        supervisor['name'],
        supervisor['employee_number'],
        supervisor['email'],
        supervisor['phone'],
        supervisor['nric'],
        supervisor['bank_name'],
        supervisor['account_number'],
        supervisor.get('personal_details'),
        supervisor['created_at'].isoformat() if supervisor.get('created_at') else None,
        supervisor['status'],
    ))
    conn.commit()
    conn.close()

def _save_auto_transaction_to_db(transaction):
    """Save auto transaction schedule to database."""
    _init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    INSERT OR REPLACE INTO auto_transactions 
    (id, supervisor_id, amount, scheduled_time, last_transaction, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        transaction['id'],
        transaction['supervisor_id'],
        transaction['amount'],
        transaction['scheduled_time'],
        transaction['last_transaction'],
        transaction['status'],
    ))
    conn.commit()
    conn.close()

def _process_scheduled_transactions():
    """Process auto-transactions scheduled for 8pm."""
    _init_db()
    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    # Check if current time is between 8:00 PM and 8:05 PM (to avoid duplicate processing)
    if current_hour == 20 and current_minute < 5:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Get all active supervisors
        c.execute("SELECT id, name, account_number, bank_name FROM supervisors WHERE status = ?", ('Active',))
        supervisors = c.fetchall()
        
        today = current_time.date().isoformat()
        
        for sup_id, sup_name, account, bank in supervisors:
            # Check if transaction already done today
            c.execute(
                "SELECT last_transaction FROM auto_transactions WHERE supervisor_id = ?",
                (sup_id,)
            )
            result = c.fetchone()
            
            if result is None or result[0] != today:
                # Process transaction
                c.execute(
                    "UPDATE auto_transactions SET last_transaction = ? WHERE supervisor_id = ?",
                    (today, sup_id)
                )
                if c.rowcount == 0:
                    # Insert new record if doesn't exist
                    trans_id = f"AUTO_{sup_id}_{int(datetime.now().timestamp())}"
                    c.execute(
                        "INSERT INTO auto_transactions (id, supervisor_id, amount, scheduled_time, last_transaction, status) VALUES (?, ?, ?, ?, ?, ?)",
                        (trans_id, sup_id, 1.50, "20:00", today, "Completed")
                    )
        
        conn.commit()
        conn.close()

# Initialize session state with data from database
def _init_session_state():
    """Load data from database into session state on app startup."""
    if 'bookings' not in st.session_state:
        st.session_state['bookings'] = _load_bookings_from_db()
    if 'cleaners' not in st.session_state:
        # Try loading from DB first
        db_cleaners = _load_cleaners_from_db()
        if db_cleaners:
            st.session_state['cleaners'] = db_cleaners
        else:
            # Initialize default cleaners if none exist
            st.session_state['cleaners'] = [
                {'name': 'Ahmad', 'lat': 2.726, 'lon': 101.938, 'status': 'Online', 'last_update': None, 'on_site_since': None, 'expected_minutes': 120, 'email': 'ahmad@example.com', 'assigned_job': None, 'next_kin_name': None, 'next_kin_contact': None, 'bank_name': None, 'account_number': None},
                {'name': 'Siti', 'lat': 2.730, 'lon': 101.940, 'status': 'Online', 'last_update': None, 'on_site_since': None, 'expected_minutes': 90, 'email': 'siti@example.com', 'assigned_job': None, 'next_kin_name': None, 'next_kin_contact': None, 'bank_name': None, 'account_number': None},
                {'name': 'Ramesh', 'lat': 2.725, 'lon': 101.935, 'status': 'Online', 'last_update': None, 'on_site_since': None, 'expected_minutes': 60, 'email': 'ramesh@example.com', 'assigned_job': None, 'next_kin_name': None, 'next_kin_contact': None, 'bank_name': None, 'account_number': None},
            ]
            # Save defaults to DB
            for cleaner in st.session_state['cleaners']:
                _save_cleaner_to_db(cleaner)
    
    if 'supervisors' not in st.session_state:
        st.session_state['supervisors'] = _load_supervisors_from_db()
    
    if 'auto_transactions' not in st.session_state:
        st.session_state['auto_transactions'] = []
    
    if 'notifications' not in st.session_state:
        st.session_state['notifications'] = []

_init_session_state()

# Process scheduled auto-transactions at 8pm daily
_process_scheduled_transactions()


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

# Define menu based on role
menu = st.sidebar.selectbox("Main Menu", MENU_OPTIONS[role], key="main_menu")

def t(text):
    # Translation temporarily disabled
    return text

# 2. DATABASE & SEASONAL LOGIC
LOCATIONS = ["Seremban 2", "Garden Homes", "Sendayan", "Nilai", "Putrajaya", "Cyberjaya", "Cheras", "Puchong", "Gaarden Homes", "Seremban 2", "Sendayan", "Suriaman", "Tiara", "Adira", "Bandar Sri Sendayan", "Kota Warisan", "Sepang", "KLIA1", "KLIA2", "Rasah Kemayan", "Port Dickson"]
RATES_RESIDENTIAL = {
    "Sweeping, Vacuuming and Mopping": {"2 bedroom Apartment": 15.0, "3 bedroom Apartment": 18.0, "Single storey 3 room": 20.0, "Single storey 4 room": 25.0, "Double storey 4 room": 35.0},
    "Sweeping, Vacuuming, Mopping and High & Low Dusting": {"2 bedroom Apartment": 20.0, "3 bedroom Apartment": 23.0, "Single storey 3 room": 25.0, "Single storey 4 room": 30.0, "Double storey 4 room": 40.0},
    "Sweeping, Vacuuming, Mopping, High & Low Dusting and Toilet Cleaning": {"2 bedroom Apartment": 25.0, "3 bedroom Apartment": 28.0, "Single storey 3 room": 30.0, "Single storey 4 room": 35.0, "Double storey 4 room": 45.0}
}
IRON_RATES = {"Short sleeve shirt": 2.0, "Long sleeve shirt": 2.5, "Trousers": 2.5, "Blouse": 4.5, "Pants": 4.0, "T-Shirt": 1.5}


# --- Simulation helpers for GPS tracking & notifications ---
def _init_cleaners():
    """Ensure cleaners are loaded in session state (called for compatibility)."""
    if 'cleaners' not in st.session_state:
        _init_session_state()



def _dist_meters(lat1, lon1, lat2, lon2):
    # rough equirectangular approximation for small distances
    R = 6371000
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = math.radians(lat2 - lat1)
    return math.sqrt(x*x + y*y) * R


def _auto_assign_jobs():
    """Auto-assign pending bookings to nearest available cleaners."""
    _init_cleaners()
    bookings = st.session_state.get('bookings', [])
    cleaners = st.session_state.get('cleaners', [])
    
    for booking in bookings:
        # Skip if already assigned
        if booking.get('assigned_to'):
            continue
        
        # Skip if booking has no location data
        if not booking.get('location_lat') or not booking.get('location_lon'):
            continue
        
        # Find available cleaners (online and not currently assigned)
        available_cleaners = [
            c for c in cleaners 
            if c.get('status') == 'Online' and not c.get('assigned_job')
        ]
        
        if not available_cleaners:
            continue
        
        # Find nearest cleaner
        job_lat, job_lon = booking['location_lat'], booking['location_lon']
        nearest_cleaner = min(
            available_cleaners,
            key=lambda c: _dist_meters(c['lat'], c['lon'], job_lat, job_lon)
        )
        
        # Assign job
        booking['assigned_to'] = nearest_cleaner['name']
        booking['assigned_at'] = datetime.now()
        nearest_cleaner['assigned_job'] = booking['id']
        
        # Save assignments to database
        _save_booking_to_db(booking)
        _save_cleaner_to_db(nearest_cleaner)


def _simulate_step():
    now = datetime.now()
    changed = False
    for c in st.session_state.get('cleaners', []):
        # if offline, randomly go moving
        if c['status'] == 'Offline' and random.random() < 0.3:
            c['status'] = 'Moving'
            c['last_update'] = now
            _save_cleaner_to_db(c)
            changed = True
            continue

        # moving: nudge position, maybe arrive
        if c['status'] == 'Moving':
            # random small move
            c['lat'] += random.uniform(-0.0003, 0.0003)
            c['lon'] += random.uniform(-0.0003, 0.0003)
            c['last_update'] = now
            # chance to arrive
            if random.random() < 0.25:
                c['status'] = 'Arriving'
            _save_cleaner_to_db(c)
            changed = True
            continue

        if c['status'] == 'Arriving':
            # smaller moves, then become On-Site
            c['lat'] += random.uniform(-0.0001, 0.0001)
            c['lon'] += random.uniform(-0.0001, 0.0001)
            c['last_update'] = now
            if random.random() < 0.5:
                c['status'] = 'On-Site'
                c['on_site_since'] = now
            _save_cleaner_to_db(c)
            changed = True
            continue

        if c['status'] == 'On-Site':
            # check elapsed time
            if c.get('on_site_since'):
                elapsed = (now - c['on_site_since']).total_seconds() / 60.0
                if elapsed > float(c.get('expected_minutes', 120)):
                    # create notification record (only once per exceed)
                    key = f"exceed_{c['name']}_{c.get('on_site_since') }"
                    # avoid duplicate notifications by checking notifications messages
                    exists = any(n for n in st.session_state['notifications'] if n.get('tag') == key)
                    if not exists:
                        msg = f"Cleaner {c['name']} has exceeded expected time ({int(elapsed)} min > {c.get('expected_minutes')} min)."
                        note = {'time': now, 'cleaner': c['name'], 'message': msg, 'tag': key}
                        st.session_state['notifications'].append(note)
                        # try email
                        smtp_host = st.secrets.get('SMTP_HOST') if 'SMTP_HOST' in st.secrets else None
                        if smtp_host and c.get('email'):
                            try:
                                import smtplib
                                from email.message import EmailMessage
                                smtp_port = int(st.secrets.get('SMTP_PORT', 587))
                                smtp_user = st.secrets.get('SMTP_USER')
                                smtp_pass = st.secrets.get('SMTP_PASS')
                                msg_email = EmailMessage()
                                msg_email['Subject'] = f"Overtime Alert: {c['name']}"
                                msg_email['From'] = st.secrets.get('FROM_EMAIL', smtp_user)
                                msg_email['To'] = c['email']
                                msg_email.set_content(msg)
                                server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                                server.starttls()
                                if smtp_user and smtp_pass:
                                    server.login(smtp_user, smtp_pass)
                                server.send_message(msg_email)
                                server.quit()
                                note['emailed'] = True
                            except Exception as e:
                                note['emailed'] = False
                                note['email_error'] = str(e)
                        changed = True

    return changed


# FESTIVAL DISCOUNT SETTINGS
FESTIVAL_NAME = "Ramadan & Raya Special"
FESTIVAL_DISCOUNT = 5.0 # MYR 5.00 Off

# Location coordinates mapping (postcode/area to lat/lon)
LOCATION_COORDS = {
    "Seremban 2": (2.726, 101.938),
    "Garden Homes": (2.730, 101.940),
    "Sendayan": (2.725, 101.935),
    "Nilai": (2.748, 101.885),
    "Putrajaya": (2.926, 101.695),
    "Cyberjaya": (2.909, 101.750),
    "Cheras": (3.135, 101.615),
    "Puchong": (2.764, 101.609),
    "Kota Warisan": (2.756, 101.630),
    "Bandar Sri Sendayan": (2.713, 101.945),
    "Tiara": (2.625, 101.851),
    "Adira": (2.650, 101.815),
    "Sepang": (2.726, 101.551),
    "KLIA1": (2.745, 101.691),
    "KLIA2": (2.748, 101.712),
    "Rasah Kemayan": (2.680, 101.925),
    "Port Dickson": (2.806, 101.834),
    "Suriaman": (2.700, 101.850),
}

# 3. CUSTOMER BOOKING
if menu == "🏠 Customer Booking":
    st.title(t("✨ AXIS Cleaning Services"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    col_main, col_summary = st.columns([2, 1])
    
    with col_main:
        st.subheader(t("📍 1. Logistics"))
        greeting = st.selectbox(t("Greeting"), ["Mr", "Mrs", "Puan", "Sir", "Dr", "Tan Sri", "Dato", "Madam"])
        c_name = st.text_input(t("Customer Name"))
        c_email = st.text_input(t("Customer Email"))
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
            st.session_state['last_booking_date'] = b_date
            # Use a simple default time to avoid Streamlit type compatibility issues
            b_time = st.time_input(t("Time"), value=datetime.now().time())
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
        with st.expander("Laundry Liability Disclaimer (click to view)"):
            st.markdown("""
            - AXIS Modern Building Management is not liable for damages exceeding 20x the service fee paid for the affected laundry item.
            - By booking, you agree to this limit of liability.
            - For full terms, please contact our support.
            """)

        # Show laundry tariff breakdown
        st.write("**Laundry Articles & Tariff**")
        laundry_rows = []
        for item, price in IRON_RATES.items():
            laundry_rows.append({"Item": item, "Price (MYR)": f"{price:.2f}", "Qty Selected": iron_qty.get(item, 0)})
        st.table(laundry_rows)

        # Clear, professional disclaimer (rendered again to ensure customers see it)
        st.markdown("""
    **Laundry Liability Disclaimer (Summary)**

    AXIS Modern Building Management takes care when handling customer garments and household linens. Our liability for proven loss or damage caused by our staff is limited: the maximum compensation payable will not exceed twenty (20) times the amount charged for the cleaning service for that particular job, or the actual replacement value of the lost/damaged item, whichever is lower. Customers should declare high-value or sentimental items before service and remove valuables prior to service. Claims must be reported within 48 hours of service completion with photographic evidence and a description. This summary does not affect statutory consumer rights.
    """)

        # Payment options
        st.write("**Payment Options**")
        payment_method = st.selectbox(t("Choose Payment Method"), ["Online Transfer", "Credit/Debit Card (via Link)", "Cash on Arrival (COD)"], index=0)
        if payment_method == "Online Transfer":
            st.write("Please transfer to:")
            st.write("**Bank Name:** RHB")
            st.write("**Account Number:** 25144100006128")
            st.write("Reference: Customer name + booking date")
        elif payment_method == "Credit/Debit Card (via Link)":
            st.write("You will receive a secure payment link after confirming the booking.")
        else:
            st.write("Please have the exact amount ready for the cleaner on arrival.")

        st.write("All services may require partial prepayment depending on promotions and scheduling.")

        # Customer service contact
        st.write("---")
        st.write("**Customer Service**")
        st.write("For assistance call: +60146814167")
        st.write("Available daily: 08:00 - 20:00")

        if st.button(t("Confirm Booking")):
            # Generate a payment link token when card payment selected
            import uuid, urllib.parse
            booking_id = str(uuid.uuid4())
            payment_token = str(uuid.uuid4())
            payment_link = f"https://payments.example.com/pay/{urllib.parse.quote(payment_token)}?amount={grand_total:.2f}&id={urllib.parse.quote(booking_id)}"

            st.session_state['last_booking'] = {
                'id': booking_id,
                'name': c_name,
                'phone': c_phone,
                'email': c_email,
                'amount': grand_total,
                'payment_method': payment_method,
                'payment_link': payment_link
            }

            # If card payment chosen, show link and attempt to email receipt (if SMTP configured)
            if payment_method == "Credit/Debit Card (via Link)":
                st.info("A secure payment link was generated below. You can copy or send it to the customer.")
                st.write(payment_link)
                # Attempt to send confirmation email
                smtp_host = st.secrets.get("SMTP_HOST") if "SMTP_HOST" in st.secrets else None
                if smtp_host and c_email:
                    try:
                        import smtplib
                        from email.message import EmailMessage
                        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
                        smtp_user = st.secrets.get("SMTP_USER")
                        smtp_pass = st.secrets.get("SMTP_PASS")

                        msg = EmailMessage()
                        msg["Subject"] = f"AXIS Booking Confirmation & Payment Link - {booking_id[:8]}"
                        msg["From"] = st.secrets.get("FROM_EMAIL", smtp_user)
                        msg["To"] = c_email
                        msg.set_content(f"Thank you {c_name},\n\nPlease pay MYR {grand_total:.2f} using the secure link:\n{payment_link}\n\nCustomer Service: +60146814167 (08:00-20:00 daily)")

                        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                        server.starttls()
                        if smtp_user and smtp_pass:
                            server.login(smtp_user, smtp_pass)
                        server.send_message(msg)
                        server.quit()
                        st.success("Payment link emailed to customer successfully.")
                    except Exception as e:
                        st.error(f"Unable to send email: {e}")
                else:
                    st.warning("SMTP not configured or customer email missing — payment link not emailed.")

            else:
                st.success(t("✅ Booking and Feedback Logged!"))

            # Persist booking in session for reporting
            # Get location coordinates from address or postcode
            location_lat, location_lon = 2.726, 101.938  # Default to Seremban 2
            for loc_name, coords in LOCATION_COORDS.items():
                if loc_name.lower() in c_address.lower() or loc_name.lower() in c_postcode.lower():
                    location_lat, location_lon = coords
                    break
            
            booking_record = {
                'id': booking_id,
                'created_at': datetime.now(),
                'service_date': st.session_state.get('last_booking_date', None),
                'amount': grand_total,
                'payment_method': payment_method,
                'customer_name': c_name,
                'location_lat': location_lat,
                'location_lon': location_lon,
                'customer_address': c_address,
                'assigned_to': None,
                'assigned_at': None,
            }
            if 'bookings' not in st.session_state:
                st.session_state['bookings'] = []
            st.session_state['bookings'].append(booking_record)
            
            # Save to database
            _save_booking_to_db(booking_record)

            st.session_state['booking_confirmed'] = True

        if 'booking_confirmed' in st.session_state and st.session_state['booking_confirmed']:
            rating = st.slider(t("Rate the service (1-5 stars)"), 1, 5, 5)
            st.write(f"{t('Thank you for your rating:')} {rating} ⭐")

# 4. PARTNER PORTAL
elif menu == "🤝 Partner Portal":
    st.title(t("🤝 Partner Job Inbox"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    _init_cleaners()
    
    # Status Toggle
    st.subheader(t("🟢 Your Status"))
    partner_name = st.session_state.get('current_partner_name', 'Partner')
    current_status = st.radio(t("Status"), ["Online", "Offline"], index=0, horizontal=True)
    
    # Update partner's status in cleaners list
    if 'cleaners' in st.session_state:
        for cleaner in st.session_state['cleaners']:
            if cleaner['name'] == partner_name:
                cleaner['status'] = current_status
                # Save status change to database
                _save_cleaner_to_db(cleaner)
                break
    
    st.write(f"**Current Status:** {current_status}")
    
    # Assigned Job Section
    st.subheader(t("📌 Assigned Jobs"))
    if current_status == "Online":
        bookings = st.session_state.get('bookings', [])
        assigned_jobs = [b for b in bookings if b.get('assigned_to') == partner_name]
        
        if assigned_jobs:
            for job in assigned_jobs:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Customer:** {job.get('customer_name')}")
                        st.write(f"**Address:** {job.get('customer_address')}")
                        st.write(f"**Amount:** MYR {job.get('amount', 0):.2f}")
                        st.write(f"**Assigned At:** {job.get('assigned_at').strftime('%Y-%m-%d %H:%M') if job.get('assigned_at') else 'N/A'}")
                    with col2:
                        st.info(f"Job ID: {job['id'][:8]}")
                        if st.button(t("Accept Job"), key=f"accept_{job['id']}"):
                            st.success(t("Job accepted! Navigate to the location now."))
                        if st.button(t("Decline"), key=f"decline_{job['id']}"):
                            job['assigned_to'] = None
                            job['assigned_at'] = None
                            # Also clear assignment from the cleaner
                            for cleaner in st.session_state.get('cleaners', []):
                                if cleaner['assigned_job'] == job['id']:
                                    cleaner['assigned_job'] = None
                                    _save_cleaner_to_db(cleaner)
                                    break
                            # Save job update to database
                            _save_booking_to_db(job)
                            st.rerun()
        else:
            st.info(t("No jobs assigned yet. You will receive a job once you're online and available."))
    else:
        st.warning(t("Go Online to receive job assignments."))
    
    # Registration Section
    st.subheader(t("Registration"))
    with st.expander(t("Complete Registration")):
        nric_passport = st.file_uploader(t("Upload NRIC or Passport"), key="partner_nric_passport")
        selfie = st.file_uploader(t("Upload Selfie for Verification"), key="partner_selfie")
        p_name = st.text_input(t("Full Name"), key="partner_full_name")
        gender = st.selectbox(t("Gender"), ["Male", "Female"], key="partner_gender")
        p_dob = st.date_input(t("Date of Birth"), key="partner_dob")
        p_contact = st.text_input(t("Contact Number"), key="partner_contact")
        next_kin_name = st.text_input(t("Next of Kin Name (required)"), key="partner_next_kin_name")
        next_kin_contact = st.text_input(t("Next of Kin Contact (required)"), key="partner_next_kin_contact")
        bank_name = st.selectbox(t("Bank Name"), ["Maybank", "CIMB", "Public Bank", "RHB", "Hong Leong Bank", "AmBank", "Bank Islam", "Bank Rakyat"], key="partner_bank_name")
        account_number = st.text_input(t("Account Number"), key="partner_account_number")
        if st.button(t("Register"), key="partner_register_btn"):
            if not next_kin_name or not next_kin_contact:
                st.error(t("Next of kin name and contact are required."))
            else:
                st.success(t("Registration Complete!"))
                _init_cleaners()
                new_name = p_name or p_contact or "New Cleaner"
                st.session_state['current_partner_name'] = new_name
                new_cleaner = {
                    'name': new_name,
                    'lat': 2.726, 'lon': 101.938,
                    'status': 'Online', 'last_update': None, 'on_site_since': None,
                    'expected_minutes': 90, 'email': p_contact, 'next_kin_name': next_kin_name, 'next_kin_contact': next_kin_contact,
                    'bank_name': bank_name, 'account_number': account_number, 'assigned_job': None
                }
                st.session_state['cleaners'].append(new_cleaner)
                # Save to database
                _save_cleaner_to_db(new_cleaner)
                st.success(t("Registration Complete!"))
                st.rerun()
    
    # Planner
    st.subheader(t("Planner"))
    with st.expander(t("View Upcoming Bookings")):
        st.write("**Tomorrow:** Cleaning at Garden Homes, 10:00 AM")
        st.write("**Next Week:** Cleaning at Sendayan, 2:00 PM")
        st.write("**Next Month:** Cleaning at Putrajaya, 11:00 AM")
    
    # Job Details
    st.subheader(t("Upcoming Job"))
    st.write(f"*{t('Service Type')}:* Sweeping, Vacuuming and Mopping")
    st.write(f"*{t('Distance to Site')}:* 5 KM (30 mins)")
    st.write(f"*{t('Customer Name')}:* Siti Aminah")
    st.write(f"*{t('Contact')}:* 012-3456789")
    st.write(f"*{t('Address')}:* Garden Homes, Seremban")
    
    # Earnings
    st.subheader(t("Earnings"))
    st.metric(t("Daily Earnings"), "MYR 135.00")
    st.metric(t("Weekly Earnings"), "MYR 945.00")
    st.metric(t("Monthly Earnings"), "MYR 3780.00")
    st.metric(t("Your 90% Payout"), f"MYR {135 * 0.9:.2f}")
    with st.expander(t("Earnings Breakdown")):
        st.write("**Daily Breakdown:**")
        st.write("- Job 1: MYR 50.00")
        st.write("- Job 2: MYR 45.00")
        st.write("- Job 3: MYR 40.00")
        st.write("**Weekly Breakdown:** Similar pattern for 7 days")
        st.write("**Monthly Breakdown:** 4 weeks accumulation")
    
    # Withdrawal
    st.subheader(t("Withdrawal"))
    if st.button(t("Withdraw Earnings")):
        st.success(t("Withdrawal processed automatically to your bank account!"))

# 5. SUPERVISOR PORTAL (REPLY FUNCTION ADDED)
elif menu == "📋 Supervisor Portal":
    st.title(t("📋 Supervisor Control"))
    st.write(f"{t('Selected Language')}: {selected_language}")
    
    _init_cleaners()
    _auto_assign_jobs()  # Auto-assign jobs to nearest available cleaners
    
    # Auto-Assignment Dashboard
    st.subheader(t("🤖 Auto-Assignment Status"))
    col1, col2, col3 = st.columns(3)
    
    bookings = st.session_state.get('bookings', [])
    unassigned_jobs = [b for b in bookings if not b.get('assigned_to')]
    assigned_jobs = [b for b in bookings if b.get('assigned_to')]
    
    with col1:
        st.metric(t("Total Jobs"), len(bookings))
    with col2:
        st.metric(t("Assigned"), len(assigned_jobs))
    with col3:
        st.metric(t("Pending"), len(unassigned_jobs))
    
    # Assigned Jobs Display
    if assigned_jobs:
        st.subheader(t("✅ Assigned Jobs"))
        for job in assigned_jobs:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**Customer:** {job.get('customer_name')}")
                    st.write(f"**Location:** {job.get('customer_address')}")
                    st.write(f"**Amount:** MYR {job.get('amount', 0):.2f}")
                with col2:
                    st.info(f"**Assigned To:** {job.get('assigned_to')}")
                with col3:
                    st.write(f"ID: {job['id'][:8]}")
    
    # Unassigned Jobs Display
    if unassigned_jobs:
        st.subheader(t("⏳ Pending Assignment"))
        st.warning(f"{len(unassigned_jobs)} jobs waiting for available cleaners...")
        for job in unassigned_jobs:
            with st.container(border=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Customer:** {job.get('customer_name')}")
                    st.write(f"**Location:** {job.get('customer_address')}")
                    st.write(f"**Amount:** MYR {job.get('amount', 0):.2f}")
                with col2:
                    st.write(f"ID: {job['id'][:8]}")
                    if st.button(t("Try Assign"), key=f"try_assign_{job['id']}"):
                        st.rerun()
    
    # Map View placeholder showing cleaner locations (simulated)
    try:
        _init_cleaners()
        import pandas as pd
        cleaners = st.session_state.get('cleaners', [])
        if cleaners:
            st.subheader(t("Map View"))
            map_df = pd.DataFrame([{'lat': c['lat'], 'lon': c['lon'], 'name': c['name'], 'status': c['status']} for c in cleaners])
            # st.map accepts columns named 'lat' and 'lon'
            st.map(map_df[['lat', 'lon']])
            with st.expander(t("Cleaner Locations")):
                for c in cleaners:
                    st.write(f"- {c['name']}: {c['status']} (Lat: {round(c['lat'],6)}, Lon: {round(c['lon'],6)})")
        else:
            st.info(t("No cleaner location data available to display."))
    except Exception:
        st.info(t("Map View not available in this environment. This is a placeholder."))
    
    # Supervisor Info
    st.info("Supervisor 1: Name: Dian, Employee number AXIS0002\n\nSupervisor 2: Name: Aya, Employee number AXIS0003")
    # Verify Cleaners
    st.subheader(t("Verify Cleaners"))
    with st.expander(t("Pending Verifications")):
        st.write("**Cleaner: Ahmad bin Abdullah**")
        st.write("NRIC: Uploaded")
        st.write("Selfie: Uploaded")
        if st.button(t("Approve Ahmad")):
            st.success(t("Ahmad approved!"))
        st.write("**Cleaner: Siti Aminah**")
        st.write("NRIC: Uploaded")
        st.write("Selfie: Pending")
        if st.button(t("Approve Siti")):
            st.success(t("Siti approved!"))
    
    # Banking Details
    st.subheader(t("Banking Details"))
    s_bank_name = st.selectbox(t("Bank Name"), ["Maybank", "CIMB", "Public Bank", "RHB", "Hong Leong Bank", "AmBank", "Bank Islam", "Bank Rakyat"], key="supervisor_bank_name")
    s_account_number = st.text_input(t("Account Number"), key="supervisor_account_number")
    
    # Earnings (split equally between both supervisors)
    st.subheader(t("Earnings (Each Supervisor)"))
    total_daily_commission = 3.00
    total_weekly_commission = 21.00
    total_monthly_commission = 84.00
    st.metric(t("Daily Commission"), f"MYR {total_daily_commission/2:.2f}")
    st.metric(t("Weekly Commission"), f"MYR {total_weekly_commission/2:.2f}")
    st.metric(t("Monthly Commission"), f"MYR {total_monthly_commission/2:.2f}")
    st.caption("*Commission is split equally between Supervisor 1 (Dian) and Supervisor 2 (Aya)*")
    
    # Auto-Transaction Status
    st.subheader(t("💳 Automatic Daily Transaction"))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("⏰ Scheduled Time: 8:00 PM Daily")
    with col2:
        st.success("✅ Status: Active")
    with col3:
        st.write("**Bank:** Maybank")
    st.caption("💬 Your earnings are automatically transferred to your bank account every day at 8:00 PM (UTC+8)")
    
    # Cleaner Movements
    st.subheader(t("Cleaner Movements & Assignments"))
    cleaners = st.session_state.get('cleaners', [])
    for cleaner in cleaners:
        assigned_status = "Assigned" if cleaner.get('assigned_job') else "Available"
        status_icon = "🟢" if cleaner['status'] == "Online" else "🔴"
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{status_icon} **{cleaner['name']}** - {cleaner['status']}")
                st.write(f"Location: Lat {round(cleaner['lat'], 4)}, Lon {round(cleaner['lon'], 4)}")
                st.write(f"Job Status: {assigned_status}")
                if cleaner.get('assigned_job'):
                    # Find the assigned job details
                    job = next((b for b in bookings if b['id'] == cleaner['assigned_job']), None)
                    if job:
                        st.write(f"📌 Working for: {job.get('customer_name')}")
            with col2:
                if cleaner['status'] == 'Online':
                    st.success(f"ID: {cleaner['name'][:3]}")
                else:
                    st.caption(f"ID: {cleaner['name'][:3]}")
    
    st.subheader(t("📬 Customer Feedback & Complaints"))
    with st.expander(t("View Pending Feedback from: En. Ahmad")):
        st.write(f"*{t('Customer Message')}:* '{t('Cleaner missed the kitchen floor.')}'")
        reply_options = st.selectbox(t("Resolution"), ["Future Discount Coupon - MYR 10", "Cleaner to Redo", "Sincerely Apologize Notes for this One Off Incident"])
        if st.button(t("Send Reply to Customer")):
            st.success(t("Reply sent to customer email & points notification."))

# 6. MEMBERSHIP & POINTS (RESTORED)
elif menu == "⭐ Membership & Points":
    st.title(t("⭐ AXIS Gold Membership"))
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
    if st.text_input(t("Key"), type="password") == "AXIS2026":
        # --- SUPERVISOR MANAGEMENT SECTION ---
        st.subheader("👥 Supervisor Onboarding & Management")
        
        supervisor_tab1, supervisor_tab2 = st.tabs(["Add New Supervisor", "Manage Supervisors"])
        
        with supervisor_tab1:
            st.write("Register a new supervisor with complete details")
            col1, col2 = st.columns(2)
            
            with col1:
                sup_name = st.text_input("Supervisor Full Name", key="sup_name_input")
                sup_email = st.text_input("Email Address", key="sup_email_input")
                sup_phone = st.text_input("Phone Number", key="sup_phone_input")
                sup_nric = st.text_input("NRIC/ID Number", key="sup_nric_input")
            
            with col2:
                sup_employee_num = st.text_input("Employee Number (e.g., AXIS0001)", key="sup_employee_num_input")
                sup_bank = st.selectbox("Bank Name", ["Maybank", "CIMB", "Public Bank", "RHB", "Hong Leong Bank", "AmBank", "Bank Islam", "Bank Rakyat"], key="sup_bank_selectbox")
                sup_account = st.text_input("Bank Account Number", key="sup_account_input")
                sup_personal = st.text_area("Personal Particulars (Address, etc.)", key="sup_personal_input")
            
            if st.button("Register Supervisor", key="add_supervisor"):
                if sup_name and sup_employee_num and sup_email and sup_bank and sup_account:
                    sup_id = f"SUP_{sup_employee_num}_{int(datetime.now().timestamp())}"
                    new_supervisor = {
                        'id': sup_id,
                        'name': sup_name,
                        'employee_number': sup_employee_num,
                        'email': sup_email,
                        'phone': sup_phone,
                        'nric': sup_nric,
                        'bank_name': sup_bank,
                        'account_number': sup_account,
                        'personal_details': sup_personal,
                        'created_at': datetime.now(),
                        'status': 'Active',
                    }
                    _save_supervisor_to_db(new_supervisor)
                    st.session_state['supervisors'].append(new_supervisor)
                    st.success(f"✅ Supervisor {sup_name} registered successfully with Employee Number: {sup_employee_num}")
                    st.rerun()
                else:
                    st.error("Please fill all required fields (Name, Employee Number, Email, Bank, Account)")
        
        with supervisor_tab2:
            supervisors = st.session_state.get('supervisors', [])
            if supervisors:
                st.write(f"Total Supervisors: {len(supervisors)}")
                for sup in supervisors:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.write(f"**Name:** {sup['name']}")
                            st.write(f"**Employee #:** {sup['employee_number']}")
                            st.write(f"**Email:** {sup['email']}")
                        with col2:
                            st.write(f"**Phone:** {sup['phone']}")
                            st.write(f"**Bank:** {sup['bank_name']}")
                            st.write(f"**Account:** {sup['account_number'][-4:]}")
                        with col3:
                            st.write(f"**Status:** {sup['status']}")
                            if st.button("Edit", key=f"edit_{sup['id']}"):
                                st.info("Edit feature coming soon")
            else:
                st.info("No supervisors registered yet")
        
        # --- GOOGLE SHEETS INTEGRATION SECTION ---
        st.subheader("📊 Google Sheets Integration")
        
        if GOOGLE_SHEETS_AVAILABLE:
            gs_tab1, gs_tab2 = st.tabs(["Setup", "Sync Data"])
            
            with gs_tab1:
                st.write("Set up Google Sheets integration to automatically sync supervisor and transaction data")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    spreadsheet_id = st.text_input(
                        "Google Sheets ID",
                        help="Enter the spreadsheet ID from your Google Sheet URL (the long alphanumeric string)"
                    )
                    if st.button("🔗 Connect to Spreadsheet", key="connect_gs"):
                        if spreadsheet_id:
                            st.session_state['google_sheets_id'] = spreadsheet_id
                            st.success(f"✅ Connected to spreadsheet: {spreadsheet_id[:20]}...")
                        else:
                            st.error("Please enter a valid Spreadsheet ID")
                
                with col2:
                    st.write("**Need help?**")
                    st.write("[Google Sheets Setup Guide](https://developers.google.com/sheets/api/quickstart/python)")
                
                st.info(
                    "📝 **Setup Instructions:**\n"
                    "1. Go to [Google Cloud Console](https://console.cloud.google.com/)\n"
                    "2. Create a new project\n"
                    "3. Enable Google Sheets API\n"
                    "4. Create OAuth 2.0 credentials\n"
                    "5. Download and save credentials.json in the project folder"
                )
            
            with gs_tab2:
                if 'google_sheets_id' in st.session_state:
                    st.success(f"✅ Connected to: {st.session_state['google_sheets_id'][:30]}...")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📤 Sync Supervisors", key="sync_supervisors"):
                            with st.spinner("Syncing supervisors..."):
                                try:
                                    if os.path.exists("credentials.json"):
                                        gs_manager = init_google_sheets("credentials.json")
                                        if gs_manager:
                                            supervisors = st.session_state.get('supervisors', [])
                                            if gs_manager.write_supervisors(st.session_state['google_sheets_id'], supervisors):
                                                st.success(f"✅ Synced {len(supervisors)} supervisors to Google Sheets")
                                            else:
                                                st.error("❌ Failed to sync supervisors")
                                        else:
                                            st.error("❌ Google Sheets authentication failed. Check credentials.json")
                                    else:
                                        st.error("❌ credentials.json not found")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                    
                    with col2:
                        if st.button("📤 Sync Transactions", key="sync_transactions"):
                            with st.spinner("Syncing transactions..."):
                                try:
                                    if os.path.exists("credentials.json"):
                                        gs_manager = init_google_sheets("credentials.json")
                                        if gs_manager:
                                            # Load transactions from database
                                            _init_db()
                                            conn = sqlite3.connect(DB_FILE)
                                            c = conn.cursor()
                                            c.execute("SELECT * FROM auto_transactions")
                                            rows = c.fetchall()
                                            conn.close()
                                            
                                            transactions = []
                                            for row in rows:
                                                trans = {
                                                    'id': row[0],
                                                    'supervisor_id': row[1],
                                                    'amount': row[2],
                                                    'scheduled_time': row[3],
                                                    'last_transaction': row[4],
                                                    'status': row[5],
                                                }
                                                transactions.append(trans)
                                            
                                            if gs_manager.write_transactions(st.session_state['google_sheets_id'], transactions):
                                                st.success(f"✅ Synced {len(transactions)} transactions to Google Sheets")
                                            else:
                                                st.error("❌ Failed to sync transactions")
                                        else:
                                            st.error("❌ Google Sheets authentication failed")
                                    else:
                                        st.error("❌ credentials.json not found")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                    
                    with col3:
                        if st.button("🔄 Sync All Data", key="sync_all"):
                            with st.spinner("Syncing all data..."):
                                try:
                                    if os.path.exists("credentials.json"):
                                        gs_manager = init_google_sheets("credentials.json")
                                        if gs_manager:
                                            supervisors = st.session_state.get('supervisors', [])
                                            
                                            # Load transactions
                                            _init_db()
                                            conn = sqlite3.connect(DB_FILE)
                                            c = conn.cursor()
                                            c.execute("SELECT * FROM auto_transactions")
                                            rows = c.fetchall()
                                            conn.close()
                                            
                                            transactions = []
                                            for row in rows:
                                                trans = {
                                                    'id': row[0],
                                                    'supervisor_id': row[1],
                                                    'amount': row[2],
                                                    'scheduled_time': row[3],
                                                    'last_transaction': row[4],
                                                    'status': row[5],
                                                }
                                                transactions.append(trans)
                                            
                                            if gs_manager.sync_all_data(st.session_state['google_sheets_id'], supervisors, transactions):
                                                st.success(f"✅ Synced all data successfully!")
                                            else:
                                                st.error("❌ Some data failed to sync")
                                        else:
                                            st.error("❌ Google Sheets authentication failed")
                                    else:
                                        st.error("❌ credentials.json not found")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                else:
                    st.info("👈 First, connect to a Google Sheet in the 'Setup' tab")
        else:
            st.warning("⚠️ Google Sheets integration libraries not installed. Run: pip install google-auth-oauthlib google-api-python-client")
        
        # --- BANKING DETAILS SECTION ---
        st.subheader(t("Banking Details"))
        a_bank_name = st.selectbox(t("Bank Name"), ["Maybank", "CIMB", "Public Bank", "RHB", "Hong Leong Bank", "AmBank", "Bank Islam", "Bank Rakyat"], key="admin_bank_name")
        a_account_number = st.text_input(t("Account Number"), key="admin_account_number")
        
        st.subheader(t("Earnings (Minus Partners & Supervisor)"))
        st.metric(t("Daily Earnings"), "MYR 13.50")
        st.metric(t("Weekly Earnings"), "MYR 94.50")
        st.metric(t("Monthly Earnings"), "MYR 378.00")

        # Weekly revenue chart and queued bookings (aggregated by service date)
        try:
            import pandas as pd
            today = datetime.now().date()
            # get bookings from session
            bookings = st.session_state.get('bookings', [])

            # build dataframe of bookings by service_date for last 7 days
            rows = []
            for b in bookings:
                svc = b.get('service_date')
                amount = float(b.get('amount', 0))
                # normalize service date to date object if possible
                svc_date = None
                if svc is not None:
                    if isinstance(svc, datetime):
                        svc_date = svc.date()
                    elif hasattr(svc, 'date'):
                        svc_date = svc
                    else:
                        try:
                            svc_date = pd.to_datetime(str(svc)).date()
                        except Exception:
                            svc_date = None
                # fallback to created_at if service_date missing
                if svc_date is None:
                    created = b.get('created_at')
                    if created:
                        if isinstance(created, datetime):
                            svc_date = created.date()
                        elif hasattr(created, 'date'):
                            svc_date = created

                if svc_date:
                    rows.append({'service_date': svc_date, 'amount': amount})

            df = pd.DataFrame(rows)

            dates = [today - pd.Timedelta(days=i) for i in range(6, -1, -1)]

            revenue_by_day = {d.strftime('%Y-%m-%d'): 0.0 for d in dates}
            if not df.empty and len(df) > 0:
                df['service_date_str'] = df['service_date'].astype(str)
                for d in revenue_by_day.keys():
                    revenue_by_day[d] = float(df.loc[df['service_date_str'] == d, 'amount'].sum())

            # queued bookings made in advance: count service_date > today
            queued_counts = {d.strftime('%Y-%m-%d'): 0 for d in dates}
            if not df.empty and len(df) > 0:
                for _, row in df.iterrows():
                    svc = row.get('service_date')
                    if svc and isinstance(svc, (datetime.date, datetime)):
                        svc_date = svc.date() if isinstance(svc, datetime) else svc
                        if svc_date > today:
                            svc_str = svc_date.strftime('%Y-%m-%d') if hasattr(svc_date, 'strftime') else str(svc_date)
                            if svc_str in queued_counts:
                                queued_counts[svc_str] += 1

            col1, col2 = st.columns(2)
            with col1:
                st.subheader('Weekly Revenue (by service date, last 7 days)')
                rev_df = pd.DataFrame({'date': list(revenue_by_day.keys()), 'revenue': list(revenue_by_day.values())})
                rev_df = rev_df.set_index('date')
                st.bar_chart(rev_df)

            with col2:
                st.subheader('Queued Bookings (scheduled)')
                queue_df = pd.DataFrame({'date': list(queued_counts.keys()), 'queued': list(queued_counts.values())}).set_index('date')
                st.bar_chart(queue_df)

        except Exception as e:
            st.error(f"Unable to generate admin charts: {e}")
        
        st.subheader(t("90/10 Financial Split"))
        st.metric(t("Partner Share"), "MYR 135.00")
        st.metric(t("Company Gross (Before Supervisor Comm)"), "MYR 15.00")
        
        # Withdrawal
        st.subheader(t("Withdrawal"))
        if st.button(t("Withdraw Salary")):
            st.success(t("Withdrawal processed automatically to your bank account!"))
        
        st.subheader(t("Area Demand"))
        st.write("**Most Demanded Areas:**")
        st.write("- Seremban 2: 45 bookings")
        st.write("- Garden Homes: 38 bookings")
        st.write("- Putrajaya: 32 bookings")

    # Footer copyright
    st.markdown("<div style='text-align:center; color:gray; margin-top:2em;'>© 2026 AXIS Modern Building Management.</div>", unsafe_allow_html=True)

    # Footer / Copyright
    st.write("---")
    st.markdown("&copy; 2026 AXIS Modern Building Management")
