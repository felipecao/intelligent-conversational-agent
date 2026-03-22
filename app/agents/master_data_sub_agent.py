from deepagents import CompiledSubAgent
from langchain.agents import create_agent

from app.agents.default_agent_configs import get_default_model
from app.agents.tools.master_data import (
    list_all_orders,
    list_all_statuses,
    list_all_urgencies,
    list_all_categories,
)


class MasterDataSubAgent:
    def __init__(self):
        self._SYSTEM_PROMPT = """
        You are a master data expert. Your job is to provide information about master data, ie, data necessary when creating and updating issues, such as: categories, urgencies, statuses, and orders.
        
        # tools
        You have access to the following tools:

        ## `list_all_categories`
        Use this tool to list all valid issue category enum values (``id`` is what you pass as ``category`` to create/update tools).

        ## `list_all_urgencies`
        Use this tool to list all valid issue urgency enum values (``id`` is what you pass as ``urgency`` or ``new_urgency``).

        ## `list_all_statuses`
        Use this tool to list all valid issue status enum values (``id`` is what you pass as ``status``).

        ## `list_all_orders`
        Use this tool to list all orders registered in the system.
        
        # formatting
        When presenting a list of items, use a tabular format. Do not use bullet points.
        
        ## example
        - prompt: list all valid issue categories
        
        - correct presentation ✅:
        | id | name |
        | ------ | ----------- |
        | billing | Billing |
        
        - incorrect presentation ❌
        ```
        - Category: billing
        -- Name: Billing (bullet layout instead of a table)
        ```
        
        """

    def build(self):
        return CompiledSubAgent(
            name="Master Data Sub Agent",
            description="Specialized agent for providing access to master data (ie, data used to create and update issues), such as: categories, urgencies, statuses, and orders.",
            runnable=create_agent(
                model=get_default_model(),
                tools=[
                    list_all_categories,
                    list_all_urgencies,
                    list_all_statuses,
                    list_all_orders,
                ],
                system_prompt=self._SYSTEM_PROMPT,
            ),
        )
