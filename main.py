import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Function to scrape price & SKU
def get_price_and_sku(product_url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    
    try:
        st.write(f"Fetching URL: {product_url}")
        driver.get(product_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        st.write("🔍 Debug: Showing partial HTML content")
        st.code(soup.prettify()[:15000])

        sku_tag = soup.select_one("div.product-number span")
        product_sku = sku_tag.text.strip() if sku_tag else "SKU not found"
        st.write(f"🆔 SKU Found: {product_sku}")

        price_tag = soup.select_one("span.price, span.value, span.product-price, div.product-price span")
        if price_tag:
            price_text = price_tag.text.strip().replace("PKR", "").replace(",", "")
            product_price = float(price_text) if price_text else None
            st.write(f"💰 Price Found: {product_price}")
        else:
            st.write("❌ Debug: No price tag found.")
            product_price = None
        
        return product_price, product_sku
    except Exception as e:
        st.error(f"Error fetching product: {e}")
        return None, None
    finally:
        driver.quit()

# Session state for tracking
if "tracking" not in st.session_state:
    st.session_state.tracking = {}
if "price" not in st.session_state:
    st.session_state.price = None
if "sku" not in st.session_state:
    st.session_state.sku = ""
if "selected_range" not in st.session_state:
    st.session_state.selected_range = (0, 0)

# Save to session state
def save_to_db(product_url, min_price, max_price, sku):
    st.session_state.tracking[product_url] = (min_price, max_price, sku)

# Streamlit UI
st.title("🛍️ Khaadi Price Tracker (Debug Mode)")
product_url = st.text_input("🔗 Enter Khaadi Product URL")

if st.button("Check Price"):
    if product_url:
        price, sku = get_price_and_sku(product_url)
        if price:
            min_price = int(price * 0.5)
            max_price = int(price)
            st.session_state.price = price
            st.session_state.sku = sku
            st.session_state.selected_range = (min_price, max_price)
            save_to_db(product_url, min_price, max_price, sku)

if st.session_state.price:
    st.success(f"✅ Current Price: {st.session_state.price} PKR")
    st.info(f"🆔 SKU: {st.session_state.sku}")
    selected_range = st.slider(
        "📉 Select Notification Price Range",
        min_value=st.session_state.selected_range[0],
        max_value=st.session_state.selected_range[1],
        value=st.session_state.selected_range
    )
    st.session_state.selected_range = selected_range

    if st.button("Start Tracking"):
        save_to_db(product_url, selected_range[0], selected_range[1], st.session_state.sku)
        st.success("✅ Tracking started!")
