# Friday Build Summary (Complete, local version)

## 1) What this project is

Friday is a local-only assistant runtime with a terminal interface.

- Core mode: local, offline, no real external services.
- Data store: local SQLite database at `local_data/friday.db` plus local JSON seed files in `friday/data/`.
- Main goals:
  - Manage local tasks and reviews.
  - Provide local suggestion handling for messages and calendar requests.
  - Track and manage contact context safely.
  - Offer local backup/restore/import/export workflows.
  - Provide privacy/safety visibility and guarded write actions.
  - Keep everything in a safety-first, token-gated, explicit-approval flow.

## 2) Startup and configuration flow

1. `friday.main.main()` initializes the DB (`setup_local_database()`), prints startup text, then starts the terminal UI.
2. `friday.storage.database` ensures local data directory/db exist, creates schema, seeds with demos.
3. `friday.app.interface.FridayInterface` owns menus, command dispatch, and review workflows.
4. Config is centralized in `friday.config`:
   - Local-only switches for external integrations are disabled.
   - Local approval model is enabled.
   - Paths and constants for DB, data, and safety defaults.

## 3) Project architecture overview

### Domains

- Interface layer: CLI menus, review screens, onboarding, help, task/contact/calendar/message flows.
- Domain agents: task/calendar/message/contact-context/morning briefing orchestration.
- Storage layer: repository pattern over SQLite.
- Safety layer: scanners + guards + hard-token checks + smoke runs.
- Data portability: backup/export/import/restore read/write preview + apply pipelines.
- Privacy layer: dashboard + data management inventory + cleanup preview + guarded cleanup writes.
- Obsidian integration: local note preview and guarded write pipeline.
- Local model scaffolding: mock/preview provider, schema validation, and logic checks.

## 4) Build feature matrix

- Task management:
  - list, search, filter, create, edit, done, archive, delete
  - status transitions (`open`, `done`, `archived`)
  - quick add path and markdown export
- Message workflow:
  - local intent detection
  - generate local draft suggestions
  - message + task suggestions flow
  - approve/reject/edit/snooze via review UI
- Calendar workflow:
  - local calendar loading
  - free slot calculation
  - attach slot proposals to suggestion text
  - select/reject suggestions
- Contact context:
  - list/load contacts
  - type/category detection
  - prompt candidate creation + parser + draft flow
  - suppression model for noisy prompts
  - sensitive context guardrails
- Safety/supervision:
  - no network/input-print scanners
  - forbidden import checks
  - approval token checks
  - safety flag regression checks
  - safety smoke runner
  - local model readiness mock/preview
- Data portability:
  - backup preview/write
  - restore dry-run + restore copy writer
  - local export preview/write with manifest
  - local import manifest read + dry-run + apply preview + guarded apply
  - scanner checks before write
- Privacy:
  - dashboard summary
  - privacy data management inventory
  - privacy cleanup preview
  - guarded cleanup execution with explicit tokens
- Obsidian:
  - local note previews (contact/task/project)
  - optional write dry-run
  - write gate

## 5) Complete function inventory (production code only, excluding tests)

Below is every callable function and method found in `friday/` source excluding test files.

### `friday.main`

- `main() -> None`

### `friday.storage.sqlite_storage`

- `query_all(connection: sqlite3.Connection, sql: str, params: Sequence[Any] = ()) -> list[Dict[str, Any]]`

### `friday.storage.database`

- `FridayConnection.__exit__(self, exc_type, exc_value, traceback) -> bool`
- `_resolve_db_path(db_path: Path | str | None = None) -> Path`
- `ensure_local_data_dir(db_path: Path | str | None = None) -> None`
- `get_connection(db_path: Path | str | None = None) -> sqlite3.Connection`
- `initialize_database(db_path: Path | str | None = None) -> None`
- `_ensure_task_priority_column(connection: sqlite3.Connection) -> None`
- `_read_json(file_name: str) -> List[Dict[str, Any]]`
- `_table_is_empty(connection: sqlite3.Connection, table_name: str) -> bool`
- `seed_database_from_json(db_path: Path | str | None = None) -> None`
- `setup_local_database(db_path: Path | str | None = None) -> None`

### `friday.storage.repositories`

