# v0.2.3
import feedparser
from datetime import datetime, timedelta
from langchain_community.llms import Tongyi

llm = Tongyi(max_retries = 30)

def get_google_news():
    # Google News RSS feed URL (近似的查询)
    rss_url_en = 'https://news.google.com/rss/search?q=satellite+space+news+when:30d+-Isreal+-Russia+-Ukraine+-military+-war+-combat+-geopolitical+-political&hl=en-US&gl=US&ceid=US:en'
    rss_url_zh = "https://news.google.com/rss/search?q=%E8%88%AA%E5%A4%A9%20%E5%8D%AB%E6%98%9F%20when%3A30d%20-%E4%BF%84%E7%BD%97%E6%96%AF%20-%E4%B9%8C%E5%85%8B%E5%85%B0%20-%E4%BB%A5%E8%89%B2%E5%88%97%20-%E6%88%98%E4%BA%89%20-%E5%9C%B0%E7%BC%98%E6%94%BF%E6%B2%BB%20-%E6%94%BF%E6%B2%BB%20-%E5%86%9B%E4%BA%8B&hl=zh-CN&gl=CN&ceid=CN%3Azh-Hans"
    # 解析 RSS feed
    feed_en = feedparser.parse(rss_url_en)
    feed_zh = feedparser.parse(rss_url_zh)
    
    news_list_en = []
    news_list_zh = []
    
    for entry in feed_en.entries:
        # 解析发布时间并加8小时(北京时间)
        published_gmt = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
        published_gmt_plus_8 = published_gmt + timedelta(hours=8)
        
        news = {
            'title': entry.title,
            'abstract': entry.title,
            'link': entry.link,
            'date': published_gmt_plus_8.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'content': entry.title
        }
        news_list_en.append(news)

    for entry in feed_zh.entries:
        # 解析发布时间并加8小时(北京时间)
        published_gmt = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
        published_gmt_plus_8 = published_gmt + timedelta(hours=8)

        # llm = QianfanLLMEndpoint(model="ERNIE-Speed-128K")
        res = llm.invoke(f"你是新闻编辑，你非常擅长将中文新闻翻译为英文。\
                    请将下面这段中文新闻标题翻译为英文，仅返回翻译的英文结果，不要返回其他的内容。 \
                    新闻标题如下：{entry.title}.")

        #print(res)
        en_title = res

        news = {
            'title': en_title,
            'abstract': en_title,
            'link': entry.link,
            'date': published_gmt_plus_8.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'content': en_title
        }
        news_list_zh.append(news)

    combined_list = news_list_en + news_list_zh
    return combined_list
