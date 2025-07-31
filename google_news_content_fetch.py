import trafilatura
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Wait for no network activity before extracting the URL
def get_real_url_from_google_news_rss(rss_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(rss_url)
        # Wait until there is no network activity with retries
        for _ in range(60):
            if driver.execute_script("return window.performance.getEntriesByType('resource').length === 0;"):
                break
            time.sleep(0.5)
        real_url = driver.current_url
    except TimeoutException:
        real_url = None
    finally:
        driver.quit()

    return real_url

# Wait for change in url from news.google.com to the real URL
def get_real_url_from_google_news_rss_alternative(rss_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(rss_url)
        # Wait until the URL changes from news.google.com to the real URL
        for _ in range(60):
            if "news.google.com" not in driver.current_url:
                break
            time.sleep(0.5)
        real_url = driver.current_url
    except TimeoutException:
        real_url = None
    finally:
        driver.quit()

    return real_url

# Extract content using trafilatura
def extract_with_trafilatura(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            result = trafilatura.extract(downloaded)
            if result:
                print("Google News Extracted Content:\n", result.strip())
                return result.strip()
    except Exception as e:
        print("Trafilatura failed:", e)
    return None
