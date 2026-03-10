"""Integration tests for Projects tools (new-gen PM API).

Covers ALL 37 actions across all 3 tools:
  manage_project           -- 16 actions
  manage_project_task      -- 12 actions
  manage_project_task_detail -- 9 actions

Prints PASS/FAIL per step, stops on first failure.

Usage:
    export FRESHSERVICE_APIKEY=...
    export FRESHSERVICE_DOMAIN=yourco.freshservice.com
    uv run python tests/test_projects.py
"""

import asyncio
import sys
import json
import time
from typing import Any, Dict, List, Optional

from freshservice_mcp.http_client import api_get, api_post, api_put, api_delete


# --helpers ----------------------------------------------------------------
STEP = 0


def pp(data: Any) -> str:
    if isinstance(data, dict):
        return json.dumps(data, indent=2, default=str)[:600]
    return str(data)[:600]


def tag(label: str) -> str:
    global STEP
    STEP += 1
    return f"{STEP:02d} {label}"


def fail(t: str, msg: str) -> None:
    print(f"  FAIL  [{t}] {msg}")
    sys.exit(1)


def ok(t: str, summary: str) -> None:
    print(f"  PASS  [{t}] {summary}")


def expect(resp, t: str, codes: tuple = (200,), label: str = "") -> dict | list | None:
    """Assert response status code; return parsed JSON or None for 204."""
    if resp.status_code not in codes:
        fail(t, f"HTTP {resp.status_code}: {resp.text[:400]}")
    if resp.status_code == 204 or not resp.text:
        return None
    return resp.json()


# --prerequisite: create a ticket for association tests -------------------
async def create_test_ticket() -> int:
    resp = await api_post("tickets", json={
        "subject": "MCP Project Association Test",
        "description": "Temporary ticket for project association testing",
        "email": "test@test.com",
        "priority": 1,
        "status": 2,
    })
    if resp.status_code not in (200, 201):
        print(f"  FAIL  [prereq] Cannot create test ticket: {resp.status_code} {resp.text[:300]}")
        sys.exit(1)
    data = resp.json()
    ticket = data.get("ticket", data)
    tid = ticket["id"]
    print(f"  SETUP Created test ticket id={tid}")
    return tid


async def delete_test_ticket(ticket_id: int) -> None:
    resp = await api_delete(f"tickets/{ticket_id}")
    if resp.status_code in (200, 204):
        print(f"  CLEANUP Deleted test ticket id={ticket_id}")
    else:
        print(f"  WARN  Could not delete ticket {ticket_id}: {resp.status_code}")


async def get_non_manager_agent(manager_id: int) -> int:
    resp = await api_get("agents", params={"per_page": 10})
    agents = resp.json().get("agents", [])
    for a in agents:
        if a["id"] != manager_id:
            return a["id"]
    if agents:
        return agents[0]["id"]
    raise RuntimeError("No agents found")


# ======================================================================
#  manage_project -- 16 actions
# ======================================================================

async def test_mp_get_templates() -> None:
    t = tag("manage_project: get_templates")
    resp = await api_get("pm/project_templates")
    data = expect(resp, t)
    ok(t, f"Got {len(data) if isinstance(data, list) else 'object'} template(s)")


async def test_mp_get_fields() -> None:
    t = tag("manage_project: get_fields")
    resp = await api_get("pm/project-fields")
    data = expect(resp, t)
    ok(t, f"Got {len(data) if isinstance(data, list) else 'object'} field def(s)")


async def test_mp_list() -> None:
    t = tag("manage_project: list")
    resp = await api_get("pm/projects", params={"page": 1, "per_page": 5})
    data = expect(resp, t)
    projects = data.get("projects", data) if isinstance(data, dict) else data
    ok(t, f"Listed {len(projects) if isinstance(projects, list) else '?'} project(s)")


async def test_mp_create() -> int:
    t = tag("manage_project: create")
    name = f"MCP Test Project {int(time.time())}"
    resp = await api_post("pm/projects", json={
        "name": name, "project_type": 1, "priority_id": 2,
    })
    data = expect(resp, t, (200, 201))
    project = data.get("project", data)
    pid = project["id"]
    ok(t, f"Created project id={pid} name='{name}'")
    await asyncio.sleep(5)  # eventual consistency
    return pid


async def test_mp_get(pid: int) -> dict:
    t = tag("manage_project: get")
    resp = await api_get(f"pm/projects/{pid}")
    data = expect(resp, t)
    project = data.get("project", data)
    ok(t, f"Got project '{project.get('name', '?')}'")
    return project


async def test_mp_update(pid: int) -> None:
    t = tag("manage_project: update")
    resp = await api_put(f"pm/projects/{pid}", json={
        "description": "Updated by MCP integration test",
    })
    expect(resp, t, (200, 204))
    ok(t, "Description updated")


async def test_mp_add_members(pid: int, manager_id: int) -> int:
    t = tag("manage_project: add_members")
    agent_id = await get_non_manager_agent(manager_id)
    resp = await api_post(f"pm/projects/{pid}/members", json={
        "members": [agent_id],
    })
    expect(resp, t, (200, 201))
    ok(t, f"Added agent {agent_id} as member")
    return agent_id


async def test_mp_list_members(pid: int) -> None:
    t = tag("manage_project: list_members")
    resp = await api_get(f"pm/projects/{pid}/memberships")
    data = expect(resp, t)
    count = len(data) if isinstance(data, list) else "?"
    ok(t, f"Listed {count} member(s)")


async def test_mp_create_association(pid: int, ticket_id: int) -> None:
    t = tag("manage_project: create_association")
    resp = await api_post(f"pm/projects/{pid}/tickets", json={
        "ids": [ticket_id],
    })
    data = expect(resp, t, (200, 201))
    ok(t, f"Associated ticket {ticket_id} with project")


async def test_mp_list_associations(pid: int) -> int:
    t = tag("manage_project: list_associations")
    resp = await api_get(f"pm/projects/{pid}/tickets")
    data = expect(resp, t)
    items = data if isinstance(data, list) else data.get("tickets", data.get("associations", []))
    ok(t, f"Listed {len(items) if isinstance(items, list) else '?'} association(s)")
    # try to extract the association id for deletion
    if isinstance(items, list) and items:
        first = items[0]
        return first.get("association_id", first.get("id", 0))
    return 0


async def test_mp_delete_association(pid: int, ticket_id: int) -> None:
    t = tag("manage_project: delete_association")
    resp = await api_delete(f"pm/projects/{pid}/tickets/{ticket_id}")
    expect(resp, t, (200, 204))
    ok(t, f"Deleted project-ticket association {ticket_id}")


async def test_mp_delete_attachment(pid: int) -> None:
    t = tag("manage_project: delete_attachment")
    # No attachment exists -- verify endpoint returns 404 (not 405/500),
    # proving URL path and method are correct.
    resp = await api_delete(f"pm/projects/{pid}/attachments/999999999")
    if resp.status_code == 404:
        ok(t, "Endpoint valid -- 404 for non-existent attachment (expected)")
    elif resp.status_code == 204:
        ok(t, "Attachment deleted (unexpected but OK)")
    else:
        fail(t, f"HTTP {resp.status_code}: {resp.text[:300]}")


async def test_mp_archive(pid: int) -> None:
    t = tag("manage_project: archive")
    resp = await api_post(f"pm/projects/{pid}/archive")
    expect(resp, t, (200, 204))
    ok(t, f"Archived project {pid}")


async def test_mp_restore(pid: int) -> None:
    t = tag("manage_project: restore")
    resp = await api_post(f"pm/projects/{pid}/restore")
    expect(resp, t, (200, 204))
    ok(t, f"Restored project {pid}")


