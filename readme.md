# PAC Filing Classifier — Canada (v1)

A multi-agent system that helps pharmaceutical regulatory professionals determine the correct filing type for post-approval changes (PACs) under Health Canada guidance.

---

## What This System Does

When a drug product manufacturer wants to make a change to an approved product — a new manufacturing site, a change in coating, a revised shelf life — they must file a submission with the health authority. The type of submission (filing type) depends on the nature of the change, the conditions it meets, and the guidance issued by the relevant health authority.

This system takes a plain-text description of a proposed change, asks the user a series of targeted questions, matches the change to the relevant section of Health Canada's guidance, verifies that the applicable conditions are met, and outputs the correct filing type along with the required supporting documents and the exact guideline section.

---

## Why This Was Built

Determining the correct filing type manually requires:
- Reading and interpreting dense regulatory guidance documents
- Correctly identifying the change item from a broader change description
- Matching the change to the right section of the right guideline
- Verifying that all conditions are met before committing to a filing type

This process is time-consuming, error-prone, and inaccessible to teams without deep regulatory expertise. This system automates the lookup and verification steps while preserving human judgment where the guidance is ambiguous.

---

## Architecture

The system is built as a pipeline of four agents. Each agent has one job. Outputs flow from one agent to the next.

```
User Input (free text change description)
            │
            ▼
    ┌───────────────┐
    │   Agent 1     │  Change Extractor
    │               │  Extracts discrete change items from the description
    └───────┬───────┘
            │  e.g. ["change in crystallization temperature range"]
            ▼
    ┌───────────────┐
    │   Agent 2     │  Candidate Filter
    │               │  Filters knowledge base by market, product type,
    │               │  material type → returns candidate rows
    └───────┬───────┘
            │  e.g. 4 candidate rows for "change in approved design space"
            ▼
    ┌───────────────┐
    │   Agent 3     │  Row Isolator
    │               │  Narrows candidates using dosage form and release
    │               │  mechanism, then verifies conditions one by one
    └───────┬───────┘
            │  e.g. exact matched row + all conditions verified
            ▼
    ┌───────────────┐
    │   Agent 4     │  Presenter
    │               │  Displays filing type, guideline section,
    │               │  and required supporting documents
    └───────────────┘
```

---

## Agent Design

### Agent 1 — Change Extractor
- **Input:** Free text change description from the user
- **Job:** Identify and extract discrete change items. A single description may contain multiple change items (e.g. a packaging change and a shelf life change are two separate items that may have different filing requirements).
- **Output:** A list of change items in plain language
- **Technology:** LLM call with a domain-specific extraction prompt

### Agent 2 — Candidate Filter
- **Input:** Change items + market + product type + material type (collected via dialogue)
- **Job:** Filter the knowledge base to rows that match the change item and the user's context
- **Output:** A shortlist of candidate rows from the knowledge base
- **Technology:** Pandas dataframe filter — no LLM needed here. Market, product type, and material type are structured columns with exact values. An LLM is used only to match the extracted change item to the `change_item` column semantically.
- **Design note:** Agent 2 asks for market, product type, and material type through a short dialogue before filtering. These three fields significantly reduce the candidate set.

### Agent 3 — Row Isolator
- **Input:** Candidate rows from Agent 2
- **Job:** Narrow down to the exact matching row and verify the user meets the required conditions
- **Flow:**
  1. Ask for dosage form → filter candidates
  2. Ask for release mechanism → filter further
  3. If one row remains → proceed to condition verification
  4. If multiple rows remain → use conditions to isolate
  5. Ask conditions one by one → verify eligibility
- **Output:** Exact matched row with all conditions confirmed, or a deferral flag
- **Deferral condition:** If the row cannot be isolated, or if any condition is not met, the system outputs: *"This particular case should be discussed with a regulatory expert as the guideline doesn't have enough information."* The system does not guess.
- **Technology:** LLM call for condition interpretation and dialogue management

### Agent 4 — Presenter
- **Input:** Matched row from Agent 3
- **Job:** Display the result clearly and completely
- **Output:**
  - Filing type (e.g. Annual Notification, Prior Approval Supplement)
  - Guideline section (exact reference in Health Canada guidance)
  - Supporting documents required (numbered list)
- **Technology:** Structured output formatting, no LLM reasoning required

---

## Knowledge Base

**Source:** Health Canada — Appendix 1: Quality Post-NOC Changes (Human Pharmaceuticals)

**Format:** ODS spreadsheet (`canada2.ods`) with one row per change scenario

**Schema:**

| Column | Description |
|---|---|
| `product_type` | Small Molecules / Biologics |
| `material_type` | Drug Substance / Drug Product |
| `change_type` | Parent change category (e.g. Change in Batch Size) |
| `change_item` | Specific change description (the matchable unit) |
| `dosage_form` | Applicable dosage form if specified |
| `release_mechanism` | IR / MR / NA |
| `market` | Jurisdiction (Canada for v1) |
| `change_scenario` | Scenario label where multiple filing paths exist |
| `conditions` | Numbered list of conditions that must be met |
| `filing_type` | The required filing type if conditions are met |
| `guideline_section` | Exact reference in the Health Canada guideline |
| `supporting_data` | Numbered list of documents required for filing |

**Coverage:** 106 rows, 89 unique change items, 13 change types

**Key structural note:** Some change items have multiple rows (multiple scenarios). Agent 2 may return more than one row for the same change item — this is expected and handled by Agent 3.

---

## System Outcomes

The system produces exactly one of three outcomes:

1. **Match found, all conditions met** → Agent 4 displays the filing type, guideline section, and document list
2. **Match not isolated** → System defers to regulatory expert
3. **Match found but conditions not met** → System defers to regulatory expert

---

## Design Principles

**One agent, one job.** Each agent does exactly one thing. This makes the system testable, debuggable, and improvable — a failure can be traced to a specific agent without unpacking the whole pipeline.

**Don't use an LLM where a filter works.** Agent 2's core logic is a pandas filter. LLMs are used only where language understanding is genuinely required — extraction (Agent 1), condition verification (Agent 3), and presentation (Agent 4).

**The system never recommends what it cannot verify.** If conditions are not met or the change cannot be matched, the system defers. It does not guess a filing type or approximate a match.

**Domain knowledge drives the architecture.** The four-agent design mirrors how a regulatory expert actually thinks through a filing decision — not how a generic RAG system would approach document retrieval. The knowledge base schema was designed around the structure of the actual Health Canada guidance document, including its nested conditions and multi-scenario entries.

---

## Roadmap

| Phase | Scope |
|---|---|
| v1 (current) | Canada — Health Canada Post-NOC Changes guidance |
| v2 | Add FDA — SUPAC-IR, SUPAC-MR, BACPAC |
| v3 | Add EMA — Variations guidance |
| v4 | Multi-jurisdiction comparison — same change, all markets |
| v5 | Web interface |

---

## Tech Stack

- **Language:** Python
- **LLM:** Google Gemini (via `google-generativeai`)
- **Data:** Pandas + ODS spreadsheet
- **Interface:** Command line (v1)

---

## Project Status

🟡 In development — architecture complete, knowledge base built, agents in progress

---

## Author

Built as a career transition project from pharmaceutical regulatory intelligence into agentic AI systems engineering.