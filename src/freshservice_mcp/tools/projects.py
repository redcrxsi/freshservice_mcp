"""Freshservice MCP — Projects tools (new-gen Project Management).

Exposes 3 tools:
  • manage_project             — CRUD + list + archive/restore + members + associations + fields/templates
  • manage_project_task        — CRUD + list + filter + types/fields/priorities/statuses/versions/sprints
  • manage_project_task_detail — notes CRUD + associations + attachment deletion
"""
from typing import Any, Dict, List, Optional

from ..config import (
    ProjectPriority,
    ProjectStatus,
    ProjectType,
    ProjectVisibility,
)
from ..http_client import (
    api_delete,
    api_get,
    api_post,
    api_put,
    handle_error,
    parse_link_header,
)


# ── registration ───────────────────────────────────────────────────────────
def register_projects_tools(mcp) -> None:  # noqa: C901 – large by nature
    """Register project-management tools on *mcp*."""

    # ------------------------------------------------------------------ #
    #  manage_project                                                      #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def manage_project(
        action: str,
        project_id: Optional[int] = None,
        # create / update fields
        name: Optional[str] = None,
        description: Optional[str] = None,
        key: Optional[str] = None,
        status_id: Optional[int] = None,
        priority_id: Optional[int] = None,
        project_type: Optional[int] = None,
        manager_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        visibility: Optional[int] = None,
        sprint_duration: Optional[int] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        # members
        member_ids: Optional[List[int]] = None,
        # associations
        associations: Optional[List[Dict[str, Any]]] = None,
        association_id: Optional[int] = None,
        # attachments
        attachment_id: Optional[int] = None,
        # pagination
        page: int = 1,
        per_page: int = 30,
    ) -> Dict[str, Any]:
        """Unified project operations (new-gen PM API).

        Args:
            action: One of 'create', 'update', 'delete', 'get', 'list',
                    'archive', 'restore', 'get_fields', 'get_templates',
                    'add_members', 'list_members',
                    'create_association', 'list_associations', 'delete_association',
                    'delete_attachment'
            project_id: Required for get/update/delete/archive/restore/members/associations/attachments
            name: Project name (create — MANDATORY)
            description: Project description
            key: Project key (short code)
            status_id: 1=Yet to start, 2=In Progress, 3=Completed
            priority_id: 1=Low, 2=Medium, 3=High, 4=Urgent
            project_type: 0=Software, 1=Business (create — MANDATORY)
            manager_id: Manager agent ID
            start_date: ISO date
            end_date: ISO date
            visibility: 0=Private, 1=Public
            sprint_duration: Sprint duration in days
            custom_fields: Custom fields dict
            member_ids: List of agent IDs (add_members)
            associations: List of association dicts (create_association)
            association_id: Association ID (delete_association)
            attachment_id: Attachment ID (delete_attachment)
            page: Page number
            per_page: Items per page 1-100
        """
        action = action.lower().strip()

        # ---------- get_fields ----------
        if action == "get_fields":
            try:
                resp = await api_get("pm/projects/fields")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "fetch project fields")

        # ---------- get_templates ----------
        if action == "get_templates":
            try:
                resp = await api_get("pm/project-templates")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "fetch project templates")

        # ---------- list ----------
        if action == "list":
            params: Dict[str, Any] = {"page": page, "per_page": per_page}
            try:
                resp = await api_get("pm/projects", params=params)
                resp.raise_for_status()
                pagination_info = parse_link_header(resp.headers.get("Link", ""))
                return {
                    "projects": resp.json(),
                    "pagination": {
                        "current_page": page,
                        "next_page": pagination_info.get("next"),
                        "prev_page": pagination_info.get("prev"),
                        "per_page": per_page,
                    },
                }
            except Exception as e:
                return handle_error(e, "list projects")

        # ---------- get ----------
        if action == "get":
            if not project_id:
                return {"error": "project_id required for get"}
            try:
                resp = await api_get(f"pm/projects/{project_id}")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "get project")

        # ---------- create ----------
        if action == "create":
            if not name or project_type is None:
                return {"error": "name and project_type are required for create"}
            data: Dict[str, Any] = {
                "name": name,
                "project_type": project_type,
            }
            for k, v in [
                ("description", description),
                ("key", key),
                ("status_id", status_id),
                ("priority_id", priority_id),
                ("manager_id", manager_id),
                ("start_date", start_date),
                ("end_date", end_date),
                ("visibility", visibility),
                ("sprint_duration", sprint_duration),
            ]:
                if v is not None:
                    data[k] = v
            if custom_fields:
                data["custom_fields"] = custom_fields
            try:
                resp = await api_post("pm/projects", json=data)
                resp.raise_for_status()
                return {"success": True, "project": resp.json()}
            except Exception as e:
                return handle_error(e, "create project")

        # ---------- update ----------
        if action == "update":
            if not project_id:
                return {"error": "project_id required for update"}
            update_data: Dict[str, Any] = {}
            for k, v in [
                ("name", name),
                ("description", description),
                ("key", key),
                ("status_id", status_id),
                ("priority_id", priority_id),
                ("project_type", project_type),
                ("manager_id", manager_id),
                ("start_date", start_date),
                ("end_date", end_date),
                ("visibility", visibility),
                ("sprint_duration", sprint_duration),
            ]:
                if v is not None:
                    update_data[k] = v
            if custom_fields:
                update_data["custom_fields"] = custom_fields
            if not update_data:
                return {"error": "No fields provided for update"}
            try:
                resp = await api_put(f"pm/projects/{project_id}", json=update_data)
                resp.raise_for_status()
                return {"success": True, "project": resp.json()}
            except Exception as e:
                return handle_error(e, "update project")

        # ---------- delete ----------
        if action == "delete":
            if not project_id:
                return {"error": "project_id required for delete"}
            try:
                resp = await api_delete(f"pm/projects/{project_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Project deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete project")

        # ---------- archive ----------
        if action == "archive":
            if not project_id:
                return {"error": "project_id required for archive"}
            try:
                resp = await api_put(f"pm/projects/{project_id}/archive")
                if resp.status_code == 204:
                    return {"success": True, "message": "Project archived"}
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "archive project")

        # ---------- restore ----------
        if action == "restore":
            if not project_id:
                return {"error": "project_id required for restore"}
            try:
                resp = await api_put(f"pm/projects/{project_id}/restore")
                if resp.status_code == 204:
                    return {"success": True, "message": "Project restored"}
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "restore project")

        # ---------- add_members ----------
        if action == "add_members":
            if not project_id or not member_ids:
                return {"error": "project_id and member_ids required for add_members"}
            try:
                resp = await api_post(
                    f"pm/projects/{project_id}/members",
                    json={"member_ids": member_ids},
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "add project members")

        # ---------- list_members ----------
        if action == "list_members":
            if not project_id:
                return {"error": "project_id required for list_members"}
            try:
                resp = await api_get(f"pm/projects/{project_id}/members")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "list project members")

        # ---------- create_association ----------
        if action == "create_association":
            if not project_id or not associations:
                return {"error": "project_id and associations required for create_association"}
            try:
                resp = await api_post(
                    f"pm/projects/{project_id}/associations",
                    json={"associations": associations},
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "create project association")

        # ---------- list_associations ----------
        if action == "list_associations":
            if not project_id:
                return {"error": "project_id required for list_associations"}
            try:
                resp = await api_get(f"pm/projects/{project_id}/associations")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "list project associations")

        # ---------- delete_association ----------
        if action == "delete_association":
            if not project_id or not association_id:
                return {"error": "project_id and association_id required for delete_association"}
            try:
                resp = await api_delete(f"pm/projects/{project_id}/associations/{association_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Association deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete project association")

        # ---------- delete_attachment ----------
        if action == "delete_attachment":
            if not project_id or not attachment_id:
                return {"error": "project_id and attachment_id required for delete_attachment"}
            try:
                resp = await api_delete(f"pm/projects/{project_id}/attachments/{attachment_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Attachment deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete project attachment")

        return {
            "error": f"Unknown action '{action}'. Valid: create, update, delete, get, list, "
            "archive, restore, get_fields, get_templates, add_members, list_members, "
            "create_association, list_associations, delete_association, delete_attachment"
        }

    # ------------------------------------------------------------------ #
    #  manage_project_task                                                 #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def manage_project_task(
        action: str,
        project_id: int,
        task_id: Optional[int] = None,
        # create / update fields
        title: Optional[str] = None,
        description: Optional[str] = None,
        type_id: Optional[int] = None,
        reporter_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        status_id: Optional[int] = None,
        priority_id: Optional[int] = None,
        story_points: Optional[int] = None,
        planned_start_date: Optional[str] = None,
        planned_end_date: Optional[str] = None,
        planned_effort: Optional[str] = None,
        planned_duration: Optional[str] = None,
        version_id: Optional[int] = None,
        sprint_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        # pagination
        page: int = 1,
        per_page: int = 30,
    ) -> Dict[str, Any]:
        """Unified project-task operations.

        Args:
            action: One of 'create', 'update', 'delete', 'get', 'list', 'filter',
                    'get_types', 'get_type_fields', 'get_priorities', 'get_statuses',
                    'get_versions', 'get_sprints'
            project_id: The project ID (always required)
            task_id: Required for get, update, delete
            title: Task title (create — MANDATORY)
            description: Task description
            type_id: Task type ID
            reporter_id: Reporter agent ID
            assignee_id: Assignee agent ID
            status_id: Task status ID
            priority_id: Task priority ID
            story_points: Story points estimate
            planned_start_date: ISO date
            planned_end_date: ISO date
            planned_effort: Planned effort string
            planned_duration: Planned duration string
            version_id: Version/release ID
            sprint_id: Sprint ID
            parent_id: Parent task ID (for sub-tasks)
            custom_fields: Custom fields dict
            page: Page number
            per_page: Items per page 1-100
        """
        action = action.lower().strip()
        base = f"pm/projects/{project_id}"

        # ---------- get_types ----------
        if action == "get_types":
            try:
                resp = await api_get(f"{base}/task-types")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "fetch task types")

        # ---------- get_type_fields ----------
        if action == "get_type_fields":
            try:
                resp = await api_get(f"{base}/task-type-fields")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "fetch task type fields")

        # ---------- get_priorities ----------
        if action == "get_priorities":
            try:
                resp = await api_get(f"{base}/task-priorities")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "fetch task priorities")

        # ---------- get_statuses ----------
        if action == "get_statuses":
            try:
                resp = await api_get(f"{base}/task-statuses")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "fetch task statuses")

        # ---------- get_versions ----------
        if action == "get_versions":
            try:
                resp = await api_get(f"{base}/versions")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "fetch project versions")

        # ---------- get_sprints ----------
        if action == "get_sprints":
            try:
                resp = await api_get(f"{base}/sprints")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "fetch project sprints")

        # ---------- list ----------
        if action == "list":
            params: Dict[str, Any] = {"page": page, "per_page": per_page}
            try:
                resp = await api_get(f"{base}/tasks", params=params)
                resp.raise_for_status()
                pagination_info = parse_link_header(resp.headers.get("Link", ""))
                return {
                    "tasks": resp.json(),
                    "pagination": {
                        "current_page": page,
                        "next_page": pagination_info.get("next"),
                        "prev_page": pagination_info.get("prev"),
                        "per_page": per_page,
                    },
                }
            except Exception as e:
                return handle_error(e, "list project tasks")

        # ---------- filter ----------
        if action == "filter":
            params = {"page": page, "per_page": per_page}
            try:
                resp = await api_get(f"{base}/tasks/filter", params=params)
                resp.raise_for_status()
                pagination_info = parse_link_header(resp.headers.get("Link", ""))
                return {
                    "tasks": resp.json(),
                    "pagination": {
                        "current_page": page,
                        "next_page": pagination_info.get("next"),
                        "prev_page": pagination_info.get("prev"),
                        "per_page": per_page,
                    },
                }
            except Exception as e:
                return handle_error(e, "filter project tasks")

        # ---------- get ----------
        if action == "get":
            if not task_id:
                return {"error": "task_id required for get"}
            try:
                resp = await api_get(f"{base}/tasks/{task_id}")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "get project task")

        # ---------- create ----------
        if action == "create":
            if not title:
                return {"error": "title is required for create"}
            data: Dict[str, Any] = {"title": title}
            for k, v in [
                ("description", description),
                ("type_id", type_id),
                ("reporter_id", reporter_id),
                ("assignee_id", assignee_id),
                ("status_id", status_id),
                ("priority_id", priority_id),
                ("story_points", story_points),
                ("planned_start_date", planned_start_date),
                ("planned_end_date", planned_end_date),
                ("planned_effort", planned_effort),
                ("planned_duration", planned_duration),
                ("version_id", version_id),
                ("sprint_id", sprint_id),
                ("parent_id", parent_id),
            ]:
                if v is not None:
                    data[k] = v
            if custom_fields:
                data["custom_fields"] = custom_fields
            try:
                resp = await api_post(f"{base}/tasks", json=data)
                resp.raise_for_status()
                return {"success": True, "task": resp.json()}
            except Exception as e:
                return handle_error(e, "create project task")

        # ---------- update ----------
        if action == "update":
            if not task_id:
                return {"error": "task_id required for update"}
            update_data: Dict[str, Any] = {}
            for k, v in [
                ("title", title),
                ("description", description),
                ("type_id", type_id),
                ("reporter_id", reporter_id),
                ("assignee_id", assignee_id),
                ("status_id", status_id),
                ("priority_id", priority_id),
                ("story_points", story_points),
                ("planned_start_date", planned_start_date),
                ("planned_end_date", planned_end_date),
                ("planned_effort", planned_effort),
                ("planned_duration", planned_duration),
                ("version_id", version_id),
                ("sprint_id", sprint_id),
                ("parent_id", parent_id),
            ]:
                if v is not None:
                    update_data[k] = v
            if custom_fields:
                update_data["custom_fields"] = custom_fields
            if not update_data:
                return {"error": "No fields provided for update"}
            try:
                resp = await api_put(f"{base}/tasks/{task_id}", json=update_data)
                resp.raise_for_status()
                return {"success": True, "task": resp.json()}
            except Exception as e:
                return handle_error(e, "update project task")

        # ---------- delete ----------
        if action == "delete":
            if not task_id:
                return {"error": "task_id required for delete"}
            try:
                resp = await api_delete(f"{base}/tasks/{task_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Task deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete project task")

        return {
            "error": f"Unknown action '{action}'. Valid: create, update, delete, get, list, filter, "
            "get_types, get_type_fields, get_priorities, get_statuses, get_versions, get_sprints"
        }

    # ------------------------------------------------------------------ #
    #  manage_project_task_detail                                          #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def manage_project_task_detail(
        action: str,
        project_id: int,
        task_id: int,
        note_id: Optional[int] = None,
        body: Optional[str] = None,
        associations: Optional[List[Dict[str, Any]]] = None,
        association_id: Optional[int] = None,
        attachment_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Manage notes, associations, and attachments on a project task.

        Args:
            action: One of 'create_note', 'list_notes', 'update_note', 'delete_note',
                    'create_association', 'list_associations', 'delete_association',
                    'delete_task_attachment', 'delete_note_attachment'
            project_id: The project ID
            task_id: The task ID
            note_id: Required for update_note, delete_note, delete_note_attachment
            body: Note body (create_note, update_note)
            associations: List of association dicts (create_association)
            association_id: Association ID (delete_association)
            attachment_id: Attachment ID (delete_task_attachment, delete_note_attachment)
        """
        action = action.lower().strip()
        base = f"pm/projects/{project_id}/tasks/{task_id}"

        # ---------- create_note ----------
        if action == "create_note":
            if not body:
                return {"error": "body required for create_note"}
            try:
                resp = await api_post(f"{base}/notes", json={"body": body})
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "create task note")

        # ---------- list_notes ----------
        if action == "list_notes":
            try:
                resp = await api_get(f"{base}/notes")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "list task notes")

        # ---------- update_note ----------
        if action == "update_note":
            if not note_id or not body:
                return {"error": "note_id and body required for update_note"}
            try:
                resp = await api_put(f"{base}/notes/{note_id}", json={"body": body})
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "update task note")

        # ---------- delete_note ----------
        if action == "delete_note":
            if not note_id:
                return {"error": "note_id required for delete_note"}
            try:
                resp = await api_delete(f"{base}/notes/{note_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Note deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete task note")

        # ---------- create_association ----------
        if action == "create_association":
            if not associations:
                return {"error": "associations required for create_association"}
            try:
                resp = await api_post(
                    f"{base}/associations",
                    json={"associations": associations},
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "create task association")

        # ---------- list_associations ----------
        if action == "list_associations":
            try:
                resp = await api_get(f"{base}/associations")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "list task associations")

        # ---------- delete_association ----------
        if action == "delete_association":
            if not association_id:
                return {"error": "association_id required for delete_association"}
            try:
                resp = await api_delete(f"{base}/associations/{association_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Association deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete task association")

        # ---------- delete_task_attachment ----------
        if action == "delete_task_attachment":
            if not attachment_id:
                return {"error": "attachment_id required for delete_task_attachment"}
            try:
                resp = await api_delete(f"{base}/attachments/{attachment_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Task attachment deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete task attachment")

        # ---------- delete_note_attachment ----------
        if action == "delete_note_attachment":
            if not note_id or not attachment_id:
                return {"error": "note_id and attachment_id required for delete_note_attachment"}
            try:
                resp = await api_delete(f"{base}/notes/{note_id}/attachments/{attachment_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Note attachment deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete note attachment")

        return {
            "error": f"Unknown action '{action}'. Valid: create_note, list_notes, update_note, "
            "delete_note, create_association, list_associations, delete_association, "
            "delete_task_attachment, delete_note_attachment"
        }
