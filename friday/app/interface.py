"""Terminal interface used to display Friday's local information."""

from __future__ import annotations

from pathlib import Path
from getpass import getpass
import sqlite3
from typing import Any, Dict, List

from friday.app.menu import (
    show_account_menu,
    show_backup_restore_menu,
    show_menu,
    show_privacy_dashboard_menu,
    show_task_menu,
)
from friday.agents.approval_agent import ApprovalAgent
from friday.agents.calendar_agent import CalendarAgent
from friday.agents.contact_context_agent import ContactContextAgent
from friday.agents.message_agent import MessageAgent
from friday.agents.morning_briefing_agent import MorningBriefingAgent
from friday.agents.task_agent import TaskAgent
from friday.app.task_markdown_export import export_tasks_markdown_to_default_path
from friday.app.day_planning_preview import build_day_plan_preview
from friday.app.day_planning_renderer import render_day_plan_preview
from friday.app.date_utils import resolve_today
from friday.app.quick_add_parser import parse_quick_add_task
from friday.app.notification_preview import build_due_task_notification_preview
from friday.app.local_ollama_runtime import is_local_ollama_url
from friday.app.email_draft_model import EmailDraft, build_email_draft
from friday.app.email_draft_renderer import render_email_draft_preview
from friday.app.email_account_store import (
    EMAIL_ACCOUNT_DELETE_TOKEN,
    EMAIL_ACCOUNT_SAVE_TOKEN,
    build_email_account_from_plain_password,
    build_email_account_from_preset,
    decrypt_email_account_password,
    delete_email_account,
    email_account_status,
    load_email_account,
    save_email_account,
    save_email_account_agent_notes,
)
from friday.app.email_activation_gate import EMAIL_ACTIVATION_TOKEN, build_email_activation_gate
from friday.app.email_imap_reader import check_imap_login, read_recent_inbox_emails
from friday.app.email_smtp_sender import check_smtp_login
from friday.app.whatsapp_bridge_activation_gate import (
    WHATSAPP_BRIDGE_ACTIVATION_TOKEN,
    apply_whatsapp_bridge_read_activation_to_config,
    build_whatsapp_bridge_activation_gate,
)
from friday.app.whatsapp_inbox_store import (
    get_whatsapp_bridge_status,
    load_whatsapp_agent_notes,
    read_recent_whatsapp_messages,
    save_whatsapp_agent_notes,
)
from friday.app.review_batch_selection_parser import parse_review_batch_selection
from friday.app.review_batch_selection_preview import (
    render_review_batch_selection_preview,
)
from friday.app.review_activity_detail_view import build_review_activity_detail_view
from friday.app.review_activity_status_filter import (
    INVALID_REVIEW_ACTIVITY_STATUS_FILTER_MESSAGE,
    build_review_activity_status_filter,
)
from friday.app.review_activity_type_filter import (
    INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE,
    build_review_activity_type_filter,
)
from friday.app.review_activity_search import (
    INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE,
    build_review_activity_search,
)
from friday.app.review_activity_summary import build_review_activity_summary
from friday.app.review_batch_apply_guard import (
    REVIEW_BATCH_APPROVE_MESSAGES_TOKEN,
    REVIEW_BATCH_CREATE_TASKS_TOKEN,
    REVIEW_BATCH_REJECT_SUGGESTIONS_TOKEN,
    check_review_batch_apply_allowed,
)
from friday.app.review_batch_apply_model import (
    ReviewBatchApplyItem,
    apply_review_batch_selection,
)
from friday.app.contact_context_prompt_draft_flow import (
    apply_contact_prompt_draft_input,
    prepare_contact_prompt_draft_flow,
)
from friday.app.contact_context_save_guard import CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE
from friday.app.contact_context_prompt_candidate import should_create_contact_prompt_candidate
from friday.app.contact_context_preview import normalize_contact_name
from friday.app.contact_context_session_suppression import (
    ContactPromptSuppressionEntry,
    is_contact_prompt_suppressed,
    mark_contact_prompt_skipped,
)
from friday.app.obsidian_brain import build_obsidian_brain_preview
from friday.app.obsidian_note_preview import (
    OBSIDIAN_WRITE_TOKEN,
    write_obsidian_note_with_approval,
)
from friday.app.backup_preview import build_backup_preview
from friday.app.backup_rotation_guard import BACKUP_ROTATION_APPROVAL_TOKEN, check_backup_rotation_allowed
from friday.app.backup_rotation_preview import build_backup_rotation_preview
from friday.app.backup_rotation_writer import apply_backup_rotation
from friday.app.backup_write_guard import BACKUP_WRITE_APPROVAL_TOKEN
from friday.app.backup_writer import write_local_backup
from friday.app.local_data_export_preview import (
    LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
    build_local_data_export_preview,
)
from friday.app.local_data_export_writer import (
    LocalDataExportPayload,
    write_local_data_export,
)
from friday.app.local_data_import_apply_preview import (
    LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
    build_local_data_import_apply_preview,
)
from friday.app.local_data_import_apply_write_guard import (
    check_local_data_import_apply_write_allowed,
)
from friday.app.local_data_import_apply_writer import apply_local_data_import
from friday.app.local_data_import_dry_run import build_local_data_import_dry_run
from friday.app.local_data_import_manifest_reader import read_local_data_import_manifest
from friday.app.restore_dry_run import build_restore_dry_run
from friday.app.restore_write_guard import RESTORE_WRITE_APPROVAL_TOKEN
from friday.app.restore_writer import write_local_restore_copy
from friday.app.safety_smoke_runner import run_safety_smoke
from friday.app.privacy_dashboard import (
    build_privacy_dashboard_summary,
    collect_privacy_dashboard_local_counts,
)
from friday.app.privacy_data_management import build_privacy_data_management_inventory
from friday.app.privacy_cleanup_preview import build_privacy_cleanup_preview
from friday.app.privacy_cleanup_db_preview import build_privacy_cleanup_db_preview
from friday.app.privacy_cleanup_db_guard import check_privacy_cleanup_db_write_allowed
from friday.app.privacy_cleanup_db_writer import apply_privacy_cleanup_db_write
from friday.app.forget_person_preview import (
    build_forget_person_preview,
)
from friday.app.forget_person_write_guard import check_forget_person_write_allowed
from friday.app.forget_person_writer import apply_forget_person_write
from friday.app.privacy_cleanup_write_guard import (
    PRIVACY_CLEANUP_TOKENS,
    check_privacy_cleanup_write_allowed,
)
from friday.app.privacy_cleanup_writer import apply_privacy_cleanup
from friday import config
from friday.app.ms_mail_account_store import ms_mail_account_status
from friday.storage.contact_context_repository import ContactContextRepository
from friday.storage.repositories import BlockedSenderRepository


INVALID_SELECTION = "Ungültige Auswahl. Bitte erneut versuchen."


