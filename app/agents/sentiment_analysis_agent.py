from deepagents import CompiledSubAgent
from langchain.agents import create_agent

from app.agents.default_agent_configs import get_default_model
from app.agents.models import HumanSentiment


class SentimentAnalysisSubAgent:
    def __init__(self):
        self._SYSTEM_PROMPT = f"""
        You are a expert in sentiment analysis. Your job is to analyze a message sent by the user, perform sentiment analysis
         and classify it into on the following categories: {list(HumanSentiment)} 
        """

    def build(self):
        return CompiledSubAgent(
            name="Sentiment Analysis Sub Agent",
            description="Specialized agent in performing sentiment analysis and classifying the tone of a human message",
            runnable=create_agent(
                model=get_default_model(),
                tools=[],
                system_prompt=self._SYSTEM_PROMPT,
            ),
        )
