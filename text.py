from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor

# --- Chrome options ---
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless")  # headless for faster scraping

ua = UserAgent()
options.add_argument(f"user-agent={ua.random}")

service = Service(ChromeDriverManager().install())

URL = "https://www.ebay.com/globaldeals/tech"

# --- Scroll function ---
def scroll_down_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# --- Scrape product details from individual page ---
def scrape_product_page(item_url):
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(item_url)
        time.sleep(2)  # wait for page to load

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            title = driver.find_element(By.CSS_SELECTOR, 'h1.it-ttl').text.strip()
        except:
            title = "N/A"

        try:
            price = driver.find_element(By.CSS_SELECTOR, 'span#prcIsum, span#prcIsum_bidPrice').text.strip()
        except:
            price = "N/A"

        try:
            original_price = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="price"]').text.strip()
        except:
            original_price = "N/A"

        try:
            shipping = driver.find_element(By.CSS_SELECTOR, 'span#fshippingCost').text.strip()
        except:
            shipping = "N/A"

        driver.quit()

        return {
            "timestamp": timestamp,
            "title": title,
            "price": price,
            "original price": original_price,
            "shipping": shipping,
            "item url": item_url
        }
    except Exception as e:
        print(f"Error scraping {item_url}: {e}")
        return None

# --- Main scraping ---
def scrape_ebay_tech_deals():
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    time.sleep(3)
    scroll_down_page(driver)

    # Get all product URLs
    products = driver.find_elements(By.CSS_SELECTOR, 'a[itemprop="url"]')
    product_urls = [p.get_attribute('href') for p in products]
    driver.quit()

    # Use ThreadPoolExecutor to scrape details from each product page
    scraped_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(scrape_product_page, product_urls)
        scraped_data.extend([r for r in results if r is not None])

    return scraped_data

# --- Save to CSV ---
def save_to_csv(data):
    file_name = "ebay_tech_deals.csv"
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "timestamp", "title", "price", "original price", "shipping", "item url"
        ])

    new_df = pd.DataFrame(data)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(file_name, index=False)

# --- Run ---
if __name__ == "__main__":
    data = scrape_ebay_tech_deals()
    if data:
        save_to_csv(data)
        print(f"Scraped {len(data)} products. Data saved to ebay_tech_deals.csv")
    else:
        print("Failed to scrape data.")
