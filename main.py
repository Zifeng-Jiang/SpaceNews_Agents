import streamlit as st
from pitcher_agent import PitcherAgent
from scripter_agent import ScripterAgent
from dingTalk_bot import *
from langgraph.graph import StateGraph
from typing import List, TypedDict
from scraper_tools import run_news_scraper
from docx import Document
from io import BytesIO
from event_scraper import *
from openai import AzureOpenAI
from db_manager import NewsDatabase
import json
import re
import os

class NewsState(TypedDict):
    region: str
    news_list: List[dict]
    selected_news: dict

# 构建完整的LangGraph
main_graph = StateGraph(NewsState)

pitcher_agent = PitcherAgent()
main_graph.add_node("pitcher", pitcher_agent.run)
scripter_agent = ScripterAgent()
main_graph.add_node("scripter", scripter_agent.run)
main_graph.add_edge("pitcher", "scripter")

# 设置图的入口点和出口点
main_graph.set_entry_point("pitcher")
main_graph.set_finish_point("scripter")

# streamlit app page
st.set_page_config(page_icon="📰", page_title="SpaceNews Agents")
st.title('📰SpaceNews Agents🤖')

"""Hello 👋🏻 You can get space/satellite news from all over the world through SpaceNews Agents."""
st.write("China | Middle East | Africa | Central Asia | Southeast Asia | Latin America | AI | Launch | Commercial | Events")

# Check database connection
with st.sidebar:
    st.subheader("Database Status")
    try:
        db = NewsDatabase()
        if db.connect():
            st.success("✅ Connected to MySQL database")
            # Show database stats
            try:
                db.cursor.execute("SELECT COUNT(*) as count FROM articles")
                article_count = db.cursor.fetchone()['count']
                db.cursor.execute("SELECT COUNT(*) as count FROM events")
                event_count = db.cursor.fetchone()['count']
                st.write(f"Articles in database: {article_count}")
                st.write(f"Events in database: {event_count}")
            except Exception as e:
                st.warning(f"Could not retrieve stats: {str(e)}")
            db.close()
        else:
            st.error("❌ Failed to connect to MySQL database")
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")

btn = st.button("Start Collecting and Summarizing")
message_placeholder = st.empty()

# Add placeholders for status display
status_container = st.container()

