import random
from unittest import TestCase

from app.agents.models import HumanSentiment, Rewards
from app.agents.tools.customer_satisfaction import offer_reward


class TestCustomerSatisfactionTool(TestCase):
    def test_offer_reward_returns_message_including_sentiment_and_valid_reward(self):
        sentiment = random.choice(list(HumanSentiment))

        message = offer_reward.invoke({"sentiment": sentiment})

        self.assertIn(f"I understand you're feeling {sentiment}", message)

        reward_phrase = self._extract_complimentary_reward_phrase(message)
        all_possible_rewards = {f"{r.name} {r.value}" for r in Rewards}

        self.assertIn(
            reward_phrase,
            all_possible_rewards,
            msg=f"Complimentary segment {reward_phrase!r} should be name + value for one Rewards member",
        )

    @staticmethod
    def _extract_complimentary_reward_phrase(message: str) -> str:
        _COMPLIMENTARY_PREFIX = "Please accept a complimentary "
        _COMPLIMENTARY_SUFFIX = " as a thank you for your patience"

        start = message.index(_COMPLIMENTARY_PREFIX) + len(_COMPLIMENTARY_PREFIX)
        end = message.index(_COMPLIMENTARY_SUFFIX)
        return message[start:end]
