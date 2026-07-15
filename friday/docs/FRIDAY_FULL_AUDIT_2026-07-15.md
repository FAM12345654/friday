# Friday Full Audit — 2026-07-15

## Executive result

Friday is materially safer and more reliable after this audit. The highest-risk
network, OAuth, external-action, desktop/mobile credential, recurrence and
semantic-index defects were fixed and covered by regression tests.

Voicebox should be piloted, not installed as an immediate replacement. Friday's
current German Orpheus path remains the production default; the new optional
Voicebox adapter allows a controlled local A/B test through Voicebox v0.5+'s
`POST /generate/stream` WAV endpoint.

## Implemented findings

### API, network and clients

- API authentication now fails closed outside loopback when no strong token is
  configured; API docs are protected and CORS is restricted.
- Start scripts and containers default to loopback. Public quick tunnels refuse
  to start without a strong token.
- ICS URLs require HTTPS and reject credentials, non-443 ports, localhost,
  private/link-local/reserved addresses and unsafe DNS/redirect targets.
- Mobile stores the API token in Expo SecureStore and transmits it only to HTTPS
  or loopback destinations. Android cleartext traffic is disabled.
- Electron uses an isolated preload bridge, a custom origin, CSP, navigation and
  permission guards, and no renderer-side token persistence.
- WhatsApp bridge reads are token-gated and story/status broadcasts are ignored.

### OAuth

- Google OAuth now uses one-time, provider-bound state plus PKCE and binds the
  callback to the exact client-secret path.
- Microsoft OAuth now uses MSAL's authorization-code-flow transaction object,
  validates state and consumes each transaction once.
- Transactions expire after ten minutes. State is stored only as SHA-256 and
  its short-lived context is encrypted with Windows DPAPI or Fernet backed by a
  dedicated ledger secret/strong API token.
- SQLite `BEGIN IMMEDIATE` consumption makes state one-time across API workers
  and preserves an unexpired flow over a process restart.

### External actions

- Calendar create/delete/source-sync and due-reminder push delivery now use
  short-lived, payload-bound, one-time approvals.
- Multiple approvals for the same action cannot produce multiple side effects
  within the approval window.
- Calendar approvals bind the Google account fingerprint and target calendar.
- Delete previews bind event title, time, location and Google ETag; a changed
  event or secondary calendar is blocked.
- Push approvals bind the exact bounded message vector and token fingerprints;
  sending uses the approved token snapshot instead of re-reading recipients.
- Calendar source-sync is capped at 100 creates. Each source event gets a
  deterministic Google-compatible event ID, preventing duplicates after partial
  failure or retry.
- Approval-bearing HTTP responses use `Cache-Control: no-store`.
- Approval IDs are stored only as SHA-256. Approval deletion and the operation
  claim commit atomically in SQLite, preventing cross-worker double consume.
- Capacity exhaustion no longer evicts active flows: APIs fail closed with a
  retryable HTTP 429; unavailable secure OAuth storage returns HTTP 503.

### Data integrity

- Recurring task completion uses one SQLite `BEGIN IMMEDIATE` transaction for
  status change and next-instance creation. Concurrent completion calls create
  exactly one successor.
- Full semantic reindex uses an atomic snapshot replacement and removes stale
  documents; an empty source snapshot correctly clears the index.

## Voicebox decision

"Voicebox" is ambiguous:

1. Meta's 2023 Voicebox research model supports German and impressive editing,
   multilingual and zero-shot capabilities, but Meta explicitly did not release
   its model or code. It is therefore not a deployable Friday engine.
2. `jamiepine/voicebox` is a newer MIT-licensed local multi-engine studio. It
   hosts Qwen3-TTS, Chatterbox, Kokoro and other engines and exposes REST/MCP.

For Friday, the open-source studio is useful as an orchestration layer:

- Qwen3-TTS supports German, instruction control and cloning. Voicebox estimates
  about 2 GB VRAM for 0.6B and 6 GB for 1.7B.
