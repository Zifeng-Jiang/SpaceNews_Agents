from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
import requests
from datetime import datetime
import logging

def setup_driver():
    """
    Initialize Selenium WebDriver with appropriate options
    """
    try:
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Use webdriver-manager to automatically manage ChromeDriver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_size(1400, 1000)
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        raise

def scrape_content(url):
    """
    Scrape the content of individual news articles using requests
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        response = requests.get(url, headers=headers, timeout=30)
        tree = html.fromstring(response.content)

        # Find the main content div and extract all text content from various elements
        content_div = tree.xpath('//div[contains(@class, "post-content")]')
        if not content_div:
            return "No Content"

        # Extract text from paragraphs, headlines, and list items
        text_elements = content_div[0].xpath('.//p|.//h3|.//h4|.//li')
        content = []

        for element in text_elements:
            text = element.text_content().strip()
            if text:
                content.append(text)

        return ' '.join(content)
    except Exception as e:
        logging.error(f"Error scraping content from {url}: {e}")
        return "No Content"

def get_spaceinafrica():
    """
    Main function to scrape Space in Africa news
    """
    driver = None
    try:
        driver = setup_driver()
        wait = WebDriverWait(driver, 30)

        # Get current date and first day of month
        current_date = datetime.now()
        first_day_of_month = current_date.replace(day=1)

        news_list = []
        processed_links = set()  # To avoid duplicate articles

        # Navigate to the main news page
        driver.get('https://spaceinafrica.com/news/')

        while True:
            try:
                # Wait for articles to load
                articles = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[contains(@class, "t-entry-text")]')
                ))

                for article in articles:
                    try:
                        # Get title and link
                        title_element = article.find_element(By.XPATH, './/h3[contains(@class, "t-entry-title")]//a')
                        link = title_element.get_attribute('href')

                        # Skip if we've already processed this article
                        if link in processed_links:
                            continue

                        processed_links.add(link)
                        title = title_element.text.strip()

                        # Get date
                        date_str = article.find_element(By.XPATH, './/p[contains(@class, "t-entry-meta")]//span').text.strip()

                        try:
                            article_date = datetime.strptime(date_str, '%B %d, %Y')

                            # Stop scraping if article is older than the first day of the month
                            if article_date < first_day_of_month:
                                return news_list

                        except ValueError:
                            continue

                        # Get article content
                        content = scrape_content(link)

                        news = {
                            'title': title,
                            'date': date_str,
                            'link': link,
                            'content': content
                        }
                        news_list.append(news)
                        print(f"Successfully scraped article: {title}")

                    except Exception as e:
                        logging.error(f"Error processing article: {str(e)}")
                        continue

            except TimeoutException:
                logging.warning("Timeout waiting for articles to load.")
                break

    except Exception as e:
        logging.error(f"Error in main scraping process: {str(e)}")
        return []

    finally:
        if driver:
            driver.quit()

    return news_list
