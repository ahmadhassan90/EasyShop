import sqlite3
import requests
from bs4 import BeautifulSoup
import smtplib
import os

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
    except requests.exceptions.RequestException:
        return None, None

# Function to check prices and notify users
def check_price():
    conn = sqlite3.connect("config.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tracking")
    tracked_items = cursor.fetchall()

    for item in tracked_items:
        product_url, min_price, max_price, sku = item
        current_price, _ = get_price_and_sku(product_url)

        if current_price and min_price <= current_price <= max_price:
            send_email(product_url, current_price, sku)

    conn.close()

# Function to send email alerts
def send_email(product_url, current_price, sku):
    sender_email = os.getenv("EMAIL_SENDER")
    receiver_email = os.getenv("EMAIL_RECEIVER")
    password = os.getenv("EMAIL_PASSWORD")

    subject = "🔥 Price Drop Alert!"
    body = f"The price for {sku} is now {current_price} PKR.\nCheck it here: {product_url}"

    email_text = f"Subject: {subject}\n\n{body}"

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, email_text)
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    check_price()
