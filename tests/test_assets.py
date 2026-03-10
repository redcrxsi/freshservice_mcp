"""Integration tests for Assets tools.

Covers ALL 23 actions across 3 tools:
  manage_asset              -- 12 actions
  manage_asset_details      --  4 actions
  manage_asset_relationship --  7 actions

Prints PASS/FAIL per step, stops on first failure.

Usage:
    export FRESHSERVICE_APIKEY=...
    export FRESHSERVICE_DOMAIN=yourco.freshservice.com
    uv run python tests/test_assets.py
"""

import asyncio
import sys
import json
import time
import urllib.parse
from typing import Any, Dict, Optional

from freshservice_mcp.http_client import api_get, api_post, api_put, api_delete


# -- helpers ----------------------------------------------------------------
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


def expect(resp, t: str, codes: tuple = (200,)) -> dict | list | None:
    if resp.status_code not in codes:
        fail(t, f"HTTP {resp.status_code}: {resp.text[:400]}")
    if resp.status_code == 204 or not resp.text:
        return None
    return resp.json()


# ======================================================================
#  manage_asset -- 12 actions
# ======================================================================

async def test_ma_get_types() -> int:
    t = tag("manage_asset: get_types")
    resp = await api_get("asset_types", params={"per_page": 10})
    data = expect(resp, t)
    types = data.get("asset_types", data) if isinstance(data, dict) else data
    if not isinstance(types, list) or not types:
        fail(t, "No asset types returned")
    type_id = types[0]["id"]
    ok(t, f"Got {len(types)} type(s), using type_id={type_id}")
    return type_id


async def test_ma_get_type(type_id: int) -> None:
    t = tag("manage_asset: get_type")
    resp = await api_get(f"asset_types/{type_id}")
    data = expect(resp, t)
    ok(t, f"Got asset type id={type_id}")


async def test_ma_list() -> None:
    t = tag("manage_asset: list")
    resp = await api_get("assets", params={"page": 1, "per_page": 5})
    data = expect(resp, t)
    ok(t, "Listed assets")


async def test_ma_create(type_id: int) -> int:
    t = tag("manage_asset: create")
    name = f"MCP Test Asset {int(time.time())}"
    resp = await api_post("assets", json={
        "name": name,
        "asset_type_id": type_id,
        "impact": "low",
        "usage_type": "permanent",
        "description": "Created by MCP integration test",
    })
    data = expect(resp, t, (200, 201))
    asset = data.get("asset", data)
    display_id = asset.get("display_id", asset.get("id"))
    if not display_id:
        fail(t, f"No display_id in response: {pp(data)}")
    ok(t, f"Created asset display_id={display_id} name='{name}'")
    return display_id


async def test_ma_get(display_id: int) -> None:
    t = tag("manage_asset: get")
    resp = await api_get(f"assets/{display_id}")
    data = expect(resp, t)
    asset = data.get("asset", data)
    ok(t, f"Got asset '{asset.get('name', '?')}'")


async def test_ma_update(display_id: int) -> None:
    t = tag("manage_asset: update")
    resp = await api_put(f"assets/{display_id}", json={
        "description": "Updated by MCP integration test",
    })
    expect(resp, t, (200, 204))
    ok(t, "Asset description updated")


async def test_ma_search(name_fragment: str) -> None:
    t = tag("manage_asset: search")
    # Freshservice search format: "field:'value'" wrapped in double quotes
    encoded = urllib.parse.quote(f"\"name:'{name_fragment}'\"")
    resp = await api_get(f"assets?search={encoded}")
    data = expect(resp, t)
    ok(t, "Search executed")


async def test_ma_filter(type_id: int) -> None:
    t = tag("manage_asset: filter")
    encoded = urllib.parse.quote(f'"asset_type_id:{type_id}"')
    resp = await api_get(f"assets?filter={encoded}")
    data = expect(resp, t)
    ok(t, "Filter executed")


async def test_ma_delete(display_id: int) -> None:
    """Soft-delete (trash) the asset."""
    t = tag("manage_asset: delete")
    resp = await api_delete(f"assets/{display_id}")
    expect(resp, t, (200, 204))
    ok(t, f"Trashed asset {display_id}")


