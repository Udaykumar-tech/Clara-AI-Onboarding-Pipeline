# Clara Answers – Zero-Cost Demo-to-Agent Automation Pipeline

> **Assignment Submission** | Build a zero-cost automation pipeline: Demo Call → Retell Agent Draft → Onboarding Updates → Agent Revision

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture and Data Flow](#architecture-and-data-flow)
3. [Folder Structure](#folder-structure)
4. [How to Run Locally](#how-to-run-locally)
5. [How to Plug In the Dataset Files](#how-to-plug-in-the-dataset-files)
6. [Pipeline Commands Reference](#pipeline-commands-reference)
7. [Output Format](#output-format)
8. [Versioning and Changelog](#versioning-and-changelog)
9. [Where Outputs Are Stored](#where-outputs-are-stored)
10. [Zero-Cost Stack](#zero-cost-stack)
11. [Known Limitations](#known-limitations)
12. [What I Would Improve with Production Access](#what-i-would-improve-with-production-access)
13. [Data Privacy](#data-privacy)

---

## Project Overview

This pipeline automates the conversion of raw demo call transcripts and onboarding call data into structured, versioned Retell AI agent configurations — without spending a single dollar.

**Pipeline A** takes a demo call transcript and produces:
- A structured `account_memo.json` (v1)
- A `agent_spec.json` (Retell Agent Draft Spec v1)

**Pipeline B** takes an onboarding call transcript or form data and produces:
- An updated `account_memo.json` (v2)
- An updated `agent_spec.json` (v2)
- A `changes.json` changelog showing exactly what changed and why

The workflow is fully local, CLI-driven, idempotent, and reproducible.

---

## Architecture and Data Flow

```
                        PIPELINE A
                        ----------
  transcript.txt
        │
        ▼
  extract_demo.py          ← Regex + rule-based extraction (zero LLM cost)
        │
        ▼
  account_memo.json (v1)   ← Structured account data per assignment schema
        │
        ▼
  generate_prompt.py       ← Template-based prompt generator
        │
        ▼
  agent_spec.json (v1)     ← Retell Agent Draft Spec

                        PIPELINE B
                        ----------
  onboarding_transcript.txt / onboarding_form.json
        │
        ▼
  onboarding_demo.py       ← Extracts updates from onboarding input
        │
        ▼
  apply_patch.py           ← Merges updates into v1 memo, preserves unchanged fields
        │
        ▼
  account_memo.json (v2)   ← Updated memo with confirmed operational rules
        │
        ▼
  generate_prompt.py       ← Regenerates prompt with v2 data
        │
        ▼
  agent_spec.json (v2)     ← Updated Retell Agent Spec
        │
        ▼
  changes.json             ← Changelog: what changed, old value, new value, reason
```

**Key design decisions:**
- All extraction uses regex and rule-based parsing — zero paid LLM calls.
- Missing fields are never hallucinated; they are captured in `questions_or_unknowns`.
- Versioning is additive: v2 patches v1 without overwriting unrelated fields.
- The pipeline is idempotent — running it twice produces the same outputs.

---

## Folder Structure

```
clara-pipeline/
│
├── datasets/
│   ├── demo/
│   │   ├── transcript_001.txt
│   │   ├── transcript_002.txt
│   │   ├── transcript_003.txt
│   │   ├── transcript_004.txt
│   │   └── transcript_005.txt
│   └── onboarding/
│       ├── onboarding_001.txt
│       ├── onboarding_002.txt
│       ├── onboarding_003.txt
│       ├── onboarding_004.txt
│       └── onboarding_005.txt
│
├── scripts/
│   ├── extract_demo.py         ← Extracts structured memo from demo transcript
│   ├── generate_prompt.py      ← Generates Retell agent spec from memo
│   ├── onboarding_demo.py      ← Extracts updates from onboarding input
│   └── apply_patch.py          ← Applies patch to existing memo, creates changelog
│
├── outputs/
│   └── accounts/
│       └── <account_id>/
│           ├── v1/
│           │   ├── account_memo.json
│           │   └── agent_spec.json
│           ├── v2/
│           │   ├── account_memo.json
│           │   └── agent_spec.json
│           └── changes.json
│
├── pipeline.py                 ← Main CLI entry point
├── requirements.txt
└── README.md
```

---

## How to Run Locally

### Prerequisites

- Python 3.8 or higher
- pip

### Step 1 – Clone the Repository

```bash
git clone https://github.com/<your-username>/clara-pipeline.git
cd clara-pipeline
```

### Step 2 – Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` contents:

```
regex
pathlib
json
argparse
```

> All dependencies are standard Python libraries or lightweight packages. No paid APIs. No external services required.

### Step 3 – Add Your Dataset Files

Place your transcript files in the correct folders:

```
datasets/demo/transcript_001.txt      ← demo call transcripts
datasets/onboarding/onboarding_001.txt ← onboarding call transcripts
```

Accepted input formats:
- `.txt` plain text transcripts (primary)
- `.json` structured onboarding form submissions

### Step 4 – Run the Full Pipeline

**Single account (demo + onboarding):**

```bash
python pipeline.py extract --input datasets/demo/transcript_001.txt --account_id ACC_001
python pipeline.py generate --account_id ACC_001
python pipeline.py onboarding --input datasets/onboarding/onboarding_001.txt --account_id ACC_001
python pipeline.py patch --account_id ACC_001
```

**Batch run (all 5 accounts):**

```bash
python pipeline.py batch --demo_dir datasets/demo/ --onboarding_dir datasets/onboarding/
```

---

## How to Plug In the Dataset Files

1. Name demo transcripts as `transcript_001.txt` through `transcript_005.txt` and place them in `datasets/demo/`.
2. Name onboarding transcripts as `onboarding_001.txt` through `onboarding_005.txt` and place them in `datasets/onboarding/`.
3. The pipeline auto-assigns `account_id` values as `ACC_001` through `ACC_005` based on file numbering.
4. If you have structured onboarding form JSON instead of a transcript, place it as `onboarding_001.json` — the pipeline detects the format automatically.

> **Audio files (.m4a, .mp3, .wav):** If you have raw recordings instead of transcripts, run Whisper locally first (see Optional: Transcription below).

### Optional: Transcription with Whisper (Zero-Cost)

```bash
pip install openai-whisper
whisper datasets/demo/recording_001.m4a --model base --output_format txt --output_dir datasets/demo/
```

Rename the output to `transcript_001.txt` and proceed normally.

---

## Pipeline Commands Reference

| Command | Description |
|---|---|
| `pipeline.py extract` | Extract account memo (v1) from a demo transcript |
| `pipeline.py generate` | Generate Retell agent spec (v1) from account memo |
| `pipeline.py onboarding` | Extract updates from onboarding transcript or form |
| `pipeline.py patch` | Apply updates to create v2 memo + agent spec + changelog |
| `pipeline.py batch` | Run full pipeline on all files in demo and onboarding dirs |

**Full options:**

```bash
python pipeline.py extract --input <path_to_transcript> --account_id <id>
python pipeline.py generate --account_id <id>
python pipeline.py onboarding --input <path_to_onboarding> --account_id <id>
python pipeline.py patch --account_id <id>
python pipeline.py batch --demo_dir datasets/demo/ --onboarding_dir datasets/onboarding/
```

---

## Output Format

### 1) Account Memo JSON (`account_memo.json`)

```json
{
  "account_id": "ACC_001",
  "company_name": "ABC Fire Protection",
  "business_hours": {
    "days": "Monday to Friday",
    "start": "08:00",
    "end": "17:00",
    "timezone": "America/Chicago"
  },
  "office_address": "123 Main St, Dallas, TX 75201",
  "services_supported": [
    "Fire sprinkler inspection",
    "Fire alarm monitoring",
    "Emergency sprinkler repair"
  ],
  "emergency_definition": [
    "Active sprinkler leak",
    "Fire alarm triggered",
    "Water flowing from system"
  ],
  "emergency_routing_rules": {
    "primary": "On-call technician: (555) 100-2000",
    "fallback": "Dispatch manager: (555) 100-3000",
    "timeout_seconds": 30
  },
  "non_emergency_routing_rules": {
    "action": "Collect name, number, service type",
    "follow_up": "Next business day callback"
  },
  "call_transfer_rules": {
    "timeout_seconds": 30,
    "retries": 2,
    "on_fail": "Apologize, assure callback within 15 minutes"
  },
  "integration_constraints": [
    "Never create sprinkler jobs in ServiceTrade",
    "Non-emergency extinguisher calls can be collected after hours"
  ],
  "after_hours_flow_summary": "Greet caller, confirm emergency status, collect name/number/address for emergencies, attempt transfer, fallback if fails, assure follow-up.",
  "office_hours_flow_summary": "Greet caller, ask purpose, collect name and number, route to correct department or technician, fallback if transfer fails, confirm next steps.",
  "questions_or_unknowns": [
    "Exact after-hours transfer number not confirmed in demo call",
    "ServiceTrade integration scope unclear"
  ],
  "notes": "Client expressed interest in reducing after-hours call volume by 60%.",
  "version": "v1",
  "source": "demo_call"
}
```

### 2) Retell Agent Draft Spec (`agent_spec.json`)

```json
{
  "agent_name": "Clara - ABC Fire Protection",
  "version": "v1",
  "voice_style": "Professional, calm, empathetic",
  "key_variables": {
    "timezone": "America/Chicago",
    "business_hours": "Monday to Friday, 8:00 AM to 5:00 PM",
    "office_address": "123 Main St, Dallas, TX 75201",
    "emergency_transfer_number": "(555) 100-2000",
    "fallback_transfer_number": "(555) 100-3000"
  },
  "tool_invocation_placeholders": {
    "transfer_call": "[TRANSFER_TOOL]",
    "log_call": "[LOG_TOOL]"
  },
  "call_transfer_protocol": "Attempt transfer to emergency line. If no answer within 30 seconds, retry once. If still no answer, attempt fallback number.",
  "fallback_protocol": "If all transfers fail: apologize sincerely, assure the caller a technician will call back within 15 minutes, and log the call details.",
  "system_prompt": "<see generated prompt below>",
  "source": "demo_call"
}
```

### Generated System Prompt Structure

The auto-generated system prompt follows the required flow:

**Business Hours Flow:**
1. Greeting
2. Ask purpose of call
3. Collect caller name and callback number
4. Route or transfer based on call type
5. Fallback script if transfer fails
6. Confirm next steps with caller
7. Ask if anything else is needed
8. Close call

**After-Hours Flow:**
1. Greeting
2. Ask purpose of call
3. Confirm if it is an emergency
4. If emergency: collect name, number, address immediately
5. Attempt transfer to on-call technician
6. If transfer fails: apologize, assure quick follow-up
7. If non-emergency: collect details, confirm follow-up during business hours
8. Ask if anything else is needed
9. Close call

> The prompt never mentions function calls or tool names to the caller.

---

## Versioning and Changelog

When onboarding data is processed, the pipeline produces:

```
outputs/accounts/ACC_001/
├── v1/
│   ├── account_memo.json    ← Based on demo call (assumptions allowed)
│   └── agent_spec.json
├── v2/
│   ├── account_memo.json    ← Updated with confirmed onboarding data
│   └── agent_spec.json
└── changes.json             ← Diff of every changed field
```

### Example `changes.json`

```json
{
  "account_id": "ACC_001",
  "updated_at": "2025-07-10T14:32:00Z",
  "source": "onboarding_call",
  "changes": [
    {
      "field": "business_hours.end",
      "old_value": "17:00",
      "new_value": "18:00",
      "reason": "Onboarding call confirmed extended hours on Fridays"
    },
    {
      "field": "emergency_routing_rules.primary",
      "old_value": "Unknown",
      "new_value": "(555) 100-2000",
      "reason": "Confirmed on-call number during onboarding"
    },
    {
      "field": "questions_or_unknowns",
      "old_value": ["After-hours transfer number not confirmed"],
      "new_value": [],
      "reason": "All unknowns resolved during onboarding call"
    }
  ]
}
```

Versioning rules:
- `v1` is always generated from the demo call. It may contain open questions.
- `v2` is generated after onboarding. It patches only the fields that changed.
- Unrelated fields are never overwritten.
- Conflicts are resolved explicitly and logged in `changes.json`.

---

## Where Outputs Are Stored

All outputs are written to:

```
outputs/accounts/<account_id>/v1/   ← Post demo call
outputs/accounts/<account_id>/v2/   ← Post onboarding
outputs/accounts/<account_id>/changes.json
```

If running the batch command, all 5 accounts are written to their respective folders automatically.

---

## Zero-Cost Stack

| Component | Tool Used | Cost |
|---|---|---|
| Transcript input | Plain `.txt` files | Free |
| Extraction engine | Python + Regex | Free |
| Prompt generation | Python templates | Free |
| Versioning and storage | Local JSON files + Git | Free |
| Transcription (optional) | Whisper (local, open-source) | Free |
| Automation orchestrator | `pipeline.py` CLI | Free |
| LLM calls | None (rule-based only) | Free |
| Retell integration | Agent Spec JSON output + manual import guide | Free |

**Total cost: $0.00**

No paid APIs, no subscriptions, no credits consumed.

---

## Known Limitations

1. **Onboarding calls are simulated** — The `onboarding_demo.py` script generates onboarding updates from onboarding transcripts using the same regex-based extraction as demo transcripts. In production, this would be connected to a Retell webhook or a structured onboarding form submission.

2. **Audio transcription is optional** — If only `.m4a` or `.mp3` audio files are provided, Whisper must be run locally first. The pipeline itself accepts `.txt` transcripts as primary input, as permitted by the assignment instructions.

3. **Tool invocation placeholders are simplified** — The `agent_spec.json` includes `[TRANSFER_TOOL]` and `[LOG_TOOL]` placeholders instead of full Retell API tool definitions, since Retell programmatic agent creation is not available on the free tier.

4. **Task tracker integration is not connected** — The assignment suggests Asana or equivalent for task tracking. This pipeline logs all runs locally. In production, this would POST to an Asana or Linear task via their free-tier API.

5. **Extraction quality depends on transcript clarity** — The regex-based extractor performs well on structured transcripts. Highly unstructured or very short transcripts may produce more `questions_or_unknowns` entries.

---

## What I Would Improve with Production Access

1. **Replace regex extraction with a local LLM** — A locally hosted model (e.g. Ollama + Mistral 7B) would significantly improve extraction quality on ambiguous transcripts, at zero cost.

2. **Connect to Retell API** — With a paid or trial Retell account, `agent_spec.json` could be POSTed directly to the Retell API to auto-create and update agents programmatically.

3. **Add n8n workflow** — The CLI pipeline could be wrapped in an n8n self-hosted workflow for a no-code trigger layer (e.g. new file in Google Drive → run pipeline → save outputs → notify team on Slack).

4. **Add a diff viewer UI** — A simple web page using React or plain HTML could render `changes.json` as a visual side-by-side diff between v1 and v2 fields.

5. **Add Supabase storage** — Replace local JSON files with a Supabase free-tier database for multi-user access, search, and audit logging.

6. **Add Asana task creation** — On each new demo call processed, auto-create an Asana task in the client onboarding board using the free Asana API.

7. **Batch summary metrics** — After batch processing all 10 files, output a `batch_summary.json` with extraction confidence scores, unresolved unknowns count, and versioning stats per account.

---

## Data Privacy

- Raw audio files (`.m4a`, `.mp3`, `.wav`) are excluded from the repository via `.gitignore`.
- No customer personal data is committed to Git beyond what appears in the provided dataset.
- Transcripts and outputs are treated as confidential per the assignment instructions.

`.gitignore` includes:

```
datasets/demo/*.m4a
datasets/demo/*.mp3
datasets/demo/*.wav
datasets/onboarding/*.m4a
datasets/onboarding/*.mp3
datasets/onboarding/*.wav
```

---

## Retell Manual Import Guide

Since programmatic Retell agent creation requires a paid plan, follow these steps to import the generated agent spec manually:

1. Log into your Retell account at [app.retellai.com](https://app.retellai.com).
2. Click **Create Agent**.
3. Set the agent name from `agent_spec.json → agent_name`.
4. Paste the `system_prompt` field into the **System Prompt** box.
5. Set the voice style from `voice_style`.
6. Configure transfer numbers from `call_transfer_protocol` and `fallback_protocol`.
7. Save and test the agent.

Repeat for v2 by updating the same agent with the v2 `agent_spec.json` values.

---


*Built for Clara Answers Intern Assignment — Zero-Cost Automation Pipeline*
