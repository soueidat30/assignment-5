from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

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

# we must use multi threading to speed up the scraping process
def scrape_products(timestamp,item_url,product ):
    try:
        title = product.find_element(By.CSS_SELECTOR, 'span.ebayui-ellipsis-3').text.strip()
    except:
        title = "N/A"
    # discounted price
    try:
        price = product.find_element(By.CSS_SELECTOR, 'span.ux-textspans').text.strip()
    except:
        price = "N/A"

    # original price
    try:
        original_price = product.find_element(By.CSS_SELECTOR, 'span.itemtile-price-strikethrough').text.strip()
    except:
        original_price = "N/A"

    # shipping details
    try:
        shipping = product.find_element(By.CSS_SELECTOR, 'span.s-item__shipping').text.strip()
    except:
        shipping = "N/A"
            
    return{
            "timestamp": timestamp,
            "title": title,
            "price": price,
            "original price": original_price,
            "Shipping": shipping,
    }

def scrape_product_data():  
    bitcoin_data = []
    driver.get(URL)
    time.sleep(3)
    scroll_down_page()  
    try:
        # Capture timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item_url = driver.find_element(By.CSS_SELECTOR, 'a[itemprop="url"]').get_attribute('href')

        products = driver.find_elements(By.CSS_SELECTOR,  'div[itemscope][itemtype="https://schema.org/Product"]')
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(scrape_products, products))
        bitcoin_data.extend(list(results))
        return bitcoin_data
    except Exception as e:
        print("Error occurred:", e)
        return None

def save_to_csv(data):
    file_name = "ebay_tech_deals.csv"
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "timestamp", "title", "price", "original price", "shipping", "item url"
        ])

    new_row = pd.DataFrame([data])

    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(file_name, index=False)

if __name__ == "__main__":
    scraped_data = scrape_product_data()

    if scraped_data:
        save_to_csv(scraped_data)
        print("Data saved to ebay_tech_deals.csv")
    else:
        print("Failed to scrape data.")

    driver.quit()