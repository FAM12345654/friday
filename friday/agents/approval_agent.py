"""Approval agent: every action requires local user confirmation."""

from __future__ import annotations

from typing import Dict, Optional


class ApprovalAgent:
    """Gatekeeper for all potential actions in the first skeleton.

    This keeps real messages, real calendar changes, and other live actions
    from running before the user explicitly approves them.
    """

    def request_approval(self, action: str, message: Optional[str] = None, context: Optional[Dict] = None) -> str:
        """Ask the user for approval and return the status.

        Status values:
        - pending: user did not clearly approve or reject
        - approved: user typed j (ja)
        - rejected: user typed n (nein)
        """
        # This remains a local confirmation only; no action executes here.
        print(f"\nFreigabe gefragt: {action}")
        if message:
            print(f"Info: {message}")
        if context:
            print(f"Kontext: {context}")
        answer = input("Genehmigen? (j = ja, n = nein, Enter = später): ").strip().lower()
        if answer == "j":
            print("Status: approved")
            return "approved"
        if answer == "n":
            print("Status: rejected")
            return "rejected"
        print("Status: pending")
        return "pending"
