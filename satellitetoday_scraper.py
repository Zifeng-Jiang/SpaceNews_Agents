import requests
from lxml import html
from datetime import datetime, timedelta

def get_satellitetoday_news():
    # 获取当前日期
    today = datetime.now()
    # 获取当前月份的第一天
    first_day_of_month = today.replace(day=1)
    
    # 构建初始 URL，注意这里包含了页码的占位符
    date_range = f"{first_day_of_month.strftime('%Y-%m-%d')}--{today.strftime('%Y-%m-%d')}"
    base_url = "https://www.satellitetoday.com/page/{page}/?s&order=desc&orderby=post_date&date_range={date_range}"
    
    news_list = []

    # 定义函数爬取新闻内容
    def scrape_content(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        paragraphs = tree.xpath('//div[@class="entry-content"]/p')  # XPath needs to match the structure of the content
        content = '\n'.join([p.text_content().strip() for p in paragraphs if p.text_content().strip()])
        content = ' '.join(content.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ').replace('\r', ' ').split())
        
        return content
    
    # 定义函数爬取单个页面的新闻
    def scrape_page(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        
        # 使用相对路径进行XPath选择
        articles = tree.xpath('//*[@id="site-content"]/div/div[1]/article')

        if not articles:
            return False
        
        for article in articles:
            title = article.xpath('.//div/div[1]/a[1]/text()')
            title = title[0].strip() if title else 'No Title'
            
            abstract = article.xpath('.//div/div[1]/div[2]/text()')
            abstract = abstract[0].strip() if abstract else 'No Abstract'
            
            tag = article.xpath('.//div/div[1]/a[2]/text()')
            tag = tag[0].strip() if tag else 'No Tag'
            
            link = article.xpath('.//div/div[1]/a[1]/@href')
            link = link[0] if link else 'No Link'
            
            date_str = article.xpath('.//div/div[1]/div[1]/text()')
            date_str = date_str[0].strip() if date_str else None

            # 确保每条新闻都有title, abstract, date
            if title == 'No Title' or date_str is None:
                continue

            # 将字符串日期转换为日期对象
            try:
                date = datetime.strptime(date_str, '%B %d, %Y')
            except ValueError:
                continue
            
            # 判断新闻是否在本月内
            if not (first_day_of_month <= date <= today):
                continue

            news_content = scrape_content(link) if link != 'No Link' else 'No Content'
            
            # 将新闻信息存储在字典中
            news = {
                'title': title,
                'abstract': abstract,
                'tag': tag,
                'date': date_str,
                'link': link,
                'content': news_content
            }
            news_list.append(news)
        
        return True
    
    # 开始爬取第一页
    page_num = 1
    
    while True:
        current_url = base_url.format(page=page_num, date_range=date_range)
        print(f'Scraping page: {current_url}...')
        continue_scraping = scrape_page(current_url)
        if not continue_scraping:
            break
        
        page_num += 1

    # 过滤新闻，排除不相关的内容
    filtered_list = []
    for news in news_list:
        if 'AI' in news['title'] or 'AI' in news['abstract']:
            news['tag'] = 'AI'
        if news['tag'].lower() not in ['government/military', 'government', 'uncategorized']:
            filtered_list.append(news)
            
    return filtered_list
