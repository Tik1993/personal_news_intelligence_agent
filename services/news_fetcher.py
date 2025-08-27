from langchain_tavily import TavilySearch

def fetch_news(topic:str):
    tool = TavilySearch(max_results=5, topic="news", time_range="day",)
    results = tool.invoke({"query":topic})
    search_result=results["results"]

    context=[
        {"title":doc["title"],"url":doc['url'], "published_date":doc['published_date'], "content":doc['content']}
         for doc in search_result
    ]

    return context