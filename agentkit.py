# chatbot.py
import os
from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpEvmServerWalletProvider,
    CdpEvmServerWalletProviderConfig,
    wallet_action_provider,
    erc20_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv() 

wallet_provider = CdpEvmServerWalletProvider(
    CdpEvmServerWalletProviderConfig(idempotency_key="386da273-4e40-4bb2-9b7d-75744a753b66"))

agentkit = AgentKit(
    AgentKitConfig(
        wallet_provider=wallet_provider,
        action_providers=[
            erc20_action_provider(),
            wallet_action_provider(),
        ]
    )
)

tools = get_langchain_tools(agentkit)

google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("Set GOOGLE_API_KEY environment variable for Gemini access")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)

agent = create_react_agent(llm, tools=tools)

def make_crypto_actions(prompt:str):
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    response = agent.invoke({"messages": [("user", prompt)]})

    return response["messages"][-1].content


if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = make_crypto_actions(user_input)
        print(f"Agent: {response}")