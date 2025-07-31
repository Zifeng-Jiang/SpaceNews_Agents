# v0.2.3
import requests
from lxml import html
from langchain_openai import AzureChatOpenAI
from content_generator import generate_event_content
import time  # Import time module for sleep

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",  # or your deployment
    temperature=0.7,
    max_tokens=8192,
    timeout=None,
    max_retries=10,
)

def script(article: dict):
        content = article['content']
        word_count = len(content.split())
        # 如果content的词数小于100，则直接返回content作为summary
        if word_count < 100:
            return content
        
        prompt = [{
            "role": "system",
            "content": "You are an expert news event editor."
        }, {
            "role": "user",
            "content": f"Here are the details of the event:\n\n"
                       f"Title: {article['title']}\n"
                       f"address: {article['address']}\n"
                       f"Date: {article['date']}\n"
                       f"Content: {article['content']}\n\n"
                       f"Your task is to summarize the event into less than 100 words, highlighting the main points and ensuring it's well-written and coherent. "
                       f"Please return the summarized event in plain text, do not return other content"
        }]

        response = llm.invoke(prompt).content

        # 解析大模型的输出
        summarized_content = response.strip().replace('\n', ' ') if response else "Failed to summarize the content."

        return summarized_content

def get_events():
    # Initialize an empty list to store event data
    event_list = []
    seen_titles = set()

    # Define function to scrape the events from the page
    # Scrape the first page
    url = 'https://spacenews.com/events/'
    response = requests.get(url)
    tree = html.fromstring(response.content)
    events = tree.xpath('//article')
    print(f'Found {len(events)} events on page {url}')

    for event in events:
        title = event.xpath('.//header/h3/a/text()')
        title = title[0].strip() if title else ''
        
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        
        print(f'Title: {title}')

        date = event.xpath('.//header/div/time/span[1]/text() | .//header/div/time/span[2]/text()')
        date = date[0].strip() if date else ''
        print(f'Date: {date}')

        address = event.xpath('.//header/address/span[2]/text()')
        address = address[0].strip() if address else ''
        print(f'Address: {address}')

        link = event.xpath('.//header/h3/a/@href')
        link = link[0] if link else 'No Link'
        print(f'Link: {link}')

        # Define function to scrape event content from its detail page
        def scrape_event_content(url):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            for i in range(5):  # Retry up to 5 times
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    print(f"DEBUG: Received 429 Too Many Requests. Retrying in {2 ** i} seconds...")
                    time.sleep(2 ** i)  # Exponential backoff
                else:
                    print(f"DEBUG: Received unexpected status code {response.status_code}. Aborting.")
                    return ''

            tree = html.fromstring(response.content)
            content_elements = tree.xpath('//*[starts-with(@id, "post-")]/p/text() | //*[starts-with(@id, "post-")]/ul/text()')
            content = '\n'.join([el.strip() for el in content_elements if el.strip()])
            content = ' '.join(content.replace('\n\n', '\n').replace('\t', ' ').replace('\xa0', ' ').replace('\r', ' ').split())

            # If scraped content is empty, generate content using LLM
            if not content:
                print(f"DEBUG: Scraped content is empty for URL: {url}. Generating content with LLM.")
                # Pass event parameters to the content generator
                event_params = {
                    'title': title,
                    'date': date,
                    'address': address,
                    'link': url
                }
                #content = generate_event_content(event_params)
                print(f"DEBUG: Generated content using LLM. Content length: {len(content)}")
            else:
                print(f"DEBUG: Scraped content length for URL {url}: {len(content)}")

            return content

        # Scrape event content if the link is available
        event_content = scrape_event_content(link) if link != 'No Link' else 'No Content'
        print(f'Content: {event_content[:100]}...')  # Only show the first 100 characters for brevity

        # Store event information in a dictionary
        event_data = {
            'title': title,
            'date': date,
            'address': address,
            'link': link,
            'content': event_content
        }
        event_list.append(event_data)

    keywords = ['military', 'politics', 'defence', 'security']
    filtered_list = [event for event in event_list if not any(keyword in event['title'].lower() for keyword in keywords)]

    for event in filtered_list:
        summarized_content = script(event)
        event['summary'] = summarized_content

    return filtered_list