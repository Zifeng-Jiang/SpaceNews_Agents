# v0.2.2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from lxml import html
import requests

def find_url():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--ignore-certificate-errors")  # Disable SSL verification
    options.add_argument("--ignore-ssl-errors")
    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.set_window_size(1400, 1000)

    url = 'https://mideastspace.substack.com/'
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="home-body"]/div[1]/div'))
    )

    links = driver.find_elements(By.XPATH, '//a[contains(text(), "Middle East Space Roundup")]')

    result_list = []
    for link in links:
        href = link.get_attribute('href')
        result_list.append(href)
        break  # Stop after the first match

    driver.quit()

    if result_list:
        print('Found Middle East Space Roundup link:', result_list[0])
        return result_list[0]
    else:
        print('No Middle East Space Roundup link found.')
        return None

def get_roundup(url):
    if not url:
        return []

    response = requests.get(url)
    response.encoding = 'utf-8'
    tree = html.fromstring(response.content)

    # Title XPath provided
    title_xpath = '//*[@id="main"]/div[2]/div/div[1]/div/article/div[2]/h1'
    paragraph_xpath = '//p'

    # Extract the title
    title_elements = tree.xpath(title_xpath)
    title = title_elements[0].text_content().strip() if title_elements else 'No Title'

    # Extract all paragraph content
    paragraphs = tree.xpath(paragraph_xpath)
    content = " ".join([p.text_content().strip() for p in paragraphs])

    # Create a dictionary for the extracted data
    entry = {
        'title': title,
        'link': url,
        'content': content
    }

    return [entry]