- Chatterbox Multilingual supports German and is estimated near 3 GB VRAM.
- Voicebox can return synchronous WAV bytes through `/generate/stream`, matching
  Friday Mobile's existing audio pipeline. The route buffers generation before
  returning audio, so it is not low-latency token streaming.
- It also introduces a larger dependency/runtime surface, first-use model
  downloads, profile management and a second local database.
- No trustworthy apples-to-apples German benchmark against Friday's current
  Orpheus-Kartoffel/Jana setup was found.

Decision: keep Orpheus for German and Kokoro for English as default. Pilot only
the German path through Voicebox, using Qwen Base 0.6B with Jana's reference
profile. Qwen CustomVoice is not suitable for voice continuity because it uses
preset voices. Promote only if a blinded local test wins on pronunciation,
naturalness, latency and failure rate.

### Required A/B gate

Use at least 30 Friday-specific German utterances:

- dates, times, names, email addresses and mixed German/English product names;
- short confirmations, longer morning briefings and emotionally neutral alerts;
- cold start and ten warm generations per engine.

Record median and p95 total latency, real-time factor, peak VRAM/RAM, failure
rate, word omissions/repetitions and a blinded 1–5 human rating. Voicebox wins
only if it improves the human score without exceeding the 8-GB GPU budget or
materially worsening p95 latency.

The local `scripts/benchmark_voice_tts.py` harness now automates the non-human
part of this comparison. It benchmarks exactly one engine per process, permits
only loopback endpoints, blocks redirects/proxies, caps response size and
reports complete-WAV latency, p50/p95, WAV duration, real-time factor and
structured failures as JSON or CSV.

## Verification

- Full Python suite: 1,613 passed, 4 skipped, with one upstream TestClient
  warning.
- Focused approval/calendar/push/source-sync suite: 51 passed.
- Focused task race and semantic-index suites: 59 passed.
- Persistent-ledger tests cover cross-instance restart, parallel consume,
  expiry, backward clock jumps, encrypted row swapping and capacity handling.
- Benchmark harness has 21 offline fake-transport cases; no TTS HTTP call is
  required for its regression tests.
- Android Expo export completed successfully.
- Expo dependency check reports all dependencies up to date.
- `git diff --check` reports no whitespace errors.

No real calendar write/delete, push delivery, OAuth callback, public tunnel or
Voicebox model download was triggered during the audit.

## Residual risks and next order

1. Run the Voicebox A/B gate on the actual PC and voice profile; research alone
   cannot establish that one voice sounds better to the owner.
2. SQLite provides cross-worker safety on one local host, not multi-host
   coordination. A future distributed Friday deployment needs PostgreSQL or
   Redis and a provider-level exactly-once strategy for unknown external results.
3. Add controlled real-provider smoke tests in a dedicated test calendar and
   test push device; hermetic tests intentionally do not prove provider uptime.
4. The remaining test warning comes from FastAPI/Starlette's TestClient adapter;
   Friday's own `on_event`, Pydantic `dict()` and tar extraction deprecations
   were removed in Phase 2.

## Primary sources

- Meta Voicebox release status and capabilities:
  https://ai.meta.com/blog/voicebox-generative-ai-model-speech/
- Open-source Voicebox repository and API:
  https://github.com/jamiepine/voicebox
- Voicebox generation architecture and VRAM estimates:
  https://docs.voicebox.sh/developer/tts-generation
- Qwen3-TTS official repository and German benchmark tables:
  https://github.com/QwenLM/Qwen3-TTS
- Chatterbox official multilingual repository:
  https://github.com/resemble-ai/chatterbox
- Orpheus-FastAPI German/OpenAI-compatible implementation:
  https://github.com/Lex-au/Orpheus-FastAPI
- Google OAuth native-app and PKCE guidance:
  https://developers.google.com/identity/protocols/oauth2/native-app
- Microsoft MSAL authorization-code-flow guidance:
  https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens
