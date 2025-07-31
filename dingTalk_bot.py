import requests
import json
import os

class dingTalkBot:
    def __init__(self, access_token=None):
        self.access_token = access_token or os.environ.get('DINGTALK_BOT_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError("DINGTALK_BOT_ACCESS_TOKEN environment variable is not set.")
        self.url = f'https://oapi.dingtalk.com/robot/send?access_token={self.access_token}'
        self.articles = "[SpaceNews]  \n  "
        self.events = "[SpaceNews]  \n  "
 
    def append_article(self, article: dict):
        region = article.get('region', 'N/A')
        title = article.get('title', 'N/A')
        link = article.get('link', 'N/A')
        date = article.get('date', 'N/A')
        tag = article.get('tag', 'N/A')
        abstract = article.get('abstract', 'N/A')
        markdown = f"""  \n  **{region}**  \n  # [{title}]({link})  \n  **Date：** {date}  \n  **Tag：** {tag}  \n  **Abstract**  \n  > {abstract}  \n  """
        self.articles += markdown

    
    def send_articles(self):
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "Recent News",
                "text": self.articles
            }
        }

        response = requests.post(self.url, headers=headers, data=json.dumps(payload))
        return response.status_code, response.text

    def append_event(self, event: dict):
        title = event.get('title', 'N/A')
        link = event.get('link', 'N/A')
        date = event.get('date', 'N/A')
        address = event.get('address', 'N/A')
        abstract = event.get('abstract', 'N/A')
        markdown = f"""# [{title}]({link})  \n  **Date：** {date}  \n  **Address：** {address}  \n  **Abstract**  \n  > {abstract}  \n  """
        self.events += markdown

    def send_events(self):
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "Upcoming Events",
                "text": self.events
            }
        }

        response = requests.post(self.url, headers=headers, data=json.dumps(payload))
        return response.status_code, response.text