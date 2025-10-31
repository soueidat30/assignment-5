from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime
import os

# -----------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------
url = "https://www.ebay.com/globaldeals/tech"
csv_file = "ebay_tech_deals.csv"

# -----------------------------------------------------------
# SETUP SELENIUM (Headless for silent background execution)
# -----------------------------------------------------------
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)

# -----------------------------------------------------------
# SCROLL TO LOAD ALL PRODUCTS
# -----------------------------------------------------------
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_pause_time = 2

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# -----------------------------------------------------------
# WAIT FOR PRODUCT ELEMENTS
# -----------------------------------------------------------
WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-listing-id]"))
)

# -----------------------------------------------------------
# EXTRACT PRODUCT DATA
# -----------------------------------------------------------
products = driver.find_elements(By.CSS_SELECTOR, "[data-listing-id]")
scraped_data = []

for product in products:
    try:
        title = product.find_element(By.CSS_SELECTOR, "h3.dne-itemtile-title").text.strip()
    except:
        title = None

    try:
        price = product.find_element(By.CSS_SELECTOR, ".dne-itemtile-price").text.strip()
    except:
        price = None

    try:
        original_price = product.find_element(By.CSS_SELECTOR, ".itemtile-price-strikethrough").text.strip()
    except:
        original_price = None

    try:
       shipping_cost = product.find_element(By.ID, "fshippingCost").text.strip()
    except:
       shipping_cost = None

    try:
       shipping_location = product.find_element(By.CSS_SELECTOR, ".sh-col").text.strip()
    except:
       shipping_location = None
    shipping_full = f"{shipping_cost} | {shipping_location}"

    try:
        item_url = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
    except:
        item_url = None

    scraped_data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": title,
        "price": price,
        "original_price": original_price,
        "shipping": shipping_full,
        "item_url": item_url
    })

# -----------------------------------------------------------
# SAVE TO CSV (Append if file exists)
# -----------------------------------------------------------
df = pd.DataFrame(scraped_data)
if os.path.exists(csv_file):
    df.to_csv(csv_file, mode='a', index=False, header=False, encoding='utf-8-sig')
else:
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')

driver.quit()

print(f"✅ Scraping completed. {len(scraped_data)} products saved to '{csv_file}'.")