- `row_to_dict(row: sqlite3.Row) -> dict`
- `_to_minutes(time_iso: str) -> int`
- `_to_time_string(minutes: int) -> str`
- `_validate_priority(priority: str | None, default: str | None = None) -> str | None`
- `_validate_suggestion_status(status: str | None) -> str`
- `_validate_calendar_suggestion_status(status: str | None) -> str`
- `_validate_task_suggestion_status(status: str | None) -> str`
- `_now_iso_timestamp() -> str`
- `_task_order_expression() -> str`
- `_ordered_task_query() -> str`
- `_task_select_sql() -> str`
- `TaskRepository.__init__(self, db_path: Path | str | None = None) -> None`
- `TaskRepository.get_task_by_id(self, task_id: int) -> dict | None`
- `TaskRepository.get_open_tasks(self) -> List[dict]`
- `TaskRepository.get_tasks_by_status(self, status: str) -> List[dict]`
- `TaskRepository.search_tasks(self, query: str) -> list[dict]`
- `TaskRepository.filter_tasks(self, category: str | None = None, status: str | None = None, due_date: str | None = None) -> list[dict]`
- `TaskRepository.create_task(self, title: str, category: str, priority: str | None = 'normal', due_date: str | None = None, notes: str | None = None) -> dict`
- `TaskRepository.update_task(self, task_id: int, updates: Mapping[str, Any]) -> dict | None`
- `TaskRepository.mark_task_done(self, task_id: int) -> dict | None`
- `TaskRepository.archive_task(self, task_id: int) -> dict | None`
- `TaskRepository.delete_task(self, task_id: int) -> bool`
- `TaskRepository.get_tasks_for_date(self, date_iso: str) -> List[dict]`
- `MessageRepository.__init__(self, db_path: Path | str | None = None) -> None`
- `MessageRepository.get_messages(self) -> List[dict]`
- `CalendarRepository.__init__(self, db_path: Path | str | None = None) -> None`
- `CalendarRepository.get_items_for_date(self, date_iso: str) -> List[dict]`
- `CalendarRepository.get_free_slots_for_date(self, date_iso: str, duration_minutes: int = 60) -> List[dict]`
- `ContactRepository.__init__(self, db_path: Path | str | None = None) -> None`
- `ContactRepository.get_contacts(self) -> List[dict]`
- `ContactRepository.get_contact_type_by_name(self, name: str) -> str`
- `MessageSuggestionRepository.__init__(self, db_path: Path | str | None = None) -> None`
- `MessageSuggestionRepository._row_to_dict(self, row: sqlite3.Row | None) -> dict | None`
- `MessageSuggestionRepository.create_suggestion(self, *, message_id: int, suggestion_type: str, suggested_text: str, intent: str | None = None, draft_text: str | None = None, confidence: float | None = None) -> dict`
- `MessageSuggestionRepository.get_suggestion_by_id(self, suggestion_id: int) -> dict | None`
- `MessageSuggestionRepository.get_suggestion_for_message(self, message_id: int, suggestion_type: str) -> dict | None`
- `MessageSuggestionRepository.get_pending_suggestions(self) -> list[dict]`
- `MessageSuggestionRepository.get_all_suggestions(self) -> list[dict]`
- `MessageSuggestionRepository.update_suggestion_status(self, suggestion_id: int, status: str, review_note: str | None = None) -> dict | None`
- `MessageSuggestionRepository.edit_suggestion_draft(self, suggestion_id: int, draft_text: str) -> dict | None`
- `TaskSuggestionRepository.__init__(self, db_path: Path | str | None = None) -> None`
- `TaskSuggestionRepository._row_to_dict(self, row: sqlite3.Row | None) -> dict | None`
- `TaskSuggestionRepository.create_task_suggestion(self, *, message_id: int, title: str, notes: str, category: str | None = None, due_date: str | None = None, priority: str = 'normal', draft_notes: str | None = None, confidence: float | None = None, preview: str | None = None) -> dict`
- `TaskSuggestionRepository.get_task_suggestion_by_id(self, suggestion_id: int) -> dict | None`
- `TaskSuggestionRepository.get_task_suggestion_for_message(self, message_id: int) -> dict | None`
- `TaskSuggestionRepository.get_pending_task_suggestions(self) -> list[dict]`
- `TaskSuggestionRepository.get_all_task_suggestions(self) -> list[dict]`
- `TaskSuggestionRepository.update_task_suggestion_status(self, suggestion_id: int, status: str, review_note: str | None = None) -> dict | None`
- `TaskSuggestionRepository.edit_task_suggestion(self, suggestion_id: int, *, title: str | None = None, notes: str | None = None, category: str | None = None, due_date: str | None = None, priority: str | None = None, draft_notes: str | None = None, preview: str | None = None) -> dict | None`
- `TaskSuggestionRepository.mark_task_suggestion_converted(self, suggestion_id: int, created_task_id: int) -> dict | None`
- `CalendarSuggestionRepository.__init__(self, db_path: Path | str | None = None) -> None`
- `CalendarSuggestionRepository._row_to_dict(self, row: sqlite3.Row | None) -> dict | None`
- `CalendarSuggestionRepository.create_calendar_suggestion(self, *, message_id: int, slot_id: str, slot_text: str, slot_start: str | None = None, slot_end: str | None = None, confidence: float | None = None, draft_text: str | None = None) -> dict`
- `CalendarSuggestionRepository.get_calendar_suggestion_by_id(self, suggestion_id: int) -> dict | None`
- `CalendarSuggestionRepository.get_calendar_suggestions_for_message(self, message_id: int) -> list[dict]`
- `CalendarSuggestionRepository.get_pending_calendar_suggestions_for_message(self, message_id: int) -> list[dict]`
- `CalendarSuggestionRepository.select_calendar_suggestion(self, suggestion_id: int) -> dict | None`
- `CalendarSuggestionRepository.reject_calendar_suggestion(self, suggestion_id: int) -> dict | None`

### `friday.storage.contact_context_repository`

- `_now_iso_timestamp() -> str`
- `_to_int_bool(value: bool | int) -> int`
- `_normalize_contact_type(contact_type: str | None) -> str`
- `ContactContextRepository.__init__(self, db_path: Path | str | None = None) -> None`
- `ContactContextRepository.create_contact_context(self, contact_id: str, display_name: str, normalized_name: str, role: str | None = None, category: str | None = None, notes: str | None = None, context: str | None = None, favorite: bool = False, relation_score: int | None = None, contact_type: str | None = None, is_blocked: bool = False) -> dict`
- `ContactContextRepository.get_contact_context(self, contact_id: str) -> dict | None`
- `ContactContextRepository.find_contact_by_normalized_name(self, normalized_name: str) -> dict | None`
- `ContactContextRepository.list_contact_contexts(self) -> list[dict]`
- `ContactContextRepository.update_contact_context(self, contact_id: str, **updates: Any) -> dict | None`
- `ContactContextRepository.delete_contact_context(self, contact_id: str) -> bool`

### `friday.agents.task_agent`

- `TaskAgent.__init__(self, db_path: Path | None = None) -> None`
- `TaskAgent.get_open_tasks(self) -> List[Dict[str, Any]]`
- `TaskAgent.get_task_by_id(self, task_id: int) -> Dict[str, Any] | None`
- `TaskAgent.get_tasks_for_date(self, date_iso: str | None = None) -> List[Dict[str, Any]]`
- `TaskAgent.get_tasks_for_dashboard(self) -> List[Dict[str, Any]]`
- `TaskAgent.get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]`
- `TaskAgent.search_tasks(self, query: str) -> List[Dict[str, Any]]`
- `TaskAgent.filter_tasks(self, category: str | None = None, status: str | None = None, due_date: str | None = None) -> List[Dict[str, Any]]`
- `TaskAgent.archive_task(self, task_id: int) -> Dict[str, Any] | None`
- `TaskAgent.delete_task(self, task_id: int) -> bool`
- `TaskAgent.create_task(self, title: str, category: str, due_date: str | None = None, notes: str | None = None, priority: str = 'normal') -> Dict[str, Any]`
- `TaskAgent.edit_task(self, task_id: int, **fields) -> Dict[str, Any] | None`
- `TaskAgent.mark_task_done(self, task_id: int) -> Dict[str, Any] | None`
- `TaskAgent._effective_today(self) -> str`
- `TaskAgent.detect_priority_hint(self, task: Dict[str, Any]) -> str`

