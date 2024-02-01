# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chains.summarize import load_summarize_chain
import requests
from bs4 import BeautifulSoup


# hugging face
from transformers import pipeline, BartTokenizer, BartForConditionalGeneration
# import safetensors  # Import the safetensors library


# Streamlit app
st.subheader('Last Hour In...')

# Get OpenAI API key, Serper API key, number of results, and search query
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", value="", type="password")
    serper_api_key = st.text_input("Serper API Key", value="", type="password")
    num_results = st.number_input(
        "Number of Search Results", min_value=3, max_value=10)
    st.caption("*Search: Uses Serper API only, retrieves search results.*")
    st.caption(
        "*Search & Summarize: Uses Serper & OpenAI APIs, summarizes each search result.*")
search_query = st.text_input("Search Query", label_visibility="collapsed")
col1, col2 = st.columns(2)

# If the 'Search' button is clicked
if col1.button("Search"):
    # Validate inputs
    if not openai_api_key.strip() or not serper_api_key.strip() or not search_query.strip():
        st.error(f"Please provide the missing fields.")
    else:
        try:
            with st.spinner("Please wait..."):
                # Show the top X relevant news articles from the previous week using Google Serper API
                search = GoogleSerperAPIWrapper(
                    type="news", tbs="qdr:h", serper_api_key=serper_api_key)
                result_dict = search.results(search_query)

                if not result_dict['news']:
                    st.error(f"No search results for: {search_query}.")
                else:
                    for i, item in zip(range(num_results), result_dict['news']):
                        st.success(
                            f"Title: {item['title']}\n\nLink: {item['link']}\n\nSnippet: {item['snippet']}")
        except Exception as e:
            st.exception(f"Exception: {e}")

# If 'Search & Summarize' button is clicked
if col2.button("Search & Summarize"):
    # Validate inputs
    if not openai_api_key.strip() or not serper_api_key.strip() or not search_query.strip():
        st.error(f"Please provide the missing fields.")
    else:
        try:
            with st.spinner("Please wait..."):
                # Show the top X relevant news articles from the previous week using Google Serper API
                search = GoogleSerperAPIWrapper(
                    type="news", tbs="qdr:h", serper_api_key=serper_api_key)
                result_dict = search.results(search_query)

                if not result_dict['news']:
                    st.error(f"No search results for: {search_query}.")
                else:

                    # Loading BART model
                    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

                    #model_name = "facebook/bart-large-cnn"
                    #tokenizer = BartTokenizer.from_pretrained(model_name, forced_bos_token_id=0)
                    #model = BartForConditionalGeneration.from_pretrained(model_name)

                    # one by one performing summarization on each news articles
                    # for i, item in zip(range(num_results), result_dict['news']):
                    #loader = UnstructuredURLLoader(urls=[item['link']])
                    #data = loader.load()

                    for i, item in zip(range(num_results), result_dict['news']):

                        try:
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'} 
                            response = requests.get(item['link'], headers=headers)
                            response.raise_for_status()  
                            
                            soup = BeautifulSoup(response.content, 'html.parser')  
                            main_content = soup.find('main')  # Adjust the selector if needed 
                            
                            content = main_content.find('article').get_text(strip=True, separator='\n') if main_content else soup.get_text(strip=True, separator='\n')
                            
                            max_length = 1024  # Set a reasonable max_length
                            
                                
                            while len(content.split()) > 100: 
                                summaries=[]
                                # Split the content into chunks if it's too long
                                chunks = [content[i:i+max_length] for i in range(0, len(content), max_length)]
                                for chunk in chunks: 
                                    summary = summarizer(chunk, max_length=max_length, min_length=20, do_sample=False)[0]['summary_text'] 
                                    summaries.append(summary)
                                content = ' '.join(summaries)

                            

    
                            st.success(f"Title: {item['title']}\n\nLink: {item['link']}\n\nSummary: {content}")
                        except Exception as e:
                            st.exception(f"Exception: {e}")
        except Exception as e:
            st.exception(f"Exception: {e}")