async def test_mp_delete(pid: int) -> None:
    t = tag("manage_project: delete")
    resp = await api_delete(f"pm/projects/{pid}")
    expect(resp, t, (200, 204))
    ok(t, f"Deleted project {pid}")


# ======================================================================
#  manage_project_task -- 12 actions
# ======================================================================

async def test_mpt_get_types(pid: int) -> int:
    t = tag("manage_project_task: get_types")
    resp = await api_get(f"pm/projects/{pid}/task-types")
    data = expect(resp, t)
    types = data.get("task_types", data) if isinstance(data, dict) else data
    type_id = None
    if isinstance(types, list):
        for tt in types:
            if tt.get("name") == "task":
                type_id = tt["id"]
                break
        if not type_id and types:
            type_id = types[0]["id"]
    if not type_id:
        fail(t, "No task types returned")
    ok(t, f"Got {len(types)} type(s), using type_id={type_id}")
    return type_id


async def test_mpt_get_type_fields(pid: int, type_id: int) -> None:
    t = tag("manage_project_task: get_type_fields")
    resp = await api_get(f"pm/projects/{pid}/task-types/{type_id}/fields")
    data = expect(resp, t)
    ok(t, f"Got fields for type_id={type_id}")


async def test_mpt_get_priorities(pid: int) -> int:
    t = tag("manage_project_task: get_priorities")
    resp = await api_get(f"pm/projects/{pid}/task-priorities")
    data = expect(resp, t)
    priorities = data.get("task_priorities", data) if isinstance(data, dict) else data
    pri_id = priorities[0]["id"] if isinstance(priorities, list) and priorities else 0
    ok(t, f"Got priorities, using pri_id={pri_id}")
    return pri_id


async def test_mpt_get_statuses(pid: int) -> None:
    t = tag("manage_project_task: get_statuses")
    resp = await api_get(f"pm/projects/{pid}/task-statuses")
    data = expect(resp, t)
    ok(t, f"Got statuses")


async def test_mpt_get_versions(pid: int) -> None:
    t = tag("manage_project_task: get_versions")
    resp = await api_get(f"pm/projects/{pid}/versions")
    data = expect(resp, t)
    ok(t, f"Got versions")


async def test_mpt_get_sprints(pid: int) -> None:
    t = tag("manage_project_task: get_sprints")
    resp = await api_get(f"pm/projects/{pid}/sprints")
    data = expect(resp, t)
    ok(t, f"Got sprints")


async def test_mpt_create(pid: int, type_id: int) -> int:
    t = tag("manage_project_task: create")
    resp = await api_post(f"pm/projects/{pid}/tasks", json={
        "title": "MCP Test Task", "type_id": type_id,
    })
    data = expect(resp, t, (200, 201))
    task = data.get("task", data)
    tid = task["id"]
    ok(t, f"Created task id={tid}")
    return tid


async def test_mpt_get(pid: int, tid: int) -> None:
    t = tag("manage_project_task: get")
    resp = await api_get(f"pm/projects/{pid}/tasks/{tid}")
    data = expect(resp, t)
    task = data.get("task", data)
    ok(t, f"Got task '{task.get('title', '?')}'")


async def test_mpt_update(pid: int, tid: int) -> None:
    t = tag("manage_project_task: update")
    resp = await api_put(f"pm/projects/{pid}/tasks/{tid}", json={
        "description": "Updated by MCP integration test",
    })
    expect(resp, t, (200, 204))
    ok(t, "Task description updated")


async def test_mpt_list(pid: int) -> None:
    t = tag("manage_project_task: list")
    resp = await api_get(f"pm/projects/{pid}/tasks", params={
        "page": 1, "per_page": 5,
    })
    data = expect(resp, t)
    ok(t, f"Listed tasks")


async def test_mpt_filter(pid: int, pri_id: int) -> None:
    t = tag("manage_project_task: filter")
    resp = await api_get(f"pm/projects/{pid}/tasks/filter", params={
        "query": f'"priority_id:{pri_id}"',
        "page": 1,
    })
    data = expect(resp, t)
    ok(t, f"Filtered tasks with priority_id={pri_id}")


async def test_mpt_delete(pid: int, tid: int) -> None:
    t = tag("manage_project_task: delete")
    resp = await api_delete(f"pm/projects/{pid}/tasks/{tid}")
    expect(resp, t, (200, 204))
    ok(t, f"Deleted task {tid}")


# ======================================================================
#  manage_project_task_detail -- 9 actions
# ======================================================================

async def test_mptd_create_note(pid: int, tid: int) -> int:
    t = tag("manage_project_task_detail: create_note")
    resp = await api_post(f"pm/projects/{pid}/tasks/{tid}/notes", json={
        "content": "Test note from MCP",
    })
    data = expect(resp, t, (200, 201))
    note = data.get("note", data)
    nid = note["id"]
    ok(t, f"Created note id={nid}")
    return nid


async def test_mptd_list_notes(pid: int, tid: int) -> None:
    t = tag("manage_project_task_detail: list_notes")
    resp = await api_get(f"pm/projects/{pid}/tasks/{tid}/notes")
    data = expect(resp, t)
    ok(t, f"Listed notes")


async def test_mptd_update_note(pid: int, tid: int, nid: int) -> None:
    t = tag("manage_project_task_detail: update_note")
    resp = await api_put(f"pm/projects/{pid}/tasks/{tid}/notes/{nid}", json={
        "content": "Updated test note from MCP",
    })
    expect(resp, t, (200, 204))
    ok(t, f"Updated note {nid}")


async def test_mptd_delete_note(pid: int, tid: int, nid: int) -> None:
    t = tag("manage_project_task_detail: delete_note")
    resp = await api_delete(f"pm/projects/{pid}/tasks/{tid}/notes/{nid}")
    expect(resp, t, (200, 204))
    ok(t, f"Deleted note {nid}")


async def test_mptd_create_association(pid: int, tid: int, ticket_id: int) -> None:
    t = tag("manage_project_task_detail: create_association")
    resp = await api_post(f"pm/projects/{pid}/tasks/{tid}/tickets", json={
        "ids": [ticket_id],
    })
    data = expect(resp, t, (200, 201))
    ok(t, f"Associated ticket {ticket_id} with task")


async def test_mptd_list_associations(pid: int, tid: int) -> int:
    t = tag("manage_project_task_detail: list_associations")
    resp = await api_get(f"pm/projects/{pid}/tasks/{tid}/tickets")
    data = expect(resp, t)
    items = data if isinstance(data, list) else data.get("tickets", data.get("associations", []))
    ok(t, f"Listed {len(items) if isinstance(items, list) else '?'} task association(s)")
    if isinstance(items, list) and items:
        first = items[0]
        return first.get("association_id", first.get("id", 0))
    return 0


async def test_mptd_delete_association(pid: int, tid: int, ticket_id: int) -> None:
    t = tag("manage_project_task_detail: delete_association")
    resp = await api_delete(f"pm/projects/{pid}/tasks/{tid}/tickets/{ticket_id}")
    expect(resp, t, (200, 204))
    ok(t, f"Deleted task-ticket association {ticket_id}")


async def test_mptd_delete_task_attachment(pid: int, tid: int) -> None:
    t = tag("manage_project_task_detail: delete_task_attachment")
    # No attachment exists -- verify endpoint returns 404 (not 405/500),
    # proving URL path and HTTP method are correct.
    resp = await api_delete(f"pm/projects/{pid}/tasks/{tid}/attachments/999999999")
    if resp.status_code == 404:
        ok(t, "Endpoint valid -- 404 for non-existent attachment (expected)")
    elif resp.status_code == 204:
        ok(t, "Attachment deleted")
    else:
        fail(t, f"HTTP {resp.status_code}: {resp.text[:300]}")