### `friday.agents.message_agent`

- `MessageAgent.__init__(self, db_path: Path | None = None, contact_agent: Any | None = None) -> None`
- `MessageAgent.get_messages(self) -> List[Dict[str, Any]]`
- `MessageAgent.detect_intent(self, text: str) -> str`
- `MessageAgent.is_scheduling_related(self, text: str) -> bool`
- `MessageAgent.create_reply_suggestion(self, message: Dict[str, Any]) -> str`
- `MessageAgent.get_contact_type(self, sender: str) -> str`
- `MessageAgent.generate_local_suggestions(self) -> list[Dict[str, Any]]`
- `MessageAgent.generate_local_task_suggestions(self) -> list[Dict[str, Any]]`
- `MessageAgent.get_pending_suggestions(self) -> list[Dict[str, Any]]`
- `MessageAgent.get_pending_task_suggestions(self) -> list[Dict[str, Any]]`
- `MessageAgent.approve_suggestion(self, suggestion_id: int) -> dict | None`
- `MessageAgent.reject_suggestion(self, suggestion_id: int) -> dict | None`
- `MessageAgent.edit_suggestion(self, suggestion_id: int, draft_text: str) -> dict | None`
- `MessageAgent.reject_task_suggestion(self, suggestion_id: int) -> dict | None`
- `MessageAgent.edit_task_suggestion(self, suggestion_id: int, *, title: str | None = None, notes: str | None = None, category: str | None = None, due_date: str | None = None, priority: str | None = None, draft_notes: str | None = None) -> dict | None`
- `MessageAgent.mark_task_suggestion_converted(self, suggestion_id: int, created_task_id: int) -> dict | None`

### `friday.agents.calendar_agent`

- `CalendarAgent.__init__(self, db_path: Path | None = None) -> None`
- `CalendarAgent.load_calendar(self) -> List[Dict[str, Any]]`
- `CalendarAgent.get_items_for_date(self, date_iso: str) -> List[Dict[str, Any]]`
- `CalendarAgent.get_free_slots_for_date(self, date_iso: str, duration_minutes: int = 60) -> List[Dict[str, str]]`
- `CalendarAgent.generate_calendar_suggestions_for_message(self, message: dict) -> list[Dict[str, str]]`
- `CalendarAgent.get_calendar_suggestions_for_message(self, message_id: int) -> list[Dict[str, Any]]`
- `CalendarAgent.get_pending_calendar_suggestions_for_message(self, message_id: int) -> list[Dict[str, Any]]`
- `CalendarAgent.get_calendar_suggestion_by_id(self, suggestion_id: int) -> dict | None`
- `CalendarAgent.select_calendar_suggestion(self, suggestion_id: int) -> dict | None`
- `CalendarAgent.reject_calendar_suggestion(self, suggestion_id: int) -> dict | None`
- `CalendarAgent._fallback_free_slots_for_date(self, date_iso: str, duration_minutes: int) -> List[Dict[str, str]]`
- `CalendarAgent._to_minutes(time_iso: str) -> int`
- `CalendarAgent._to_time_string(minutes: int) -> str`
- `CalendarAgent._effective_today(self) -> str`
- `CalendarAgent.get_free_slots_today(self, duration_minutes: int = 60) -> List[Dict[str, str]]`
- `CalendarAgent.sync_real_calendar(self) -> str`

### `friday.agents.contact_context_agent`

- `ContactContextAgent.__init__(self, db_path: Path | None = None) -> None`
- `ContactContextAgent.load_contacts(self) -> List[Dict[str, Any]]`
- `ContactContextAgent.get_category_for_sender(self, sender: str) -> str`

### `friday.agents.morning_briefing_agent`

- `MorningBriefingAgent.__init__(self, task_agent: TaskAgent | None = None, calendar_agent: CalendarAgent | None = None) -> None`
- `MorningBriefingAgent.build_preview(self, today_iso: str | None = None) -> Dict[str, Any]`
- `MorningBriefingAgent._effective_today(self) -> str`

### `friday.agents.approval_agent`

- `ApprovalAgent.request_approval(self, action: str, message: Optional[str] = None, context: Optional[Dict] = None) -> str`

### `friday.app.interface`

