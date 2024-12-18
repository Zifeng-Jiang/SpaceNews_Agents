import requests
from lxml import html
from datetime import datetime, timedelta

def get_spaceinafrica():
    # 获取当前日期并设置为本月的第一天
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    
    # 初始化一个空列表用于存储新闻数据
    news_list = []

    # 定义函数爬取单个页面的新闻
    def scrape_page(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        articles = tree.xpath('//*[@id="index-2"]/div/div/div/div/div/div/div')  # 修改Xpath
        # print(f'Found {len(articles)} articles on page {url}')

        for article in articles:
            title = article.xpath('.//h3[@class="t-entry-title h5 title-scale"]/a/text()')
            title = title[0].strip() if title else ''
            # print(f'Title: {title}')
            
            date_str = article.xpath('.//p[@class="t-entry-meta"]/span/text()')
            date_str = date_str[0].strip() if date_str else None
            # print(f'Date: {date_str}')

            # 确保每条新闻都有title, date
            if title == '' or date_str is None:
                # print('Missing necessary information. Skipping...')
                continue

            try:
                # 将字符串日期转换为日期对象
                date = datetime.strptime(date_str, '%B %d, %Y') if date_str else None
            except ValueError:
                continue

            # 判断新闻是否在本月内
            if date and date < first_day_of_month:
                # 如果新闻的日期小于本月第一天，则跳过
                return False

            link = article.xpath('.//h3[@class="t-entry-title h5 title-scale"]/a/@href')
            link = link[0] if link else 'No Link'
            # print(f'Link: {link}')
            
            # 爬取新闻内容
            news_content = scrape_content(link) if link != 'No Link' else 'No Content'
            # print(f'Content: {news_content[:100]}...')  # 仅显示前100个字符以节省空间
            
            # 将新闻信息存储在字典中
            news = {
                'title': title,
                'date': date_str,
                'link': link,
                'content': news_content
            }
            news_list.append(news)

        return True

    # 定义函数爬取新闻内容
    def scrape_content(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        paragraphs = tree.xpath('//article[contains(@id, "post-")]/div/div/div/div/div/div[1]/div/p')
        content = '\n'.join([p.text_content().strip() for p in paragraphs if p.text_content().strip()])
        return ' '.join(content.replace('\n\n', '\n').replace('\t', ' ').replace('\xa0', ' ').replace('\r', ' ').split())

    # 开始爬取第一页
    base_url = 'https://spaceinafrica.com/news/'
    page_num = 1

    while True:
        page_url = f'{base_url}page/{page_num}/'
        print(f'Scraping page {page_num}...')
        if not scrape_page(page_url):
            break
        page_num += 1

    return news_list
