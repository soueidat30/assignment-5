from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

ua = UserAgent()
options.add_argument(f"user-agent={ua.random}")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

URL = "https://www.ebay.com/globaldeals/tech"

def scroll_down_page():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_product(product, timestamp):
    """Scrape a single product WebElement. Returns a dict."""
    try:
        title = product.find_element(By.CSS_SELECTOR, 'span[itemprop="name"]').text.strip()
    except:
        title = "N/A"

    try:
        price = product.find_element(By.CSS_SELECTOR, 'span.ux-textspans').text.strip()
    except:
        price = "N/A"

    try:
        original_price = product.find_element(By.CSS_SELECTOR, 'span.ux-textspans--STRIKETHROUGH').text.strip()
    except:
        original_price = "N/A"

    try:
        shipping = product.find_element(By.CSS_SELECTOR, 'span.ux-textspans--SECONDARY').text.strip()
    except:
        shipping = "N/A"

    try:
        item_url = product.find_element(By.CSS_SELECTOR, 'a[itemprop="url"]').get_attribute('href')
    except:
        item_url = "N/A"

    return {
        "timestamp": timestamp,
        "title": title,
        "price": price,
        "original price": original_price,
        "shipping": shipping,
        "item url": item_url
    }

def scrape_product_data():  
    rows = []
    driver.get(URL)
    time.sleep(3)
    scroll_down_page()

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        products = driver.find_elements(By.CSS_SELECTOR, 'div[itemscope][itemtype="https://schema.org/Product"]')

        # Sequential (safe) scraping of elements
        for p in products:
            rows.append(scrape_product(p, timestamp))

        return rows

    except Exception as e:
        print("Error occurred:", e)
        return None

def save_to_csv(list_of_dicts):
    file_name = "ebay_tech_deals.csv"
    try:
        df_existing = pd.read_csv(file_name)
    except FileNotFoundError:
        df_existing = pd.DataFrame(columns=[
            "timestamp", "title", "price", "original price", "shipping", "item url"
        ])

    df_new = pd.DataFrame(list_of_dicts)

    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_csv(file_name, index=False)

if __name__ == "__main__":
    try:
        scraped_data = scrape_product_data()

        if scraped_data:
            save_to_csv(scraped_data)
            print("Data saved to ebay_tech_deals.csv")
        else:
            print("Failed to scrape data or no products found.")

    finally:
        driver.quit()