- `FridayInterface.__init__(self) -> None`
- `_section_title(self, title: str) -> None`
- `_format_calendar_slot_text(self, slot: dict) -> str`
- `_merge_calendar_slot_into_draft(self, draft_text: str, slot_text: str) -> str`
- `_show_open_tasks(self) -> None`
- `_show_messages_with_suggestions(self) -> List[Dict[str, Any]]`
- `_intent_label(self, intent: str) -> str`
- `_show_calendar(self) -> None`
- `_ask_approvals_for_messages(self, messages: List[Dict[str, Any]]) -> None`
- `_ask_approvals_for_calendar(self) -> None`
- `review_pending_suggestions(self) -> None`
- `_get_review_counts(self, contact_candidates: list[dict] | None = None) -> dict[str, int]`
- `_print_review_overview(self, message_count: int, task_count: int, contact_count: int = 0) -> None`
- `_get_review_contact_candidates(self, messages: list[dict]) -> list[dict]`
- `_print_review_contact_candidate_preview(self, candidates: list[dict]) -> None`
- `_review_contact_candidates_loop(self, contact_candidates: list[dict]) -> None`
- `_review_single_contact_candidate(self, candidate: dict) -> bool`
- `_generate_local_task_suggestions(self) -> None`
- `_get_pending_message_suggestions(self) -> list[dict]`
- `_get_pending_task_suggestions(self) -> list[dict]`
- `_get_messages_by_id(self) -> dict[int, dict]`
- `_review_message_suggestions(self, pending_suggestions: list[dict], messages: dict[int, dict]) -> bool`
- `_print_task_suggestions(self, suggestions: list[dict], messages: dict[int, dict]) -> None`
- `_review_message_suggestions_loop(self, pending_suggestions: list[dict], messages: dict[int, dict]) -> None`
- `_review_task_suggestions_loop(self, pending_task_suggestions: list[dict], messages: dict[int, dict]) -> None`
- `_print_task_suggestion_detail(self, suggestion: dict, message: dict) -> None`
- `_build_task_contact_snapshot_for_message(self, message: dict) -> str | None`
- `_merge_task_notes_with_contact_snapshot(self, notes: str | None, message: dict) -> str | None`
- `_review_task_suggestions(self, pending_task_suggestions: list[dict], messages: dict[int, dict]) -> bool`
- `_handle_task_suggestion_action(self, suggestion: dict, action: str) -> bool`
- `_is_task_suggestion_convertible(self, suggestion: dict) -> bool`
- `_print_reviewable_suggestions(self, suggestions: list[dict], messages: dict[int, dict]) -> None`
- `_print_single_suggestion_detail(self, suggestion: dict, message: dict) -> None`
- `_print_calendar_slots(self, slots: list[dict]) -> None`
- `_handle_review_action(self, suggestion: dict) -> None`
- `_quick_add_task_from_input(self) -> None`
- `_create_task_from_input(self) -> None`
- `_edit_task_from_input(self) -> None`
- `_print_task_list(self, tasks: List[Dict[str, Any]], empty_message: str) -> None`
- `_mark_task_done_from_input(self) -> None`
- `_search_or_filter_tasks_from_input(self) -> None`
- `_archive_task_from_input(self) -> None`
- `_collect_all_tasks_for_markdown_export(self) -> List[Dict[str, Any]]`
- `_task_export_base_dir(self) -> Path`
- `_export_tasks_to_markdown(self) -> None`
- `_collect_obsidian_task_records(self) -> list[dict]`
- `_collect_obsidian_contact_records(self) -> list[dict]`
- `show_obsidian_brain_preview(self) -> None`
- `_backup_restore_base_dir(self) -> Path`
- `_show_backup_preview(self) -> None`
- `_show_local_data_export_preview(self) -> None`
- `_collect_tasks_for_local_data_export(self) -> tuple[dict, ...]`
- `_build_local_data_export_payload(self, scanner_smoke_passed: bool) -> LocalDataExportPayload`
- `_create_local_data_export_from_input(self) -> None`
- `_review_local_data_import_from_input(self) -> None`
- `_show_local_data_import_apply_preview_from_input(self) -> None`
- `_local_data_import_apply_backup_ready(self) -> bool`
- `_local_database_path(self) -> Path`
- `_apply_local_data_import_from_input(self) -> None`
- `_restore_dry_run_from_input(self) -> None`
- `_create_backup_from_input(self) -> None`
- `_create_restore_copy_from_input(self) -> None`
- `open_backup_restore_menu(self) -> None`
- `_show_privacy_dashboard_intro(self) -> None`
- `_show_privacy_data_areas(self) -> None`
- `_show_privacy_safety_flags(self) -> None`
- `_show_privacy_external_actions(self) -> None`
- `_show_privacy_gated_actions(self) -> None`
- `_show_privacy_safety_scanners(self) -> None`
- `_show_privacy_data_management_inventory(self) -> None`
- `_show_privacy_cleanup_preview(self) -> None`
- `_local_project_root(self) -> Path`
- `_privacy_cleanup_area_from_choice(self, choice: str) -> tuple[str, str, str] | None`
- `_latest_backup_path(self, backups_root: Path) -> Path | None`
- `_run_privacy_cleanup_from_input(self) -> None`
- `open_privacy_dashboard_menu(self) -> None`
- `_delete_task_from_input(self) -> None`
- `open_task_management(self) -> None`
- `show_morning_briefing(self) -> None`
- `_show_local_onboarding_note(self) -> None`
- `show_dashboard(self) -> None`
- `_show_help_overview(self) -> None`
- `_print_contact_contexts(self, contacts: list[dict], empty_message: str) -> None`
- `_show_contact_contexts(self) -> None`
- `_search_contact_contexts_from_input(self) -> None`
- `_edit_contact_context_draft_from_input(self) -> None`
- `_forget_contact_context_from_input(self) -> None`
- `open_contact_context_menu(self) -> None`
- `_show_safety_status(self) -> None`
- `handle_menu_choice(self, choice: str) -> bool`
- `run(self) -> None`

### `friday.app.menu`

- `show_menu() -> str`
- `show_task_menu() -> str`
- `show_backup_restore_menu() -> str`
- `show_privacy_dashboard_menu() -> str`
- `is_exit(choice: str) -> bool`

### `friday.app.task_markdown_export`

- `format_tasks_as_markdown(tasks: Iterable[Mapping[str, Any]]) -> str`
- `write_tasks_markdown(output_path: Path, tasks: Iterable[Mapping[str, Any]]) -> Path`
- `build_default_tasks_export_path() -> Path`
- `export_tasks_markdown_to_default_path(tasks: Iterable[Mapping[str, Any]]) -> Path`
- `_sort_key(task: Mapping[str, Any]) -> int`

### `friday.app.backup_preview`

- `_count_files(path: Path) -> int`
- `_section(status: str, details: str, count: int, size: int | None = None) -> BackupPreviewSection`
- `build_backup_preview(project_root: Path) -> BackupPreview`

### `friday.app.backup_writer`

- `_relative_backup_path(target_root: Path, file_path: Path) -> str`
- `_is_excluded_copy_path(path: Path) -> bool`
- `_write_text_file(target_root: Path, relative_path: str, text: str) -> BackupWrittenFile`
- `_copy_file(target_root: Path, source: Path, relative_path: str) -> BackupWrittenFile`
- `_copy_directory(target_root: Path, source: Path, relative_root: Path, copied: list[BackupWrittenFile]) -> None`
- `_write_manifest(target_root: Path, preview: BackupPreview) -> BackupWrittenFile`
- `_write_safety_docs(target_root: Path, project_root: Path) -> tuple[BackupWrittenFile, ...]`
- `write_local_backup(project_root: Path, backups_root: Path, scanner_smoke_passed: bool, snapshot_path: Path | None = None) -> BackupWriteResult`

