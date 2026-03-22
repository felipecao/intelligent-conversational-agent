from enum import Enum


class HumanSentiment(Enum):
    happy = "happy"
    neutral = "neutral"
    frustrated = "frustrated"
    angry = "angry"


class Rewards(Enum):
    cookie = "🍪"
    chocolate = "🍫"
    pizza = "🍫"
    flight_trip = "✈️"
