import random

from langchain_core.tools import tool

from app.agents.models import HumanSentiment, Rewards


@tool(
    description=f"Use this tool when sentiment analysis flags that a user is {HumanSentiment.angry} or {HumanSentiment.frustrated}"
)
def offer_reward(sentiment: HumanSentiment) -> str:
    reward = random.choice(list(Rewards))
    return f"I understand you're feeling {sentiment}. Please accept a complimentary {reward.name} {reward.value} as a thank you for your patience"
