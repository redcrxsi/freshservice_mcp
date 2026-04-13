# Prompt: Add Journeys Scope to FreshService MCP

## Context check first
Before starting, read `CLAUDE.md` and `README.md`. Both are slightly out of date — `tools/projects.py` exists and is registered in `SCOPE_REGISTRY`, but neither doc mentions it. Treat the architecture description as accurate otherwise.

## Task
Add a new "journeys" scope to this project that wraps the Freshservice Journey API. The full API spec is in `FreshService Journey API.pdf` at the repo root — read it first.

Follow the existing patterns exactly (see `tools/changes.py` and `tools/projects.py` as references). Specifically:

1. Create `src/freshservice_mcp/tools/journeys.py` with a `register_journeys_tools(mcp)` function.
2. Use the action-dispatch pattern — each tool takes an `action` string and dispatches internally. Use `api_get/post/put/delete` from `http_client.py` (never hand-roll auth or URLs). Wrap exceptions with `handle_error(e, "...")`.
3. Register the new scope in `SCOPE_REGISTRY` in `tools/__init__.py` and add the import + `__all__` entry.

Consolidate the 10 endpoints into 2 tools to stay under the 128-tool limit:

### `manage_journey_config` — actions:
- `list` → GET /api/v2/journeys/configs (supports `page`)
- `get_data_fields` → GET /api/v2/journeys/configs/{id}/data-fields

### `manage_journey_request` — actions:
- `create` → POST /api/v2/journeys/requests (body: `journey_id`, `initiator_data`)
- `get` → GET /api/v2/journeys/requests/{id}
- `list` → GET /api/v2/journeys/requests (supports `filter` [completed|all|in_progress|my_completed|my_in_progress], `order_type` [asc|desc], `page`, `per_page`)
- `filter` → POST /api/v2/journeys/requests/view (body: `data.query.filter` with attributes array; supports `page` query param). Filterable fields: `type`, `requester_id`, `journey_id`, `owner_id`, `requested_for_id`, `status`, `created_at`. Status values: In Progress=1, Completed=2, Failed=3, Cancelled=5, Expired=8.
- `update` → PATCH /api/v2/journeys/requests/{id} (body: `initiator_data`)
- `cancel` → PUT /api/v2/journeys/requests/{id}/cancel
- `delete` → DELETE /api/v2/journeys/requests/{id} (returns 204)
- `list_activities` → GET /api/v2/journeys/requests/{id}/activities (optional `activity_type` query param: EMAIL | SERVICE_REQUEST | PLAIN | TASK)

### Also:
- Add a `JourneyRequestStatus` enum to `config.py` (IN_PROGRESS=1, COMPLETED=2, FAILED=3, CANCELLED=5, EXPIRED=8).
- Update `CLAUDE.md`: add `journeys.py` to the Source Layout block, bump the tool count, and fix the existing omission — `projects.py` is currently missing from that block.
- Update `README.md`: add a "Journey Management" section to the supported modules list and tools table, mirroring the style of the Change Management section. Also add a Projects section if it's missing.

## Testing (READ-ONLY first, then sandboxed writes)
After implementation, run end-to-end tests against the live Freshservice instance, but **do not touch production data**. Follow this protocol:

1. **Read-only sanity checks first** (safe):
   - `manage_journey_config` action `list` — confirm published journeys come back.
   - For one returned journey id, call `get_data_fields`.
   - `manage_journey_request` action `list` with `filter=all` and `per_page=5`.
   - `filter` action with a narrow query (e.g., `status is_in [2]` for completed).
   - For one returned request id, call `get` and `list_activities`.

2. **Write tests** — only proceed if the user confirms. Before any create/update/cancel/delete:
   - Ask the user explicitly which `journey_id` is safe to use (a test/sandbox journey, not production onboarding).
   - Use a clearly-marked test value in `initiator_data` (e.g., `cf_text: "MCP-TEST-<timestamp>"`, test email like `mcp-test@example.com`).
   - Sequence: `create` → `get` (verify) → `update` → `cancel` → `delete`. Print the response from each step.
   - If anything looks off, stop and report — do not retry blindly.

3. Add the test scaffolding as new functions in `tests/test-fs-mcp.py` following the existing style there. Mark journey write tests clearly with comments like `# DESTRUCTIVE — requires test journey_id`.

Do not run write tests automatically. Print the proposed plan and wait for go-ahead.
