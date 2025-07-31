import json
from openai import AzureOpenAI
from google_news_content_fetch import *

import os

class ScripterAgent:
    def script(self, article: dict):
        content = article.get('content', '')
        word_count = len(content.split())
        # 如果content的词数小于100，则直接返回content作为abstract
        if word_count < 100:
            return content
        
        prompt = [{
            "role": "system",
            "content": "You are an expert news editor."
        }, {
            "role": "user",
            "content": f"Here are the details of the best news article:\n\n"
                       f"Title: {article.get('title', 'No title available')}\n"
                       f"Content: {article.get('content', 'No content available')[:8000]}\n\n"
                       f"Your task is to write a precise abstract less than 100 words according to the given content. "
                       f"Please return the abstract in plain text, do not return other content"
        }]

        api_key = os.environ.get('AZURE_OPENAI_API_KEY')
        azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
        api_version = os.environ.get('AZURE_OPENAI_API_VERSION')
        # 检查是否正确读取了环境变量
        if not api_key or not azure_endpoint:
            raise ValueError("Azure OpenAI API Key or Endpoint is not set in the environment variables.")

        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key, 
            api_version=api_version
        )

        response = client.chat.completions.create(
            model="gpt-4o",  # 指定模型名称
            messages=prompt,
            temperature=0.7,
        )

        response_content = response.choices[0].message.content

        # 解析大模型的输出
        summarized_content = response_content.strip().replace('\n', ' ') if response_content else "Failed to summarize the content."

        return summarized_content

    def translate(self, article: dict):
        # Check if article is likely already in English
        title = article.get('title', '')
        abstract = article.get('abstract', '')
        url = article.get('link', '')
        
        if not 'news.google.com' in url:
            return article  # If the URL is not a Google News RSS link, return the article as is

        real_url = get_real_url_from_google_news_rss(url)
        if not real_url:
            print("Failed to extract the real URL from Google News RSS.")
            return article
        print("Google News Extracted URL:\n", real_url)
        #Replace the url with the real URL
        article['link'] = real_url
        
        content = extract_with_trafilatura(real_url)
        if content is None:
            content = title  # Default to the title if content is None
        article['content'] = content
        
        def contains_chinese(text):
            for ch in text:
                if '\u4e00' <= ch <= '\u9fff':  # Common CJK Unified Ideographs range
                    return True
            return False
        
        if not contains_chinese(title) and not contains_chinese(abstract):
            print("The article is likely already in English. No translation needed.")
            return article
        
        # 否则使用大模型翻译，并删除原本的dict
        json_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The translated title of the news article"
                },
                "abstract": {
                    "type": "string", 
                    "description": "The translated abstract of the news article"
                },
                "content": {
                    "type": "string",
                    "description": "The translated content of the news article"
                }
            },
            "required": ["title", "abstract", "content"],
            "additionalProperties": False
        }
        
        prompt = [{
            "role": "system",
            "content": "You are an expert Chinese-to-English news translator. "
            f"First, given the title and link, please fetch the actual content of the news from the link."
            f"Second, translate the provided Chinese news article into English while maintaining accuracy and readability."
        }, {
            "role": "user",
            "content":  f"Please fetch and translate the following Chinese news into English:\n\n"
                f"Title: {title}\n"
                f"Abstract: {abstract}\n"
                f"Link: {url}\n"
                f"Content: {content[:8000]}\n\n"
                f"If any field is empty or not available, return an empty string for that field."
                f"If my content is same as the title, you can ignore my content and fetch the content from the link directly."
        }]

        api_key = os.environ.get('AZURE_OPENAI_API_KEY')
        azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
        api_version = os.environ.get('AZURE_OPENAI_API_VERSION')
        # 检查是否正确读取了环境变量
        if not api_key or not azure_endpoint:
            raise ValueError("Azure OpenAI API Key or Endpoint is not set in the environment variables.")

        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key, 
            api_version=api_version
        )

        response = client.chat.completions.create(
            model="gpt-4o",  # 指定模型名称
            messages=prompt,
            temperature=0.7,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "translation_response",
                    "schema": json_schema,
                    "strict": True
                }
            }
        )

        response_content = response.choices[0].message.content

        # Debugging: Print the response_content to inspect its value
        print(f"Response Content: {response_content}")

        # 解析大模型的输出 - With structured output, this should always be valid JSON
        try:
            translated_article = json.loads(response_content)
        except json.JSONDecodeError as e:
            translated_article = {
                "title": "Translation failed",
                "abstract": "Translation failed", 
                "content": "Translation failed"
            }
        # Print the original and translated titles, abstracts, and contents for comparison
        print(f"Original Title: {title}")
        print(f"Translated Title: {translated_article.get('title', 'No title available')}")
        print(f"Translated Content: {translated_article.get('content', 'No content available')[:100]}...")
        # Delete original Chinese content and replace with translated content
        # Keep other fields like 'link', 'date', etc.
        new_article = {key: value for key, value in article.items() 
                      if key not in ['title', 'abstract', 'content']}
        new_article.update(translated_article)
        
        return new_article
    
    def run(self, state: dict):
        selected_news = state['selected_news']
        if 'news' not in selected_news:
            # Translate and replace the selected news completely
            selected_news = self.translate(selected_news)
            summarized_abstract = self.script(selected_news)
            selected_news['abstract'] = summarized_abstract
            state['selected_news'] = selected_news
        return state

