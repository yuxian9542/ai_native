from elasticsearch import Elasticsearch
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ElasticConfig:
    url='http://elastic:changeme@localhost:9200'
    
    
def get_es():
    while True:
        try:    
            es = Elasticsearch([ElasticConfig.url]) 
            return es
        except:
            print('ElasticSearch conn failed, retry')
            time.sleep(3)
            
# API URLs - can be overridden by environment variables
EMBEDDING_URL = os.getenv('EMBEDDING_URL', "http://test.2brain.cn:9800/v1/emb")
RERANK_URL = os.getenv('RERANK_URL', "http://test.2brain.cn:2260/rerank")
IMAGE_MODEL_URL = os.getenv('IMAGE_MODEL_URL', 'http://test.2brain.cn:23333/v1')

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Web Search API Key (already used in websearch.py)
WEB_SEARCH_KEY = os.getenv('WEB_SEARCH_KEY')
