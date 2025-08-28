from langchain_tavily import TavilySearch
from db.db_client import news_collection 

def save_news_to_db(news_item):
    if news_collection.count_documents({"url":news_item["url"]},limit=1) == 0: 
        news_collection.insert_one(news_item)
    else:
        print("news already exist in DB")

def fetch_news(topic:str):
    tool = TavilySearch(max_results=5, topic="news", time_range="day",)
    results = tool.invoke({"query":topic})
    search_result=results["results"]

    context=[]
    for doc in search_result:
       news_item = {
          "title":doc["title"],
          "url":doc['url'], 
          "published_date":doc['published_date'], 
          "content":doc['content']
       }
       save_news_to_db(news_item)
       context.append(news_item)

    return context