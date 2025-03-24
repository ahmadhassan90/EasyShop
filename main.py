import streamlit as st
import json
import requests
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
        if price_tag:
            product_price = float(price_tag.text.strip().replace("PKR ", "").replace(",", ""))
        else:
            product_price = None

        return product_price, product_sku
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching product: {e}")
        return None, None

# Streamlit UI
st.title("🛍️ Khaadi Price Tracker")

# Initialize session state
if "product_url" not in st.session_state:
    st.session_state.product_url = ""
if "price" not in st.session_state:
    st.session_state.price = None
if "sku" not in st.session_state:
    st.session_state.sku = ""
if "selected_range" not in st.session_state:
    st.session_state.selected_range = (0, 0)

# User inputs product URL
product_url = st.text_input("🔗 Enter Khaadi Product URL", st.session_state.product_url)

if st.button("Check Price"):
    if product_url:
        price, sku = get_price_and_sku(product_url)

        if price:
            st.session_state.product_url = product_url
            st.session_state.price = price
            st.session_state.sku = sku
            st.session_state.selected_range = (int(price * 0.5), int(price))

# Show scraped details if available
if st.session_state.price:
    st.success(f"✅ Current Price: {st.session_state.price} PKR")
    st.info(f"🆔 SKU: {st.session_state.sku}")

    # Price range slider (50% of price to current price)
    min_price = int(st.session_state.price * 0.5)
    max_price = int(st.session_state.price)

    selected_range = st.slider(
        "📉 Select Notification Price Range", 
        min_value=min_price, 
        max_value=max_price, 
        value=st.session_state.selected_range
    )

    # Save range to session state
    st.session_state.selected_range = selected_range

    # Save settings for tracking
    if st.button("Start Tracking"):
        user_config = {
            "product_url": st.session_state.product_url,
            "min_price": st.session_state.selected_range[0],
            "max_price": st.session_state.selected_range[1],
            "sku": st.session_state.sku
        }
        with open("config.json", "w") as f:
            json.dump(user_config, f)
        st.success("✅ Tracking started! You'll be notified when the price is within range.")
