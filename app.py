import pandas as pd
import streamlit as st
from utils import get_articles, get_sources_by_country, save_pdf
from streamlit_tags import st_tags
import shutil
from datetime import date, timedelta

st.title('News Scraper')

with st.sidebar:
    gen_zip = st.checkbox('Get download links')

keywords = st_tags(
    label='Enter Keywords:',
    text='Press enter to add more',
    value=['China', 'semiconductors',],
    )

from_date = st.date_input(
    label='From date',
    value=date.today() - timedelta(days=1),
    max_value=date.today() - timedelta(days=1),
    min_value=date.today() - timedelta(days=30)
)

country_limit = st.checkbox('Limit sources by country', value=True)
if country_limit:
    country = st.selectbox(
        label='country',
        options=['ae',
                 'ar',
                 'at', 'au' , 'be' , 'bg' , 'br' , 'ca' , 'ch' , 'cn' , 'co' , 'cu' , 'cz' , 'de' , 'eg' , 'fr' , 'gb'
            , 'gr' , 'hk' , 'hu' , 'id' , 'ie' , 'il' , 'in' , 'it' , 'jp' , 'kr' , 'lt' , 'lv' , 'ma' , 'mx' , 'my' , 'ng' , 'nl' , 'no' , 'nz' , 'ph' , 'pl' , 'pt' , 'ro' , 'rs' , 'ru' , 'sa' , 'se' , 'sg' , 'si' , 'sk' , 'th' , 'tr' , 'tw' , 'ua' , 'us' , 've' , 'za'],
        index=23
    )

get_results = st.button('Get News Articles')
if get_results:
    if country_limit:
        sources = get_sources_by_country(country=country)
        # st.text(sources)
        articles = get_articles(keywords=keywords, sources=sources, from_date=from_date)
    else:
        articles = get_articles(keywords=keywords, from_date=from_date)

    # st.json(articles)
    keys = []
    num_results = []
    for key, results in articles.items():
        keys.append(key)
        num_results.append(results['totalResults'])
    st.table(pd.DataFrame({'keyword':keys, 'total results':num_results}))

    tabs = st.tabs(keys)

    for i,results in enumerate(articles.values()):
        with tabs[i]:
            for article in results['articles']:
                st.markdown(f"### {article['title']}")
                st.caption(f"**{article['source']['name']}** \n {article['description']}")
                st.markdown(f'[link]({article["url"]})')
                st.divider()



    if gen_zip:
        with st.sidebar:
            st.info('Making pdfs')
            folder = save_pdf(articles)
            # st.write(folder)
            st.info('Zipping the pdfs..')
            shutil.make_archive(f'{folder}', 'zip', folder)
            shutil.rmtree(f'{folder}')
            with open(f'{folder}.zip', 'rb') as file:
                st.download_button(
                    label='Download zip',
                    data = file,
                    file_name = "newspdfs.zip",
                    mime='application/zip'
                )
