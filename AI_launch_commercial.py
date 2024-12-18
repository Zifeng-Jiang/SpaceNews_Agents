import requests
from lxml import html
from datetime import datetime, timedelta

def add_news(topic):
    url = ''
    if topic == 'AI':
        url = "https://spacenews.com/section/AI/"
    elif topic == 'launch':
        url = "https://spacenews.com/section/launch-archive/"
    elif topic == 'commercial': 
        url = "https://spacenews.com/section/commercial-archive/"

    # 获取当前月份的第一天
    today = datetime.now()
    first_day_of_month = today.replace(day=1)

    # 初始化一个空列表用于存储新闻数据
    news_list = []

    # 定义函数爬取单个页面的新闻
    def scrape_page(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        articles = tree.xpath('//article') 

        for article in articles:
            title = article.xpath('.//header/h2/a/text()')
            title = title[0].strip() if title else ''
            
            abstract = article.xpath('.//div[1]/p/text()')
            abstract = abstract[0].strip() if abstract else ''
            
            date_str = article.xpath('.//div/span[3]/a/time[1]/@datetime')
            date_str = date_str[0] if date_str else None

            # 确保每条新闻都有title, abstract, date
            if title == '' or date_str is None:
                continue

            date = datetime.strptime(date_str[:10], '%Y-%m-%d') if date_str else None

            # 判断新闻是否在当月内（不包括未来日期）
            if not (first_day_of_month <= date <= today):
                return False

            link = article.xpath('./div/header/h2/a/@href')
            link = link[0] if link else 'No Link'

            news_content = scrape_content(link) if link != 'No Link' else 'No Content'
            
            news = {
                'title': title,
                'date': date_str,
                'link': link,
                'abstract': abstract,               
                'content': news_content
            }
            news_list.append(news)

        return True

    # 定义函数爬取新闻内容
    def scrape_content(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        paragraphs = tree.xpath('//div[@class="entry-content"]/p')
        content = '\n'.join([p.text_content().strip() for p in paragraphs if p.text_content().strip()])
        content = ' '.join(content.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ').replace('\r', ' ').split())
        return content

    # 开始爬取第一页
    base_url = url
    page_num = 1

    while True:
        page_url = f'{base_url}?paged={page_num}'
        print(f'Scraping page {page_num}...')
        if not scrape_page(page_url):
            break
        page_num += 1

    # 过滤新闻
    filtered_list = []
    for news in news_list:
        if 'military' not in news['title'] and 'military' not in news['abstract'] and \
           'politics' not in news['title'] and 'politics' not in news['abstract']:
            news['tag'] = topic
            filtered_list.append(news)
    return filtered_list