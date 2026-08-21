# Copyright (c) 2026 Nishant Sinha
#
# Licensed under the MIT License. See LICENSE.txt in the project
# root for full license information.
#
# END COPYRIGHT

"""
crewAI agent executor for an A2A server example
See https://github.com/a2aproject/a2a-samples/tree/main/samples/python
"""

from typing_extensions import override

# pylint: disable=import-error
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution import RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from agent import CrewAiResearchReport


class CrewAiAgentExecutor(AgentExecutor):
    """Agent executor for crewAI agents

    adapted from https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/agent_executor.py
    """

    def __init__(self):
        self.agent = CrewAiResearchReport()

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """
        Handles incoming requests that expect a response or a stream of events.
        It processes the user's input (available via context) and uses the event_queue to send back Message
        """
        # Get query from the context
        query: str = context.get_user_input()
        if not context.message:
            raise ValueError("No message provided")

        # Invoke the underlying agent
        result = await self.agent.ainvoke(query)
        await event_queue.enqueue_event(new_agent_text_message(result))

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """
        Handles requests to cancel an ongoing task. Cancellation is not supported for this example.
        """
        raise NotImplementedError
