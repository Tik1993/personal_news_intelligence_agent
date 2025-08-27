import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", temperature=0) 

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import START, END, StateGraph

import operator
from typing import List, Annotated
from typing_extensions import TypedDict

class GeneralState(TypedDict):
    topic:str
    context:Annotated[list, operator.add]
    output:str
    

def inputTopicNode(state:GeneralState):
    # topic=input("what is your desried topic?")
    topic="The latest AI news"
    return {"topic":topic}


from data import sample_data
from services.news_fetcher import fetch_news

def searchOnlineNewsNode(state:GeneralState):
    topic = state["topic"]
    context = fetch_news(topic=topic)
    
    # formatted_search_docs = "\n\n---\n\n".join([
    #     f'<Document href="{doc['url']}" published_date="{doc['published_date']}"/>\n{doc['content']}\n</Document>'
    #     for doc in search_result
    # ])
    # search_result = sample_data["results"]

    return {"context":context}

summarize_instructions = """
You are a summary assistant. 
Your task is to create a clear, human-readable summary. 

You are given a summary within ###:
###
{summary}
###

Your tasks are:
1. Summarize the content in 2-5 sentences.
2. Focus only on the key points (who, what, when, why, and any important metrics).
3. Remove any repetitive, irrelevant, or boilerplate information.
4. Produce exactly **one paragraph** per article. Do not include lists, bullet points, or extra sections.
"""

from data import summary_data
def summarizeNode(state:GeneralState):

    for item in state["context"]:
        system_message = summarize_instructions.format(summary=item["content"])
        summary=llm.invoke([SystemMessage(content=system_message)])
        item["revised_content"]=summary.content 
    
    # for idx, item in enumerate(state["context"]):
    #     item["revised_content"] = summary_data[idx]

    # pass

def outputNode(state:GeneralState):
    combined_output = ""
    for item in state["context"]:
        title = item.get("title","")
        published_date = item.get("published_date","")
        url=item.get("url","")
        revised = item.get("revised_content","")
        combined_output += "Title: "+title+"\n\n"+url+"\n\n"+published_date+"\n\n"+revised+"\n\n"

    return {"output":combined_output}


import smtplib
from email.message import EmailMessage

def sendEmailNode(state:GeneralState):
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    msg = EmailMessage()
    msg['Subject']="The latest AI news today"
    msg["From"]="ernestdev1993@gmail.com"
    msg["To"]="linchongtik@gmail.com"

    content = state["output"]
    msg.set_content(content )

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(email_address, email_password)
        smtp.send_message(msg)

    print("Email send")
    pass

tool_builder = StateGraph(GeneralState)
tool_builder.add_node("input_topic",inputTopicNode)
tool_builder.add_node("search_online_news", searchOnlineNewsNode)
tool_builder.add_node("summarize_news", summarizeNode)
tool_builder.add_node("output",outputNode)
tool_builder.add_node("sendEmail",sendEmailNode)

tool_builder.add_edge(START, "input_topic")
tool_builder.add_edge("input_topic", "search_online_news")
tool_builder.add_edge("search_online_news", "summarize_news")
tool_builder.add_edge("summarize_news", "output")
tool_builder.add_edge("output", "sendEmail")
tool_builder.add_edge("sendEmail", END)

tool_graph = tool_builder.compile()

response = tool_graph.invoke({})
# print(response["output"])