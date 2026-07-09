"""Agent modules for Friday."""

from friday.agents.approval_agent import ApprovalAgent
from friday.agents.calendar_agent import CalendarAgent
from friday.agents.contact_context_agent import ContactContextAgent
from friday.agents.email_forward_agent import EmailForwardPreview, build_email_forward_preview
from friday.agents.message_agent import MessageAgent
from friday.agents.morning_briefing_agent import MorningBriefingAgent
from friday.agents.task_agent import TaskAgent
from friday.agents.whatsapp_forward_agent import (
    WhatsAppForwardPreview,
    build_whatsapp_forward_preview,
)

__all__ = [
    "ApprovalAgent",
    "CalendarAgent",
    "ContactContextAgent",
    "EmailForwardPreview",
    "MessageAgent",
    "MorningBriefingAgent",
    "TaskAgent",
    "WhatsAppForwardPreview",
    "build_email_forward_preview",
    "build_whatsapp_forward_preview",
]
