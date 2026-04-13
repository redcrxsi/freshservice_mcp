# Freshservice MCP Server

[![smithery badge](https://smithery.ai/badge/@effytech/freshservice_mcp)](https://smithery.ai/server/@effytech/freshservice_mcp)

## Overview

A powerful MCP (Model Context Protocol) server implementation that seamlessly integrates with Freshservice, enabling AI models to interact with Freshservice modules and perform various IT service management operations. This integration bridge empowers your AI assistants to manage and resolve IT service tickets, streamlining your support workflow.

## Key Features

- **Enterprise-Grade Freshservice Integration**: Direct, secure communication with Freshservice API endpoints
- **AI Model Compatibility**: Enables Claude and other AI models to execute service desk operations through Freshservice
- **Automated ITSM Management**: Efficiently handle ticket creation, updates, responses, and asset management
- **Workflow Acceleration**: Reduce manual intervention in routine IT service tasks

## Components & Tools

The server consolidates 115+ Freshservice API endpoints into **24 action-based tools** across 10 scopes. Each tool accepts an `action` parameter that dispatches to the relevant operation.

### Ticket Management

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_ticket` | create, update, delete, get, list, filter, get_fields | Unified ticket CRUD, filtering, and field discovery |
| `manage_ticket_conversation` | reply, add_note, update, list | Manage ticket replies and notes |
| `manage_service_catalog` | list_items, get_requested_items, place_request | Browse and order from the service catalog |

### Change Management

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_change` | create, update, delete, get, list, filter, close, move, get_fields | Unified change CRUD, filtering, close, and workspace move |
| `manage_change_note` | create, view, list, update, delete | Notes on a change |
| `manage_change_task` | create, view, list, update, delete | Tasks on a change |
| `manage_change_time_entry` | create, view, list, update, delete | Time entries on a change |
| `manage_change_approval` | list_groups, create_group, update_group, cancel_group, list, view, remind, cancel, set_chain_rule | Approval groups and individual approvals |

### Asset / CMDB Management

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_asset` | create, update, delete, delete_permanently, restore, get, list, search, filter, move, get_types, get_type | Unified asset CRUD, search, filter, and asset type discovery |
| `manage_asset_details` | components, assignment_history, requests, contracts | Retrieve asset sub-resources (hardware components, history, linked tickets/contracts) |
| `manage_asset_relationship` | list_for_asset, list_all, get, create, delete, get_types, job_status | Manage relationships between assets |

### Agent & Requester Management

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_agent` | create, update, get, list, filter, get_fields | Agent CRUD with filtering and field discovery |
| `manage_agent_group` | create, update, get, list | Agent group management |
| `manage_requester` | create, update, get, list, filter, get_fields, add_to_group | Requester CRUD with filtering and group membership |
| `manage_requester_group` | create, update, get, list, list_members | Requester group management |

### Solutions (Knowledge Base)

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_solution` | list_categories, get_category, create_category, update_category, list_folders, get_folder, create_folder, update_folder, list_articles, get_article, create_article, update_article, publish_article | Full knowledge base management with file attachment support |

### Products

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_product` | create, update, get, list | Product CRUD |

### Project Management

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_project` | create, update, delete, get, list, archive, restore, get_fields, get_templates, add_members, list_members, create_association, list_associations, delete_association, delete_attachment | Full project lifecycle management |
| `manage_project_task` | create, update, delete, get, list, filter, get_types, get_type_fields, get_priorities, get_statuses, get_versions, get_sprints | Project task management with metadata discovery |
| `manage_project_task_detail` | create_note, list_notes, update_note, delete_note, create_association, list_associations, delete_association, delete_task_attachment, delete_note_attachment | Task notes, associations, and attachments |

### Journey Management

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_journey_config` | list, get_data_fields | List published journey configs and retrieve initiator form fields |
| `manage_journey_request` | create, get, list, filter, update, cancel, delete, list_activities | Full journey request lifecycle including activity tracking |

**Journey Request Status Values:** 1=In Progress, 2=Completed, 3=Failed, 5=Cancelled, 8=Expired

### Canned Responses & Workspaces

| Tool | Actions | Description |
| ---- | ------- | ----------- |
| `manage_canned_response` | list, get, list_folders, get_folder | Browse canned responses and folders |
| `manage_workspace` | list, get | View workspaces |

### Query Syntax for Filtering

When using filter actions with a `query` parameter, **the query string must be wrapped in double quotes** for the Freshservice API to work correctly:

- **CORRECT**: `"status:3"`, `"approval_status:1 AND status:<6"`
- **WRONG**: `status:3` (will cause 500 Internal Server Error)

## Getting Started

### Installing via Smithery

To install freshservice_mcp automatically via Smithery:

```bash
npx -y @smithery/cli install @effytech/freshservice_mcp --client claude
```

### Prerequisites

- A Freshservice account (sign up at [freshservice.com](https://www.freshservice.com))
- Freshservice API key
- `uvx` installed (`pip install uv` or `brew install uv`)

### Configuration

1. Generate your Freshservice API key from the admin panel:
   - Navigate to Profile Settings → API Settings
   - Copy your API key for configuration

2. Set up your domain and authentication details as shown below

### Usage with Claude Desktop

1. Install Claude Desktop from the [official website](https://claude.ai/desktop)
2. Add the following configuration to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "freshservice-mcp": {
    "command": "uvx",
    "args": [
        "freshservice-mcp"
    ],
    "env": {
      "FRESHSERVICE_APIKEY": "<YOUR_FRESHSERVICE_APIKEY>",
      "FRESHSERVICE_DOMAIN": "<YOUR_FRESHSERVICE_DOMAIN>"
    }
  }
}
```

**Important**: Replace `<YOUR_FRESHSERVICE_APIKEY>` with your actual API key and `<YOUR_FRESHSERVICE_DOMAIN>` with your domain (e.g., `yourcompany.freshservice.com`)

## Example Operations

Once configured, you can ask Claude to perform operations like:

**Tickets:**

- "Create a new incident ticket with subject 'Network connectivity issue in Marketing department' and description 'Users unable to connect to Wi-Fi in Marketing area', set priority to high"
- "List all critical incidents reported in the last 24 hours"
- "Update ticket #12345 status to resolved"

**Changes:**

- "Create a change request for scheduled server maintenance next Tuesday at 2 AM"
- "Update the status of change request #45678 to 'Approved'"
- "Close change #5092 with result explanation 'Successfully deployed to production. All tests passed.'"
- "List all pending changes"

**Other Operations:**

- "Show asset details for laptop with asset tag 'LT-2023-087'"
- "Create a solution article about password reset procedures"

**Assets / CMDB:**

- "List all assets in the CMDB"
- "Create a new hardware asset named 'Dell Latitude 5540' with asset type 'Laptop'"
- "Search assets with serial number 'HSN12345'"
- "Filter assets by state 'IN USE' in department 5"
- "Show all components of asset #42 (CPU, memory, disk, etc.)"
- "Show the assignment history for asset #115"
- "List all relationships for asset #42"
- "Move asset #99 to workspace 3"

## Testing

For testing purposes, you can start the server manually:

```bash
uvx freshservice-mcp --env FRESHSERVICE_APIKEY=<your_api_key> --env FRESHSERVICE_DOMAIN=<your_domain>
```

## Troubleshooting

- Verify your Freshservice API key and domain are correct
- Ensure proper network connectivity to Freshservice servers
- Check API rate limits and quotas
- Verify the `uvx` command is available in your PATH

## License

This MCP server is licensed under the MIT License. See the LICENSE file in the project repository for full details.

## Additional Resources

- [Freshservice API Documentation](https://api.freshservice.com/)
- [Claude Desktop Integration Guide](https://docs.anthropic.com/claude/docs/claude-desktop)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

---

<p align="center">Built with ❤️ by effy</p>