class FridayInterface:
    """Simple local terminal UI.

    This class only reads local sample data and prints suggestions.
    """

    def __init__(
        self,
        task_agent: TaskAgent | None = None,
        message_agent: MessageAgent | None = None,
        calendar_agent: CalendarAgent | None = None,
        contact_agent: ContactContextAgent | None = None,
        contact_context_repository: ContactContextRepository | None = None,
        approval_agent: ApprovalAgent | None = None,
        briefing_agent: MorningBriefingAgent | None = None,
    ) -> None:
        # Use dependency injection so the code stays testable and easy to extend.
        self.task_agent = task_agent or TaskAgent()
        self.message_agent = message_agent or MessageAgent(contact_agent=contact_agent or ContactContextAgent())
        self.calendar_agent = calendar_agent or CalendarAgent()
        self.contact_context_repository = contact_context_repository or ContactContextRepository(
            getattr(self.task_agent, "db_path", None)
        )
        self.contact_prompt_suppression_entries: tuple[ContactPromptSuppressionEntry, ...] = ()
        self.email_drafts: list[EmailDraft] = []
        self.approval_agent = approval_agent or ApprovalAgent()
        self.briefing_agent = briefing_agent or MorningBriefingAgent(
            task_agent=self.task_agent,
            calendar_agent=self.calendar_agent,
        )

    def _section_title(self, title: str) -> None:
        print("\n" + "-" * 40)
        print(title)
        print("-" * 40)

    def _format_calendar_slot_text(self, slot: dict) -> str:
        """Format a selected calendar slot as draft text."""
        return (
            f"Möglicher Termin: {slot.get('slot_date', '')} "
            f"von {slot.get('start', '')} bis {slot.get('end', '')}."
        )

    def _merge_calendar_slot_into_draft(self, draft_text: str, slot_text: str) -> str:
        """Replace or append one local calendar slot line inside a message draft."""
        lines = (draft_text or "").splitlines()
        merged_lines: list[str] = []
        replaced = False

        for line in lines:
            if line.startswith("Möglicher Termin:"):
                if not replaced:
                    merged_lines.append(slot_text)
                    replaced = True
            else:
                merged_lines.append(line)

        if not replaced:
            if merged_lines:
                return "\n".join(merged_lines + [slot_text])
            return slot_text
        return "\n".join(merged_lines)

    def _show_open_tasks(self) -> None:
        tasks = self.task_agent.get_open_tasks()
        self._section_title("Offene Aufgaben")
        # Show only local open tasks. This makes it safe and fast.
        if not tasks:
            print("Keine offenen Aufgaben gefunden.")
            return
        for task in tasks:
            priority = task.get("priority") or self.task_agent.detect_priority_hint(task)
            category = task.get("category") or "sonstiges"
            recurrence = task.get("recurrence")
            recurrence_suffix = f" [{recurrence}]" if recurrence else ""
            print(f"- [{task['id']}] {task['title']}{recurrence_suffix} ({category}) | Priorität: {priority}")

    def _show_local_day_plan_preview(self) -> None:
        """Show a read-only local day planning preview from open tasks."""
        tasks = self.task_agent.get_open_tasks()
        preview = build_day_plan_preview(tasks, today=resolve_today())
        print(render_day_plan_preview(preview))

    def _show_messages_with_suggestions(self) -> List[Dict[str, Any]]:
        messages = self.message_agent.get_messages()
        self._section_title("Eingehende Nachrichten")
        # Show all sample messages and prepare a safe suggestion list per message.
        shown = []
        for message in messages:
            text = message.get("text", "")
            if hasattr(self.message_agent, "detect_intent"):
                intent = self.message_agent.detect_intent(text)
            elif self.message_agent.is_scheduling_related(text):
                intent = "scheduling"
            else:
                intent = "unclear"
            is_scheduling = intent == "scheduling"
            label = "Termin/Meeting möglich" if is_scheduling else "Keine Aktion erkannt"
            intent_label = self._intent_label(intent)
            suggestion = self.message_agent.create_reply_suggestion(message)
            contact_type = self.message_agent.get_contact_type(message.get("sender", "unbekannt"))
            print(f"\nID: {message['id']}")
            print(f"Von: {message['sender']} ({contact_type})")
            print(f"Text: {message['text']}")
            print(f"Erkannte Absicht: {intent_label}")
            print(f"Aktionshinweis: {label}")
            print(f"Antwortvorschlag: {suggestion}")
            shown.append({"message": message, "is_scheduling": is_scheduling, "suggestion": suggestion})
        self._show_email_inbox_preview()
        self._show_whatsapp_inbox_preview()
        return shown

    def _show_email_inbox_preview(self) -> None:
        """Show a read-only local email inbox preview when an account is connected."""
        account = load_email_account()
        if account is None:
            print("\nE-Mail-Posteingang: Kein E-Mail-Konto verbunden.")
            return
        try:
            password = decrypt_email_account_password(account)
            result = read_recent_inbox_emails(account=account, app_password=password, limit=10)
        except Exception:
            print("\nE-Mail-Posteingang: Vorschau konnte nicht geladen werden.")
            return
        print("\nE-Mail-Posteingang (letzte 10, nur lesen)")
        if not result.ok:
            print(f"E-Mail-Posteingang nicht erreichbar: {result.error or 'unbekannter Fehler'}")
            return
        if not result.items:
            print("Keine E-Mails gefunden.")
            return
        for item in result.items:
            print(f"- Von: {item.sender} | Betreff: {item.subject} | Datum: {item.date}")
            print(f"  {item.text_preview}")

    def _show_whatsapp_inbox_preview(self) -> None:
        """Show mirrored WhatsApp messages as a read-only local preview."""
        status = get_whatsapp_bridge_status(getattr(self.message_agent, "db_path", None))
        print("\nWhatsApp (mitgelesen, letzte 10)")
        print("Hinweis: Nur Mitlesen. Senden nur durch dich per WhatsApp-Link.")
        print(f"Read-Bridge aktiv: {status['read_enabled']}")
        items = read_recent_whatsapp_messages(
            limit=10,
            db_path=getattr(self.message_agent, "db_path", None),
        )
        if not items:
            print("Keine lokal gespiegelten WhatsApp-Nachrichten.")
            return
        for item in items:
            print(f"- Von: {item.get('sender_name') or 'WhatsApp'} | {item.get('received_at')}")
            print(f"  Nummer: {item.get('sender_number_masked')}")
            print(f"  {item.get('body')}")

    def _show_spam_and_blocked_senders(self) -> None:
        """Show local spam previews and allow local sender unblock."""
        self._section_title("Spam / Blockiert")
        repository = BlockedSenderRepository(getattr(self.message_agent, "db_path", None))
        blocked = repository.list_blocked_senders()
        print("Hinweis: Diese Liste ist nur lokal. Echte Postfächer bleiben unverändert.")
        if blocked:
            print("Blockierte Absender:")
            for item in blocked:
                print(
                    f"- [{item['id']}] {item.get('label') or item.get('sender_key')} "
                    f"({item.get('source')})"
                )
        else:
            print("Keine lokal blockierten Absender.")

        if getattr(self.message_agent, "ms_mail_repository", None) is not None:
            spam_mails = self.message_agent.ms_mail_repository.list_messages(
                limit=20,
                include_spam=True,
            )
            spam_mails = [item for item in spam_mails if int(item.get("is_spam") or 0) == 1]
            if spam_mails:
                print("\nLokale Spam-Mails:")
                for item in spam_mails:
                    print(f"- [{item['id']}] {item.get('sender')}: {item.get('subject')}")

        spam_whatsapp = [
            item
            for item in read_recent_whatsapp_messages(
                limit=20,
                include_spam=True,
                db_path=getattr(self.message_agent, "db_path", None),
            )
            if int(item.get("is_spam") or 0) == 1
        ]
        if spam_whatsapp:
            print("\nLokale WhatsApp-Spam-Vorschauen:")
            for item in spam_whatsapp:
                print(f"- [{item['id']}] {item.get('sender_name') or 'WhatsApp'}: {item.get('body')}")

        if not blocked:
            return
        selected = input("Block-ID zum Entblocken (leer = zurück): ").strip()
        if not selected:
            return
        if not selected.isdigit():
            print(INVALID_SELECTION)
            return
        unblocked = repository.unblock_sender(int(selected))
        if unblocked is None:
            print("Blockierter Absender wurde nicht gefunden.")
            return
        print("Absender wurde lokal entblockt.")

    def _intent_label(self, intent: str) -> str:
        """Map internal intent to German display labels."""
        mapping = {
            "scheduling": "Termin/Planung",
            "task": "Aufgabe",
            "question": "Frage",
            "info": "Information",
            "unclear": "Unklar",
        }
        return mapping.get(intent, "Unklar")

    def _show_calendar(self) -> None:
        suggestions = self.calendar_agent.get_free_slots_today()
        self._section_title("Kalender-Vorschläge")
        # Fridays current behavior: only suggest free slots from sample calendar.
        if not suggestions:
            print("Heute keine freien Slots in der Musterdatenbank.")
            return
        for slot in suggestions:
            print(f"- Frei: {slot['start']} bis {slot['end']}")

    def _ask_approvals_for_messages(self, messages: List[Dict[str, Any]]) -> None:
        # This method is only used when user opens the review menu.
        for item in messages:
            message = item["message"]
            if not item["is_scheduling"]:
                continue
            action = f"Nachricht {message['id']} als Terminvorschlag beantworten"
            status = self.approval_agent.request_approval(action, message=item["suggestion"])
            print(f"Status: {status}")

    def _ask_approvals_for_calendar(self) -> None:
        # This method is only used when user opens the review menu.
        slots = self.calendar_agent.get_free_slots_today()
        # Approval is needed for each potential calendar booking idea.
        for slot in slots:
            action = f"Freien Slot buchen: {slot['start']} bis {slot['end']} (Demo)"
            status = self.approval_agent.request_approval(action, message="Nur Demo, kein echter Termin wird geschrieben.")
            print(f"Status: {status}")

    def review_pending_suggestions(self) -> None:
        """Review collected suggestions and ask for approval in one place."""
        self._section_title("Vorschläge prüfen / freigeben")
        print(
            "Hinweis: Alle Aktionen sind lokal. Es wird nichts gesendet und kein echter Termin erstellt."
        )

        while True:
            self.message_agent.generate_local_suggestions()
            self._generate_local_task_suggestions()

            messages = self.message_agent.get_messages()
            contact_candidates = self._get_review_contact_candidates(messages)
            review_counts = self._get_review_counts(contact_candidates)
            has_review_activity = bool(
                self._get_all_message_suggestions()
                or self._get_all_task_suggestions()
            )
            if (
                review_counts["message"] == 0
                and review_counts["task"] == 0
                and review_counts["contact"] == 0
                and not has_review_activity
            ):
                print("Keine offenen Vorschläge vorhanden.")
                return

            self._print_review_overview(
                review_counts["message"],
                review_counts["task"],
                review_counts["contact"],
            )
            self._print_review_contact_candidate_preview(contact_candidates)

            area = input("Bereich wählen: ").strip().lower()
            if not area or area == "z":
                return

            if area == "1":
                if review_counts["message"] == 0:
                    print(INVALID_SELECTION)
                    continue
                self._review_message_suggestions_loop(
                    self._get_pending_message_suggestions(),
                    self._get_messages_by_id(),
                )
                continue

            if area == "2":
                if review_counts["task"] == 0:
                    print(INVALID_SELECTION)
                    continue
                self._review_task_suggestions_loop(
                    self._get_pending_task_suggestions(),
                    self._get_messages_by_id(),
                )
                continue

            if area == "3":
                continue

            if area == "4":
                if review_counts["contact"] == 0:
                    print(INVALID_SELECTION)
                    continue
                self._review_contact_candidates_loop(contact_candidates)
                continue

            if area == "5":
                if review_counts["message"] == 0 and review_counts["task"] == 0:
                    print(INVALID_SELECTION)
                    continue
                self._show_review_batch_selection_preview(
                    self._get_pending_message_suggestions(),
                    self._get_pending_task_suggestions(),
                    self._get_messages_by_id(),
                )
                continue

            if area == "6":
                self._show_review_activity_summary()
                continue

            if area == "7":
                self._show_review_activity_detail_view()
                continue

            if area == "8":
                self._show_review_activity_status_filter()
                continue

            if area == "9":
                self._show_review_activity_type_filter()
                continue

            if area == "10":
                self._show_review_activity_search()
                continue

            print(INVALID_SELECTION)

    def _get_review_counts(self, contact_candidates: list[dict] | None = None) -> dict[str, int]:
        """Return the number of pending message/task suggestions."""
        return {
            "message": len(self._get_pending_message_suggestions()),
            "task": len(self._get_pending_task_suggestions()),
            "contact": len(contact_candidates or []),
        }

    def _print_review_overview(self, message_count: int, task_count: int, contact_count: int = 0) -> None:
        """Print combined review summary and available areas."""
        print(f"Offene Nachrichten-Vorschläge: {message_count}")
        print(f"Offene Aufgaben-Vorschläge: {task_count}")
        print(f"Offene Kontakt-Kontext-Hinweise: {contact_count}")
        print("Bereich wählen:")
        print("1. Nachrichten-Vorschläge prüfen")
        print("2. Aufgaben-Vorschläge prüfen")
        print("3. Übersicht aktualisieren")
        print("4. Kontakt-Kontext prüfen")
        print("5. Batch-Auswahl als Vorschau anzeigen")
        print("6. Review-Aktivität anzeigen")
        print("7. Review-Aktivität im Detail anzeigen")
        print("8. Review-Aktivität nach Status filtern")
        print("9. Review-Aktivität nach Typ filtern")
        print("10. Review-Aktivität durchsuchen")
        print("Enter/z. Zurück zum Hauptmenü")

    def _get_all_message_suggestions(self) -> list[dict]:
        """Return all local message suggestions if the repository is available."""
        repository = getattr(self.message_agent, "suggestion_repository", None)
        if repository is None:
            return []
        return repository.get_all_suggestions()

    def _get_all_task_suggestions(self) -> list[dict]:
        """Return all local task suggestions if the repository is available."""
        repository = getattr(self.message_agent, "task_suggestion_repository", None)
        if repository is None:
            return []
        return repository.get_all_task_suggestions()

    def _show_review_activity_summary(self) -> None:
        """Show a read-only summary of local review activity."""
        summary = build_review_activity_summary(
            self._get_all_message_suggestions(),
            self._get_all_task_suggestions(),
        )
        self._section_title("Review-Aktivität")
        print("Nachrichten-Vorschläge:")
        print(f"- Offen: {summary.message_counts.open}")
        print(f"- Lokal freigegeben: {summary.message_counts.approved}")
        print(f"- Abgelehnt: {summary.message_counts.rejected}")

        print("\nAufgaben-Vorschläge:")
        print(f"- Offen: {summary.task_counts.open}")
        print(f"- Abgelehnt: {summary.task_counts.rejected}")
        print(f"- In Aufgaben umgewandelt: {summary.task_counts.converted}")
        print(f"- Mit lokaler Aufgabe verknüpft: {summary.task_counts.with_created_task_id}")

        print("\nZuletzt lokal geändert:")
        if not summary.recent_items:
            print("- Keine zuletzt geänderten Vorschläge gefunden.")
            return

        for item in summary.recent_items:
            label = (
                "Nachrichten-Vorschlag"
                if item.suggestion_type == "message"
                else "Aufgaben-Vorschlag"
            )
            suffix = (
                f" -> Aufgabe {item.created_task_id}"
                if item.created_task_id is not None
                else ""
            )
            suggestion_id = item.suggestion_id if item.suggestion_id is not None else "unbekannt"
            print(f"- {label} {suggestion_id}: {item.status}{suffix}")

    def _show_review_activity_detail_view(self) -> None:
        """Show read-only local review activity details."""
        detail_view = build_review_activity_detail_view(
            self._get_all_message_suggestions(),
            self._get_all_task_suggestions(),
        )
        self._section_title("Review-Aktivität im Detail")
        if not detail_view.all_items:
            print("Keine lokalen Review-Details vorhanden.")
            return

        print("Nachrichten-Vorschläge:")
        if detail_view.message_items:
            for item in detail_view.message_items:
                self._print_review_activity_detail_item(item)
        else:
            print("- Keine Nachrichten-Vorschläge gefunden.")

        print("\nAufgaben-Vorschläge:")
        if detail_view.task_items:
            for item in detail_view.task_items:
                self._print_review_activity_detail_item(item)
        else:
            print("- Keine Aufgaben-Vorschläge gefunden.")

    def _print_review_activity_detail_item(self, item: Any) -> None:
        suggestion_id = item.suggestion_id if item.suggestion_id is not None else "unbekannt"
        status = item.status or "unbekannt"
        label = item.primary_label or "Unbekannt"
        excerpt = f": {item.excerpt}" if item.excerpt else ""
        task_suffix = (
            f" -> Aufgabe {item.created_task_id}"
            if item.created_task_id is not None
            else ""
        )
        print(f"- #{suggestion_id} [{status}] {label}{excerpt}{task_suffix}")

    def _show_review_activity_status_filter(self) -> None:
        """Show read-only local review activity details filtered by status."""
        raw_filter = input(
            "Statusfilter (all/open/pending/edited/approved/rejected/converted, leer/z = zurück): "
        ).strip()
        if not raw_filter or raw_filter.lower() == "z":
            return

        detail_view = build_review_activity_detail_view(
            self._get_all_message_suggestions(),
            self._get_all_task_suggestions(),
        )
        result = build_review_activity_status_filter(detail_view.all_items, raw_filter)
        self._section_title("Review-Aktivität nach Status")

        if not result.is_valid:
            print(result.error_message or INVALID_REVIEW_ACTIVITY_STATUS_FILTER_MESSAGE)
            return

        print(f"Statusfilter: {result.normalized_filter}")
        if not result.items:
            print("Keine lokalen Review-Details für diesen Status gefunden.")
            return

        for item in result.items:
            self._print_review_activity_detail_item(item)

    def _show_review_activity_type_filter(self) -> None:
        """Show read-only local review activity details filtered by type."""
        raw_filter = input(
            "Typfilter (all/message/task, leer/z = zurück): "
        ).strip()
        if not raw_filter or raw_filter.lower() == "z":
            return

        detail_view = build_review_activity_detail_view(
            self._get_all_message_suggestions(),
            self._get_all_task_suggestions(),
        )
        result = build_review_activity_type_filter(detail_view.all_items, raw_filter)
        self._section_title("Review-Aktivität nach Typ")

        if not result.is_valid:
            print(result.error_message or INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE)
            return

        print(f"Typfilter: {result.normalized_filter}")
        if not result.items:
            print("Keine lokalen Review-Details für diesen Typ gefunden.")
            return

        for item in result.items:
            self._print_review_activity_detail_item(item)

    def _show_review_activity_search(self) -> None:
        """Show read-only local review activity details matching a query."""
        raw_query = input(
            "Suchbegriff (mind. 2 Zeichen, leer/z = zurück): "
        ).strip()
        if not raw_query or raw_query.lower() == "z":
            return

        detail_view = build_review_activity_detail_view(
            self._get_all_message_suggestions(),
            self._get_all_task_suggestions(),
        )
        result = build_review_activity_search(detail_view.all_items, raw_query)
        self._section_title("Review-Aktivität durchsuchen")

        if not result.is_valid:
            print(result.error_message or INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE)
            return

        print(f"Suchbegriff: {result.normalized_query}")
        if not result.items:
            print("Keine lokalen Review-Details für diesen Suchbegriff gefunden.")
            return

        if result.was_limited:
            print(f"Treffer begrenzt: {len(result.items)} von {result.total_matches}")

        for item in result.items:
            self._print_review_activity_detail_item(item)

    def _build_review_batch_preview_items(
        self,
        message_suggestions: list[dict],
        task_suggestions: list[dict],
        messages_by_id: dict[int, dict],
    ) -> list[dict]:
        """Build visible review items with virtual IDs for batch preview only."""
        visible_items: list[dict] = []
        virtual_id = 1

        for suggestion in message_suggestions:
            message = messages_by_id.get(int(suggestion.get("message_id") or 0), {})
            sender = str(message.get("sender") or "Nachricht").strip()
            draft_text = str(suggestion.get("draft_text") or "").strip()
            visible_items.append(
                {
                    "id": virtual_id,
                    "suggestion_id": int(suggestion.get("id") or 0),
                    "suggestion_type": "message",
                    "sender": sender,
                    "title": f"Nachrichten-Vorschlag {suggestion.get('id')}",
                    "summary": draft_text,
                }
            )
            virtual_id += 1

        for suggestion in task_suggestions:
            title = str(suggestion.get("title") or "Aufgaben-Vorschlag").strip()
            visible_items.append(
                {
                    "id": virtual_id,
                    "suggestion_id": int(suggestion.get("id") or 0),
                    "suggestion_type": "task",
                    "title": f"Aufgaben-Vorschlag {suggestion.get('id')}: {title}",
                    "summary": title,
                }
            )
            virtual_id += 1

        return visible_items

    def _show_review_batch_selection_preview(
        self,
        message_suggestions: list[dict],
        task_suggestions: list[dict],
        messages_by_id: dict[int, dict],
    ) -> None:
        """Show a read-only batch selection preview without changing suggestions."""
        visible_items = self._build_review_batch_preview_items(
            message_suggestions,
            task_suggestions,
            messages_by_id,
        )
        if not visible_items:
            print("Keine Vorschläge für Batch-Auswahl vorhanden.")
            return

        self._section_title("Batch-Auswahl Vorschläge")
        for item in visible_items:
            print(f"{item['id']}. {item['title']}")

        raw_selection = input(
            "Batch-Auswahl eingeben (1,2,3 / all / none / z): "
        )
        parsed = parse_review_batch_selection(
            raw_selection,
            visible_ids=[int(item["id"]) for item in visible_items],
        )
        print(render_review_batch_selection_preview(parsed, visible_items))

        if parsed.status not in {"selected", "all"}:
            return

        print("Lokale Batch-Aktion wählen:")
        print("1. Nachrichten-Vorschläge lokal freigeben")
        print("2. Vorschläge lokal ablehnen")
        print("3. Aufgaben lokal erstellen")
        print("Enter/z. Abbrechen")
        action_choice = input("Aktion wählen: ").strip().lower()
        if not action_choice or action_choice == "z":
            print("Batch-Aktion wurde abgebrochen.")
            return

        action_mapping = {
            "1": ("approve_messages", REVIEW_BATCH_APPROVE_MESSAGES_TOKEN),
            "2": ("reject_suggestions", REVIEW_BATCH_REJECT_SUGGESTIONS_TOKEN),
            "3": ("create_tasks", REVIEW_BATCH_CREATE_TASKS_TOKEN),
        }
        selected_action = action_mapping.get(action_choice)
        if selected_action is None:
            print(INVALID_SELECTION)
            return

        action_type, expected_token = selected_action
        selected_id_set = set(parsed.selected_ids)
        selected_visible_items = [
            item
            for item in visible_items
            if int(item["id"]) in selected_id_set
        ]
        contains_mixed_types = (
            len({str(item["suggestion_type"]) for item in selected_visible_items}) > 1
        )

        smoke_result = run_safety_smoke()
        print(f"Safety Smoke: {'PASS' if smoke_result.passed else 'FAIL'}")
        print("Zum Ausführen tippe exakt:")
        print(expected_token)
        approval_token = input("Token: ")

        guard_result = check_review_batch_apply_allowed(
            action_type=action_type,
            selected_ids=parsed.selected_ids,
            visible_pending_ids=[int(item["id"]) for item in visible_items],
            preview_was_shown=True,
            approval_token=approval_token,
            scanner_smoke_passed=smoke_result.passed,
            external_actions_enabled=(
                config.ENABLE_REAL_EMAIL
                or config.ENABLE_REAL_WHATSAPP
                or config.ENABLE_REAL_SMS
                or config.ENABLE_REAL_WEATHER
                or config.ENABLE_REAL_MUSIC
            ),
            contains_mixed_suggestion_types=contains_mixed_types,
            contains_already_processed_suggestions=False,
        )
        if not guard_result.allowed:
            print(guard_result.message or "Batch-Aktion wurde nicht freigegeben.")
            for reason in guard_result.blocked_reasons:
                print(f"- {reason}")
            return

        apply_items = tuple(
            ReviewBatchApplyItem(
                virtual_id=int(item["id"]),
                suggestion_id=int(item["suggestion_id"]),
                suggestion_type=str(item["suggestion_type"]),  # type: ignore[arg-type]
            )
            for item in visible_items
        )
        result = apply_review_batch_selection(
            guard_result=guard_result,
            visible_items=apply_items,
            message_agent=self.message_agent,
            task_agent=self.task_agent,
        )
        print(result.message)
        for reason in result.blocked_reasons:
            print(f"- {reason}")
        if result.affected_ids:
            print(
                "Betroffene Vorschläge: "
                + ", ".join(str(item_id) for item_id in result.affected_ids)
            )
        if result.created_task_ids:
            print(
                "Erstellte lokale Aufgaben: "
                + ", ".join(str(task_id) for task_id in result.created_task_ids)
            )

    def _get_review_contact_candidates(self, messages: list[dict]) -> list[dict]:
        """Return local contact prompt candidates for unknown review senders."""
        candidates: list[dict] = []
        seen_names: set[str] = set()

        for message in messages:
            sender = str(message.get("sender") or "").strip()
            normalized_sender = normalize_contact_name(sender)
            if not sender or not normalized_sender or normalized_sender in seen_names:
                continue
            seen_names.add(normalized_sender)

            try:
                known_context = self.contact_context_repository.find_contact_by_normalized_name(normalized_sender)
            except sqlite3.OperationalError:
                known_context = None

            if known_context is not None:
                continue
            if is_contact_prompt_suppressed(
                display_name=sender,
                source_context="nachrichten_review",
                entries=self.contact_prompt_suppression_entries,
            ):
                continue

            candidate = should_create_contact_prompt_candidate(
                display_name=sender,
                contact_type="unbekannt",
                source_context="nachrichten_review",
            )
            if candidate.status == "allowed":
                candidates.append(
                    {
                        "display_name": candidate.display_name,
                        "normalized_name": candidate.normalized_name,
                        "question": candidate.question,
                    }
                )

        return candidates

    def _print_review_contact_candidate_preview(self, candidates: list[dict]) -> None:
        """Print contact context candidates as preview only."""
        if not candidates:
            return

        print("Kontakt-Kontext Hinweise:")
        for candidate in candidates:
            print(
                f"- Kontakt-Kontext möglich: {candidate['display_name']} "
                "ist noch unbekannt."
            )

    def _review_contact_candidates_loop(self, contact_candidates: list[dict]) -> None:
        """Review contact candidates with draft flow and optional local save."""
        while True:
            if not contact_candidates:
                print("Keine offenen Kontakt-Kontext-Hinweise vorhanden.")
                return

            print("Offene Kontakt-Kontext-Hinweise:")
            for index, candidate in enumerate(contact_candidates, start=1):
                print(f"{index}. {candidate['display_name']}")

            raw_index = input("Kontakt-Hinweis prüfen (leer/z = zurück): ").strip().lower()
            if not raw_index or raw_index == "z":
                return

            try:
                selected_index = int(raw_index)
            except ValueError:
                print("Ungültige Kontakt-Auswahl.")
                continue

            if selected_index < 1 or selected_index > len(contact_candidates):
                print("Kontakt-Hinweis wurde nicht gefunden.")
                continue

            candidate = contact_candidates[selected_index - 1]
            if not self._review_single_contact_candidate(candidate):
                return

            contact_candidates = [
                item
                for item in contact_candidates
                if self.contact_context_repository.find_contact_by_normalized_name(item["normalized_name"]) is None
                and not is_contact_prompt_suppressed(
                    display_name=item["display_name"],
                    source_context="nachrichten_review",
                    entries=self.contact_prompt_suppression_entries,
                )
            ]

    def _review_single_contact_candidate(self, candidate: dict) -> bool:
        """Apply contact draft input for one candidate. Returns False to leave loop."""
        prepared = prepare_contact_prompt_draft_flow(
            display_name=str(candidate["display_name"]),
            contact_type="unbekannt",
            source_context="nachrichten_review",
        )
        if prepared.rendered.question:
            print(prepared.rendered.question)

        raw_choice = input("Auswahl für Vorschau: ")
        result = apply_contact_prompt_draft_input(prepared, raw_choice)

        if result.status == "skipped":
            self.contact_prompt_suppression_entries = mark_contact_prompt_skipped(
                display_name=result.display_name,
                source_context=result.source_context,
                entries=self.contact_prompt_suppression_entries,
            )
            print("Kontakt-Hinweis wurde für diese Sitzung übersprungen.")
            return True

        if result.status == "invalid":
            print(result.error_message or INVALID_SELECTION)
            return True

        if result.status != "selected":
            return True

        self._section_title("Kontakt-Kontext Vorschau")
        print(f"Name: {result.display_name}")
        print(f"Kontaktart: {result.selected_contact_type}")
        print("Speicherung: Noch nicht")
        confirmation = input(
            "Soll dieser Kontakt-Kontext lokal gespeichert werden? "
            "Tippe SPEICHERN zum Speichern oder Enter zum Abbrechen: "
        ).strip()
        if confirmation != "SPEICHERN":
            print("Speichern wurde abgebrochen.")
            return True

        contact_id = f"review-{result.rendered.prompt_preview.context_preview.normalized_name.replace(' ', '-')}"
        try:
            self.contact_context_repository.create_contact_context(
                contact_id=contact_id,
                display_name=result.display_name,
                contact_type=result.selected_contact_type,
                source_context="nachrichten_review",
                user_approved_persistence=True,
                sensitivity_checked=True,
            )
        except ValueError as error:
            if str(error) == CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE:
                print(CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE)
                return True
            raise
        print("Kontakt-Kontext wurde lokal gespeichert.")
        return True

    def _generate_local_task_suggestions(self) -> None:
        generate_task_suggestions = getattr(self.message_agent, "generate_local_task_suggestions", None)
        if callable(generate_task_suggestions):
            generate_task_suggestions()

    def _get_pending_message_suggestions(self) -> list[dict]:
        getter = getattr(self.message_agent, "get_pending_suggestions", None)
        if callable(getter):
            return getter()
        return []

    def _get_pending_task_suggestions(self) -> list[dict]:
        getter = getattr(self.message_agent, "get_pending_task_suggestions", None)
        if callable(getter):
            return getter()
        return []

    def _get_messages_by_id(self) -> dict[int, dict]:
        messages = self.message_agent.get_messages()
        return {int(message["id"]): message for message in messages}

    def _review_message_suggestions(self, pending_suggestions: list[dict], messages: dict[int, dict]) -> bool:
        suggestion_id_raw = input("ID des Vorschlags prüfen (leer = zurück): ").strip()
        if suggestion_id_raw.lower() == "z":
            return False
        if not suggestion_id_raw:
            return False

        try:
            suggestion_id = int(suggestion_id_raw)
        except ValueError:
            print("Ungültige Vorschlags-ID.")
            return True

        selected = next(
            (item for item in pending_suggestions if item["id"] == suggestion_id),
            None,
        )
        if selected is None:
            print("Vorschlag wurde nicht gefunden.")
            return True

        self._print_single_suggestion_detail(
            selected,
            messages.get(int(selected["message_id"]), {}),
        )
        calendar_suggestions = self.calendar_agent.generate_calendar_suggestions_for_message(
            message_id=int(selected["message_id"])
        )
        self._print_calendar_slots(calendar_suggestions)

        action = input(
            "Aktion: a=lokal freigeben, r=ablehnen, e=Text bearbeiten, "
            "k=Kalender-Slot auswählen, s=später, z=zurück: "
        ).strip().lower()
        return self._handle_review_action(selected, action, calendar_suggestions)

    def _print_task_suggestions(self, suggestions: list[dict], messages: dict[int, dict]) -> None:
        print("Offene Aufgaben-Vorschläge:")
        for suggestion in suggestions:
            message = messages.get(int(suggestion["message_id"]), {})
            sender = message.get("sender", "Unbekannt")
            print(
                f"- Vorschlags-ID: {suggestion['id']} | "
                f"Nachrichten-ID: {suggestion['message_id']} | "
                f"Nachricht von: {sender} | "
                f"Titel: {suggestion['title']} | "
                f"Priorität: {suggestion.get('priority') or 'normal'} | "
                f"Status: {suggestion.get('status')}"
            )

    def _review_message_suggestions_loop(
        self,
        pending_suggestions: list[dict],
        messages: dict[int, dict],
    ) -> None:
        """Review message suggestions until user goes back."""
        while True:
            if not pending_suggestions:
                pending_suggestions = self._get_pending_message_suggestions()
            if not pending_suggestions:
                print("Keine offenen Nachrichten-Vorschläge vorhanden.")
                return
            self._print_reviewable_suggestions(pending_suggestions, messages)
            if not self._review_message_suggestions(pending_suggestions, messages):
                return
            pending_suggestions = self._get_pending_message_suggestions()

    def _review_task_suggestions_loop(
        self,
        pending_task_suggestions: list[dict],
        messages: dict[int, dict],
    ) -> None:
        """Review task suggestions until user goes back."""
        while True:
            if not pending_task_suggestions:
                pending_task_suggestions = self._get_pending_task_suggestions()
            if not pending_task_suggestions:
                print("Keine offenen Aufgaben-Vorschläge vorhanden.")
                return
            self._print_task_suggestions(pending_task_suggestions, messages)
            if not self._review_task_suggestions(pending_task_suggestions, messages):
                return
            pending_task_suggestions = self._get_pending_task_suggestions()

    def _print_task_suggestion_detail(self, suggestion: dict, message: dict) -> None:
        print(f"Aufgaben-Vorschlags-ID: {suggestion['id']}")
        print(f"Nachrichten-ID: {suggestion['message_id']}")
        print(f"Absender: {message.get('sender', 'Unbekannt')}")
        print(f"Titel: {suggestion['title']}")
        print(f"Kategorie: {suggestion.get('category') or 'other'}")
        print(f"Fälligkeitsdatum: {suggestion.get('due_date') or 'kein Datum'}")
        print(f"Priorität: {suggestion.get('priority') or 'normal'}")
        print(f"Status: {suggestion.get('status')}")
        print(f"Notizen: {suggestion.get('notes') or ''}")
        contact_snapshot = self._build_task_contact_snapshot_for_message(message)
        if contact_snapshot:
            print(contact_snapshot.replace("\n", " | "))

    def _build_task_contact_snapshot_for_message(self, message: dict) -> str | None:
        """Build a safe local contact snapshot for task preview/notes."""
        sender = str(message.get("sender") or "").strip()
        if not sender:
            return None

        try:
            contact = self.contact_context_repository.find_contact_by_normalized_name(sender)
        except sqlite3.OperationalError:
            return None

        if contact is None:
            return None

        lines = [
            "Kontakt-Snapshot:",
            f"Quelle: {contact['display_name']}",
            f"Kontaktart: {contact.get('contact_type') or 'unbekannt'}",
        ]
        relationship = (contact.get("relationship_context") or "").strip()
        if (
            relationship
            and int(contact.get("user_approved_persistence") or 0) == 1
            and int(contact.get("sensitivity_checked") or 0) == 1
        ):
            lines.append(f"Beziehungskontext: {relationship}")
        return "\n".join(lines)

    def _merge_task_notes_with_contact_snapshot(self, notes: str | None, message: dict) -> str | None:
        """Append contact snapshot to local task notes when available."""
        snapshot = self._build_task_contact_snapshot_for_message(message)
        if not snapshot:
            return notes

        base_notes = (notes or "").strip()
        if not base_notes:
            return snapshot
        if "Kontakt-Snapshot:" in base_notes:
            return base_notes
        return f"{base_notes}\n\n{snapshot}"

    def _review_task_suggestions(self, pending_task_suggestions: list[dict], messages: dict[int, dict]) -> bool:
        suggestion_id_raw = input("ID des Aufgaben-Vorschlags prüfen (leer = weiter/zurück): ").strip()
        if suggestion_id_raw.lower() == "z":
            return False
        if not suggestion_id_raw:
            return False

        try:
            suggestion_id = int(suggestion_id_raw)
        except ValueError:
            print("Ungültige Aufgaben-Vorschlags-ID.")
            return True

        selected = next(
            (item for item in pending_task_suggestions if item["id"] == suggestion_id),
            None,
        )
        if selected is None:
            print("Aufgaben-Vorschlag wurde nicht gefunden.")
            return True

        self._print_task_suggestion_detail(selected, messages.get(int(selected["message_id"]), {}))
        action = input(
            "Aktion: a=lokal als Aufgabe erstellen, r=ablehnen, e=bearbeiten, "
            "s=später, z=zurück: "
        ).strip().lower()
        return self._handle_task_suggestion_action(selected, action)

    def _handle_task_suggestion_action(self, suggestion: dict, action: str) -> bool:
        suggestion_id = int(suggestion["id"])

        def _input(prompt: str) -> str:
            try:
                return input(prompt).strip()
            except StopIteration:
                return ""

        if action == "a":
            if not self._is_task_suggestion_convertible(suggestion):
                print("Aufgaben-Vorschlag wurde bereits in eine lokale Aufgabe umgewandelt.")
                return False

            created_task = self.task_agent.create_task(
                title=str(suggestion["title"]),
                category=str(suggestion.get("category") or "other"),
                due_date=suggestion.get("due_date"),
                notes=self._merge_task_notes_with_contact_snapshot(
                    notes=suggestion.get("notes"),
                    message=self._get_messages_by_id().get(int(suggestion["message_id"]), {}),
                ),
                priority=suggestion.get("priority") or "normal",
            )
            mark = getattr(self.message_agent, "mark_task_suggestion_converted", None)
            if callable(mark):
                mark(suggestion_id=suggestion_id, created_task_id=int(created_task["id"]))
            print("Aufgaben-Vorschlag wurde als lokale Aufgabe erstellt.")
            return True

        if action == "r":
            reject = getattr(self.message_agent, "reject_task_suggestion", None)
            if callable(reject):
                reject(suggestion_id=suggestion_id)
            print("Aufgaben-Vorschlag wurde abgelehnt.")
            return True

        if action == "e":
            title = _input("Neuer Titel (leer = behalten): ")
            category = _input("Neue Kategorie (leer = behalten): ")
            due_date = _input("Neues Fälligkeitsdatum (YYYY-MM-DD, leer = behalten): ")
            notes = _input("Neue Notizen (leer = behalten): ")
            priority = _input("Neue Priorität (low/normal/high/urgent, leer = behalten): ")

            if not (title or category or due_date or notes or priority):
                print("Ein Aufgaben-Vorschlag braucht einen Titel.")
                return False

            edit = getattr(self.message_agent, "edit_task_suggestion", None)
            if callable(edit):
                try:
                    edit(
                        suggestion_id=suggestion_id,
                        title=(title or None),
                        category=(category or None),
                        due_date=(due_date or None),
                        notes=(notes or None),
                        priority=(priority or None),
                    )
                except ValueError as error:
                    print(str(error))
                    return False
            print("Aufgaben-Vorschlag wurde lokal bearbeitet.")
            return False

        if action == "s":
            print("Aufgaben-Vorschlag bleibt offen.")
            return False

        if action == "z":
            return False

        print(INVALID_SELECTION)
        return True

    def _is_task_suggestion_convertible(self, suggestion: dict) -> bool:
        suggestion_id = int(suggestion["id"])
        status = str(suggestion.get("status", "")).lower()
        if status not in {"pending", "edited"}:
            return False

        if suggestion.get("created_task_id"):
            return False

        return any(
            item["id"] == suggestion_id
            for item in self._get_pending_task_suggestions()
        )

    def _print_reviewable_suggestions(self, suggestions: list[dict], messages: dict[int, dict]) -> None:
        """Print compact overview for suggestions that still need local review."""
        print("Reviewbare Vorschläge:")
        for suggestion in suggestions:
            message = messages.get(int(suggestion["message_id"]), {})
            sender = message.get("sender", "Unbekannt")
            print(
                f"- [{suggestion['id']}] Nachricht {suggestion['message_id']} ({sender}) | "
                f"Status: {suggestion.get('status')}"
            )

    def _print_single_suggestion_detail(self, suggestion: dict, message: dict) -> None:
        """Print detailed info for one selected suggestion."""
        print(f"Vorschlags-ID: {suggestion['id']}")
        print(f"Nachrichten-ID: {suggestion['message_id']}")
        print(f"Absender: {message.get('sender', 'Unbekannt')}")
        print(f"Status: {suggestion.get('status')}")
        print(f"Vorschlagstext: {suggestion.get('draft_text')}")

    def _print_calendar_slots(self, slots: list[dict]) -> None:
        """Print all local calendar slot suggestions."""
        if not slots:
            print("Keine Kalender-Slots verfügbar.")
            return

        print("Mögliche lokale Kalender-Slots:")
        for slot in slots:
            print(f"Kalender-Slot-ID: {slot['id']}")
            print(f"Datum: {slot['slot_date']}")
            print(f"Zeit: {slot['start']} bis {slot['end']}")
            print(f"Status: {slot['status']}")

    def _handle_review_action(
        self,
        suggestion: dict,
        action: str,
        calendar_suggestions: list[dict],
    ) -> bool:
        """Execute one local review action. Returns False when user wants to leave."""
        suggestion_id = int(suggestion["id"])

        if action == "a":
            self.message_agent.approve_suggestion(suggestion_id)
            print("Vorschlag wurde lokal freigegeben. Es wurde nichts gesendet.")
            return True
        if action == "r":
            self.message_agent.reject_suggestion(suggestion_id)
            print("Vorschlag wurde abgelehnt.")
            return True
        if action == "e":
            new_text = input("Neuer Vorschlagstext: ").strip()
            if not new_text:
                print("Ein Vorschlag braucht Text.")
                return True
            self.message_agent.edit_suggestion(suggestion_id, new_text)
            print("Vorschlag wurde lokal bearbeitet.")
            return True
        if action == "k":
            if not calendar_suggestions:
                print("Keine Kalender-Slots verfügbar.")
                return True
            slot_id_raw = input("ID des Kalender-Slots auswählen: ").strip()
            try:
                slot_id = int(slot_id_raw)
            except ValueError:
                print("Ungültige Kalender-Slot-ID.")
                return True

            selected_slot = next(
                (slot for slot in calendar_suggestions if slot["id"] == slot_id),
                None,
            )
            if selected_slot is None:
                selected_slot = self.calendar_agent.get_calendar_suggestion_by_id(slot_id)
                if selected_slot is None:
                    print("Kalender-Slot wurde nicht gefunden.")
                    return True
                if int(selected_slot.get("message_id", 0)) != int(suggestion["message_id"]):
                    print("Kalender-Slot gehört nicht zu diesem Vorschlag.")
                    return True

            updated_slot = self.calendar_agent.select_calendar_suggestion(slot_id)
            if updated_slot is None:
                print("Kalender-Slot wurde nicht gefunden.")
                return True
            current_text = str(suggestion.get("draft_text") or "")
            appended = self._format_calendar_slot_text(updated_slot)
            new_draft = self._merge_calendar_slot_into_draft(current_text, appended)
            self.message_agent.edit_suggestion(suggestion_id, new_draft)
            print(
                "Kalender-Slot wurde lokal mit dem Vorschlag verbunden. "
                "Es wurde kein echter Termin erstellt."
            )
            return True
        if action == "s":
            print("Vorschlag bleibt offen.")
            return True
        if action == "z":
            return False

        print(INVALID_SELECTION)
        return True

    def _quick_add_task_from_input(self) -> None:
        """Create a local task from a one-line preview-confirmed input."""
        raw_text = input("Schnelle Aufgabe (z. B. zahnarzt anrufen !hoch @morgen): ").strip()
        parsed = parse_quick_add_task(raw_text)
        if not parsed.valid:
            print(parsed.error)
            return

        self._section_title("Quick-Add Vorschau")
        print(f"Titel: {parsed.title}")
        print("Kategorie: sonstiges")
        print(f"Priorität: {parsed.priority}")
        print(f"Fällig: {parsed.due_date or 'kein Datum'}")
        if parsed.recurrence:
            print(f"Wiederholung: {parsed.recurrence}")
        confirmation = input("Aufgabe so lokal anlegen? (j/n): ").strip().lower()
        if confirmation != "j":
            print("Schnellerfassung wurde abgebrochen.")
            return

        try:
            self.task_agent.create_task(
                title=parsed.title,
                category="sonstiges",
                due_date=parsed.due_date,
                notes=None,
                priority=parsed.priority,
                recurrence=parsed.recurrence,
            )
        except ValueError as error:
            print(str(error))
            return

        print("Aufgabe wurde schnell erstellt.")

    def _create_task_from_input(self) -> None:
        """Collect task input and create a local task."""
        title = input("Titel: ").strip()
        if not title:
            print("Eine Aufgabe braucht mindestens einen Titel.")
            return

        category = input(
            "Kategorie (privat/arbeit/kunde/familie/sonstiges, leer = sonstiges): "
        ).strip()
        due_date = input("Fälligkeitsdatum (YYYY-MM-DD, leer = kein Datum): ").strip()
        notes = input("Notizen (optional): ").strip()
        priority = input(
            "Priorität (low/normal/high/urgent, leer = normal): "
        ).strip()
        recurrence = input(
            "Wiederholung (taeglich/woechentlich/monatlich, leer = keine): "
        ).strip()

        # Create local task only; no external services are used here.
        try:
            self.task_agent.create_task(
                title=title,
                category=category or None,
                due_date=due_date or None,
                notes=notes or None,
                priority=priority or "normal",
                recurrence=recurrence or None,
            )
        except ValueError as error:
            print(str(error))
            return
        print("Aufgabe wurde erstellt.")

    def _edit_task_from_input(self) -> None:
        """Collect one id and optional updates for local task editing."""
        task_id_raw = input("ID der Aufgabe: ").strip()
        try:
            task_id = int(task_id_raw)
        except ValueError:
            print("Ungültige Aufgaben-ID.")
            return

        task = self.task_agent.get_task_by_id(task_id)
        if task is None:
            print("Aufgabe wurde nicht gefunden.")
            return

        print(f"Aktuelle Aufgabe: [{task['id']}] {task['title']} ({task.get('category') or 'sonstiges'})")

        title = input(f"Titel [{task['title']}]: ").strip()
        category = input(f"Kategorie [{task.get('category') or 'sonstiges'}]: ").strip()
        due_date = input(f"Fälligkeitsdatum [{task.get('due_date') or 'kein Datum'}]: ").strip()
        notes = input(f"Notizen [{task.get('notes') or 'keine'}]: ").strip()
        priority = input(f"Priorität [{task.get('priority') or 'normal'}]: ").strip()
        recurrence = input(f"Wiederholung [{task.get('recurrence') or 'keine'}]: ").strip()

        try:
            updated = self.task_agent.edit_task(
                task_id=task_id,
                title=title or None,
                category=category or None,
                due_date=due_date or None,
                notes=notes or None,
                priority=priority or None,
                recurrence=recurrence or None,
            )
        except ValueError as error:
            print(str(error))
            return
        if updated is None:
            print("Aufgabe wurde nicht gefunden.")
            return
        print("Aufgabe wurde aktualisiert.")

    def _print_task_list(self, tasks: List[Dict[str, Any]], empty_message: str) -> None:
        """Print a compact local task list."""
        if not tasks:
            print(empty_message)
            return
        for task in tasks:
            category = task.get("category") or "sonstiges"
            status = task.get("status") or "open"
            due_date = task.get("due_date") or "kein Datum"
            priority = task.get("priority") or "normal"
            print(
                f"- [{task['id']}] {task['title']} ({category}) | "
                f"Status: {status} | Fällig: {due_date} | Priorität: {priority}"
            )

    def _mark_task_done_from_input(self) -> None:
        """Collect one task id and mark it done locally."""
        task_id_raw = input("ID der Aufgabe: ").strip()
        try:
            task_id = int(task_id_raw)
        except ValueError:
            print("Ungültige Aufgaben-ID.")
            return

        task = self.task_agent.get_task_by_id(task_id)
        if task is None:
            print("Aufgabe wurde nicht gefunden.")
            return

        self.task_agent.mark_task_done(task_id)
        print("Aufgabe wurde als erledigt markiert.")

    def _search_or_filter_tasks_from_input(self) -> None:
        """Collect local search and filter values and print matching tasks."""
        query = input("Suchtext (leer = keine Suche): ").strip()
        status = input("Status filtern (open/done/archived, leer = egal): ").strip()
        category = input("Kategorie filtern (leer = egal): ").strip()
        due_date = input("Fälligkeitsdatum filtern (YYYY-MM-DD, leer = egal): ").strip()

        if query:
            tasks = self.task_agent.search_tasks(
                query=query,
                status=status or None,
                category=category or None,
            )
        else:
            tasks = self.task_agent.filter_tasks(
                status=status or None,
                category=category or None,
                due_date=due_date or None,
            )
        self._print_task_list(tasks, "Keine passenden Aufgaben gefunden.")

    def _archive_task_from_input(self) -> None:
        """Collect one task id and archive it locally."""
        task_id_raw = input("ID der Aufgabe zum Archivieren: ").strip()
        try:
            task_id = int(task_id_raw)
        except ValueError:
            print("Ungültige Aufgaben-ID.")
            return

        if self.task_agent.get_task_by_id(task_id) is None:
            print("Aufgabe wurde nicht gefunden.")
            return

        archived = self.task_agent.archive_task(task_id)
        if archived is None:
            print("Aufgabe wurde nicht gefunden.")
            return
        print("Aufgabe wurde archiviert.")

    def _collect_all_tasks_for_markdown_export(self) -> List[Dict[str, Any]]:
        """Collect open, done and archived tasks for deterministic local export."""
        tasks = []
        tasks.extend(self.task_agent.get_tasks_by_status("open"))
        tasks.extend(self.task_agent.get_tasks_by_status("done"))
        tasks.extend(self.task_agent.get_tasks_by_status("archived"))
        return tasks

    def _task_export_base_dir(self) -> Path:
        """Return a safe local base directory for exports.

        If the configured database is the default local_data database,
        keep project-root local behavior (`local_data/exports`).
        For injected temporary databases (e.g. tests), use the DB folder parent.
        """
        db_path = Path(self.task_agent.db_path).resolve()
        if db_path.name == "friday.db" and db_path.parent.name == "local_data":
            return db_path.parent.parent
        return db_path.parent

    def _export_tasks_to_markdown(self) -> None:
        """Export all task statuses to a local markdown file."""
        try:
            tasks = self._collect_all_tasks_for_markdown_export()
            output_path = export_tasks_markdown_to_default_path(
                base_dir=self._task_export_base_dir(),
                tasks=tasks,
            )
            print(f"Aufgaben wurden lokal exportiert: {output_path}")
            return
        except Exception:
            print("Aufgaben konnten nicht exportiert werden.")
            return

    def _collect_obsidian_task_records(self) -> list[dict]:
        """Collect task records for local Obsidian previews."""
        tasks_by_id: dict[int, dict] = {}
        status_getter = getattr(self.task_agent, "get_tasks_by_status", None)
        if status_getter is not None:
            for status in ("open", "done", "archived"):
                for task in status_getter(status):
                    tasks_by_id[int(task["id"])] = task

        if not tasks_by_id:
            open_getter = getattr(self.task_agent, "get_open_tasks", None)
            if open_getter is not None:
                for task in open_getter():
                    tasks_by_id[int(task["id"])] = task

        return list(tasks_by_id.values())

    def _collect_obsidian_contact_records(self) -> list[dict]:
        """Collect contact records for local Obsidian previews."""
        try:
            return list(self.contact_context_repository.list_contact_contexts())
        except (AttributeError, sqlite3.Error):
            return []

    def show_obsidian_brain_preview(self) -> None:
        """Show local Obsidian Brain previews and guarded write status."""
        self._section_title("Obsidian Brain Preview")

        brain_preview = build_obsidian_brain_preview(
            tasks=self._collect_obsidian_task_records(),
            contacts=self._collect_obsidian_contact_records(),
        )
        note_previews = brain_preview.all_previews()

        print("Friday zeigt hier nur lokale Obsidian-Notiz-Previews.")
        print("Standardmäßig wird nichts in ein Vault geschrieben.")
        print()
        print(f"Aufgaben-Notizen: {len(brain_preview.task_previews)}")
        print(f"Kontakt-Notizen: {len(brain_preview.contact_previews)}")
        print(f"Projekt-Notizen: {len(brain_preview.project_previews)}")
        print()

        if not note_previews:
            print("Keine lokalen Daten für Obsidian-Previews gefunden.")
            return

        print("Vorschau-Dateien:")
        for note in note_previews[:10]:
            print(f"- {note.relative_path}")
        if len(note_previews) > 10:
            print(f"- ... und {len(note_previews) - 10} weitere")

        print()
        if not config.OBSIDIAN_VAULT_PATH or not config.OBSIDIAN_WRITE_ENABLED:
            print("Obsidian Write ist deaktiviert. Es wurde nichts geschrieben.")
            print("Zum Schreiben braucht Friday einen Vault-Pfad, aktiviertes Write-Flag")
            print(f"und den exakten Bestätigungstoken: {OBSIDIAN_WRITE_TOKEN}")
            return

        confirmation = input(
            f"Tippe {OBSIDIAN_WRITE_TOKEN} zum lokalen Schreiben oder Enter zum Abbrechen: "
        ).strip()
        written_count = 0
        blocked_count = 0
        for note in note_previews:
            result = write_obsidian_note_with_approval(
                vault_path=Path(config.OBSIDIAN_VAULT_PATH),
                allowed_subdir=config.OBSIDIAN_ALLOWED_SUBDIR,
                preview=note,
                confirmation=confirmation,
                write_enabled=config.OBSIDIAN_WRITE_ENABLED,
            )
            if result.persisted:
                written_count += 1
            else:
                blocked_count += 1

        if written_count:
            print(f"{written_count} Obsidian-Notizen wurden lokal geschrieben.")
        if blocked_count:
            print(f"{blocked_count} Obsidian-Notizen wurden nicht geschrieben.")

    def _backup_restore_base_dir(self) -> Path:
        """Return the local base directory used for backup/restore previews."""
        db_path_raw = getattr(self.task_agent, "db_path", None)
        if db_path_raw is None:
            return Path.cwd()

        db_path = Path(db_path_raw).resolve()
        if db_path.name == "friday.db" and db_path.parent.name == "local_data":
            return db_path.parent.parent
        return db_path.parent

    def _show_backup_preview(self) -> None:
        """Show a local backup preview without writing a backup."""
        self._section_title("Backup-Vorschau")
        preview = build_backup_preview(self._backup_restore_base_dir())
        print(f"Geplanter Zielordner: {preview.planned_backup_root}")
        print("Es wurde nichts geschrieben.")
        print("Sektionen:")
        for section in preview.sections:
            path = section.path or "-"
            print(
                f"- {section.name}: {section.status} | "
                f"Dateien: {section.file_count} | Pfad: {path}"
            )

    def _show_local_data_export_preview(self) -> None:
        """Show a local data export preview without creating export files."""
        self._section_title("Lokaler Datenexport Vorschau")
        preview = build_local_data_export_preview(
            project_root=self._backup_restore_base_dir(),
            local_data_dir=self._backup_restore_base_dir() / "local_data",
        )
        print(f"Geplanter Zielordner: {preview.target_root}")
        print("Es wurde kein Export erstellt.")
        print("Es wurde kein Token abgefragt.")
        print("Externe Aktionen: deaktiviert.")
        print("Geplante Bereiche:")
        for section in preview.sections:
            print(
                f"- {section.name}: {section.file_format} | "
                f"sensible Details ausgeschlossen: {section.sensitive_details_excluded}"
            )
        print("Ausgeschlossene Inhalte:")
        for item in preview.excluded_items:
            print(f"- {item}")

    def _collect_tasks_for_local_data_export(self) -> tuple[dict, ...]:
        """Collect local tasks for export without using external services."""
        collected: list[dict] = []
        seen_ids: set[object] = set()

        def _append_tasks(tasks: list[dict]) -> None:
            for task in tasks:
                task_id = task.get("id")
                if task_id in seen_ids:
                    continue
                seen_ids.add(task_id)
                collected.append(task)

        get_open_tasks = getattr(self.task_agent, "get_open_tasks", None)
        if callable(get_open_tasks):
            _append_tasks(list(get_open_tasks()))

        get_tasks_by_status = getattr(self.task_agent, "get_tasks_by_status", None)
        if callable(get_tasks_by_status):
            for status in ("done", "archived"):
                _append_tasks(list(get_tasks_by_status(status)))

        return tuple(collected)

    def _build_local_data_export_payload(self, scanner_smoke_passed: bool) -> LocalDataExportPayload:
        """Build explicit local data payload for the guarded export writer."""
        contact_contexts = []
        list_contact_contexts = getattr(self.contact_context_repository, "list_contact_contexts", None)
        if callable(list_contact_contexts):
            contact_contexts = list(list_contact_contexts())

        review_suggestions: list[dict] = []
        get_pending_suggestions = getattr(self.message_agent, "get_pending_suggestions", None)
        if callable(get_pending_suggestions):
            review_suggestions.extend(list(get_pending_suggestions()))

        get_pending_task_suggestions = getattr(self.message_agent, "get_pending_task_suggestions", None)
        if callable(get_pending_task_suggestions):
            review_suggestions.extend(list(get_pending_task_suggestions()))

        return LocalDataExportPayload(
            tasks=self._collect_tasks_for_local_data_export(),
            contact_contexts=tuple(contact_contexts),
            review_suggestions=tuple(review_suggestions),
            safety_status={
                "scanner_smoke_passed": scanner_smoke_passed,
                "external_actions_enabled": False,
                "real_email_enabled": config.ENABLE_REAL_EMAIL,
                "real_whatsapp_enabled": config.ENABLE_REAL_WHATSAPP,
                "real_sms_enabled": config.ENABLE_REAL_SMS,
                "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
                "real_weather_enabled": config.ENABLE_REAL_WEATHER,
                "real_music_enabled": config.ENABLE_REAL_MUSIC,
                "requires_user_approval": config.REQUIRE_USER_APPROVAL,
            },
        )

    def _create_local_data_export_from_input(self) -> None:
        """Create a guarded local data export only after hard approval."""
        self._show_local_data_export_preview()
        base_dir = self._backup_restore_base_dir()
        preview = build_local_data_export_preview(
            project_root=base_dir,
            local_data_dir=base_dir / "local_data",
        )

        print("Vor dem Export wird der lokale Safety Smoke geprüft.")
        smoke_result = run_safety_smoke()
        print(f"Safety Smoke: {'PASS' if smoke_result.passed else 'FAIL'}")
        if not smoke_result.passed:
            print("Datenexport wurde blockiert, weil der Safety Smoke nicht erfolgreich war.")
            return

        confirmation = input(
            f"Tippe {LOCAL_DATA_EXPORT_APPROVAL_TOKEN} zum Exportieren oder Enter zum Abbrechen: "
        )
        if not confirmation:
            print("Datenexport wurde abgebrochen.")
            return

        payload = self._build_local_data_export_payload(scanner_smoke_passed=smoke_result.passed)
        result = write_local_data_export(
            preview=preview,
            approval_token=confirmation,
            scanner_smoke_passed=smoke_result.passed,
            project_root=base_dir,
            payload=payload,
        )

        print(result.message)
        if result.target_path:
            print(f"Ziel: {result.target_path}")
        if result.written_files:
            print("Geschriebene Dateien:")
            for written_file in result.written_files:
                print(f"- {written_file.relative_path}")
        if result.blocked_reasons:
            print("Blockiert wegen:")
            for reason in result.blocked_reasons:
                print(f"- {reason}")

    def _review_local_data_import_from_input(self) -> None:
        """Review a local data export folder without importing or restoring anything."""
        export_path_raw = input("Export-Ordner für Import-Prüfung (leer/z = zurück): ").strip()
        if not export_path_raw or export_path_raw.lower() == "z":
            return

        self._section_title("Lokalen Datenimport prüfen")
        base_dir = self._backup_restore_base_dir()
        export_root = Path(export_path_raw)
        if not export_root.is_absolute():
            export_root = base_dir / export_root

        manifest_result = read_local_data_import_manifest(
            manifest_path=export_root / "manifest.json",
            project_root=base_dir,
        )
        dry_run = build_local_data_import_dry_run(
            export_root=export_root,
            manifest_result=manifest_result,
            project_root=base_dir,
        )

        print("Import-Review wurde read-only geprüft.")
        print("Es wurde nichts importiert.")
        print("Es wurde nichts wiederhergestellt.")
        print("Es wurde nichts geschrieben.")
        print(manifest_result.message)
        print(dry_run.message)
        print(f"Export-Ordner: {export_root}")

        if manifest_result.summary is not None:
            print("Manifest:")
            print(f"- Typ: {manifest_result.summary.export_type}")
            print(f"- Bereiche: {', '.join(manifest_result.summary.sections)}")
            print(f"- Dateien: {len(manifest_result.summary.written_files)}")

        if dry_run.sections_checked:
            print("Geprüfte Dateien:")
            for section in dry_run.sections_checked:
                print(f"- {section.relative_path}: {section.status}")

        blocked_reasons = tuple(
            dict.fromkeys((*manifest_result.blocked_reasons, *dry_run.blocked_reasons))
        )
        if blocked_reasons:
            print("Blockiert wegen:")
            for reason in blocked_reasons:
                print(f"- {reason}")

        if dry_run.warnings:
            print("Warnungen:")
            for warning in dry_run.warnings:
                print(f"- {warning}")

    def _show_local_data_import_apply_preview_from_input(self) -> None:
        """Show a read-only apply preview for local data import without applying it."""
        export_path_raw = input("Export-Ordner fuer Apply-Vorschau (leer/z = zurueck): ").strip()
        if not export_path_raw or export_path_raw.lower() == "z":
            return

        self._section_title("Import-Apply-Vorschau")
        base_dir = self._backup_restore_base_dir()
        export_root = Path(export_path_raw)
        if not export_root.is_absolute():
            export_root = base_dir / export_root

        manifest_result = read_local_data_import_manifest(
            manifest_path=export_root / "manifest.json",
            project_root=base_dir,
        )
        dry_run = build_local_data_import_dry_run(
            export_root=export_root,
            manifest_result=manifest_result,
            project_root=base_dir,
        )
        preview = build_local_data_import_apply_preview(
            manifest_result=manifest_result,
            dry_run_result=dry_run,
            backup_ready=False,
        )

        print("Import-Apply-Vorschau wurde read-only erstellt.")
        print("Es wurde nichts importiert.")
        print("Es wurde nichts wiederhergestellt.")
        print("Es wurde nichts geschrieben.")
        print("Import anwenden ist noch nicht freigegeben.")
        print("Es wurde kein Token abgefragt.")
        print(preview.message)
        print(f"Export-Ordner: {preview.export_root}")
        print(f"Status: {preview.status}")
        print(f"Backup-Schutz bereit: {preview.backup_ready}")

        if preview.sections:
            print("Geplante Sektionen:")
            for section in preview.sections:
                print(f"- {section.name}: {section.planned_count} | {section.action}")

        if preview.blocked_reasons:
            print("Blockiert wegen:")
            for reason in preview.blocked_reasons:
                print(f"- {reason}")

        if preview.warnings:
            print("Warnungen:")
            for warning in preview.warnings:
                print(f"- {warning}")

    def _local_data_import_apply_backup_ready(self) -> bool:
        """Return whether a local backup marker exists before import apply."""
        backups_dir = self._backup_restore_base_dir() / "local_data" / "backups"
        if not backups_dir.exists() or not backups_dir.is_dir():
            return False
        return any(backups_dir.iterdir())

    def _local_database_path(self) -> Path:
        """Return the active local SQLite database path for guarded imports."""
        db_path_raw = getattr(self.task_agent, "db_path", None)
        if db_path_raw is not None:
            return Path(db_path_raw)
        return self._backup_restore_base_dir() / "local_data" / "friday.db"

    def _apply_local_data_import_from_input(self) -> None:
        """Apply a local data import only after guard, smoke PASS and hard token."""
        export_path_raw = input("Export-Ordner fuer Import-Apply (leer/z = zurueck): ").strip()
        if not export_path_raw or export_path_raw.lower() == "z":
            return

        self._section_title("Import nach Freigabe anwenden")
        base_dir = self._backup_restore_base_dir()
        export_root = Path(export_path_raw)
        if not export_root.is_absolute():
            export_root = base_dir / export_root

        manifest_result = read_local_data_import_manifest(
            manifest_path=export_root / "manifest.json",
            project_root=base_dir,
        )
        dry_run = build_local_data_import_dry_run(
            export_root=export_root,
            manifest_result=manifest_result,
            project_root=base_dir,
        )
        preview = build_local_data_import_apply_preview(
            manifest_result=manifest_result,
            dry_run_result=dry_run,
            backup_ready=self._local_data_import_apply_backup_ready(),
        )

        print(preview.message)
        print(f"Export-Ordner: {preview.export_root}")
        print(f"Status: {preview.status}")
        print(f"Backup-Schutz bereit: {preview.backup_ready}")
        if preview.blocked_reasons:
            print("Blockiert wegen:")
            for reason in preview.blocked_reasons:
                print(f"- {reason}")

        if not preview.allowed_to_request_token:
            print("Import-Apply wurde blockiert. Es wurde kein Token abgefragt.")
            return

        print("Vor dem Import-Apply wird der lokale Safety Smoke geprüft.")
        smoke_result = run_safety_smoke()
        print(f"Safety Smoke: {'PASS' if smoke_result.passed else 'FAIL'}")
        if not smoke_result.passed:
            print("Import-Apply wurde blockiert, weil der Safety Smoke nicht erfolgreich war.")
            return

        confirmation = input(
            f"Tippe {LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN} zum Anwenden oder Enter zum Abbrechen: "
        ).strip()
        if not confirmation:
            print("Import-Apply wurde abgebrochen.")
            return

        guard = check_local_data_import_apply_write_allowed(
            preview=preview,
            approval_token=confirmation,
            scanner_smoke_passed=smoke_result.passed,
        )
        if not guard.allowed:
            print(guard.message or "Import-Apply wurde nicht freigegeben.")
            if guard.blocked_reasons:
                print("Blockiert wegen:")
                for reason in guard.blocked_reasons:
                    print(f"- {reason}")
            return

        result = apply_local_data_import(
            guard_result=guard,
            export_root=export_root,
            db_path=self._local_database_path(),
        )
        print(result.message)
        print(f"Erstellte Aufgaben: {result.created_counts.tasks}")
        print(f"Erstellte Kontakt-Kontexte: {result.created_counts.contact_contexts}")
        print(f"Erstellte Review-Vorschläge: {result.created_counts.review_suggestions}")
        print(f"Uebersprungene Aufgaben: {result.skipped_counts.tasks}")
        print(f"Rollback verwendet: {result.rollback_used}")
        if result.blocked_reasons:
            print("Blockiert wegen:")
            for reason in result.blocked_reasons:
                print(f"- {reason}")

    def _restore_dry_run_from_input(self) -> None:
        """Run a local restore dry-run without restoring files."""
        backup_path_raw = input("Backup-Ordner prüfen (leer = zurück): ").strip()
        if not backup_path_raw:
            return

        self._section_title("Restore-Dry-Run")
        result = build_restore_dry_run(
            backup_root=Path(backup_path_raw),
            project_root=self._backup_restore_base_dir(),
        )
        print(result.message)
        print(f"Erlaubt: {result.allowed}")
        print(f"Manifest gefunden: {result.manifest_found}")
        print(f"Manifest gültig: {result.manifest_valid}")
        if result.blocked_reasons:
            print("Blockiert wegen:")
            for reason in result.blocked_reasons:
                print(f"- {reason}")
        if result.warnings:
            print("Warnungen:")
            for warning in result.warnings:
                print(f"- {warning}")
        if result.sections_checked:
            print("Geprüfte Sektionen:")
            for section in result.sections_checked:
                print(f"- {section.name}: {section.status} | Dateien: {section.file_count}")
        print("Es wurde nichts zurückgeschrieben.")

    def _create_backup_from_input(self) -> None:
        """Create a local backup only with smoke PASS and hard approval token."""
        self._section_title("Backup lokal erstellen")
        base_dir = self._backup_restore_base_dir()
        preview = build_backup_preview(base_dir)
        print(f"Zielordner: {preview.planned_backup_root}")
        print("Nicht enthalten: .env, Secrets, Obsidian Vault, Caches")
        print("Vor dem Schreiben wird der lokale Safety Smoke geprüft.")

        smoke_result = run_safety_smoke()
        if not smoke_result.passed:
            print("Backup wurde blockiert, weil der Safety Smoke nicht erfolgreich war.")
            return

        confirmation = input(
            f"Tippe {BACKUP_WRITE_APPROVAL_TOKEN} zum Erstellen oder Enter zum Abbrechen: "
        ).strip()
        if not confirmation:
            print("Backup wurde abgebrochen.")
            return

        result = write_local_backup(
            preview=preview,
            approval_token=confirmation,
            scanner_smoke_passed=smoke_result.passed,
            project_root=base_dir,
        )
        print(result.message)
        if result.target_path:
            print(f"Ziel: {result.target_path}")
        if result.blocked_reasons:
            print("Blockiert wegen:")
            for reason in result.blocked_reasons:
                print(f"- {reason}")

    def _run_backup_rotation_from_input(self) -> None:
        """Clean up old local backups only after preview, smoke PASS and hard token."""
        self._section_title("Backups aufraeumen")
        base_dir = self._backup_restore_base_dir()
        preview = build_backup_rotation_preview(base_dir)
        print(f"Backup-Ordner: {preview.backups_root}")
        print(f"Neueste geschuetzte Backups: {preview.protected_count}")
        print(f"Alte Backups zum Aufraeumen: {preview.cleanup_count}")

        if preview.candidates:
            print("Kandidaten:")
            for candidate in preview.candidates:
                status = "geschuetzt" if candidate.protected else "wird geloescht"
                print(f"- {candidate.name}: {status}")
        else:
            print("Keine lokalen Backups gefunden.")

        if preview.cleanup_count <= 0:
            print("Backup-Rotation wurde abgebrochen: keine alten Backups vorhanden.")
            return

        print("Vor dem Aufraeumen wird der lokale Safety Smoke geprueft.")
        smoke_result = run_safety_smoke()
        print(f"Safety Smoke: {'PASS' if smoke_result.passed else 'FAIL'}")
        if not smoke_result.passed:
            print("Backup-Rotation wurde blockiert: Safety Smoke fehlgeschlagen.")
            return

        confirmation = input(
            f"Tippe {BACKUP_ROTATION_APPROVAL_TOKEN} zum Aufraeumen oder Enter zum Abbrechen: "
        )
        if not confirmation:
            print("Backup-Rotation wurde abgebrochen.")
            return

        guard = check_backup_rotation_allowed(
            preview=preview,
            approval_token=confirmation,
            scanner_smoke_passed=smoke_result.passed,
            project_root=base_dir,
        )
        result = apply_backup_rotation(guard)
        print(result.message)
        if result.blocked_reasons:
            print("Blockiert wegen:")
            for reason in result.blocked_reasons:
                print(f"- {reason}")
        if result.deleted_paths:
            print("Geloeschte Backup-Ordner:")
            for path in result.deleted_paths:
                print(f"- {path}")
        if result.protected_paths:
            print("Geschuetzte Backup-Ordner:")
            for path in result.protected_paths:
                print(f"- {path}")

    def _create_restore_copy_from_input(self) -> None:
        """Create a guarded local restore copy without replacing active data."""
        backup_path_raw = input("Backup-Ordner für Restore-Kopie (leer = zurück): ").strip()
        if not backup_path_raw:
            return

        self._section_title("Restore-Kopie erstellen")
        base_dir = self._backup_restore_base_dir()
        dry_run = build_restore_dry_run(
            backup_root=Path(backup_path_raw),
            project_root=base_dir,
        )
        if not dry_run.allowed:
            print("Restore wurde blockiert, weil der Dry-Run nicht erfolgreich war.")
            if dry_run.blocked_reasons:
                print("Blockiert wegen:")
                for reason in dry_run.blocked_reasons:
                    print(f"- {reason}")
            return

        print("Friday erstellt nur eine lokale Restore-Kopie.")
        print("Die aktive Datenbank wird nicht ersetzt.")
        print("Zielbereich: local_data/restores/")
        confirmation = input(
            f"Tippe {RESTORE_WRITE_APPROVAL_TOKEN} zum Erstellen oder Enter zum Abbrechen: "
        ).strip()
        if not confirmation:
            print("Restore wurde abgebrochen.")
            return

        result = write_local_restore_copy(
            dry_run=dry_run,
            approval_token=confirmation,
            project_root=base_dir,
        )
        print(result.message)
        if result.target_root:
            print(f"Ziel: {result.target_root}")
        if result.blocked_reasons:
            print("Blockiert wegen:")
            for reason in result.blocked_reasons:
                print(f"- {reason}")
        if result.warnings:
            print("Warnungen:")
            for warning in result.warnings:
                print(f"- {warning}")

    def open_backup_restore_menu(self) -> None:
        """Show read-only backup/restore previews."""
        while True:
            choice = show_backup_restore_menu()
            if choice == "1":
                self._show_backup_preview()
            elif choice == "2":
                self._create_backup_from_input()
            elif choice == "3":
                self._restore_dry_run_from_input()
            elif choice == "4":
                self._create_restore_copy_from_input()
            elif choice == "5":
                self._create_local_data_export_from_input()
            elif choice == "6":
                self._review_local_data_import_from_input()
            elif choice == "7":
                self._show_local_data_import_apply_preview_from_input()
            elif choice == "8":
                self._apply_local_data_import_from_input()
            elif choice == "9":
                return
            elif choice == "10":
                self._run_backup_rotation_from_input()
            else:
                print(INVALID_SELECTION)

    def _show_privacy_dashboard_intro(self) -> None:
        self._section_title("Privacy Dashboard")
        print("Friday arbeitet lokal.")
        print("Externe Aktionen sind deaktiviert.")
        print("Schreibaktionen brauchen harte Tokens.")

    def _privacy_dashboard_paths(self) -> tuple[Path, Path, Path]:
        """Return project, local data and database paths for privacy counts."""
        db_path_raw = getattr(self.task_agent, "db_path", None)
        if db_path_raw is None:
            return config.PROJECT_ROOT, config.LOCAL_DATA_DIR, config.get_database_path()

        database_path = Path(db_path_raw)
        project_root = self._local_project_root()
        return project_root, project_root / "local_data", database_path

    def _build_privacy_dashboard_summary_from_local_state(self):
        project_root, local_data_dir, database_path = self._privacy_dashboard_paths()
        counts = collect_privacy_dashboard_local_counts(
            local_data_dir=local_data_dir,
            database_path=database_path,
        )
        summary = build_privacy_dashboard_summary(
            project_root=project_root,
            local_data_dir=local_data_dir,
            database_path=database_path,
            task_count=counts.task_count,
            contact_count=counts.contact_count,
            contact_context_count=counts.contact_context_count,
            review_suggestion_count=counts.review_suggestion_count,
            backup_count=counts.backup_count,
            restore_copy_count=counts.restore_copy_count,
        )
        return summary, counts

    def _show_privacy_data_areas(self) -> None:
        summary, counts = self._build_privacy_dashboard_summary_from_local_state()
        self._section_title("Lokale Datenbereiche")
        print(f"Projektpfad: {summary.project_root}")
        print(f"Lokale Daten: {summary.local_data_dir}")
        print(f"SQLite-Datenbank: {summary.database_path}")
        if counts.database_readable:
            print("SQLite-Status: read-only gezaehlt.")
        elif counts.database_available:
            print("SQLite-Status: vorhanden, aber nicht read-only lesbar.")
        else:
            print("SQLite-Status: keine lokale DB gefunden.")
        for area in summary.data_areas:
            print(f"- {area.name}: {area.storage}")
            print(f"  Pfad: {area.path}")
            print(f"  Anzahl: {area.count_label}")
            print(f"  Status: {area.write_status}")
            if area.sensitive_details_hidden:
                print("  Details: sensible Inhalte werden nicht angezeigt.")

    def _show_privacy_safety_flags(self) -> None:
        summary = build_privacy_dashboard_summary()
        self._section_title("Safety-Flags")
        for flag in summary.safety_flags:
            print(
                f"- {flag.name}: {flag.value} "
                f"(erwartet: {flag.expected_value}, Status: {flag.status})"
            )

    def _show_privacy_external_actions(self) -> None:
        summary = build_privacy_dashboard_summary()
        self._section_title("Externe Aktionen")
        for action in summary.external_actions:
            print(f"- {action.name}: {action.status} (aktiv: {action.enabled})")

    def _show_privacy_gated_actions(self) -> None:
        summary = build_privacy_dashboard_summary()
        self._section_title("Gated Actions")
        for action in summary.gated_actions:
            print(f"- {action.name}: {action.status}, Token: {action.token}")

    def _show_privacy_safety_scanners(self) -> None:
        summary = build_privacy_dashboard_summary()
        self._section_title("Safety Scanner")
        for scanner_name in summary.scanner_names:
            print(f"- {scanner_name}")
        print("Safety Smoke bleibt ein lokaler Prüfpfad.")

    def _show_privacy_data_management_inventory(self) -> None:
        project_root, local_data_dir, database_path = self._privacy_dashboard_paths()
        counts = collect_privacy_dashboard_local_counts(
            local_data_dir=local_data_dir,
            database_path=database_path,
        )
        inventory = build_privacy_data_management_inventory(
            local_data_dir=local_data_dir,
            database_path=database_path,
            task_count=counts.task_count,
            contact_context_count=counts.contact_context_count,
            review_suggestion_count=counts.review_suggestion_count,
            backup_count=counts.backup_count,
            restore_copy_count=counts.restore_copy_count,
        )
        self._section_title("Privacy Data Management Inventory")
        print("Hinweis: Diese Ansicht ist read-only.")
        print("Es wird nichts gelöscht, exportiert, importiert oder geschrieben.")
        for area in inventory.areas:
            print(f"- {area.name}")
            print(f"  Speicher: {area.storage}")
            print(f"  Pfad: {area.path}")
            print(f"  Sichtbarkeit: {area.visibility}")
            print(f"  Aktueller Zugriff: {area.current_access}")
            print(f"  Pflege-Idee: {area.future_management}")
            print(f"  Safety: {area.safety_boundary}")
            print(f"  Anzahl: {area.count_label}")
            if area.sensitive_details_hidden:
                print("  Details: sensible Inhalte werden nicht angezeigt.")

        print("Blockierte Aktionen:")
        for action in inventory.blocked_actions:
            print(f"- {action.name}: {action.reason}")

    def _show_privacy_cleanup_preview(self) -> None:
        preview = build_privacy_cleanup_preview(
            requested_areas=(
                "Exporte",
                "Backups",
                "Restore-Kopien",
                "Review-Vorschlaege",
                "Kontakt-Kontexte",
                "aktive SQLite-DB",
                ".env / Secrets",
                "Obsidian Vault",
                "global",
            )
        )
        self._section_title("Privacy Cleanup Preview")
        print("Hinweis: Diese Ansicht ist read-only.")
        print("Es wird nichts gelöscht, exportiert, importiert oder geschrieben.")
        for item in preview.items:
            status = "erlaubt fuer spaetere Preview" if item.allowed else "blockiert"
            print(f"- {item.area_name}")
            print(f"  Typ: {item.cleanup_type}")
            print(f"  Ziel: {item.target_path}")
            print(f"  Erlaubter Root: {item.allowed_root}")
            print(f"  Anzahl: {item.count_label}")
            print(f"  Erforderlicher Token: {item.requires_token}")
            print(f"  Status: {status}")
            if item.blocked_reasons:
                print(f"  Blockiert wegen: {', '.join(item.blocked_reasons)}")

        if preview.blocked_actions:
            print("Blockierte Cleanup-Aktionen:")
            for reason in preview.blocked_actions:
                print(f"- {reason}")

    def _show_privacy_cleanup_db_preview(self) -> None:
        """Show read-only SQLite cleanup candidates without running a write."""
        self._section_title("DB-Cleanup Preview")
        print("Hinweis: Diese Ansicht ist read-only.")
        print("Es wird nichts aus SQLite gelöscht oder geschrieben.")
        print("Guard und Writer werden nicht ausgeführt.")

        db_path = getattr(self.task_agent, "db_path", None) or config.get_database_path()
        try:
            preview = build_privacy_cleanup_db_preview(
                db_path=db_path,
                requested_areas=(
                    "Review-History",
                    "Kontakt-Kontext",
                    "Aufgaben",
                    "Nachrichten",
                    "Kalender",
                    "Datenbankschema",
                    "unbekannte Tabellen",
                ),
            )
        except sqlite3.Error:
            print("Lokale SQLite-Datenbank konnte nicht read-only geöffnet werden.")
            print("Es wurde nichts gelöscht oder geschrieben.")
            return

        for item in preview.items:
            status = "read-only preview" if item.allowed else "blockiert"
            print(f"- {item.area_name}")
            print(f"  Tabelle: {item.table_name}")
            print(f"  Filter: {item.status_filter}")
            print(f"  Kandidaten: {item.candidate_count}")
            print(f"  Erforderlicher Token: {item.requires_token}")
            print(f"  Status: {status}")
            print(f"  Backup erforderlich: {item.backup_required}")
            print(f"  Transaktion erforderlich: {item.transaction_required}")
            print(f"  Rollback erforderlich: {item.rollback_required}")
            print(f"  Sensible Inhalte ausgeblendet: {item.sensitive_content_hidden}")
            if item.blocked_reasons:
                print(f"  Blockiert wegen: {', '.join(item.blocked_reasons)}")

        if preview.blocked_actions:
            print("Blockierte DB-Cleanup-Aktionen:")
            for reason in preview.blocked_actions:
                print(f"- {reason}")

    def _privacy_cleanup_db_area_from_choice(self, choice: str) -> tuple[str, str | None] | None:
        mapping = {
            "1": ("Review-History", None),
            "2": ("Kontakt-Kontext", "contact"),
        }
        return mapping.get(choice)

    def _has_local_backup_for_db_cleanup(self) -> bool:
        backups_root = self._local_project_root() / "local_data" / "backups"
        return self._latest_backup_path(backups_root) is not None

    def _contact_context_db_path(self) -> Path:
        db_path = getattr(self.contact_context_repository, "db_path", None)
        if db_path is not None:
            return Path(db_path)
        return Path(getattr(self.task_agent, "db_path", None) or config.get_database_path())

    def _project_root_for_db_path(self, db_path: Path) -> Path:
        if db_path.name == "friday.db" and db_path.parent.name == "local_data":
            return db_path.parent.parent
        return db_path.parent

    def _has_local_backup_for_forget_person(self, db_path: Path) -> bool:
        backups_root = self._project_root_for_db_path(db_path) / "local_data" / "backups"
        return self._latest_backup_path(backups_root) is not None

    def _run_privacy_cleanup_db_from_input(self) -> None:
        """Run guarded SQLite privacy cleanup after preview, backup and token checks."""
        self._section_title("DB-Cleanup ausführen")
        print("WARNUNG: Diese Aktion kann lokale SQLite-Daten entfernen.")
        print("Friday zeigt zuerst eine frische Vorschau und prüft danach den Safety Guard.")
        print("Es werden keine externen Aktionen ausgeführt.")
        print("Unterstützte Bereiche:")
        print("1. Review-History")
        print("2. Einzelner Kontakt-Kontext")
        print("Enter/z. Zurück")

        area_choice = input("DB-Cleanup-Bereich wählen: ").strip().lower()
        if not area_choice or area_choice == "z":
            print("DB-Cleanup wurde abgebrochen.")
            return

        selected_area = self._privacy_cleanup_db_area_from_choice(area_choice)
        if selected_area is None:
            print(INVALID_SELECTION)
            return

        cleanup_area, contact_marker = selected_area
        contact_id: str | None = None
        if contact_marker == "contact":
            contact_id = input("Kontakt-ID eingeben: ").strip()
            if not contact_id:
                print("DB-Cleanup wurde abgebrochen.")
                return

        db_path = getattr(self.task_agent, "db_path", None) or config.get_database_path()
        try:
            preview = build_privacy_cleanup_db_preview(
                db_path=db_path,
                requested_areas=(cleanup_area,),
                contact_id=contact_id,
            )
        except sqlite3.Error:
            print("Lokale SQLite-Datenbank konnte nicht read-only geöffnet werden.")
            print("DB-Cleanup wurde abgebrochen.")
            return

        self._section_title("DB-Cleanup Preview")
        for item in preview.items:
            status = "read-only preview" if item.allowed else "blockiert"
            print(f"- {item.area_name}")
            print(f"  Tabelle: {item.table_name}")
            print(f"  Filter: {item.status_filter}")
            print(f"  Kandidaten: {item.candidate_count}")
            print(f"  Erforderlicher Token: {item.requires_token}")
            print(f"  Status: {status}")
            if item.blocked_reasons:
                print(f"  Blockiert wegen: {', '.join(item.blocked_reasons)}")

        if not self._has_local_backup_for_db_cleanup():
            print("DB-Cleanup wurde blockiert: Backup fehlt.")
            return

        smoke_result = run_safety_smoke()
        print(f"Safety Smoke: {'PASS' if smoke_result.passed else 'FAIL'}")
        if not smoke_result.passed:
            print("DB-Cleanup wurde blockiert: Safety Smoke fehlgeschlagen.")
            return

        required_token = preview.items[0].requires_token if preview.items else "nicht freigegeben"
        print("Zum Ausführen tippe exakt:")
        print(required_token)
        approval_token = input("Token: ")

        guard = check_privacy_cleanup_db_write_allowed(
            cleanup_area=cleanup_area,
            preview=preview,
            approval_token=approval_token,
            backup_available=True,
            transaction_available=True,
            rollback_available=True,
            scanner_smoke_passed=smoke_result.passed,
            external_actions_enabled=False,
        )
        if not guard.allowed:
            print("DB-Cleanup wurde nicht freigegeben.")
            for reason in guard.blocked_reasons:
                print(f"- {reason}")
            return

        result = apply_privacy_cleanup_db_write(
            db_path=db_path,
            guard_result=guard,
            contact_id=contact_id,
        )
        if not result.allowed:
            print("DB-Cleanup wurde nicht ausgefuehrt.")
            for reason in result.blocked_reasons:
                print(f"- {reason}")
            return

        print("DB-Cleanup wurde lokal ausgefuehrt.")
        print("Gelöschte Datensätze:")
        for table_name, count in result.deleted_counts.items():
            print(f"- {table_name}: {count}")

    def _local_project_root(self) -> Path:
        db_path = getattr(self.task_agent, "db_path", None)
        if db_path is None:
            return Path.cwd()

        db_path = Path(db_path)
        if db_path.name == "friday.db" and db_path.parent.name == "local_data":
            return db_path.parent.parent
        return db_path.parent

    def _privacy_cleanup_area_from_choice(self, choice: str) -> tuple[str, str, str] | None:
        mapping = {
            "1": ("exports", "Exporte", "local_data/exports"),
            "2": ("backups", "Backups", "local_data/backups"),
            "3": ("restore_work", "Restore-Kopien", "local_data/restores"),
        }
        return mapping.get(choice)

    def _latest_backup_path(self, backups_root: Path) -> Path | None:
        if not backups_root.exists() or not backups_root.is_dir():
            return None
        candidates = sorted(path for path in backups_root.iterdir() if path.is_dir())
        if not candidates:
            return None
        return candidates[-1]

    def _run_privacy_cleanup_from_input(self) -> None:
        self._section_title("Privacy Cleanup ausführen")
        print("WARNUNG: Diese Aktion kann lokale Dateien entfernen.")
        print("Friday zeigt zuerst eine Vorschau und prüft danach den Safety Guard.")
        print("Es werden keine externen Aktionen ausgeführt.")
        print("Unterstützte Bereiche:")
        print("1. Exporte")
        print("2. Backups")
        print("3. Restore-Kopien")
        print("Enter/z. Zurück")

        area_choice = input("Cleanup-Bereich wählen: ").strip().lower()
        if not area_choice or area_choice == "z":
            print("Cleanup wurde abgebrochen.")
            return

        selected_area = self._privacy_cleanup_area_from_choice(area_choice)
        if selected_area is None:
            print(INVALID_SELECTION)
            return

        cleanup_area, preview_area_name, allowed_root = selected_area
        project_root = self._local_project_root()
        allowed_base_path = project_root / allowed_root
        target_raw = input("Konkreten lokalen Zielpfad eingeben: ").strip()
        if not target_raw:
            print("Cleanup wurde abgebrochen.")
            return

        target_path = Path(target_raw)
        if not target_path.is_absolute():
            target_path = project_root / target_path

        preview = build_privacy_cleanup_preview(
            requested_areas=(preview_area_name,),
            target_paths={preview_area_name: target_path.as_posix()},
        )
        self._section_title("Privacy Cleanup Vorschau")
        for item in preview.items:
            print(f"- {item.area_name}")
            print(f"  Ziel: {item.target_path}")
            print(f"  Erlaubter Root: {item.allowed_root}")
            print(f"  Erforderlicher Token: {item.requires_token}")
            if item.blocked_reasons:
                print(f"  Blockiert wegen: {', '.join(item.blocked_reasons)}")

        smoke_result = run_safety_smoke()
        print(f"Safety Smoke: {'PASS' if smoke_result.passed else 'FAIL'}")
        if not smoke_result.passed:
            print("Cleanup wurde abgebrochen.")
            return

        expected_token = PRIVACY_CLEANUP_TOKENS[cleanup_area]
        print("Zum Ausführen tippe exakt:")
        print(expected_token)
        approval_token = input("Token: ")

        guard = check_privacy_cleanup_write_allowed(
            cleanup_area=cleanup_area,
            target_path=target_path,
            project_root=project_root,
            allowed_base_path=allowed_base_path,
            preview_was_shown=True,
            approval_token=approval_token,
            scanner_smoke_passed=smoke_result.passed,
            external_actions_enabled=False,
            active_database_path=getattr(self.task_agent, "db_path", None),
            obsidian_vault_path=config.OBSIDIAN_VAULT_PATH or None,
        )
        if not guard.allowed:
            print("Privacy Cleanup wurde nicht freigegeben.")
            for reason in guard.blocked_reasons:
                print(f"- {reason}")
            return

        latest_backup_path = (
            self._latest_backup_path(allowed_base_path)
            if cleanup_area == "backups"
            else None
        )
        result = apply_privacy_cleanup(
            guard_result=guard,
            cleanup_area=cleanup_area,
            target_path=target_path,
            dry_run=False,
            latest_backup_path=latest_backup_path,
        )
        print(result.message)
        if result.blocked_reasons:
            for reason in result.blocked_reasons:
                print(f"- {reason}")
        if result.performed:
            print(f"Gelöscht: {result.deleted_count}")
            print(f"Übersprungen: {result.skipped_count}")

    def open_privacy_dashboard_menu(self) -> None:
        """Show the read-only privacy dashboard submenu."""
        self._show_privacy_dashboard_intro()
        while True:
            choice = show_privacy_dashboard_menu()
            if choice == "1":
                self._show_privacy_data_areas()
            elif choice == "2":
                self._show_privacy_safety_flags()
            elif choice == "3":
                self._show_privacy_external_actions()
            elif choice == "4":
                self._show_privacy_gated_actions()
            elif choice == "5":
                self._show_privacy_safety_scanners()
            elif choice == "6":
                self._show_privacy_data_management_inventory()
            elif choice == "7":
                self._show_privacy_cleanup_preview()
            elif choice == "8":
                self._run_privacy_cleanup_from_input()
            elif choice == "9":
                self._show_privacy_cleanup_db_preview()
            elif choice == "10":
                self._run_privacy_cleanup_db_from_input()
            elif choice == "11":
                return
            else:
                print(INVALID_SELECTION)

    def _delete_task_from_input(self) -> None:
        """Collect one id and confirm permanent deletion."""
        task_id_raw = input("ID der Aufgabe zum dauerhaften Löschen: ").strip()
        try:
            task_id = int(task_id_raw)
        except ValueError:
            print("Ungültige Aufgaben-ID.")
            return

        if self.task_agent.get_task_by_id(task_id) is None:
            print("Aufgabe wurde nicht gefunden.")
            return

        print("Achtung: Diese Aufgabe wird dauerhaft gelöscht.")
        confirmation = input("Zum Bestätigen bitte JA eingeben: ").strip()
        if confirmation != "JA":
            print("Löschen wurde abgebrochen.")
            return

        if self.task_agent.delete_task(task_id):
            print("Aufgabe wurde dauerhaft gelöscht.")
            return
        print("Aufgabe wurde nicht gefunden.")

    def open_task_management(self) -> None:
        """Show and process the task submenu."""
        while True:
            task_choice = show_task_menu()
            if task_choice == "1":
                self._show_open_tasks()
            elif task_choice == "2":
                self._create_task_from_input()
            elif task_choice == "3":
                self._edit_task_from_input()
            elif task_choice == "4":
                self._mark_task_done_from_input()
            elif task_choice == "5":
                self._search_or_filter_tasks_from_input()
            elif task_choice == "6":
                self._archive_task_from_input()
            elif task_choice == "7":
                self._delete_task_from_input()
            elif task_choice == "9":
                self._quick_add_task_from_input()
            elif task_choice == "10":
                self._export_tasks_to_markdown()
            elif task_choice == "11":
                self._show_local_day_plan_preview()
            elif task_choice == "12":
                return
            else:
                print(INVALID_SELECTION)

    def show_morning_briefing(self) -> None:
        self._section_title("Morgenübersicht")
        briefing = self.briefing_agent.build_preview()
        print(f"Datum: {briefing['date']}")
        print("Aufgaben heute:")
        for task in briefing["tasks"]:
            print(f"- {task['title']} ({task['category']})")
        print("\nKalender heute:")
        for item in briefing["calendar_items"]:
            print(f"- {item['start']} - {item['end']}: {item['title']}")
        print(f"\nWetter: {briefing['weather']}")
        print(f"Musik: {briefing['music']}")

    def _show_local_onboarding_note(self) -> None:
        """Show a one-time local onboarding note on startup."""
        self._section_title("Start-Hinweis")
        print(f"Willkommen bei Friday {config.APP_VERSION} (lokale CLI).")
        print(f"Friday {config.APP_VERSION} – lokaler Assistent gestartet.")
        print("Nutze das Hauptmenü für Aufgaben, Nachrichten, Kalender und Review-Workflows.")
        print("Alle Aktionen sind lokal: Es werden keine echten Nachrichten gesendet und keine echten Termine erstellt.")

    def show_dashboard(self) -> None:
        # Show a compact dashboard for the startup screen.
        self._section_title("Live-Dashboard")
        self._show_open_tasks()
        self._show_messages_with_suggestions()
        self._show_calendar()
        self._show_local_onboarding_note()

    def _show_help_overview(self) -> None:
        """Show a short local command overview and safety boundaries."""
        self._section_title("Hilfe / Übersicht")
        print(f"Friday Version: {config.APP_VERSION}")
        print("Startbefehl: python -m friday.main")
        print("Grundregel: Alles bleibt lokal, bis ein eigenes Safety-Gate etwas anderes erlaubt.")
        print("Lokaler CLI-Überblick:")
        print(" - Aufgaben: anzeigen, erstellen, bearbeiten, erledigen, suchen, archivieren, löschen")
        print(" - Aufgabe schnell erfassen: eine Zeile mit Markern, z. B. !hoch @morgen #taeglich")
        print(" - Wiederkehrende Aufgaben: taeglich, woechentlich oder monatlich")
        print(" - Nachrichten: lokale Nachrichtenerkennung und Aktionen anzeigen")
        print(" - Kalender-Vorschläge: mögliche freie Slots als lokaler Entwurf")
        print(" - Morgenübersicht: heute + Wetter/Musik als lokale Vorschau")
        print(" - Sicherheitsstatus: lokale Aktivierung/Deaktivierung")
        print(" - Vorschläge prüfen / freigeben: Nachrichten- und Aufgabenideen verwalten")
        print(" - Kontakt-Kontext: lokale Kontakt-Kontexte anzeigen und suchen")
        print(" - Obsidian Brain Preview: lokale Notiz-Vorschau mit deaktiviertem Write-Gate")
        print(" - Backup / Restore: lokale Backup-Vorschau und Restore-Dry-Run")
        print(" - E-Mail-Entwurf Preview: lokaler Entwurf, kein Provider, kein Versand")
        print(" - Beenden: beendet den Lauf sauber")
        print(" - Zurück: Untermenüs bieten eine eigene Zurück-Option oder Enter/z im Review.")
        print("Lokale Safety-Hinweise:")
        print(" - Kontakt-Kontext: bleibt lokal; Speichern/Löschen braucht harte Tokens.")
        print(" - E-Mail-Entwurf Preview: Session-only; kein Provider, kein Versand.")
        print(" - Backup / Restore: schreibt nur lokal und nur nach hartem Token.")
        print(" - Privacy Dashboard: Anzeigen sind read-only; Cleanup ist hart gegated.")
        print(" - Lokale Modell-Diagnose: siehe Sicherheitsstatus. Es werden keine externen Modellaufrufe genutzt.")
        print(" - Help ist lokal, es werden nur Informationen angezeigt.")
        print("Es werden keine echten Nachrichten gesendet.")
        print("Es werden keine echten Kalendertermine erstellt.")

    def _print_contact_contexts(self, contacts: list[dict], empty_message: str) -> None:
        """Print local contact context rows without changing storage."""
        if not contacts:
            print(empty_message)
            return

        for contact in contacts:
            nickname = contact.get("nickname") or "kein Spitzname"
            relationship = contact.get("relationship_context") or "kein Kontext"
            print(
                f"- [{contact['contact_id']}] {contact['display_name']} | "
                f"Typ: {contact.get('contact_type') or 'unbekannt'} | "
                f"Spitzname: {nickname} | Kontext: {relationship}"
            )

    def _show_contact_contexts(self) -> None:
        """Show all locally stored contact contexts."""
        self._section_title("Lokale Kontakt-Kontexte")
        contacts = self.contact_context_repository.list_contact_contexts()
        self._print_contact_contexts(contacts, "Keine lokalen Kontakt-Kontexte vorhanden.")

    def _search_contact_contexts_from_input(self) -> None:
        """Search local contact contexts by simple visible fields."""
        query = input("Kontakt suchen (leer = zurück): ").strip().lower()
        if not query:
            return

        contacts = self.contact_context_repository.list_contact_contexts()
        matches = [
            contact
            for contact in contacts
            if query
            in " ".join(
                [
                    str(contact.get("display_name") or ""),
                    str(contact.get("normalized_name") or ""),
                    str(contact.get("nickname") or ""),
                    str(contact.get("contact_type") or ""),
                    str(contact.get("source_context") or ""),
                ]
            ).lower()
        ]
        self._section_title("Kontakt-Suche")
        self._print_contact_contexts(matches, "Keine passenden Kontakt-Kontexte gefunden.")

    def _edit_contact_context_draft_from_input(self) -> None:
        """Build a local contact edit draft without writing changes."""
        contact_id = input("Kontakt-ID bearbeiten (leer = zurück): ").strip()
        if not contact_id:
            return

        contact = self.contact_context_repository.get_contact_context(contact_id)
        if contact is None:
            print("Kontakt-Kontext wurde nicht gefunden.")
            return

        prepared = prepare_contact_prompt_draft_flow(
            display_name=str(contact.get("display_name") or ""),
            contact_type="unbekannt",
            source_context="person_bearbeiten",
        )

        if not prepared.prompt_rendered:
            print("Kontakt-Kontext-Draft ist aktuell blockiert.")
            return

        if prepared.rendered.question:
            print(prepared.rendered.question)

        raw_choice = input("Auswahl für Vorschau: ")
        result = apply_contact_prompt_draft_input(prepared, raw_choice)

        if result.status == "selected":
            self._section_title("Kontakt-Kontext Vorschau")
            print(f"Name: {contact['display_name']}")
            print(f"Kontaktart: {result.selected_contact_type}")
            print("Speicherung: Noch nicht")
            print("Hinweis: Ohne Freigabe wird nichts gespeichert.")
            confirmation = input(
                "Soll dieser Kontakt-Kontext lokal gespeichert werden? "
                "Tippe SPEICHERN zum Speichern oder Enter zum Abbrechen: "
            ).strip()
            if confirmation != "SPEICHERN":
                print("Speichern wurde abgebrochen.")
                return

            try:
                updated = self.contact_context_repository.update_contact_context(
                    contact_id=str(contact["contact_id"]),
                    contact_type=result.selected_contact_type,
                    source_context="person_bearbeiten",
                    user_approved_persistence=True,
                    sensitivity_checked=True,
                )
            except ValueError as error:
                if str(error) == CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE:
                    print(CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE)
                    return
                raise
            if updated is None:
                print("Kontakt-Kontext wurde nicht gefunden.")
                return
            print("Kontakt-Kontext wurde lokal gespeichert.")
            return

        if result.status == "skipped":
            print("Kontakt-Bearbeitung wurde übersprungen.")
            return

        print(result.error_message or INVALID_SELECTION)

    def _forget_contact_context_from_input(self) -> None:
        """Forget one local contact context through preview, guard, and writer."""
        person_identifier = input("Kontakt-ID oder Name vergessen (leer = zurück): ").strip()
        if not person_identifier:
            return

        db_path = self._contact_context_db_path()
        preview = build_forget_person_preview(
            db_path=db_path,
            person_identifier=person_identifier,
        )

        if not preview.allowed:
            print("Forget Person wurde blockiert.")
            for reason in preview.blocked_reasons:
                print(f"- {reason}")
            return

        if preview.candidate_count <= 0:
            print("Kontakt-Kontext wurde nicht gefunden.")
            return

        print("Forget Person Preview:")
        print("Zieltabelle: contact_contexts")
        print(f"Kandidaten: {preview.candidate_count}")
        print("Treffer:")
        for contact in preview.matched_contacts:
            print(f"- [{contact.contact_id}] {contact.display_name} | Typ: {contact.contact_type}")
        print("Es werden keine Obsidian-Dateien geschrieben.")
        print("Es werden keine externen Aktionen ausgeführt.")

        backup_available = self._has_local_backup_for_forget_person(db_path)
        if not backup_available:
            print("Forget Person wurde blockiert: Backup fehlt.")
            return

        smoke_result = run_safety_smoke()
        print(f"Safety Smoke: {'PASS' if smoke_result.passed else 'FAIL'}")
        if not smoke_result.passed:
            print("Forget Person wurde blockiert: Safety Smoke fehlgeschlagen.")
            return

        print("Zum Ausführen tippe exakt:")
        print(preview.requires_token)
        approval_token = input("Token: ")

        guard = check_forget_person_write_allowed(
            preview=preview,
            approval_token=approval_token,
            backup_available=backup_available,
            transaction_available=True,
            rollback_available=True,
            scanner_smoke_passed=smoke_result.passed,
            external_actions_enabled=False,
            obsidian_write_requested=False,
        )
        if not guard.allowed:
            print("Forget Person wurde nicht freigegeben.")
            for reason in guard.blocked_reasons:
                print(f"- {reason}")
            return

        result = apply_forget_person_write(
            db_path=db_path,
            guard_result=guard,
        )
        if not result.allowed:
            print("Forget Person wurde nicht ausgefuehrt.")
            for reason in result.blocked_reasons:
                print(f"- {reason}")
            return

        print("Forget Person wurde lokal ausgefuehrt.")
        print("Gelöschte Datensätze:")
        for table_name, count in result.deleted_counts.items():
            print(f"- {table_name}: {count}")

    def open_contact_context_menu(self) -> None:
        """Show the local contact context menu with hard-gated write paths."""
        while True:
            print("\n" + "-" * 40)
            print("Kontakt-Kontext")
            print("-" * 40)
            print("Hinweis: Alle Kontakt-Aktionen bleiben lokal. 5 führt zurück zum Hauptmenü.")
            print("1. Kontakte anzeigen")
            print("2. Kontakt suchen")
            print("3. Kontakt bearbeiten (Vorschau)")
            print("4. Kontakt vergessen")
            print("5. Zurück zum Hauptmenü")
            print("6. Einfachen Kontakt speichern")

            choice = input("Auswahl (1-6): ").strip()
            if choice == "1":
                self._show_contact_contexts()
            elif choice == "2":
                self._search_contact_contexts_from_input()
            elif choice == "3":
                self._edit_contact_context_draft_from_input()
            elif choice == "4":
                self._forget_contact_context_from_input()
            elif choice == "5":
                return
            elif choice == "6":
                self._create_simple_contact_from_input()
            else:
                print(INVALID_SELECTION)

    def _create_simple_contact_from_input(self) -> None:
        """Create a simple local contact used by message and task rules."""
        repository = getattr(self.message_agent, "contact_repository", None)
        if repository is None:
            print("Kontakt-Speicher ist nicht verfügbar.")
            return

        self._section_title("Einfachen Kontakt speichern")
        name = input("Name / Absender: ").strip()
        if not name:
            print("Kontaktname ist erforderlich.")
            return

        contact_type = input(
            "Kontaktart (arbeit/freund/familie/kunde/sonstiges): "
        ).strip().lower() or "sonstiges"
        betreuer = None
        if contact_type == "kunde":
            betreuer = input("Betreuer (flo/philip/alex, leer = keiner): ").strip().lower() or None

        notes = input("Notiz (optional): ").strip()
        try:
            contact = repository.create_contact(
                name=name,
                contact_type=contact_type,
                notes=notes,
                betreuer=betreuer,
            )
        except ValueError as error:
            print(str(error))
            return

        print("Kontakt wurde lokal gespeichert.")
        print(f"Name: {contact['name']}")
        print(f"Kontaktart: {contact['contact_type']}")
        if contact.get("betreuer"):
            print(f"Betreuer: {contact['betreuer']}")

    def _show_safety_status(self) -> None:
        """Show which real services are currently disabled."""
        self._section_title("Sicherheitsstatus")
        ms_mail_status = ms_mail_account_status()
        print(f"E-Mail echt aktiv: {config.ENABLE_REAL_EMAIL}")
        print(f"WhatsApp echt aktiv: {config.ENABLE_REAL_WHATSAPP}")
        print(f"WhatsApp Read-Bridge aktiv: {config.ENABLE_WHATSAPP_BRIDGE_READ}")
        print(f"Microsoft Mail Lesen aktiv: {config.ENABLE_MS_MAIL_READ}")
        print(f"Microsoft Mail Postfaecher: {ms_mail_status.get('account_count', 0)}")
        for account in ms_mail_status.get("accounts", []):
            print(
                " - "
                f"{account.get('username_masked') or account.get('account_id')}: "
                f"Test OK: {account.get('last_test_ok')}"
            )
        print(f"SMS echt aktiv: {config.ENABLE_REAL_SMS}")
        print(f"Kalender echt aktiv: {config.ENABLE_REAL_CALENDAR}")
        print(f"Wetter echt aktiv: {config.ENABLE_REAL_WEATHER}")
        print(f"Musik echt aktiv: {config.ENABLE_REAL_MUSIC}")
        print(f"Obsidian Write aktiv: {config.OBSIDIAN_WRITE_ENABLED}")
        print(f"Obsidian Vault gesetzt: {bool(config.OBSIDIAN_VAULT_PATH)}")
        print(f"Nutzerfreigabe erforderlich: {config.REQUIRE_USER_APPROVAL}")
        blocked_count = len(
            BlockedSenderRepository(getattr(self.message_agent, "db_path", None)).list_blocked_senders()
        )
        print(f"Lokal blockierte Absender: {blocked_count}")
        print("Kompakter Systemstatus:")
        print(f"Local Mode: {config.LOCAL_MODE}")
        print(f"Demo Mode: {config.DEMO_MODE}")
        print(f"Use Real Today: {config.USE_REAL_TODAY}")
        print(f"SQLite Storage: {config.USE_SQLITE_STORAGE}")
        print(f"Aktive Datenbank: {config.get_database_path().name}")
        print(f"Lokale Benachrichtigungen: {config.ENABLE_LOCAL_NOTIFICATIONS}")
        print("Empfohlene lokale Prüfkommandos (werden hier nicht ausgeführt):")
        print("python -m pytest friday/tests")
        print("python -m compileall friday")
        print("python scripts\\friday_safety_smoke.py")
        print("git diff --check")
        print("Lokaler Modell-Diagnosemodus: Mock/Preview")
        print(f"ENABLE_LOCAL_OLLAMA: {config.ENABLE_LOCAL_OLLAMA}")
        print(f"Ollama Modell gesetzt: {bool(config.OLLAMA_MODEL.strip())}")
        print(f"Ollama URL lokal erlaubt: {is_local_ollama_url(config.OLLAMA_BASE_URL)}")
        print("Ollama Live-Health-Check: nicht automatisch ausgeführt")
        print("Externe Modellaufrufe: False")
        print("Produktfluss angebunden: False")

    def handle_menu_choice(self, choice: str) -> bool:
        """Process one user choice and return False to stop the loop."""
        if choice == "1":
            self.open_task_management()
            return True
        if choice == "2":
            self._show_messages_with_suggestions()
            return True
        if choice == "3":
            self._show_calendar()
            return True
        if choice == "4":
            self.show_morning_briefing()
            return True
        if choice == "5":
            self._show_safety_status()
            return True
        if choice == "6":
            self.review_pending_suggestions()
            return True
        if choice == "8":
            self._show_help_overview()
            return True
        if choice == "9":
            self.open_contact_context_menu()
            return True
        if choice == "10":
            self.show_obsidian_brain_preview()
            return True
        if choice == "11":
            self.open_backup_restore_menu()
            return True
        if choice == "12":
            self.open_privacy_dashboard_menu()
            return True
        if choice == "13":
            self.show_email_draft_preview()
            return True
        if choice == "14":
            self.open_account_menu()
            return True
        if choice == "15":
            self._show_spam_and_blocked_senders()
            return True
        if choice == "7":
            print("Friday wird beendet.")
            return False

        print("Ungültige Auswahl. Bitte erneut versuchen.")
        return True

    def open_account_menu(self) -> None:
        """Show local account connection options."""
        while True:
            choice = show_account_menu()
            if choice == "1":
                self._show_email_account_status()
            elif choice == "2":
                self._connect_email_account_from_input()
            elif choice == "3":
                self._test_email_account_from_input()
            elif choice == "4":
                self._delete_email_account_from_input()
            elif choice == "5":
                self._show_email_activation_gate_from_input()
            elif choice == "6":
                self._show_whatsapp_bridge_status()
            elif choice == "7":
                self._show_whatsapp_bridge_activation_gate_from_input()
            elif choice == "8":
                self._edit_email_agent_notes_from_input()
            elif choice == "9":
                self._edit_whatsapp_agent_notes_from_input()
            elif choice == "10" or not choice:
                return
            else:
                print(INVALID_SELECTION)

    def _show_email_account_status(self) -> None:
        """Print password-free email account status."""
        self._section_title("E-Mail-Konto Status")
        status = email_account_status()
        print(f"Verbunden: {status['connected']}")
        print(f"E-Mail: {status.get('email_address') or '-'}")
        print(f"Letzter Test OK: {status['last_test_ok']}")
        print(f"Real-Versand aktiv: {status['real_email_enabled']}")
        print(f"Tageslimit: {status['send_limit_per_day']}")
        print(f"Agent-Notiz vorhanden: {status.get('agent_notes_configured', False)}")
        print("WhatsApp: Deep-Link ueber dein Handy, kein Konto-Login.")

    def _connect_email_account_from_input(self) -> None:
        """Connect and store one email account after live login tests."""
        self._section_title("E-Mail-Konto verbinden")
        print("Am sichersten ist die Verbindung direkt am PC.")
        preset = input("Preset (gmail/outlook/gmx/web.de/custom): ").strip().lower() or "gmail"
        email_address = input("E-Mail-Adresse: ").strip()
        username = input("Benutzername (leer = E-Mail-Adresse): ").strip() or email_address
        agent_notes = input("Agent-Notiz fuer dieses Konto (optional): ").strip()
        app_password = getpass("App-Passwort (wird nicht angezeigt): ")
        try:
            if preset == "custom":
                smtp_host = input("SMTP Host: ").strip()
                smtp_port = int(input("SMTP Port (465 oder 587): ").strip())
                imap_host = input("IMAP Host: ").strip()
                imap_port = int(input("IMAP Port (993): ").strip())
                account = build_email_account_from_plain_password(
                    display_name=email_address,
                    email_address=email_address,
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    imap_host=imap_host,
                    imap_port=imap_port,
                    username=username,
                    app_password=app_password,
                    agent_notes=agent_notes,
                )
            else:
                account = build_email_account_from_preset(
                    preset_name=preset,
                    email_address=email_address,
                    username=username,
                    app_password=app_password,
                    agent_notes=agent_notes,
                )
        except ValueError as error:
            print(str(error))
            return
        smtp_result = check_smtp_login(account=account, app_password=app_password)
        imap_result = check_imap_login(account=account, app_password=app_password)
        print(f"SMTP Test: {'erfolgreich' if smtp_result.ok else 'Fehler'}")
        print(f"IMAP Test: {'erfolgreich' if imap_result.ok else 'Fehler'}")
        if not smtp_result.ok or not imap_result.ok:
            print("Konto wurde nicht gespeichert.")
            return
        token = input(f"Zum Speichern exakt {EMAIL_ACCOUNT_SAVE_TOKEN} eingeben: ")
        tested_account = build_email_account_from_plain_password(
            display_name=account.display_name,
            email_address=account.email_address,
            smtp_host=account.smtp_host,
            smtp_port=account.smtp_port,
            imap_host=account.imap_host,
            imap_port=account.imap_port,
            username=account.username,
            app_password=app_password,
            last_test_ok=True,
            agent_notes=account.agent_notes,
        )
        result = save_email_account(tested_account, approval_token=token)
        print(result.message)

    def _edit_email_agent_notes_from_input(self) -> None:
        """Edit local AI-readable notes for the stored email account."""
        self._section_title("E-Mail-Agent-Notiz")
        status = email_account_status()
        if not status["connected"]:
            print("Kein E-Mail-Konto verbunden.")
            return
        print("Diese Notiz bleibt lokal und wird nur fuer lokale KI-Entwuerfe genutzt.")
        current = status.get("agent_notes") or ""
        if current:
            print("Aktuelle Notiz:")
            print(current)
        notes = input("Neue Agent-Notiz (leer = loeschen): ")
        result = save_email_account_agent_notes(notes)
        print(result.message)

    def _edit_whatsapp_agent_notes_from_input(self) -> None:
        """Edit local AI-readable WhatsApp notes."""
        self._section_title("WhatsApp-Agent-Notiz")
        current = load_whatsapp_agent_notes()
        print("Diese Notiz bleibt lokal und wird nur fuer lokale KI-Entwuerfe genutzt.")
        if current.get("agent_notes"):
            print("Aktuelle Notiz:")
            print(current["agent_notes"])
        notes = input("Neue Agent-Notiz (leer = loeschen): ")
        result = save_whatsapp_agent_notes(notes)
        print("WhatsApp-Agent-Notiz wurde lokal gespeichert.")
        print(f"Notiz vorhanden: {result['agent_notes_configured']}")

    def _test_email_account_from_input(self) -> None:
        """Test stored SMTP/IMAP credentials without sending."""
        account = load_email_account()
        if account is None:
            print("Kein E-Mail-Konto verbunden.")
            return
        try:
            password = decrypt_email_account_password(account)
        except Exception:
            print("E-Mail-Passwort konnte lokal nicht entschluesselt werden.")
            return
        smtp_result = check_smtp_login(account=account, app_password=password)
        imap_result = check_imap_login(account=account, app_password=password)
        print(f"SMTP Test: {'erfolgreich' if smtp_result.ok else 'Fehler'}")
        print(f"IMAP Test: {'erfolgreich' if imap_result.ok else 'Fehler'}")

    def _delete_email_account_from_input(self) -> None:
        """Delete stored email account with hard token."""
        token = input(f"Zum Loeschen exakt {EMAIL_ACCOUNT_DELETE_TOKEN} eingeben: ")
        result = delete_email_account(approval_token=token)
        print(result.message)

    def _show_email_activation_gate_from_input(self) -> None:
        """Show whether real email activation could be allowed later."""
        token = input(f"Token fuer Pruefung ({EMAIL_ACTIVATION_TOKEN}): ")
        smoke = run_safety_smoke()
        gate = build_email_activation_gate(
            approval_token=token,
            scanner_smoke_passed=smoke.passed,
        )
        print(f"EMAIL AKTIVIEREN erlaubt: {gate.allowed}")
        print(f"Safety Smoke: {'PASS' if smoke.passed else 'FAIL'}")
        if gate.blocked_reasons:
            print("Blocker:")
            for reason in gate.blocked_reasons:
                print(f"- {reason}")
        print("Hinweis: Dieser Lauf setzt ENABLE_REAL_EMAIL nicht automatisch auf True.")

    def _show_whatsapp_bridge_status(self) -> None:
        """Print read-only WhatsApp bridge status without raw phone numbers."""
        self._section_title("WhatsApp Read-Bridge Status")
        status = get_whatsapp_bridge_status(getattr(self.message_agent, "db_path", None))
        print(f"Read-Bridge aktiv: {status['read_enabled']}")
        print(f"WhatsApp echt senden aktiv: {status['real_whatsapp_enabled']}")
        print(f"Verbunden erkannt: {status['connected']}")
        print(f"Lokale Nachrichten: {status['message_count']}")
        print(f"Letzter Empfang: {status['last_received_at'] or '-'}")
        print(f"Bridge Token vorhanden: {status['token_configured']}")
        print(f"Agent-Notiz vorhanden: {status.get('agent_notes_configured', False)}")
        print("Hinweis: Nur Mitlesen. Senden bleibt ausschliesslich Deep-Link mit Nutzerfinger.")
        print("Risiko: WhatsApp-Web-Bridges koennen gegen WhatsApp-Regeln verstossen.")

    def _show_whatsapp_bridge_activation_gate_from_input(self) -> None:
        """Run the local WhatsApp read bridge activation gate."""
        self._section_title("WhatsApp Read-Bridge Aktivierung")
        print("Risiko-Hinweis: Diese lokale Bruecke nutzt WhatsApp Web nur zum Mitlesen.")
        print("Das kann gegen WhatsApp-Regeln verstossen und eine Kontosperre riskieren.")
        print("Friday sendet ueber diese Bruecke nie automatisch.")
        token = input(f"Zum Aktivieren exakt {WHATSAPP_BRIDGE_ACTIVATION_TOKEN} eingeben: ")
        smoke = run_safety_smoke()
        gate = build_whatsapp_bridge_activation_gate(
            approval_token=token,
            scanner_smoke_passed=smoke.passed,
        )
        print(f"Read-Bridge Aktivierung erlaubt: {gate.allowed}")
        print(f"Safety Smoke: {'PASS' if smoke.passed else 'FAIL'}")
        if gate.blocked_reasons:
            print("Blocker:")
            for reason in gate.blocked_reasons:
                print(f"- {reason}")
            return
        apply_result = apply_whatsapp_bridge_read_activation_to_config(
            approval_token=token,
            scanner_smoke_passed=smoke.passed,
            execute_write=True,
        )
        print(apply_result.message)
        if apply_result.backup_path:
            print(f"Backup: {apply_result.backup_path}")

    def run(self) -> None:
        """Run the basic interaction loop until the user exits."""
        # Show full dashboard once when Friday starts.
        self.show_dashboard()
        self._show_startup_notification_preview_if_enabled()
        while True:
            choice = show_menu()
            if not self.handle_menu_choice(choice):
                break

    def _show_startup_notification_preview_if_enabled(self) -> None:
        """Show a local startup notification summary when explicitly enabled."""
        if not config.ENABLE_LOCAL_NOTIFICATIONS:
            return
        preview = build_due_task_notification_preview(self.task_agent.get_open_tasks())
        if not preview.should_show:
            return
        self._section_title("Lokale Benachrichtigung")
        print(preview.text)

    def show_email_draft_preview(self) -> None:
        """Manage local in-memory email draft previews without provider or external delivery."""
        while True:
            self._section_title("E-Mail-Entwurf Preview")
            print("Hinweis: Entwürfe bleiben nur in dieser Session. 6 oder Enter führt zurück.")
            print("1. Entwurf aus lokaler Nachricht erstellen")
            print("2. Freien lokalen Entwurf erstellen")
            print("3. Session-Entwürfe anzeigen")
            print("4. Letzten Entwurf bearbeiten")
            print("5. Letzten Entwurf verwerfen")
            print("6. Zurück zum Hauptmenü")
            choice = input("Auswahl (1-6): ").strip()

            if choice == "1":
                self._create_email_draft_from_local_message()
            elif choice == "2":
                self._create_email_draft_from_input()
            elif choice == "3":
                self._show_email_drafts()
            elif choice == "4":
                self._edit_latest_email_draft_from_input()
            elif choice == "5":
                self._discard_latest_email_draft()
            elif choice == "6" or not choice:
                return
            else:
                print(INVALID_SELECTION)

    def _store_and_print_email_draft(self, draft: EmailDraft) -> None:
        """Store one session draft and print its safe preview."""
        self.email_drafts.append(draft)
        print(render_email_draft_preview(draft))

    def _create_email_draft_from_local_message(self) -> None:
        """Create a local draft from the first local message suggestion."""
        messages = self.message_agent.get_messages()
        if not messages:
            print("Keine lokale Nachricht für einen Entwurf gefunden.")
            return

        message = messages[0]
        sender = str(message.get("sender") or "Unbekannter Kontakt")
        draft = build_email_draft(
            recipient_label=sender,
            subject=f"Rueckmeldung an {sender}",
            body=str(self.message_agent.create_reply_suggestion(message)),
            source_context="message_preview",
        )
        self._store_and_print_email_draft(draft)

    def _create_email_draft_from_input(self) -> None:
        """Create a free local email draft from user input."""
        recipient = input("Empfaenger-Label: ")
        subject = input("Betreff: ")
        body = input("Nachrichtentext: ")
        draft = build_email_draft(
            recipient_label=recipient,
            subject=subject,
            body=body,
            source_context="free_email_draft_preview",
        )
        self._store_and_print_email_draft(draft)

    def _show_email_drafts(self) -> None:
        """Show all local in-memory email drafts for this CLI session."""
        if not self.email_drafts:
            print("Keine lokalen E-Mail-Entwürfe in dieser Session.")
            return
        for index, draft in enumerate(self.email_drafts, start=1):
            print(f"\nEntwurf {index}:")
            print(render_email_draft_preview(draft))

    def _edit_latest_email_draft_from_input(self) -> None:
        """Edit the latest session draft without persistence or provider."""
        if not self.email_drafts:
            print("Kein lokaler E-Mail-Entwurf zum Bearbeiten vorhanden.")
            return
        current = self.email_drafts[-1]
        subject = input("Neuer Betreff (leer = behalten): ").strip() or current.subject
        body = input("Neuer Nachrichtentext (leer = behalten): ").strip() or current.body
        edited = build_email_draft(
            recipient_label=current.recipient_label,
            subject=subject,
            body=body,
            source_context=current.source_context,
            status="edited",
        )
        self.email_drafts[-1] = edited
        print(render_email_draft_preview(edited))

    def _discard_latest_email_draft(self) -> None:
        """Mark the latest local draft as discarded for this session."""
        if not self.email_drafts:
            print("Kein lokaler E-Mail-Entwurf zum Verwerfen vorhanden.")
            return
        current = self.email_drafts[-1]
        discarded = build_email_draft(
            recipient_label=current.recipient_label,
            subject=current.subject,
            body=current.body,
            source_context=current.source_context,
            status="discarded",
        )
        self.email_drafts[-1] = discarded
        print("E-Mail-Entwurf wurde lokal verworfen.")
        print(render_email_draft_preview(discarded))
