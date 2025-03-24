import requests
from bs4 import BeautifulSoup
import smtplib
import os
import json
import time

# Load config
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# Scrape price and SKU
def get_price_and_sku(product_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract price (Modify the selector as needed)
    price_tag = soup.find("span", {"class": "price"})
    sku_tag = soup.find("span", {"class": "sku"})  # Adjust selector as needed

    if price_tag and sku_tag:
        price = float(price_tag.text.strip().replace("PKR ", "").replace(",", ""))
        sku = sku_tag.text.strip()
        return price, sku
    return None, None

# Email notification
def send_email(price, sku, product_url):
    sender_email = os.getenv("EMAIL_SENDER")
    receiver_email = os.getenv("EMAIL_RECEIVER")
    email_password = os.getenv("EMAIL_PASSWORD")

    subject = "🎉 Price Drop Alert!"
    body = f"The product (SKU: {sku}) is now {price} PKR!\nCheck it out: {product_url}"

    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver_email, message)
        print("✅ Email Sent Successfully!")
    except Exception as e:
        print(f"❌ Error Sending Email: {e}")

# Scheduled price check
def check_price():
    config = load_config()
    product_url = config["product_url"]
    min_price = config["min_price"]
    max_price = config["max_price"]

    current_price, product_sku = get_price_and_sku(product_url)

    if current_price:
        print(f"🔎 Checking... Current Price: {current_price} PKR | SKU: {product_sku}")

        if min_price <= current_price <= max_price:
            send_email(current_price, product_sku, product_url)