### `friday.app.backup_write_guard`

- `_is_relative_to(path: Path, parent: Path) -> bool`
- `_section_names_by_status(result: BackupWriteGuardResult) -> tuple[str, ...]`
- `check_backup_write_allowed(*, preview: BackupPreview, requested_token: str | None, db_path: Path | str | None = None, project_root: Path | None = None, backups_root: Path | None = None) -> BackupWriteGuardResult`

### `friday.app.local_data_export_preview`

- `build_local_data_export_preview(payload: Mapping[str, Any]) -> LocalDataExportPreview`

### `friday.app.local_data_export_guard`

- `_is_relative_to(path: Path, parent: Path) -> bool`
- `check_local_data_export_allowed(*, preview: LocalDataExportPreview, requested_token: str | None, db_path: Path | str | None = None, export_root: Path | None = None) -> LocalDataExportGuardResult`

### `friday.app.local_data_export_writer`

- `_write_text_file(target_root: Path, relative_path: str, text: str) -> LocalDataExportWrittenFile`
- `_write_json_file(target_root: Path, relative_path: str, content: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> LocalDataExportWrittenFile`
- `_filter_mapping(data: Mapping[str, Any], *allowed: str) -> dict[str, Any]`
- `_build_manifest(payload: LocalDataExportPayload) -> dict[str, Any]`
- `write_local_data_export(project_root: Path, payload: LocalDataExportPayload, backup_protection_passed: bool) -> LocalDataExportWriteResult`

### `friday.app.local_data_import_manifest_reader`

- `_is_relative_to(path: Path, parent: Path) -> bool`
- `_blocked(message: str) -> LocalDataImportManifestReadResult`
- `_as_string_tuple(value: object) -> tuple[str, ...]`
- `_as_counts(value: object) -> dict[str, int]`
- `_contains_forbidden_manifest_content(value: object) -> bool`
- `read_local_data_import_manifest(export_root: Path) -> LocalDataImportManifestReadResult`

### `friday.app.local_data_import_dry_run`

- `_is_relative_to(path: Path, parent: Path) -> bool`
- `_section(name: str, path: Path | None, status: str, details: str, count: int = 0) -> LocalDataImportDryRunSection`
- `_has_forbidden_content(value: object) -> bool`
- `_has_external_lookup_used(value: object) -> bool`
- `_load_json_file(path: Path) -> object | None`
- `_contacts_have_only_allowed_fields(value: object) -> bool`
- `_review_has_only_allowed_fields(value: object) -> bool`
- `_safety_flags_are_local_only(value: object) -> bool`
- `build_local_data_import_dry_run(export_root: Path, db_path: Path | None = None) -> LocalDataImportDryRunResult`

### `friday.app.local_data_import_apply_preview`

- `_section(name: str, planned_count: int, action: str) -> LocalDataImportApplyPreviewSection`
- `_planned_sections(read_result: LocalDataImportManifestReadResult, dry_run: LocalDataImportDryRunResult) -> tuple[LocalDataImportApplyPreviewSection, ...]`
- `build_local_data_import_apply_preview(export_root: Path, db_path: Path | None = None) -> LocalDataImportApplyPreviewResult`

### `friday.app.local_data_import_apply_write_guard`

- `_preview_write_scope(read_result: LocalDataImportManifestReadResult | None) -> str`
- `check_local_data_import_apply_write_allowed(*, apply_preview: LocalDataImportApplyPreviewResult, requested_token: str | None, db_path: Path | str | None = None, import_root: Path | None = None) -> LocalDataImportApplyWriteGuardResult`

### `friday.app.local_data_import_apply_writer`

- `_read_json_list(export_root: Path, relative_path: str) -> list[Mapping[str, Any]]`
- `_normalize_task(item: Mapping[str, Any]) -> dict[str, Any]`
- `_normalize_contact_context(item: Mapping[str, Any]) -> dict[str, Any]`
- `_normalize_review_suggestion(item: Mapping[str, Any]) -> dict[str, Any] | None`
- `_task_is_identical(existing: sqlite3.Row, task: Mapping[str, Any]) -> bool`
- `_apply_tasks(connection: sqlite3.Connection, items: list[Mapping[str, Any]]) -> tuple[int, int]`
- `_apply_contact_contexts(connection: sqlite3.Connection, items: list[Mapping[str, Any]]) -> tuple[int, int]`
- `_apply_review_suggestions(connection: sqlite3.Connection, items: list[Mapping[str, Any]]) -> tuple[int, int]`
- `apply_local_data_import(export_root: Path, db_path: Path | None = None) -> LocalDataImportApplyWriterResult`

### `friday.app.local_data_import_apply_write`

- This module name is a namespace group in this project:
  - `friday.app.local_data_import_apply_writer.py` and
  - `friday.app.local_data_import_apply_write_guard.py`

### `friday.app.local_model_mock`

- `LocalModelMockResult.__str__(self) -> str`
- `LocalModelReadinessStatus.as_dict(self) -> dict`
- `LocalModelMockAdapter.__init__(self) -> None`
- `LocalModelMockAdapter.is_available(self) -> bool`
- `LocalModelMockAdapter.get_readiness_status(self) -> LocalModelReadinessStatus`
- `LocalModelMockAdapter.get_fallback_status(self) -> str`
- `LocalModelMockAdapter.generate(self, prompt: str) -> LocalModelMockResult`

### `friday.app.local_model_provider`

- `safety_flags_locked() -> bool`
- `LocalModelProvider.health_check(self) -> ProviderHealth`
- `LocalModelProvider.generate_json(self, prompt: str, schema: Mapping[str, Any]) -> ProviderResult`
- `MockLocalModelProvider.__init__(self) -> None`
- `MockLocalModelProvider.health_check(self) -> ProviderHealth`
- `MockLocalModelProvider.generate_json(self, prompt: str, schema: Mapping[str, Any]) -> ProviderResult`