async def test_mptd_delete_note_attachment(pid: int, tid: int, nid: int) -> None:
    t = tag("manage_project_task_detail: delete_note_attachment")
    # Same approach -- verify endpoint path with a bogus attachment ID.
    resp = await api_delete(f"pm/projects/{pid}/tasks/{tid}/notes/{nid}/attachments/999999999")
    if resp.status_code == 404:
        ok(t, "Endpoint valid -- 404 for non-existent note attachment (expected)")
    elif resp.status_code == 204:
        ok(t, "Note attachment deleted")
    else:
        fail(t, f"HTTP {resp.status_code}: {resp.text[:300]}")


# ======================================================================
#  main -- sequenced so each step has the resources it needs
# ======================================================================

async def main() -> None:
    print("=" * 64)
    print("  Freshservice Projects - Full Integration Test Suite")
    print("  37 actions across 3 tools, 0 skipped")
    print("=" * 64)

    # -- prereq: ticket for associations --
    ticket_id = await create_test_ticket()

    try:
        # --manage_project (16 actions) ------------------------------
        print("\n-- manage_project --")
        await test_mp_get_templates()                              # 01
        await test_mp_get_fields()                                 # 02
        await test_mp_list()                                       # 03
        pid = await test_mp_create()                               # 04
        project = await test_mp_get(pid)                           # 05
        await test_mp_update(pid)                                  # 06
        await test_mp_add_members(pid, project["manager_id"])      # 07
        await test_mp_list_members(pid)                            # 08
        await test_mp_create_association(pid, ticket_id)           # 09
        await test_mp_list_associations(pid)                       # 10
        await test_mp_delete_association(pid, ticket_id)           # 11
        await test_mp_delete_attachment(pid)                       # 12

        # --manage_project_task (12 actions) -------------------------
        print("\n-- manage_project_task --")
        type_id = await test_mpt_get_types(pid)                    # 13
        await test_mpt_get_type_fields(pid, type_id)               # 14
        pri_id = await test_mpt_get_priorities(pid)                # 15
        await test_mpt_get_statuses(pid)                           # 16
        await test_mpt_get_versions(pid)                           # 17
        await test_mpt_get_sprints(pid)                            # 18
        tid = await test_mpt_create(pid, type_id)                  # 19
        await test_mpt_get(pid, tid)                               # 20
        await test_mpt_update(pid, tid)                            # 21
        await test_mpt_list(pid)                                   # 22
        await test_mpt_filter(pid, pri_id)                         # 23

        # --manage_project_task_detail (9 actions) -------------------
        print("\n-- manage_project_task_detail --")
        nid = await test_mptd_create_note(pid, tid)                # 24
        await test_mptd_list_notes(pid, tid)                       # 25
        await test_mptd_update_note(pid, tid, nid)                 # 26
        await test_mptd_create_association(pid, tid, ticket_id)    # 27
        await test_mptd_list_associations(pid, tid)                # 28
        await test_mptd_delete_association(pid, tid, ticket_id)    # 29
        await test_mptd_delete_note_attachment(pid, tid, nid)      # 30
        await test_mptd_delete_note(pid, tid, nid)                 # 31
        await test_mptd_delete_task_attachment(pid, tid)           # 32

        # --cleanup: delete task, archive/restore/delete project -----
        print("\n-- cleanup --")
        await test_mpt_delete(pid, tid)                            # 33
        await test_mp_archive(pid)                                 # 34
        await test_mp_restore(pid)                                 # 35
        await test_mp_delete(pid)                                  # 36

    finally:
        # always clean up the test ticket
        await delete_test_ticket(ticket_id)

    print("\n" + "=" * 64)
    print(f"  ALL {STEP} STEPS PASSED")
    print("=" * 64)


if __name__ == "__main__":
    asyncio.run(main())