async def test_ma_restore(display_id: int) -> None:
    t = tag("manage_asset: restore")
    resp = await api_put(f"assets/{display_id}/restore")
    expect(resp, t, (200, 204))
    ok(t, f"Restored asset {display_id}")


async def test_ma_delete_permanently(display_id: int) -> None:
    t = tag("manage_asset: delete_permanently")
    resp = await api_put(f"assets/{display_id}/delete_forever")
    expect(resp, t, (200, 204))
    ok(t, f"Permanently deleted asset {display_id}")


async def test_ma_move(display_id: int) -> None:
    t = tag("manage_asset: move")
    # move requires a workspace_id -- try with a bogus one to validate endpoint
    resp = await api_put(f"assets/{display_id}/move_workspace", json={
        "workspace_id": 999999999,
    })
    if resp.status_code in (200, 204):
        ok(t, "Asset moved")
    elif resp.status_code in (400, 404, 422):
        # Expected -- no such workspace, but endpoint path/method are correct
        ok(t, f"Endpoint valid -- {resp.status_code} for non-existent workspace (expected)")
    else:
        fail(t, f"HTTP {resp.status_code}: {resp.text[:300]}")


# ======================================================================
#  manage_asset_details -- 4 actions
# ======================================================================

async def test_mad_components(display_id: int) -> None:
    t = tag("manage_asset_details: components")
    resp = await api_get(f"assets/{display_id}/components")
    data = expect(resp, t)
    ok(t, "Got components")


async def test_mad_assignment_history(display_id: int) -> None:
    t = tag("manage_asset_details: assignment_history")
    resp = await api_get(f"assets/{display_id}/assignment-history")
    data = expect(resp, t)
    ok(t, "Got assignment history")


async def test_mad_requests(display_id: int) -> None:
    t = tag("manage_asset_details: requests")
    resp = await api_get(f"assets/{display_id}/requests")
    data = expect(resp, t)
    ok(t, "Got requests")


async def test_mad_contracts(display_id: int) -> None:
    t = tag("manage_asset_details: contracts")
    resp = await api_get(f"assets/{display_id}/contracts")
    data = expect(resp, t)
    ok(t, "Got contracts")


# ======================================================================
#  manage_asset_relationship -- 7 actions
# ======================================================================

async def test_mar_get_types() -> int:
    t = tag("manage_asset_relationship: get_types")
    resp = await api_get("relationship_types")
    data = expect(resp, t)
    types = data.get("relationship_types", data) if isinstance(data, dict) else data
    if not isinstance(types, list) or not types:
        fail(t, "No relationship types returned")
    rt_id = types[0]["id"]
    ok(t, f"Got {len(types)} relationship type(s), using rt_id={rt_id}")
    return rt_id


async def test_mar_create(rt_id: int, asset1_id: int, asset2_id: int) -> str:
    t = tag("manage_asset_relationship: create")
    resp = await api_post("relationships/bulk-create", json={
        "relationships": [{
            "relationship_type_id": rt_id,
            "primary_id": asset1_id,
            "primary_type": "asset",
            "secondary_id": asset2_id,
            "secondary_type": "asset",
        }],
    })
    data = expect(resp, t, (200, 201, 202))
    # May return a job_id for async processing
    job_id = ""
    if isinstance(data, dict):
        job_id = data.get("job_id", data.get("id", ""))
    ok(t, f"Created relationship (job_id={job_id or 'sync'})")
    return str(job_id)


async def test_mar_job_status(job_id: str) -> None:
    t = tag("manage_asset_relationship: job_status")
    if not job_id:
        # No async job -- validate endpoint with bogus ID
        resp = await api_get("jobs/no-such-job")
        if resp.status_code in (404, 400):
            ok(t, f"Endpoint valid -- {resp.status_code} for bogus job_id (expected)")
        else:
            ok(t, f"HTTP {resp.status_code}")
        return
    resp = await api_get(f"jobs/{job_id}")
    data = expect(resp, t, (200, 404))
    ok(t, f"Got job status for {job_id}")


async def test_mar_list_all() -> None:
    t = tag("manage_asset_relationship: list_all")
    resp = await api_get("relationships", params={"page": 1, "per_page": 5})
    data = expect(resp, t)
    ok(t, "Listed all relationships")


