"""Agent modules for Friday."""

from friday.agents.approval_agent import ApprovalAgent
from friday.agents.calendar_agent import CalendarAgent
from friday.agents.contact_context_agent import ContactContextAgent
from friday.agents.message_agent import MessageAgent
from friday.agents.morning_briefing_agent import MorningBriefingAgent
from friday.agents.task_agent import TaskAgent

__all__ = [
    "ApprovalAgent",
    "CalendarAgent",
    "ContactContextAgent",
    "MessageAgent",
    "MorningBriefingAgent",
    "TaskAgent",
]
