"""Integration tests for Solutions tool.

Covers ALL 13 actions in manage_solution:
  Categories: list_categories, get_category, create_category, update_category
  Folders:    list_folders, get_folder, create_folder, update_folder
  Articles:   list_articles, get_article, create_article, update_article, publish_article

Prints PASS/FAIL per step, stops on first failure.

Usage:
    export FRESHSERVICE_APIKEY=...
    export FRESHSERVICE_DOMAIN=yourco.freshservice.com
    uv run python tests/test_solutions.py
"""

import asyncio
import sys
import json
import time
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
#  Categories (4 actions)
# ======================================================================

async def test_list_categories() -> None:
    t = tag("manage_solution: list_categories")
    resp = await api_get("solutions/categories")
    data = expect(resp, t)
    ok(t, "Listed categories")


async def test_create_category() -> int:
    t = tag("manage_solution: create_category")
    name = f"MCP Test Category {int(time.time())}"
    resp = await api_post("solutions/categories", json={
        "name": name,
        "description": "Created by MCP integration test",
    })
    data = expect(resp, t, (200, 201))
    cat = data.get("category", data)
    cid = cat.get("id")
    if not cid:
        fail(t, f"No category ID in response: {pp(data)}")
    ok(t, f"Created category id={cid} name='{name}'")
    return cid


async def test_get_category(cid: int) -> None:
    t = tag("manage_solution: get_category")
    resp = await api_get(f"solutions/categories/{cid}")
    data = expect(resp, t)
    cat = data.get("category", data)
    ok(t, f"Got category '{cat.get('name', '?')}'")


async def test_update_category(cid: int) -> None:
    t = tag("manage_solution: update_category")
    resp = await api_put(f"solutions/categories/{cid}", json={
        "description": "Updated by MCP integration test",
    })
    expect(resp, t, (200, 204))
    ok(t, f"Updated category {cid}")


# ======================================================================
#  Folders (4 actions)
# ======================================================================

async def test_list_folders(cid: int) -> None:
    t = tag("manage_solution: list_folders")
    resp = await api_get("solutions/folders", params={"category_id": cid})
    data = expect(resp, t)
    ok(t, "Listed folders")


async def test_create_folder(cid: int) -> int:
    t = tag("manage_solution: create_folder")
    name = f"MCP Test Folder {int(time.time())}"
    resp = await api_post("solutions/folders", json={
        "name": name,
        "description": "Created by MCP integration test",
        "category_id": cid,
        "visibility": 1,
    })
    data = expect(resp, t, (200, 201))
    folder = data.get("folder", data)
    fid = folder.get("id")
    if not fid:
        fail(t, f"No folder ID in response: {pp(data)}")
    ok(t, f"Created folder id={fid} name='{name}'")
    return fid


async def test_get_folder(fid: int) -> None:
    t = tag("manage_solution: get_folder")
    resp = await api_get(f"solutions/folders/{fid}")
    data = expect(resp, t)
    folder = data.get("folder", data)
    ok(t, f"Got folder '{folder.get('name', '?')}'")


async def test_update_folder(fid: int) -> None:
    t = tag("manage_solution: update_folder")
    resp = await api_put(f"solutions/folders/{fid}", json={
        "description": "Updated by MCP integration test",
    })
    expect(resp, t, (200, 204))
    ok(t, f"Updated folder {fid}")


# ======================================================================
#  Articles (5 actions)
# ======================================================================

async def test_list_articles(fid: int) -> None:
    t = tag("manage_solution: list_articles")
    resp = await api_get("solutions/articles", params={"folder_id": fid})
    data = expect(resp, t)
    ok(t, "Listed articles")


async def test_create_article(fid: int) -> int:
    t = tag("manage_solution: create_article")
    title = f"MCP Test Article {int(time.time())}"
    resp = await api_post("solutions/articles", json={
        "title": title,
        "description": "<p>Created by MCP integration test</p>",
        "folder_id": fid,
        "article_type": 1,
        "status": 1,
    })
    data = expect(resp, t, (200, 201))
    article = data.get("article", data)
    aid = article.get("id")
    if not aid:
        fail(t, f"No article ID in response: {pp(data)}")
    ok(t, f"Created article id={aid} title='{title}'")
    return aid


async def test_get_article(aid: int) -> None:
    t = tag("manage_solution: get_article")
    resp = await api_get(f"solutions/articles/{aid}")
    data = expect(resp, t)
    article = data.get("article", data)
    ok(t, f"Got article '{article.get('title', '?')}'")


async def test_update_article(aid: int) -> None:
    t = tag("manage_solution: update_article")
    resp = await api_put(f"solutions/articles/{aid}", json={
        "description": "<p>Updated by MCP integration test</p>",
    })
    expect(resp, t, (200, 204))
    ok(t, f"Updated article {aid}")


async def test_publish_article(aid: int) -> None:
    t = tag("manage_solution: publish_article")
    resp = await api_put(f"solutions/articles/{aid}", json={
        "status": 2,
    })
    expect(resp, t, (200, 204))
    ok(t, f"Published article {aid}")


# ======================================================================
#  Cleanup helpers
# ======================================================================

async def delete_article(aid: int) -> None:
    resp = await api_delete(f"solutions/articles/{aid}")
    if resp.status_code in (200, 204):
        print(f"  CLEANUP Deleted article {aid}")
    else:
        print(f"  WARN Could not delete article {aid}: {resp.status_code}")


async def delete_folder(fid: int) -> None:
    resp = await api_delete(f"solutions/folders/{fid}")
    if resp.status_code in (200, 204):
        print(f"  CLEANUP Deleted folder {fid}")
    else:
        print(f"  WARN Could not delete folder {fid}: {resp.status_code}")


async def delete_category(cid: int) -> None:
    resp = await api_delete(f"solutions/categories/{cid}")
    if resp.status_code in (200, 204):
        print(f"  CLEANUP Deleted category {cid}")
    else:
        print(f"  WARN Could not delete category {cid}: {resp.status_code}")


# ======================================================================
#  main
# ======================================================================

async def main() -> None:
    print("=" * 64)
    print("  Freshservice Solutions - Full Integration Test Suite")
    print("  13 actions in manage_solution, 0 skipped")
    print("=" * 64)

    cid = 0
    fid = 0
    aid = 0

    try:
        # -- Categories (4 actions) --
        print("\n-- Categories --")
        await test_list_categories()                               # 01
        cid = await test_create_category()                         # 02
        await test_get_category(cid)                               # 03
        await test_update_category(cid)                            # 04

        # -- Folders (4 actions) --
        print("\n-- Folders --")
        await test_list_folders(cid)                               # 05
        fid = await test_create_folder(cid)                        # 06
        await test_get_folder(fid)                                 # 07
        await test_update_folder(fid)                              # 08

        # -- Articles (5 actions) --
        print("\n-- Articles --")
        await test_list_articles(fid)                              # 09
        aid = await test_create_article(fid)                       # 10
        await test_get_article(aid)                                # 11
        await test_update_article(aid)                             # 12
        await test_publish_article(aid)                            # 13

    finally:
        # Clean up in reverse order: article -> folder -> category
        print("\n-- cleanup --")
        if aid:
            await delete_article(aid)
        if fid:
            await delete_folder(fid)
        if cid:
            await delete_category(cid)

    print("\n" + "=" * 64)
    print(f"  ALL {STEP} STEPS PASSED")
    print("=" * 64)


if __name__ == "__main__":
    asyncio.run(main())