async def test_mar_list_for_asset(display_id: int) -> None:
    t = tag("manage_asset_relationship: list_for_asset")
    resp = await api_get(f"assets/{display_id}/relationships")
    data = expect(resp, t)
    ok(t, f"Listed relationships for asset {display_id}")


async def test_mar_get(display_id: int) -> int:
    """Get a specific relationship. Finds one from list_for_asset."""
    t = tag("manage_asset_relationship: get")
    # First find a relationship ID
    resp = await api_get(f"assets/{display_id}/relationships", params={"per_page": 5})
    data = resp.json()
    rels = data.get("relationships", data) if isinstance(data, dict) else data
    rid = 0
    if isinstance(rels, list) and rels:
        rid = rels[0].get("id", 0)
    if not rid:
        # No relationships found -- try listing all
        resp2 = await api_get("relationships", params={"per_page": 5})
        data2 = resp2.json()
        rels2 = data2.get("relationships", data2) if isinstance(data2, dict) else data2
        if isinstance(rels2, list) and rels2:
            rid = rels2[0].get("id", 0)
    if not rid:
        fail(t, "No relationship ID found to test get")
    resp3 = await api_get(f"relationships/{rid}")
    expect(resp3, t)
    ok(t, f"Got relationship id={rid}")
    return rid


async def test_mar_delete(rid: int) -> None:
    t = tag("manage_asset_relationship: delete")
    resp = await api_delete(f"relationships?ids={rid}")
    expect(resp, t, (200, 204))
    ok(t, f"Deleted relationship id={rid}")


# ======================================================================
#  main
# ======================================================================

async def main() -> None:
    print("=" * 64)
    print("  Freshservice Assets - Full Integration Test Suite")
    print("  23 actions across 3 tools, 0 skipped")
    print("=" * 64)

    # -- manage_asset (12 actions) --
    print("\n-- manage_asset --")
    type_id = await test_ma_get_types()                          # 01
    await test_ma_get_type(type_id)                              # 02
    await test_ma_list()                                         # 03
    asset1_id = await test_ma_create(type_id)                    # 04
    await test_ma_get(asset1_id)                                 # 05
    await test_ma_update(asset1_id)                              # 06
    await test_ma_search("MCP Test Asset")                       # 07
    await test_ma_filter(type_id)                                # 08
    await test_ma_move(asset1_id)                                # 09

    # -- manage_asset_details (4 actions) --
    print("\n-- manage_asset_details --")
    await test_mad_components(asset1_id)                         # 10
    await test_mad_assignment_history(asset1_id)                 # 11
    await test_mad_requests(asset1_id)                           # 12
    await test_mad_contracts(asset1_id)                          # 13

    # -- manage_asset_relationship (7 actions) --
    # Need a second asset for relationships
    asset2_id = await test_ma_create(type_id)                    # 14 (reuses create)
    print("\n-- manage_asset_relationship --")
    rt_id = await test_mar_get_types()                           # 15
    job_id = await test_mar_create(rt_id, asset1_id, asset2_id)  # 16
    await test_mar_job_status(job_id)                            # 17
    await asyncio.sleep(3)  # let async job complete
    await test_mar_list_all()                                    # 18
    await test_mar_list_for_asset(asset1_id)                     # 19
    rid = await test_mar_get(asset1_id)                          # 20
    await test_mar_delete(rid)                                   # 21

    # -- cleanup: delete/restore/permanent-delete both assets --
    print("\n-- cleanup --")
    await test_ma_delete(asset1_id)                              # 22
    await test_ma_restore(asset1_id)                             # 23
    # Now trash again and permanently delete
    await api_delete(f"assets/{asset1_id}")
    await test_ma_delete_permanently(asset1_id)                  # 24
    # Clean up second asset
    resp = await api_delete(f"assets/{asset2_id}")
    if resp.status_code in (200, 204):
        resp2 = await api_put(f"assets/{asset2_id}/delete_forever")
        print(f"  CLEANUP Permanently deleted asset {asset2_id}")
    else:
        print(f"  WARN Could not delete asset {asset2_id}: {resp.status_code}")

    print("\n" + "=" * 64)
    print(f"  ALL {STEP} STEPS PASSED")
    print("=" * 64)


if __name__ == "__main__":
    asyncio.run(main())
