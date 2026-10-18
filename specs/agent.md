# AUCoFF Agent Spec

| Field | Value |
|-------|-------|
| Status | Draft |
| Version | 0.1.0 |
| Owner | TODO |
| Last updated | TODO |

> Purpose: defines the agentic AI layer: roles, tools, orchestration, guardrails and evaluation.

Related: [constitution.md](constitution.md) (section 5) · [spec.md](spec.md) · [backend-spec.md](backend-spec.md) · [database-spec.md](database-spec.md)

## 1. Agent Overview
<!-- Single agent or multi-agent? Why? -->
TODO

## 2. Agent Roster
| ID | Agent | Responsibility | Inputs | Outputs | Autonomy level |
|----|-------|----------------|--------|---------|----------------|
| AG-1 | TODO (e.g. Control Mapper) | TODO | TODO | TODO | TODO |
| AG-2 | TODO (e.g. Evidence Collector) | TODO | TODO | TODO | TODO |
| AG-3 | TODO (e.g. Gap Analyzer) | TODO | TODO | TODO | TODO |

## 3. Orchestration
<!-- Pattern (supervisor, pipeline, graph), state handling, retries, concurrency. Diagram welcome. -->
TODO

## 4. Models
| Purpose | Model | Provider | Params | Fallback |
|---------|-------|----------|--------|----------|
| TODO | TODO | TODO | TODO | TODO |

## 5. Tools
| Tool | Description | Side effects | Permissions | Approval required |
|------|-------------|--------------|-------------|-------------------|
| TODO | TODO | TODO | TODO | TODO |

## 6. Knowledge and Memory
- RAG sources (regulations, policies, evidence): TODO
- Vector store: PostgreSQL `pgvector` (`embeddings` table, always tenant-filtered, DB-6); schema in [database-spec.md](database-spec.md) section 3.4
- Chunking / refresh cadence: TODO
- Short-term vs long-term memory: TODO

## 7. Prompts
<!-- Location, versioning scheme, template variables. -->
TODO

## 8. Guardrails
- Input validation / prompt injection defence: TODO
- Output validation (schema, citations to control IDs): TODO
- PII redaction before LLM calls: TODO
- Disallowed actions: TODO

## 9. Human-in-the-Loop
| Action | Trigger | Approver role | Timeout / default |
|--------|---------|---------------|-------------------|
| TODO | TODO | TODO | TODO |

## 10. Evaluation
- Golden datasets: TODO
- Metrics (accuracy, citation correctness, hallucination rate): TODO
- Regression gate in CI: TODO

## 11. Audit Logging
<!-- What is logged per agent run: prompt version, inputs, tool calls, outputs, approvals. Retention. -->
TODO

## 12. Failure Handling and Cost Controls
TODO
