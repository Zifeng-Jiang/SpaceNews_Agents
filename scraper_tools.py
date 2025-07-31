from spacenews_scraper import *
from find_news_mideast import *
from satellitetoday_scraper import *
from AI_launch_commercial import *
from google_news_scraper import *
from space_africa_scraper import *
import time

def run_news_scraper(status_callback=None):
    def update_status(module, running=False, completed=False, elapsed_time=0.0):
        if status_callback:
            status_callback(module, running, completed, elapsed_time)
    
    result = []
    
    # SpaceNews
    start_time = time.time()
    update_status('SpaceNews', running=True)
    spacenews_result = get_spacenews()
    result = spacenews_result
    elapsed = time.time() - start_time
    update_status('SpaceNews', completed=True, elapsed_time=elapsed)

    # Mideast Roundup
    start_time = time.time()
    update_status('Mideast Roundup', running=True)
    roundup = get_roundup(find_url())
    result = result + roundup
    elapsed = time.time() - start_time
    update_status('Mideast Roundup', completed=True, elapsed_time=elapsed)

    # Satellite Today
    start_time = time.time()
    update_status('Satellite Today', running=True)
    satellitetoday_news = get_satellitetoday_news()
    result = result + satellitetoday_news
    elapsed = time.time() - start_time
    update_status('Satellite Today', completed=True, elapsed_time=elapsed)

    # AI News
    start_time = time.time()
    update_status('AI News', running=True)
    AI_news = add_news('AI')
    result = result + AI_news
    elapsed = time.time() - start_time
    update_status('AI News', completed=True, elapsed_time=elapsed)

    # Launch News
    start_time = time.time()
    update_status('Launch News', running=True)
    launch_news = add_news('launch')
    result = result + launch_news
    elapsed = time.time() - start_time
    update_status('Launch News', completed=True, elapsed_time=elapsed)

    # Commercial News
    start_time = time.time()
    update_status('Commercial News', running=True)
    commercial_news = add_news('commercial')
    result = result + commercial_news
    elapsed = time.time() - start_time
    update_status('Commercial News', completed=True, elapsed_time=elapsed)

    # Google News
    start_time = time.time()
    update_status('Google News', running=True)
    google_news = get_google_news()
    result = result + google_news
    elapsed = time.time() - start_time
    update_status('Google News', completed=True, elapsed_time=elapsed)

    # Space in Africa
    start_time = time.time()
    update_status('Space in Africa', running=True)
    africa_news = get_spaceinafrica()
    result = result + africa_news
    elapsed = time.time() - start_time
    update_status('Space in Africa', completed=True, elapsed_time=elapsed)
    
    result = [article for article in result if 'link' in article and article['link']]

    # 有些文章没有abstruct，则将标题作为abstruct
    for article in result:
        if 'abstract' not in article or article['abstract'] == '':
            article['abstract'] = article['title']
    for article in result:
        if 'content' not in article or article['content'] == '':
            article['content'] = article['abstract']

    return result