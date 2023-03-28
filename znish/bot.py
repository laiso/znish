import logging
import os
import re
from datetime import datetime

import openai
from langchain import OpenAI, GoogleSearchAPIWrapper, PromptTemplate, LLMChain
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.tools.google_search.tool import GoogleSearchRun

memory = ConversationSummaryBufferMemory(llm=OpenAI(temperature=0), return_messages=True, memory_key='chat_history')

BOT_NAME = os.environ.get("BOT_NAME")
BOT_PROFILE = os.environ.get("BOT_PROFILE")

def send_message(text):
    SYETEM_MESSAGE = """あなたは{BOT_NAME}です。GTP-4に対応しています。
    {BOT_NAME}は{BOT_PROFILE}
    
    これまでの会話: {chat_history}
    
    次の会話を補完してください。
    
    現在の日時: """ + datetime.now().strftime("%Y/%m/%d %H:%M") + """
    User: {input}
    {BOT_NAME}: """

    
    tools = [
        GoogleSearchRun(description="""Google Searchのラッパーです。時事問題に関する質問に答える必要があるときに便利です。入力は検索クエリである。""",
                        api_wrapper=GoogleSearchAPIWrapper(google_api_key=os.environ.get("GOOGLE_API_KEY"), google_cse_id=os.environ.get("GOOGLE_CSE_ID")))
    ]
    agent_executor = initialize_agent(tools,
                                      ChatOpenAI(model_name='gpt-4', temperature=float(os.environ.get('BOT_TEMPERATURE', 0.0))),
                                      agent="chat-conversational-react-description",
                                      memory=memory,
                                      agent_kwargs=dict(system_message=SYETEM_MESSAGE))

    reply: str
    try:
        reply = agent_executor.run(input=text)
    except openai.error.InvalidRequestError as e:
        logging.exception(e)
        reply = "無理です: "+e.user_message
    except ValueError as e:
        logging.exception(e)
        pattern = r"Could not parse LLM output: (.*)"
        match = re.search(pattern, text)
        reply = match.group(1) if match else "だめです: "+e.user_message

    return reply