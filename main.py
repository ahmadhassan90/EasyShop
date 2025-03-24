import streamlit as st
import requests
import sqlite3
from bs4 import BeautifulSoup

# Function to scrape price & SKU
def get_price_and_sku(product_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract SKU
        sku_tag = soup.select_one("div.product-number span")
        product_sku = sku_tag.text.strip() if sku_tag else "SKU not found"

        # Extract Price
        price_tag = soup.select_one("span.value.cc-price")
        product_price = float(price_tag.text.strip().replace("PKR ", "").replace(",", "")) if price_tag else None

        return product_price, product_sku
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching product: {e}")
        return None, None

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("config.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracking (
            product_url TEXT PRIMARY KEY,
            min_price INTEGER,
            max_price INTEGER,
            sku TEXT
        )
    """)
    conn.commit()
    conn.close()

# Save data to SQLite
def save_to_db(product_url, min_price, max_price, sku):
    conn = sqlite3.connect("config.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO tracking VALUES (?, ?, ?, ?)", 
                   (product_url, min_price, max_price, sku))
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# Streamlit UI
st.title("🛍️ Khaadi Price Tracker")

# Session state for tracking UI updates
if "price" not in st.session_state:
    st.session_state.price = None
if "sku" not in st.session_state:
    st.session_state.sku = ""
if "selected_range" not in st.session_state:
    st.session_state.selected_range = (0, 0)

# User inputs product URL
product_url = st.text_input("🔗 Enter Khaadi Product URL")

if st.button("Check Price"):
    if product_url:
        price, sku = get_price_and_sku(product_url)

        if price:
            min_price = int(price * 0.5)
            max_price = int(price)

            # Update session state
            st.session_state.price = price
            st.session_state.sku = sku
            st.session_state.selected_range = (min_price, max_price)

            # Save to database
            save_to_db(product_url, min_price, max_price, sku)

# Show details only after fetching price
if st.session_state.price:
    st.success(f"✅ Current Price: {st.session_state.price} PKR")
    st.info(f"🆔 SKU: {st.session_state.sku}")

    # Price range slider
    selected_range = st.slider(
        "📉 Select Notification Price Range",
        min_value=st.session_state.selected_range[0],
        max_value=st.session_state.selected_range[1],
        value=st.session_state.selected_range
    )

    # Update session state
    st.session_state.selected_range = selected_range

    # Start Tracking Button
    if st.button("Start Tracking"):
        save_to_db(product_url, selected_range[0], selected_range[1], st.session_state.sku)
        st.success("✅ Tracking started! You'll be notified when the price is within range.")
