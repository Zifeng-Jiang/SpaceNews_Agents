# v0.2.3
from openai import AzureOpenAI
import os

class ScripterAgent:
    def script(self, article: dict):
        content = article.get('content', '')
        word_count = len(content.split())
        # 如果content的词数小于150，则直接返回content作为summary
        if word_count < 150:
            return content
        
        prompt = [{
            "role": "system",
            "content": "You are an expert news editor."
        }, {
            "role": "user",
            "content": f"Here are the details of the best news article:\n\n"
                       f"Title: {article['title']}\n"
                       f"Abstract: {article['abstract']}\n"
                       f"Content: {article['content'][:8000]}\n\n"
                       f"Your task is to summarize the article into less than 150 words, highlighting the main points and ensuring it's well-written and coherent. "
                       f"Please return the summarized article in plain text, do not return other content"
        }]

        api_key = "322066cba4f44a708a07e1be88205eaa"
        azure_endpoint = "https://openai-starvision.openai.azure.com/"
        api_version = "2024-05-01-preview"
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

    def run(self, state: dict):
        selected_news = state['selected_news']
        if 'news' not in selected_news:
            summarized_content = self.script(selected_news)
            selected_news['summary'] = summarized_content
            state['selected_news'] = selected_news  # 更新 state
        return state