if btn:
    message_placeholder.empty()  # Clear previous success or error messages
    
    # Create status tracking
    status_placeholder = status_container.empty()
    module_status = {
        'SpaceNews': {'running': False, 'time': 0.0, 'completed': False},
        'Mideast Roundup': {'running': False, 'time': 0.0, 'completed': False},
        'Satellite Today': {'running': False, 'time': 0.0, 'completed': False},
        'AI News': {'running': False, 'time': 0.0, 'completed': False},
        'Launch News': {'running': False, 'time': 0.0, 'completed': False},
        'Commercial News': {'running': False, 'time': 0.0, 'completed': False},
        'Google News': {'running': False, 'time': 0.0, 'completed': False},
        'Space in Africa': {'running': False, 'time': 0.0, 'completed': False}
    }
    
    def update_status_display():
        status_text = "## Module Status\n\n"
        for module, status in module_status.items():
            if status['completed']:
                status_text += f"✅ **{module}**: {status['time']:.2f}s\n\n"
            elif status['running']:
                status_text += f"🔄 **{module}**: {status['time']:.2f}s\n\n"
            else:
                status_text += f"⏳ **{module}**: {status['time']:.2f}s\n\n"
        status_placeholder.markdown(status_text)
    
    # Initial display
    update_status_display()
    
    # Define status callback function
    def status_callback(module, running=False, completed=False, elapsed_time=0.0):
        if running:
            module_status[module]['running'] = True
            module_status[module]['completed'] = False
        elif completed:
            module_status[module]['running'] = False
            module_status[module]['completed'] = True
            module_status[module]['time'] = elapsed_time
        update_status_display()
    
    with st.spinner('Collecting and summarizing news...'):
        best_news = []
        news_list = run_news_scraper(status_callback)
        
        # Initialize database connection
        db = NewsDatabase()
        if not db.connect():
            message_placeholder.error("Failed to connect to the database. Please check your configuration.")
            st.stop()
        
        regions = ["china", "middle_east", "africa", "central_asia", "southeast_asia", "latin_america", "AI", "launch", "commercial"]
        for region in regions:
            if region not in ["AI", "launch", "commercial"]:
                # 初始化状态
                initial_state = {
                    "region": region,
                    "news_list": news_list,
                    "selected_news": {}
                }
            elif region == 'AI':
                initial_state = {
                    "region": region,
                    "news_list": [news for news in news_list if news.get("tag") == "AI"],
                    "selected_news": {}
                }
            elif region == 'launch':
                initial_state = {
                    "region": region,
                    "news_list": [news for news in news_list if news.get("tag") == "launch"],
                    "selected_news": {}
                }
            else:
                initial_state = {
                    "region": region,
                    "news_list": [news for news in news_list if news.get("tag") == "commercial"],
                    "selected_news": {}
                }
            # 运行LangGraph
            app = main_graph.compile()
            final_state = app.invoke(initial_state)
            selected_news = final_state["selected_news"]
            if 'title' in selected_news:
                existing_titles = {news["title"] for news in best_news}

                if selected_news["title"] not in existing_titles:
                    selected_news["region"] = region 
                    
                    if 'tag' not in selected_news or selected_news['tag'] == '':           
                        tag_list = ['AI', 'Civil', 'Commercial', 'Finance', 'Launch', 'Opinion', 'Manufacturing', 'Imagery and Sensing']
                        example = {'tag': 'AI'}

                        api_key = os.environ.get('AZURE_OPENAI_API_KEY')
                        azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
                        api_version = "2025-04-01-preview"

                        # 检查是否正确读取了环境变量
                        if not api_key or not azure_endpoint:
                            raise ValueError("Azure OpenAI API Key or Endpoint is not set in the environment variables.")

                        client = AzureOpenAI(
                            azure_endpoint=azure_endpoint,
                            api_key=api_key, 
                            api_version=api_version
                        )
                        # 调用 Azure OpenAI 的 ChatCompletion 模型
                        messages = [
                            {"role": "system", "content": f"You are a news editor expert in select the most relevant tag for news articles.\
                            Choose only one tag from the following list: {tag_list}. \
                            Return the selected tag as a JSON object with the key 'tag'. For example, {example}. Do not reply other information" },
                            {"role": "user", "content": f"The news title is: '{selected_news['title']}'. News content is: '{selected_news['content'][:8000]}'."}
                        ]

                        response = client.chat.completions.create(
                            model="gpt-4o",  # 指定模型名称
                            messages=messages,
                            temperature=0.7,
                            #stream=True
                        )
                        tag_response = response.choices[0].message.content
                        print("tag response:", tag_response)

                        # 解析大模型的输出
                        pattern = r'\{[^{}]*\}'
                        match = re.search(pattern, tag_response)
                        if match:
                            tag_response_str = match.group(0)
                            
                            # 替换单引号为双引号
                            tag_response_str = tag_response_str.replace("'", '"')
                            
                            try:
                                tag_response_dict = json.loads(tag_response_str)
                            except json.JSONDecodeError as e:
                                print(f"JSONDecodeError: {e}")
                                tag_response_dict = {"tag": 'Unknown'}
                        else:
                            tag_response_dict = {"tag": 'Unknown'}
                            print("Warning: Could not parse tag for news title.")
                        selected_news['tag'] = tag_response_dict['tag']
                    
                    # Add to best_news for Word document (all articles)
                    best_news.append(selected_news)

        events = get_events()
        bot = dingTalkBot(os.environ.get('DINGTALK_BOT_ACCESS_TOKEN'))
        
        # Filter articles for DingTalk - only send new ones not in database
        for article in best_news:
            if not db.article_exists(article.get("link", "")):
                db.save_article(article)
                bot.append_article(article)
        
        # Send only new articles to DingTalk
        bot.send_articles()
        
        # Save events to database and filter out duplicates for DingTalk
        for event in events:
            if not db.event_exists(event.get('link', '')):
                db.save_event(event)
                bot.append_event(event)
        
        # 爬取所有best_news的图片，并创建Word文档 (all articles, not just new ones)
        doc = Document()
        for article in best_news:
            doc.add_heading(article.get('region', 'N/A'), level=1)
            doc.add_heading(article.get('title', 'N/A'), level=2)
            doc.add_paragraph(f"Link: {article.get('link', 'N/A')}")
            doc.add_paragraph(f"Date: {article.get('date', 'N/A')}")
            doc.add_paragraph(f"Tag: {article.get('tag', 'N/A')}")
            doc.add_paragraph(f"Abstract: {article.get('abstract', 'N/A')}")
            doc.add_paragraph(f"Content: {article.get('content', 'N/A')}")
            doc.add_paragraph("\n")  # 每两个新闻条目之间间隔一行
        
        doc.add_heading('Events', level=1)
        # Add all events to Word document (not just unique ones)
        for event in events:
            doc.add_heading(event.get('title', 'N/A'), level=2)
            doc.add_paragraph(f"Link: {event.get('link', 'N/A')}")
            doc.add_paragraph(f"Date: {event.get('date', 'N/A')}")
            doc.add_paragraph(f"Address: {event.get('address', 'N/A')}")
            doc.add_paragraph(f"Summary: {event.get('summary', 'N/A')}")
            doc.add_paragraph("\n")  # 每两个events条目之间间隔一行

        #bot.send_events()
        # 保存Word文档到内存缓冲区
        news_word = BytesIO()
        doc.save(news_word)
        news_word.seek(0)
        
        # Close database connection
        db.close()

        message_placeholder.success("News summarization completed successfully!")
        st.download_button(
            label="Download News Summary as Word",
            data=news_word,
            file_name="news_summary.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