### `friday.app.local_model_preview`

- `preview_local_model_response(prompt: str) -> LocalModelPreview`

### `friday.app.local_ollama_adapter_preview`

- `default_ollama_preview_config() -> OllamaAdapterPreviewConfig`
- `_is_local_ollama_base_url(base_url: str) -> bool`
- `validate_ollama_preview_config(config: OllamaAdapterPreviewConfig) -> bool`
- `OllamaLocalAdapterPreview.__init__(self, preview_config: OllamaAdapterPreviewConfig | None = None) -> None`
- `OllamaLocalAdapterPreview.health_check(self) -> OllamaAdapterPreviewHealth`
- `OllamaLocalAdapterPreview.build_json_request_preview(self, prompt: str, schema: Mapping[str, Any]) -> OllamaRequestPreview`

### `friday.app.logic_check_agent`

- `_base_result(ok: bool, errors: list[str] = None) -> LogicCheckResult`
- `_all_text_values(data: Mapping[str, Any]) -> list[str]`
- `LogicCheckAgent.check_validated_output(self, data: Any, requirements: Sequence[str] | None = None) -> LogicCheckResult`

### `friday.app.model_output_validator`

- `_error_result(errors: list[str]) -> ModelOutputValidationResult`
- `_parse_output(output: Mapping[str, Any] | str | None) -> tuple[dict[str, Any], list[str]]`
- `_matches_expected_type(value: Any, expected: Any) -> bool`
- `reject_unknown_fields(schema: Mapping[str, Any], data: Mapping[str, Any]) -> list[str]`
- `require_confidence(data: Mapping[str, Any], min_confidence: float) -> list[str]`
- `validate_model_json(schema: Mapping[str, Any], output: Any, *, min_confidence: float = 0.0) -> ModelOutputValidationResult`

### `friday.app.safety_smoke_runner`

- `SafetySmokeCheckResult.__init__(self, name: str, passed: bool, message: str = '', details: str | None = None) -> None`
- `SafetySmokeResult.__init__(self, checks: list[SafetySmokeCheckResult], timestamp: str, all_passed: bool) -> None`
- `run_safety_smoke() -> SafetySmokeResult`
- `format_safety_smoke_result(result: SafetySmokeResult) -> str`

### `friday.app.safety_flag_regression_scanner`

- `_literal_bool(node: ast.AST) -> tuple[bool | None, bool]`
- `_target_name(node: ast.AST) -> str | None`
- `scan_python_source_for_safety_flags(file_path: Path) -> list[SafetyFlagAssignment]`
- `evaluate_safety_flag_assignments(assignments: Sequence[SafetyFlagAssignment], expected_locked: bool, expected_flags: Mapping[str, bool], expected_defaults: Mapping[str, bool]) -> SafetyFlagRegressionScanResult`
- `scan_python_file_for_safety_flags(path: Path | str) -> SafetyFlagRegressionScanResult`
- `iter_python_files(root: Path | str) -> tuple[Path, ...]`
- `scan_paths_for_safety_flag_regressions(roots: Sequence[Path | str]) -> SafetyFlagRegressionScanResult`

### `friday.app.no_network_scanner`

- `_attribute_name(node: ast.AST) -> str | None`
- `_collect_import_aliases(tree: ast.AST) -> dict[str, str]`
- `_resolve_call_name(call_name: str, aliases: dict[str, str]) -> str`
- `scan_python_source_for_network_usage(file_path: Path) -> list[NetworkUsageFinding]`
- `scan_python_file_for_network_usage(path: Path | str) -> NoNetworkScanResult`
- `iter_python_files(root: Path | str) -> tuple[Path, ...]`
- `scan_paths_for_network_usage(roots: Sequence[Path | str]) -> NoNetworkScanResult`

### `friday.app.no_input_print_scanner`

- `_attribute_name(node: ast.AST) -> str | None`
- `_collect_builtin_aliases(tree: ast.AST) -> dict[str, str]`
- `_resolve_call_name(call_name: str, aliases: dict[str, str]) -> str`
- `scan_python_source_for_input_print(file_path: Path) -> list[InputPrintFinding]`
- `scan_python_file_for_input_print(path: Path | str) -> NoInputPrintScanResult`
- `iter_python_files(root: Path | str) -> tuple[Path, ...]`
- `scan_paths_for_input_print(roots: Sequence[Path | str]) -> NoInputPrintScanResult`

### `friday.app.forbidden_import_scanner`

- `_import_root(name: str) -> str`
- `_is_forbidden_import(name: str, forbidden_roots: Iterable[str]) -> bool`
- `scan_python_source_for_forbidden_imports(file_path: Path, forbidden_roots: Sequence[str]) -> list[ForbiddenImportFinding]`
- `scan_python_file_for_forbidden_imports(path: Path | str, forbidden_roots: Sequence[str] = ()) -> ForbiddenImportScanResult`
- `iter_python_files(root: Path | str) -> tuple[Path, ...]`
- `scan_python_paths_for_forbidden_imports(roots: Sequence[Path | str], forbidden_roots: Sequence[str] = ()) -> ForbiddenImportScanResult`

### `friday.app.approval_token_scanner`

- `scan_python_source_for_string_literals(file_path: Path) -> tuple[ApprovalTokenLiteral, ...]`
- `evaluate_approval_token_literals(literals: tuple[ApprovalTokenLiteral, ...]) -> ApprovalTokenScanResult`
- `scan_python_file_for_approval_tokens(path: Path | str) -> ApprovalTokenScanResult`
- `iter_python_files(root: Path | str) -> tuple[Path, ...]`
- `scan_paths_for_approval_token_regressions(roots: Sequence[Path | str]) -> ApprovalTokenScanResult`

### `friday.app.contact_context_preview`

