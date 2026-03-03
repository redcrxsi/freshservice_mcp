# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FreshService MCP is a Python 3.13+ MCP (Model Context Protocol) server that integrates AI models with Freshservice's ITSM platform. It uses FastMCP with async httpx for the Freshservice REST API v2. Originally 115+ individual tools were consolidated into 21 unified, action-based tools to stay under VS Code Copilot's 128-tool limit.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the server locally (all scopes)
uv run freshservice-mcp

# Run with specific scopes only
uv run freshservice-mcp --scope tickets changes

# Run via uvx (published package)
uvx freshservice-mcp
```

There is no test runner configured — `tests/test-fs-mcp.py` contains integration test functions meant to be run manually against a live Freshservice instance.

## Required Environment Variables

```bash
FRESHSERVICE_APIKEY=<api_key>
FRESHSERVICE_DOMAIN=<company>.freshservice.com
# Optional:
FRESHSERVICE_SCOPES=tickets,changes     # comma-separated, defaults to all
FRESHSERVICE_CACHE_DIR=~/.cache/freshservice_mcp
FRESHSERVICE_CACHE_TTL=3600             # seconds
```

## Architecture

### Entry Point & Scope Loading

`server.py` is a thin entry point (~90 lines). It creates a FastMCP instance, always registers 2 discovery tools, then selectively loads tool scopes via the **SCOPE_REGISTRY** in `tools/__init__.py`. Scope priority: CLI `--scope` args > `FRESHSERVICE_SCOPES` env var > all scopes.

### Source Layout

```
src/freshservice_mcp/
├── server.py          # Entry point, scope resolution, mcp.run(transport="stdio")
├── config.py          # Env vars, enums (TicketStatus, ChangePriority, etc.)
├── http_client.py     # api_get/post/put/delete, auth headers, error handling, pagination
├── discovery.py       # Form field discovery with 2-level TTL cache (memory + disk)
└── tools/
    ├── __init__.py    # SCOPE_REGISTRY: maps scope name → register_*_tools function
    ├── tickets.py     # 3 tools: manage_ticket, manage_ticket_conversation, manage_service_catalog
    ├── changes.py     # 5 tools: manage_change, manage_change_note/task/time_entry/approval
    ├── assets.py      # 3 tools: manage_asset, manage_asset_details, manage_asset_relationship
    ├── agents.py      # 2 tools: manage_agent, manage_agent_group
    ├── requesters.py  # 2 tools: manage_requester, manage_requester_group
    ├── solutions.py   # 1 tool: manage_solution (categories, folders, articles)
    ├── products.py    # 1 tool: manage_product
    └── misc.py        # 2 tools: manage_canned_response, manage_workspace
```

### Key Patterns

**Action-based tool dispatch**: Each tool function accepts an `action` string parameter (e.g., `"create"`, `"update"`, `"list"`, `"filter"`) and dispatches internally. This consolidates many CRUD operations into one tool.

**HTTP client** (`http_client.py`): All API calls go through `api_get/post/put/delete` which handle Basic auth (`FRESHSERVICE_APIKEY:X`), build URLs (`https://{domain}/api/v2/{path}`), and provide `handle_error()` for standardized error responses (`{"success": false, "error": "...", "details": ...}`).

**Pagination**: List endpoints return `parse_link_header()` results with `next`/`prev` page numbers from HTTP Link headers.

**Query filtering**: Freshservice filter endpoints require double-quoted query strings — `"status:3 AND priority:1"` is correct, bare `status:3` causes 500 errors.

**Discovery & caching** (`discovery.py`): Two-level cache (in-memory dict + disk JSON in `~/.cache/freshservice_mcp/`) with configurable TTL. Supports ticket, change, agent, requester field definitions and asset types.

### Adding a New Tool Module

1. Create `tools/<scope>.py` with a `register_<scope>_tools(mcp)` function
2. Inside it, define tools using `@mcp.tool()` async decorators following the action-dispatch pattern
3. Add the scope to `SCOPE_REGISTRY` in `tools/__init__.py`
4. Use `api_get/post/put/delete` from `http_client.py` — never construct auth or URLs manually
5. Return error dicts via `handle_error(e, "description")` in except blocks

### Legacy Reference

`server_legacy.py` (~4269 lines) is the pre-refactor monolith with all 115 tools in one file. It is kept as an archived reference but is not used.
