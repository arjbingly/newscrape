import uuid

from newsapi import NewsApiClient
from datetime import date, timedelta, datetime
import pdfkit
from pathlib import Path
from dotenv import load_dotenv
import os
from tqdm import tqdm
import uuid
from pyppeteer import launch
import asyncio

def get_newsapi_client():
    load_dotenv()
    newsapi = NewsApiClient(api_key=os.environ.get('NEWSAPI'))
    return newsapi
def get_sources_by_country(country='in', return_raw=False):
    newsapi = get_newsapi_client()
    sources = newsapi.get_sources(country=country)
    output_list = []
    for s in sources['sources']:
        output_list.append(s['id'])
    print(f'Total sources returned={len(output_list)}')
    if return_raw:
        return output_list, sources
    else:
        return output_list

def get_articles(keywords,
                 sources=None,
                 language='en',
                 from_date=date.today() - timedelta(days=1),
                 sort_by='relevancy'):
    articles={}
    newsapi = get_newsapi_client()
    if sources:
        sources = ','.join(sources)
    for keyword in tqdm(keywords):
        if sources:
            articles[keyword] = newsapi.get_everything(q=keyword,
                                                       sources=sources,
                                                       from_param=from_date,
                                                       language=language,
                                                       sort_by=sort_by,
                                                       )
        else:
            articles[keyword] = newsapi.get_everything(q=keyword,
                                                       from_param=from_date,
                                                       language=language,
                                                       sort_by=sort_by,
                                                       )
    return articles


def save_pdf(articles):
    temp_folder = 'temp'
    temp_folder_path = Path(temp_folder)
    temp_folder_path.mkdir(parents=True, exist_ok=True)

    root_folder = str(uuid.uuid4())
    root_folder_path = temp_folder_path / root_folder
    root_folder_path.mkdir(parents=True, exist_ok=True)

    main_folder_path = root_folder_path / datetime.now().strftime('%Y%m%d')
    main_folder_path.mkdir(parents=True, exist_ok=True)

    for keyword, article in articles.items():
        keyword_folder_path = main_folder_path / keyword
        keyword_folder_path.mkdir(parents=True, exist_ok=True)
        for article in article['articles']:
            if len(article['title']) > 30:
                fileName = f"{article['source']['name']}-{article['title'][:25]}.pdf"
            else:
                fileName = f"{article['source']['name']}-{article['title']}.pdf"
            # pdfkit.from_url(article['url'], f"{keyword_folder_path}/{fileName}", options={"enable-local-file-access": ""})
            convert_url_to_pdf(article['url'],f"{keyword_folder_path}/{fileName}")
    return root_folder_path

def convert_url_to_pdf(url, pdf_path):
    try:
        pdfkit.from_url(url, pdf_path)
        print(f"PDF generated and saved at {pdf_path}")
    except Exception as e:
        print(f"PDF generation failed: {e}")