- `normalize_contact_name(name: str) -> str`
- `normalize_contact_type(contact_type: str | None) -> ContactType`
- `build_contact_context_preview(contacts: Iterable[Mapping[str, Any]]) -> ContactContextPreview`

### `friday.app.contact_context_candidate + draft / prompt modules`

- `build_contact_prompt_question(display_name: str) -> str`
- `should_create_contact_prompt_candidate(sender: str, body: str) -> bool`
- `ContactPromptInputParseResult.__init__(self, value: str, choice: str | None, target_contact_id: str | None, raw: str, parse_error: str | None = None) -> None`
- `normalize_contact_prompt_input(raw_input: str | None) -> str`
- `parse_contact_prompt_input(raw_input: str | None) -> ContactPromptInputParseResult`
- `ContactPromptDraftFlowResult.__init__(self, state: str, raw_input: str | None = None, chosen_contact_id: str | None = None, candidate: dict[str, Any] | None = None, errors: list[str] | None = None) -> None`
- `prepare_contact_prompt_draft_flow(raw_input: str | None) -> ContactPromptDraftFlowResult`
- `apply_contact_prompt_draft_input(raw_input: str | None, contacts: Sequence[Mapping[str, Any]], suppression: Sequence[Mapping[str, Any]]) -> tuple[str | None, dict[str, Any] | None, str | None]`
- `ContactPromptPreview.__init__(self, contact_id: str, display_name: str, normalized_name: str, prompt_question: str, prompt_target_display: str, preview_lines: tuple[str, ...]) -> None`
- `build_contact_prompt_preview(contacts: Sequence[Mapping[str, Any]]) -> ContactPromptPreview`
- `ContactPromptUIRender.__init__(self, candidate: Mapping[str, Any], prompt: ContactPromptDraftFlowResult) -> None`
- `build_contact_prompt_text(display_name: str) -> str`
- `render_contact_prompt_ui(contact_name: str, normalized_name: str, category: str, notes: str | None = None) -> str`
- `ContactPromptSuppressionEntry.__init__(self, contact_id: str, normalized_sender: str, suppression_key: str, reason: str, created_at: str) -> None`
- `normalize_suppression_key(contact_id: str) -> str`
- `ContactPromptSuppressionEntry.__hash__(self) -> int`
- `ContactPromptSuppressionEntry.__eq__(self, other: object) -> bool`
- `_without_matching_entry(entries: list[ContactPromptSuppressionEntry], target_key: str) -> list[ContactPromptSuppressionEntry]`
- `mark_contact_prompt_skipped(suppression_file: Path, contact_id: str) -> None`
- `is_contact_prompt_suppressed(suppression_file: Path, contact_id: str) -> bool`
- `clear_contact_prompt_suppression(suppression_file: Path) -> int`
- `check_contact_context_fields_for_save(raw_payload: Mapping[str, Any]) -> ContactContextSaveGuardResult`

### `friday.app.contact_context_prompt_save_guard`

- `check_contact_context_fields_for_save(raw_payload: Mapping[str, Any]) -> ContactContextSaveGuardResult`

### `friday.app.contact_context_session_suppression`

- functions and class helpers listed under "contact_context_candidate + draft / prompt modules".

### `friday.app.obsidian_note_preview`

- `safe_obsidian_filename(value: str) -> str`
- `_frontmatter(kind: str, title: str) -> list[str]`
- `build_contact_note_preview(contact_context: Mapping[str, Any]) -> ObsidianNotePreview`
- `build_task_note_preview(task: Mapping[str, Any]) -> ObsidianNotePreview`
- `build_project_note_preview(project: Mapping[str, Any]) -> ObsidianNotePreview`
- `build_obsidian_target_path(kind: str, title: str, vault_root: Path | str, allowed_subdir: str | None = None) -> str`
- `build_obsidian_write_dry_run(task_records: Sequence[Mapping[str, Any]], contact_records: Sequence[Mapping[str, Any]], vault_root: Path | None = None, allowed_subdir: str | None = None, max_per_type: int | None = None) -> ObsidianWriteDryRun`
- `write_obsidian_note_with_approval(dry_run: ObsidianWriteDryRun, requested_token: str | None, db_path: Path | str | None = None, vault_root: Path | str | None = None, allowed_subdir: str | None = None) -> ObsidianWriteDryRun`

### `friday.app.obsidian_brain`

- `ObsidianBrainPreview.__init__(self, contact_previews: tuple[ObsidianNotePreview, ...], task_previews: tuple[ObsidianNotePreview, ...], project_previews: tuple[ObsidianNotePreview, ...], token_required: str) -> None`
- `ObsidianBrainPreview.all_previews(self) -> tuple[ObsidianNotePreview, ...]`
- `build_obsidian_brain_preview(task_records: Sequence[Mapping[str, Any]], contact_records: Sequence[Mapping[str, Any]], max_per_type: int = 3, vault_root: Path | str | None = None, allowed_subdir: str | None = None) -> ObsidianBrainPreview`

### `friday.app.obsidian_guard`

- `check_obsidian_note_for_write(text: str, vault_root: Path | str) -> ObsidianGuardResult`

### `friday.app.privacy_dashboard`

- `_flag_status(value: bool, expected_value: bool) -> str`
- `_count_label(count: int | None) -> str`
- `build_privacy_dashboard_summary(db_path: Path | str | None = None) -> PrivacyDashboardSummary`

### `friday.app.privacy_data_management`

- `_count_label(count: int | None) -> str`
- `build_privacy_data_management_inventory(db_path: Path | str | None = None) -> PrivacyDataManagementInventory`

### `friday.app.privacy_cleanup_db_preview`

- `_connect_read_only(db_path: Path | str) -> sqlite3.Connection`
- `_count_rejected_message_suggestions(connection: sqlite3.Connection) -> int`
- `_count_converted_task_suggestions(connection: sqlite3.Connection) -> int`
- `_count_contact_context(connection: sqlite3.Connection, contact_id: str) -> int`
- `_review_history_item(connection: sqlite3.Connection) -> PrivacyCleanupDBPreviewItem`
- `_contact_context_item(connection: sqlite3.Connection, contact_id: str) -> PrivacyCleanupDBPreviewItem`
- `_blocked_item(area_name: str, reason: str) -> PrivacyCleanupDBPreviewItem`
- `build_privacy_cleanup_db_preview(db_path: Path | str | None = None) -> PrivacyCleanupDBPreview`

