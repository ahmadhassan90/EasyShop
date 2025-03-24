import streamlit as st
import sqlite3
import requests
from bs4 import BeautifulSoup

# Initialize session state variables
if "price" not in st.session_state:
    st.session_state.price = None
if "sku" not in st.session_state:
    st.session_state.sku = None
if "selected_range" not in st.session_state:
    st.session_state.selected_range = None

# Streamlit UI
st.title("🛍️ Khaadi Price Tracker")
product_url = st.text_input("🔗 Enter Khaadi Product URL", "")

# Database setup
conn = sqlite3.connect("prices.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS prices (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                          url TEXT, price TEXT, sku TEXT)"""
)
conn.commit()


def get_price_and_sku(url):
    """Scrapes the product price & SKU from Khaadi's website."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Mobile) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        st.write(f"🔍 Status Code: {response.status_code}")  # Debugging

        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract price
        price_element = soup.find("span", {"class": "price"})  # Update selector if needed
        price = price_element.text.strip() if price_element else None

        # Extract SKU
        sku_element = soup.find("span", {"class": "sku"})
        sku = sku_element.text.strip() if sku_element else None

        return price, sku
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return None, None


# Button Click Logic
if st.button("Check Price"):
    st.write("✅ Button Clicked!")  # Debugging

    if product_url:
        price, sku = get_price_and_sku(product_url)
        st.write(f"💰 Scraped Price: {price}")  # Debugging
        st.write(f"🆔 SKU: {sku}")  # Debugging

        if price:
            st.session_state.price = price
            st.session_state.sku = sku
            st.session_state.selected_range = (int(float(price) * 0.5), int(float(price)))

            # Store in database
            c.execute("INSERT INTO prices (url, price, sku) VALUES (?, ?, ?)", (product_url, price, sku))
            conn.commit()

            st.success("✅ Price checked and saved!")
            st.experimental_rerun()  # Force UI refresh
        else:
            st.warning("⚠️ Could not fetch the price. Try again!")
    else:
        st.warning("⚠️ Please enter a product URL!")

# Display Last Saved Price
if st.session_state.price:
    st.subheader("🔍 Last Checked Price")
    st.write(f"💰 **Price:** {st.session_state.price}")
    st.write(f"🆔 **SKU:** {st.session_state.sku}")

# Close DB connection
conn.close()
