"""Freshservice MCP — Journeys tools (Journey Management).

Exposes 2 tools:
  * manage_journey_config   -- list published configs, get initiator form data-fields
  * manage_journey_request  -- CRUD + list + filter + cancel + activities
"""
from typing import Any, Dict, List, Optional

from ..http_client import (
    api_delete,
    api_get,
    api_patch,
    api_post,
    api_put,
    handle_error,
)


# -- registration ------------------------------------------------------------
def register_journeys_tools(mcp) -> None:  # noqa: C901 - large by nature
    """Register journey-related tools on *mcp*."""

    # ------------------------------------------------------------------ #
    #  manage_journey_config                                               #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def manage_journey_config(
        action: str,
        config_id: Optional[int] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Manage Journey configurations (published journeys).

        Args:
            action: One of 'list', 'get_data_fields'
            config_id: Journey config ID (required for get_data_fields)
            page: Page number for list (default 30 per page)
        """
        action = action.lower().strip()

        # ---------- list ----------
        if action == "list":
            params: Dict[str, Any] = {"page": page}
            try:
                resp = await api_get("journeys/configs", params=params)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "list journey configs")

        # ---------- get_data_fields ----------
        if action == "get_data_fields":
            if not config_id:
                return {"error": "config_id required for get_data_fields"}
            try:
                resp = await api_get(f"journeys/configs/{config_id}/data-fields")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "get journey config data fields")

        return {"error": f"Unknown action '{action}'. Valid: list, get_data_fields"}

    # ------------------------------------------------------------------ #
    #  manage_journey_request                                              #
    # ------------------------------------------------------------------ #
    @mcp.tool()
    async def manage_journey_request(
        action: str,
        request_id: Optional[int] = None,
        # create
        journey_id: Optional[int] = None,
        initiator_data: Optional[Dict[str, Any]] = None,
        # list
        filter: Optional[str] = None,
        order_type: Optional[str] = None,
        # filter (POST body)
        filter_attributes: Optional[List[Dict[str, Any]]] = None,
        # list_activities
        activity_type: Optional[str] = None,
        # pagination
        page: int = 1,
        per_page: int = 30,
    ) -> Dict[str, Any]:
        """Manage Journey Requests — create, view, list, filter, update, cancel, delete, and list activities.

        Args:
            action: One of 'create', 'get', 'list', 'filter', 'update', 'cancel',
                    'delete', 'list_activities'
            request_id: Journey request display_id (required for get, update, cancel,
                delete, list_activities). Use the display_id from list/filter results, not
                the internal id.
            journey_id: Journey config ID (required for create)
            initiator_data: Dict with 'request_for' and/or 'custom_fields' (create, update).
                Example: {"request_for": "user@example.com", "custom_fields": {"cf_text": "value"}}
            filter: Predefined filter for list — one of 'completed', 'all', 'in_progress',
                    'my_completed', 'my_in_progress'
            order_type: Sort order for list — 'asc' or 'desc' (default desc)
            filter_attributes: List of attribute dicts for the filter action (POST body).
                Each dict: {"field": "<name>", "operator": "is_in", "value": [...]}.
                Filterable fields: type, requester_id, journey_id, owner_id,
                requested_for_id, status, created_at.
                Status values: 1=In Progress, 2=Completed, 3=Failed, 5=Cancelled, 8=Expired.
                Example: [{"field": "status", "operator": "is_in", "value": [2]}]
            activity_type: Filter activities by type — EMAIL, SERVICE_REQUEST, PLAIN, or TASK
            page: Page number
            per_page: Items per page (default 30)
        """
        action = action.lower().strip()

        # ---------- list ----------
        if action == "list":
            params: Dict[str, Any] = {"page": page, "per_page": per_page}
            if filter:
                params["filter"] = filter
            if order_type:
                params["order_type"] = order_type
            try:
                resp = await api_get("journeys/requests", params=params)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "list journey requests")

        # ---------- filter (POST) ----------
        if action == "filter":
            if not filter_attributes:
                return {"error": "filter_attributes required for filter action"}
            body: Dict[str, Any] = {
                "data": {
                    "query": {
                        "filter": [
                            {"attributes": filter_attributes}
                        ]
                    }
                }
            }
            params = {"page": page}
            try:
                resp = await api_post("journeys/requests/view", json=body)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "filter journey requests")

        # ---------- get ----------
        if action == "get":
            if not request_id:
                return {"error": "request_id required for get"}
            try:
                resp = await api_get(f"journeys/requests/{request_id}")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "get journey request")

        # ---------- create ----------
        if action == "create":
            if not journey_id or not initiator_data:
                return {"error": "journey_id and initiator_data required for create"}
            data: Dict[str, Any] = {
                "journey_id": journey_id,
                "initiator_data": initiator_data,
            }
            try:
                resp = await api_post("journeys/requests", json=data)
                resp.raise_for_status()
                return {"success": True, "journey_request": resp.json()}
            except Exception as e:
                return handle_error(e, "create journey request")

        # ---------- update (PATCH) ----------
        if action == "update":
            if not request_id or not initiator_data:
                return {"error": "request_id and initiator_data required for update"}
            data = {"initiator_data": initiator_data}
            try:
                resp = await api_patch(f"journeys/requests/{request_id}", json=data)
                resp.raise_for_status()
                return {"success": True, "journey_request": resp.json()}
            except Exception as e:
                return handle_error(e, "update journey request")

        # ---------- cancel ----------
        if action == "cancel":
            if not request_id:
                return {"error": "request_id required for cancel"}
            try:
                resp = await api_put(f"journeys/requests/{request_id}/cancel")
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "cancel journey request")

        # ---------- delete ----------
        if action == "delete":
            if not request_id:
                return {"error": "request_id required for delete"}
            try:
                resp = await api_delete(f"journeys/requests/{request_id}")
                if resp.status_code == 204:
                    return {"success": True, "message": "Journey request deleted"}
                return {"error": f"Unexpected status {resp.status_code}"}
            except Exception as e:
                return handle_error(e, "delete journey request")

        # ---------- list_activities ----------
        if action == "list_activities":
            if not request_id:
                return {"error": "request_id required for list_activities"}
            params = {}
            if activity_type:
                params["activity_type"] = activity_type
            try:
                resp = await api_get(
                    f"journeys/requests/{request_id}/activities", params=params
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                return handle_error(e, "list journey request activities")

        return {
            "error": f"Unknown action '{action}'. Valid: create, get, list, filter, "
            "update, cancel, delete, list_activities"
        }