### `friday.app.privacy_cleanup_db_guard`

- `_find_preview_item(preview: PrivacyCleanupDBPreview, target_area: str) -> PrivacyCleanupDBPreviewItem | None`
- `check_privacy_cleanup_db_write_allowed(*, preview: PrivacyCleanupDBPreview, requested_token: str | None) -> PrivacyCleanupDBGuardResult`

### `friday.app.privacy_cleanup_preview`

- `_count_label(count: int | None) -> str`
- `_is_under_allowed_root(target_path: str, allowed_root: str) -> bool`
- `build_privacy_cleanup_preview(db_path: Path | str | None = None, allowed_root: Path | str | None = None) -> PrivacyCleanupPreview`

### `friday.app.privacy_cleanup_writer`

- `_same_path(left: str | Path | None, right: str | Path | None) -> bool`
- `_planned_entries(target: Path) -> tuple[Path, ...]`
- `_has_symlink(entries: tuple[Path, ...]) -> bool`
- `_delete_target(target: Path) -> int`
- `apply_privacy_cleanup(target_path: str, dry_run: bool = True, allowed_root: str | None = None) -> PrivacyCleanupWriterResult`

### `friday.app.privacy_cleanup_write_guard`

- `_is_relative_to(path: Path, parent: Path) -> bool`
- `_is_root_path(path: Path) -> bool`
- `_has_sensitive_path_part(path: Path) -> bool`
- `_is_protected_project_file(path: Path, project_root: Path) -> bool`
- `_is_same_or_inside(path: Path, parent: Path) -> bool`
- `check_privacy_cleanup_write_allowed(*, target_path: str, backup_root: Path | None = None, restore_root: Path | None = None, exports_root: Path | None = None, db_path: Path | str | None = None, requested_token: str | None = None) -> PrivacyCleanupWriteGuardResult`

### `friday.app.restore_dry_run`

- `_is_relative_to(path: Path, parent: Path) -> bool`
- `_count_files(path: Path) -> int`
- `_section(name: str, path: Path, message: str) -> RestoreDryRunSection`
- `_has_forbidden_backup_content(backup_root: Path) -> bool`
- `_manifest_has_external_path(manifest: Mapping[str, Any]) -> bool`
- `_included_sections_from_manifest(manifest: dict[str, object]) -> tuple[str, ...]`
- `build_restore_dry_run(backup_root: Path, db_path: Path | None = None) -> RestoreDryRunResult`

### `friday.app.restore_writer`

- `_write_text_file(target_root: Path, relative_path: str, text: str) -> RestoreWrittenFile`
- `_copy_file(target_root: Path, source: Path, relative_path: str) -> RestoreWrittenFile`
- `_copy_directory(target_root: Path, source: Path, relative_root: Path, copied: list[RestoreWrittenFile]) -> None`
- `_write_restore_manifest(target_root: Path, result: RestoreDryRunResult) -> RestoreWrittenFile`
- `_restore_target_root(project_root: Path, timestamp: str) -> Path`
- `write_local_restore_copy(project_root: Path, backup_root: Path, scanner_smoke_passed: bool, requested_token: str | None = None, backup_dir: Path | None = None) -> RestoreWriteResult`

### `friday.app.restore_write_guard`

- `_is_relative_to(path: Path, parent: Path) -> bool`
- `check_restore_write_allowed(*, backup_path: Path | None = None, requested_token: str | None = None, restore_root: Path | str | None = None) -> RestoreWriteGuardResult`

### `friday.app.contact_context_save_guard`

- `check_contact_context_fields_for_save(raw_payload: Mapping[str, Any]) -> ContactContextSaveGuardResult`

### `friday.app.contact_context_session_suppression`

- same method block already listed above under context prompt section.

### `friday.app.sensitive_contact_context_guard`

- `normalize_sensitive_guard_text(text: str | None) -> str`
- `check_sensitive_contact_context(text: str | None) -> SensitiveContactContextGuardResult`

### `friday.app.privacy_cleanup_db_*`, `restore_*`, `contact_context_*`, and related `*guard` modules

- All call-path blockers and status models above are enumerated in their own module sections.

## 6) Functional build summary (by domain)

1. **Core entry / UI**
   - Launch via `python -m friday.main` to initialize storage and start `FridayInterface`.
   - Menus are terminal-driven and route to task, review, backup, and privacy sections.

2. **Data persistence and repositories**
   - Single DB-backed local store for tasks/messages/calendar/contact suggestions and task suggestions.
   - Repositories implement CRUD + query + transition logic.

3. **Suggestion engines**
   - Messages are classified by intent.
   - Message suggestions and task suggestions are generated locally.
   - All suggestion approvals/rejections/edits occur through UI actions and local status updates only.

4. **Backup/restore/import/export**
   - Preview-only flows for safety-first UX.
   - Write flows require explicit approvals, smoke checks, and hard token values.
   - Separate modules enforce guard policy and path restrictions.

5. **Privacy and safety**
   - Multiple scanners for prohibited patterns (network/input/print/forbidden imports/approval token drift).
   - Smoke checks produce a consolidated result for runtime transparency.
   - Cleanup and write operations are token-gated and guard-gated.

6. **Extensibility points**
   - Local model mock/preview interfaces and adapters already provide a safe path for later adapter wiring.
   - Contact and Obsidian workflows are preview-first and can be expanded into write-enabled features.

## 7) Current safety boundaries (important)

- No real email/WhatsApp/SMS/calendar/weather/music integrations are enabled in config.
- All local operations are the default unless a hard token and guard conditions pass.
- Sensitive data and cleanup actions are constrained to bounded roots and explicit confirmation paths.

## 8) Note on scope

This summary intentionally excludes tests and focuses on production code in `friday/main.py`, `friday/app/*`, `friday/agents/*`, and `friday/storage/*`.
