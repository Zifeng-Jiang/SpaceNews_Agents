from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
from datetime import datetime
import logging

def setup_driver():
    """
    初始化 Selenium WebDriver
    """
    try:
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")  # Disable SSL verification
        options.add_argument("--ignore-ssl-errors")
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # Use webdriver-manager to automatically manage ChromeDriver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_size(1400, 1000)
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        raise

def get_news_content(driver, url):
    """
    爬取新闻详情页的内容和标签
    """
    try:
        driver.get(url)
        # Wait for the entry-content div to be present before proceeding
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.entry-content'))
        )
        
        page_source = driver.page_source
        tree = html.fromstring(page_source)
        
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
        page_num = 1  # 页面计数器
        
        # 构造当前页面URL
        current_url = base_url
        driver.get(current_url)
        
        while True:
            # 等待文章元素加载
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.post')))
            
            # 获取当前页面上所有文章
            articles = driver.find_elements(By.CSS_SELECTOR, 'article.post')
            
            # 用于检查本次循环是否有新文章被处理
            new_articles_found = False
            
            # Extract all article data upfront to avoid stale element issues
            article_data_list = []
            for article in articles:
                try:
                    # 获取文章链接
                    link_element = article.find_element(By.CSS_SELECTOR, 'h2.entry-title a')
                    link = link_element.get_attribute('href')
                    
                    # 如果这个链接已经处理过，跳过
                    if link in processed_links:
                        continue
                    
                    # 获取标题
                    title = link_element.text.strip()
                    
                    # 获取日期
                    date_element = article.find_element(By.CSS_SELECTOR, 'time[datetime]')
                    date_str = date_element.get_attribute('datetime')
                    article_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                    
                    # 检查日期是否在当月
                    if article_date < first_day_of_month:
                        break
                    
                    # 获取摘要
                    try:
                        abstract = article.find_element(By.CSS_SELECTOR, 'div.entry-content p, div.excerpt p').text.strip()
                    except:
                        abstract = ""
                    
                    article_data = {
                        'link': link,
                        'title': title,
                        'date_str': date_str,
                        'abstract': abstract
                    }
                    article_data_list.append(article_data)
                    processed_links.add(link)
                    new_articles_found = True
                    print(f"Added SpaceNews article: {link}")
                    
                except Exception as e:
                    logging.error(f"Error extracting article data: {str(e)}")
                    continue
            
            # Now process each article's detailed content
            for article_data in article_data_list:
                try:
                    # 获取详细内容和标签
                    content, tag = get_news_content(driver, article_data['link'])
                    print(f"Successfully scraped spacenews article: {article_data['title']}\n{content[:150]}...")
                    news = {
                        'title': article_data['title'],
                        'abstract': article_data['abstract'],
                        'date': article_data['date_str'],
                        'link': article_data['link'],
                        'content': content,
                        'tag': tag
                    }
                    news_list.append(news)

                except Exception as e:
                    logging.error(f"Error processing article content: {str(e)}")
                    continue
            
            # 如果本次循环没有发现新文章，说明已经到底或者出现问题
            if not new_articles_found:
                print("No new articles found in this batch")
                break
                
            # 使用url翻页
            page_num += 1
            if page_num == 2:
                # 第二页开始使用page/n/格式
                current_url = f"{base_url.rstrip('/')}/page/{page_num}/"
            else:
                # 后续页面
                current_url = f"https://spacenews.com/section/news-archive/page/{page_num}/"
            
            print(f"Moving to page {page_num}: {current_url}")
            
            try:
                driver.get(current_url)
                # 等待页面加载
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.post')))
            except Exception as e:
                logging.error(f"Error loading page {page_num}: {str(e)}")
                break
            

    except Exception as e:
        logging.error(f"Error in main crawling process: {str(e)}")
        return []
        
    finally:
        if driver:
            driver.quit()

    return filter_news(news_list)
