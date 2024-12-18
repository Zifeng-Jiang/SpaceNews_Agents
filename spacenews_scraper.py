import requests
from lxml import html
from datetime import datetime

def get_spacenews():
    # 获取当前日期并设置为本月的第一天
    today = datetime.now()
    first_day_of_month = today.replace(day=1)

    # 初始化一个空列表用于存储新闻数据
    news_list = []

    # 定义函数爬取单个页面的新闻
    def scrape_page(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        articles = tree.xpath('//article')  # 提取所有新闻文章
        # print(f'Found {len(articles)} articles on page {url}')

        for article in articles:
            title = article.xpath('.//header/h2/a/text()')
            title = title[0].strip() if title else ''
            # print(f'Title: {title}')
            
            abstract = article.xpath('.//div[1]/p/text()')
            abstract = abstract[0].strip() if abstract else ''
            # print(f'Abstract: {abstract}')
            
            tag = article.xpath('.//span/a/text()')
            tag = tag[0].strip() if tag else ''
            # print(f'Tag: {tag}')
            
            date_str = article.xpath('.//div[2]/span[3]/a/time[1]/@datetime')
            date_str = date_str[0] if date_str else None
            # print(f'Date: {date_str}')

            # 确保每条新闻都有title, abstract, date
            if title == '' or date_str is None:
                # print('Missing necessary information. Skipping...')
                continue

            date = datetime.strptime(date_str[:10], '%Y-%m-%d') if date_str else None

            # 判断新闻是否在本月内
            if date and date < first_day_of_month:
                # 如果新闻的日期早于本月第一天，则跳过
                return False

            link = article.xpath('.//header/h2/a/@href')
            link = link[0] if link else 'No Link'
            # print(f'Link: {link}')
            
            # 爬取新闻内容和图片
            news_content = scrape_content_and_images(link) if link != 'No Link' else 'No Content'
            # print(f'Content: {news_content[:100]}...')  # 仅显示前100个字符以节省空间
            
            # 将新闻信息存储在字典中
            news = {
                'title': title,
                'tag': tag,
                'date': date_str,
                'link': link,
                'abstract': abstract,
                'content': news_content
            }
            news_list.append(news)

        return True

    # 定义函数爬取新闻内容和图片
    def scrape_content_and_images(url):
        response = requests.get(url)
        tree = html.fromstring(response.content)
        paragraphs = tree.xpath('//div[@class="entry-content"]/p')
        content = '\n'.join([p.text_content().strip() for p in paragraphs if p.text_content().strip()])
        content = ' '.join(content.replace('\n', ' ').replace('\t', ' ').replace('\xa0', ' ').replace('\r', ' ').split())
        
        return content

    # 开始爬取第一页
    base_url = 'https://spacenews.com/?s&orderby=post_date&order=desc'
    page_num = 1

    while True:
        page_url = f'{base_url}&paged={page_num}'
        print(f'Scraping page {page_num}...')
        if not scrape_page(page_url):
            break
        page_num += 1

    # 过滤标签和标题，排除一些不需要的内容
    filtered_list = []
    for news in news_list:
        if news['tag'].lower() not in ['video', 'policy & politics', 'military', 'opinion', 'launch', 'commercial'] and \
        not any(word in news['title'].lower() for word in ['geopolitical', 'politics']):
            filtered_list.append(news)

    return filtered_list
