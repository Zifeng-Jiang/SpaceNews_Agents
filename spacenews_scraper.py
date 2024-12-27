from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from lxml import html
import requests
from datetime import datetime
import logging

def setup_driver():
    """
    初始化 Selenium WebDriver
    """
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")  # Disable SSL verification
        options.add_argument("--ignore-ssl-errors")
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(service=ChromeService(), options=options)
        driver.set_window_size(1400, 1000)
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        raise

def get_news_content(url):
    """
    爬取新闻详情页的内容和标签
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        tree = html.fromstring(response.content)
        
        # 获取文章内容
        content_paragraphs = tree.cssselect('div.entry-content p')
        content = ' '.join([p.text_content().strip() for p in content_paragraphs if p.text_content().strip()])
        
        # 获取标签
        tags = tree.cssselect('header span.cat-links a')
        tag = tags[0].text_content().strip() if tags else "No Tag"
        
        return content, tag
        
    except Exception as e:
        logging.error(f"Error fetching content from {url}: {e}")
        return "", ""
    
def filter_news(news_list):
    """
    过滤新闻列表，去除不需要的内容
    """
    filtered_list = []
    for news in news_list:
        if news['tag'].lower() not in ['video', 'policy & politics', 'military', 'opinion', 'launch', 'commercial'] and \
        not any(word in news['title'].lower() for word in ['geopolitical', 'politics', 'war', 'warfare']):
            filtered_list.append(news)
    return filtered_list

def get_spacenews(base_url="https://spacenews.com/section/news-archive/"):
    """
    爬取 SpaceNews 的当月新闻信息
    """
    driver = None
    try:
        driver = setup_driver()
        wait = WebDriverWait(driver, 5)
        
        current_date = datetime.now()
        first_day_of_month = current_date.replace(day=1)
        
        news_list = []
        processed_links = set()  # 用于记录已处理的文章链接
        
        driver.get(base_url)
        
        while True:
            # 等待文章元素加载
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.post')))
            
            # 获取当前页面上所有文章
            articles = driver.find_elements(By.CSS_SELECTOR, 'article.post')
            
            # 用于检查本次循环是否有新文章被处理
            new_articles_found = False
            
            for article in articles:
                try:
                    # 首先获取文章链接，用于去重
                    link_element = article.find_element(By.CSS_SELECTOR, 'h2.entry-title a')
                    link = link_element.get_attribute('href')
                    
                    # 如果这个链接已经处理过，跳过
                    if link in processed_links:
                        continue
                        
                    processed_links.add(link)
                    new_articles_found = True
                    
                    # 获取标题
                    title = link_element.text.strip()
                    
                    # 获取日期
                    date_element = article.find_element(By.CSS_SELECTOR, 'time[datetime]')
                    date_str = date_element.get_attribute('datetime')
                    article_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                    
                    # 检查日期是否在当月
                    if article_date < first_day_of_month:
                        return filter_news(news_list)
                    
                    # 获取摘要
                    try:
                        abstract = article.find_element(By.CSS_SELECTOR, 'div.entry-content p, div.excerpt p').text.strip()
                    except:
                        abstract = ""
                    
                    # 获取详细内容和标签
                    content, tag = get_news_content(link)
                    
                    news = {
                        'title': title,
                        'abstract': abstract,
                        'date': date_str,
                        'link': link,
                        'content': content,
                        'tag': tag
                    }
                    news_list.append(news)
                    print(f"Successfully scraped spacenews article: {title}")
                    

                except Exception as e:
                    logging.error(f"Error processing article: {str(e)}")
                    continue
            
            # 如果本次循环没有发现新文章，说明已经到底或者出现问题
            if not new_articles_found:
                print("No new articles found in this batch")
                break
                
            # 尝试加载更多
            try:
                # 滚动到页面底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                load_more = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#infinite-handle span button, .load-more a')
                ))  # 等待加载更多按钮可点击
                
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more)
                driver.execute_script("arguments[0].click();", load_more)

                # 等待新文章加载完成，通过比较加载的文章数量来确保内容加载完成
                current_articles = len(driver.find_elements(By.CSS_SELECTOR, 'article.post'))
                
                # 等待新文章数量增加，最多等 3 秒
                wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'article.post')) > current_articles)
                
            except Exception as e:
                print("No more content to load or loading failed")
                break

    except Exception as e:
        logging.error(f"Error in main crawling process: {str(e)}")
        return []
        
    finally:
        if driver:
            driver.quit()

    return filter_news(news_list)
