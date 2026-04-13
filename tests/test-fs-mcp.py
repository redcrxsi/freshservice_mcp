import asyncio
from freshservice_mcp.server import add_requester_to_group, create_ticket, filter_agents, filter_requesters, filter_tickets, publish_solution_article,update_ticket,delete_ticket,get_ticket_by_id,list_service_items,get_requested_items,create_service_request,create_ticket_note,send_ticket_reply,list_all_ticket_conversation,update_ticket_conversation,get_all_products,get_products_by_id,create_product,update_product,create_requester,get_requester_id,update_requester,list_all_requester_fields,create_agent,get_agent,get_all_agents,update_agent,get_agent_fields,get_all_agent_groups,getAgentGroupById,create_group,update_requester_group,update_group,get_requester_groups_by_id,list_requester_group_members,create_requester_group,list_all_workspaces,get_workspace,get_all_canned_response,get_canned_response,list_all_canned_response_folder,get_all_solution_category,get_solution_category,create_solution_category,update_solution_category,get_list_of_solution_folder,create_solution_folder,update_solution_folder,create_solution_article,update_solution_article,get_list_of_solution_article,get_solution_article

async def test_create_ticket():
    payload = {
  "email": "marketing.lead@company.com",
  "source": 2,
  "status": 2,
  "subject": "Network Connectivity Issues in Marketing Department",
  "priority": 3,
  "description": "Several employees in the Marketing department are experiencing intermittent network connectivity issues. The problem started this morning around 9:30 AM. Users report that their internet connection drops every 15-20 minutes and reconnects after about 30 seconds. This is disrupting their workflow, especially for those working on time-sensitive campaign materials."
}
    result = await create_ticket(payload["subject"],payload["description"],payload["source"],payload["priority"],payload["status"],payload["email"])
    print(result)

async def test_update_ticket():
    ticket_id = 862
    ticket_fields = {
        "source": 3,
        "status": 2,
        "subject": "UPDATED",
        "priority": 4,
    }
    result = await update_ticket(ticket_id,ticket_fields)
    print(result)

async def test_delete_ticket():
    ticket_id = 862
    result = await delete_ticket(ticket_id)
    print(result)

async def test_get_ticket_by_id():
    ticket_id = 861
    result = await get_ticket_by_id(ticket_id)
    print(result)

async def test_list_service_items():
    result = await list_service_items()
    print(result)

async def test_get_requested_items():
    ticket_id = 848
    result = await get_requested_items(ticket_id)
    print(result)

async def test_create_service_request():
    display_id = 10
    email = "maanaesh.s@effy.co.in"
    requested_for = "gopi@effy.co.in"
    quantity= 2
    result = await create_service_request(display_id,email,requested_for,quantity)
    print(result)

async def test_create_ticket_note():
    ticket_id = 848
    body="<h1>TEST NOTE</h1>"
    result = await create_ticket_note(ticket_id,body)
    print(result)


async def test_send_ticket_reply():
    ticket_id = 848
    body = "Thank you for reaching out. We are reviewing your ticket and will get back to you shortly."
    result = await send_ticket_reply(
        ticket_id=ticket_id,
        body=body,    
    )
    print(result)

async def test_list_all_ticket_conversation():
    ticket_id = 848
    result = await list_all_ticket_conversation(ticket_id)
    print(result)

async def test_update_ticket_conversation():
  
    id = 27094915080
    body = "<h1>Hiiii</h1>"
    result = await update_ticket_conversation(id,body)
    print(result)

async def test_get_all_products():
    result = await get_all_products()
    print(result)

async def test_get_products_by_id():
    id = 27000094367
    result = await get_products_by_id(id)
    print(result)

async def test_create_product():
    result = await create_product(
        name="Laptop X100",
        asset_type_id=27000798668,
        manufacturer="TechCorp",
        status="In Pipeline",
        mode_of_procurement="Buy",
        description="High-performance business laptop",
    )
    print(result)
async def test_update_product():
    updated_product = await update_product(
        id=27000331519,
        name="Laptop X100 - Updated",
        asset_type_id=27000798668,
        manufacturer="TechCorp International",
        status=1,
        mode_of_procurement="Lease",
        description="<div>Updated: Now with better specs</div>",
    )
    print(updated_product)

async def test_create_requester():
    first_name="Havertz",
    primary_email="havertz@arsenal.com"
    result = await create_requester(first_name=str(first_name),primary_email=primary_email)
    print(result)

async def test_get_requester_id():
    id = 27005859432
    result = await get_requester_id(id)
    print(result)

async def test_update_requester():
    id = 27005859432
    result = await update_requester(requester_id=id,first_name="Kai")
    print(result)

async def test_list_all_requester_fields():
    result = await list_all_requester_fields()
    print(result)
async def test_create_agent():
    name = "Raya"
    email = "davidraya@arsenal.com"
    result = await create_agent(first_name=name,email=email)
    print(result)
async def test_get_agent():
    id = 27005859458
    result = await get_agent(id)
    print(result)

async def test_get_all_agents():
    result = await get_all_agents()
    print(result)

async def test_update_agent():
    id=27005859458
    email="leno@afc.co.in"
    result = await update_agent(agent_id=id,email=email)
    print(result)

async def test_get_agent_fields():
    result = await get_agent_fields()
    print(result)

async def test_get_all_agent_groups():
    result = await get_all_agent_groups()
    print(result)

async def test_getAgentGroupById():
    id = 27000298443
    result = await getAgentGroupById(id)
    print(result)

async def test_create_group():
    payload = {
  "name": "Support Team effy x TEST",
  "description": "Handles general support inquiries",
  "agent_ids": [27000465570],
  "auto_ticket_assign": True,
  "escalate_to": 201,
  "unassigned_for": "THIRTY_MIN"
}
    result = await create_group(group_fields= payload)
    print(result)

async def test_update_group():
    id = 27000298443
    payload = {
        
  "name": "Support Team effy x TEST",
  "description": "Handles general support inquiries",
    }
    result = await update_group(group_id=id , group_fields= payload)
    print(result)

async def test_update_requester_group():
    id = 27000229326
    name = "Capacity Ops"
    result = await update_requester_group(id=id,name=name)
    print(result)

async def test_get_requester_groups_by_id():
    id = 27000229326
    result = await get_requester_groups_by_id(id)
    print(result)

async def test_list_requester_group_members():
    id = 27000229326
    result = await list_requester_group_members(id)
    print(result)

async def test_create_requester_group():
    name="Group A"
    description="List Of teams that belong to Group A"
    result = await create_requester_group(name=name,description=description)
    print(result)

async def test_list_all_workspaces():
    result = await list_all_workspaces()
    print(result)

async def test_get_workspace():
    id=2
    result = await get_workspace(id=id)
    print(result)

async def test_get_all_canned_response():
    result = await get_all_canned_response()
    print(result)

async def test_get_canned_response():
    id = 27000031007
    result = await get_canned_response(id=id)
    print(result)

async def test_list_all_canned_response_folder():
    result = await list_all_canned_response_folder()
    print(result)

async def test_get_all_solution_category():
    result = await get_all_solution_category()
    print(result)

async def test_get_solution_category():
    id = 27000124576
    result = await get_solution_category(id)
    print(result)

async def test_create_solution_category():
    name="Tactical Solutions"
    description="List of tactics to follow"
    result = await create_solution_category(name=name,description=description)
    print(result)

async def test_update_solution_category ():
    id =27000124578
    name = "Football Tactic"
    result = await update_solution_category(category_id=id,name=name)
    print(result)
async def test_get_list_of_solution_folder():
    id = 27000124578
    result = await get_list_of_solution_folder(id=id)
    print(result)

async def test_create_solution_folder():
    name="433 Tactics"
    category_id = 27000124578
    department_ids = [27001017280]
    result = await create_solution_folder(name=name,category_id=category_id,department_ids=department_ids)
    print(result)
    #27000183948

async def test_update_solution_folder():
    id = 27000183948
    name = "GengenPress Tactics"
    result = await update_solution_folder(id=id,name=name)
    print(result)

async def test_create_solution_article():
    title = "GengenPress Football Tactics"
    description = """
        <p>The GengenPress is a high-intensity football tactic where a team immediately presses the ball after losing possession, aiming to win it back quickly.</p>
        <p>This article covers the key principles, advantages, and how to train your squad to master this approach.</p>
    """
    folder_id = 27000183948 
    article_type = 1         # Permanent
    status = 2               # Published
    tags = ["football", "tactics", "pressing", "gengenpress"]
    keywords = ["gengenpress", "football tactics", "high press"]
    review_date = "2025-12-01"

    result = await create_solution_article(
        title=title,
        description=description,
        folder_id=folder_id,
        article_type=article_type,
        status=status,
        tags=tags,
        keywords=keywords,
        review_date=review_date
    )
    # id 27000093242
    print(result)

async def test_update_solution_article():
    id = 27000093242
    title = "GengenPress Football Tactics - A complete guide"
    result = await update_solution_article(article_id=id,title=title)
    print (result)

async def test_get_list_of_solution_article():
    id= 27000183948
    result = await get_list_of_solution_article(id=id)
    print(result)

async def test_get_solution_article():
    id = 27000093242
    result = await get_solution_article(id=id)
    print(result)

async def test_filter_tickets():
    # Quotes are now automatically added by the function
    query = "priority:3"
    result = await filter_tickets(query)
    print(result)

async def test_filter_requesters():
    query = "primary_email:'vijay.r@effy.co.in'"  
    include_agents = True  

    result = await filter_requesters(query, include_agents)
    print(result)
        
async def test_filter_agents():
    # Quotes are now automatically added by the function
    # Note: use valid filter fields like first_name, email, etc.
    query = "first_name:John"
    agents = await filter_agents(query)
    print(agents)

async def test_add_requester_to_group():
    group_id = 27000229326  
    requester_id = 27005854063  

    result = await add_requester_to_group(group_id, requester_id)
    print(result)

async def test_publish_solution_article():
    article_id = 27000093217 
    result = await publish_solution_article(article_id)
    print(result)

# ---------------------------------------------------------------------------
# Journey tests — read-only (safe to run against live instance)
# ---------------------------------------------------------------------------

async def test_journey_list_configs():
    """List all published journey configs."""
    from freshservice_mcp.tools.journeys import register_journeys_tools
    from freshservice_mcp.http_client import api_get
    resp = await api_get("journeys/configs", params={"page": 1})
    resp.raise_for_status()
    data = resp.json()
    print("=== Journey Configs ===")
    print(data)
    return data

async def test_journey_get_data_fields(config_id: int):
    """Get initiator form data-fields for a given journey config."""
    from freshservice_mcp.http_client import api_get
    resp = await api_get(f"journeys/configs/{config_id}/data-fields")
    resp.raise_for_status()
    data = resp.json()
    print(f"=== Data Fields for config {config_id} ===")
    print(data)
    return data

async def test_journey_list_requests():
    """List journey requests (filter=all, per_page=5)."""
    from freshservice_mcp.http_client import api_get
    resp = await api_get("journeys/requests", params={"filter": "all", "per_page": 5, "page": 1})
    resp.raise_for_status()
    data = resp.json()
    print("=== Journey Requests (all, first 5) ===")
    print(data)
    return data

async def test_journey_filter_requests():
    """Filter journey requests — completed status (2)."""
    from freshservice_mcp.http_client import api_post
    body = {
        "data": {
            "query": {
                "filter": [
                    {
                        "attributes": [
                            {"field": "status", "operator": "is_in", "value": [2]}
                        ]
                    }
                ]
            }
        }
    }
    resp = await api_post("journeys/requests/view", json=body)
    resp.raise_for_status()
    data = resp.json()
    print("=== Filtered Journey Requests (completed) ===")
    print(data)
    return data

async def test_journey_get_request(request_id: int):
    """Get a single journey request by ID."""
    from freshservice_mcp.http_client import api_get
    resp = await api_get(f"journeys/requests/{request_id}")
    resp.raise_for_status()
    data = resp.json()
    print(f"=== Journey Request {request_id} ===")
    print(data)
    return data

async def test_journey_list_activities(request_id: int):
    """List activities for a journey request."""
    from freshservice_mcp.http_client import api_get
    resp = await api_get(f"journeys/requests/{request_id}/activities")
    resp.raise_for_status()
    data = resp.json()
    print(f"=== Activities for request {request_id} ===")
    print(data)
    return data

async def test_journey_read_only_suite():
    """Run all read-only journey tests in sequence."""
    print("\n--- 1. List configs ---")
    configs = await test_journey_list_configs()

    # Pick first config id for data-fields test
    journey_configs = configs.get("journey_configs", [])
    if journey_configs:
        cid = journey_configs[0]["id"]
        print(f"\n--- 2. Get data-fields for config {cid} ---")
        await test_journey_get_data_fields(cid)

    print("\n--- 3. List requests (all) ---")
    requests_data = await test_journey_list_requests()

    print("\n--- 4. Filter requests (completed) ---")
    await test_journey_filter_requests()

    # Pick first request id for get + activities
    journey_requests = requests_data.get("journey_requests", [])
    if journey_requests:
        rid = journey_requests[0]["id"]
        print(f"\n--- 5. Get request {rid} ---")
        await test_journey_get_request(rid)
        print(f"\n--- 6. List activities for request {rid} ---")
        await test_journey_list_activities(rid)

    print("\n=== Read-only journey test suite complete ===")


# ---------------------------------------------------------------------------
# Journey tests — DESTRUCTIVE — requires test journey_id
# Do NOT run automatically. Confirm journey_id with user first.
# ---------------------------------------------------------------------------

async def test_journey_write_suite(journey_id: int, initiator_data: dict):
    """Run create -> get -> update -> cancel -> delete sequence.

    Args:
        journey_id: A test/sandbox journey config ID (NOT production).
        initiator_data: Dict matching the journey's initiator form, e.g.
            {"request_for": "test@example.com", "custom_fields": {"cf_text": "MCP-TEST"}}
    """
    import time
    from freshservice_mcp.http_client import api_post, api_get, api_patch, api_put, api_delete

    tag = f"MCP-TEST-{int(time.time())}"
    print(f"\n=== WRITE SUITE (tag={tag}) ===")

    # -- create --
    print("\n--- create ---")
    create_body = {"journey_id": journey_id, "initiator_data": initiator_data}
    resp = await api_post("journeys/requests", json=create_body)
    resp.raise_for_status()
    created = resp.json()
    print(created)
    req = created.get("journey_request", created)
    request_id = req["id"]
    print(f"Created request_id={request_id}")

    # -- get (verify) --
    print(f"\n--- get {request_id} ---")
    resp = await api_get(f"journeys/requests/{request_id}")
    resp.raise_for_status()
    print(resp.json())

    # -- update --
    print(f"\n--- update {request_id} ---")
    update_body = {"initiator_data": {"custom_fields": {"cf_text": f"{tag}-UPDATED"}}}
    resp = await api_patch(f"journeys/requests/{request_id}", json=update_body)
    resp.raise_for_status()
    print(resp.json())

    # -- cancel --
    print(f"\n--- cancel {request_id} ---")
    resp = await api_put(f"journeys/requests/{request_id}/cancel")
    resp.raise_for_status()
    print(resp.json())

    # -- delete --
    print(f"\n--- delete {request_id} ---")
    resp = await api_delete(f"journeys/requests/{request_id}")
    print(f"Status: {resp.status_code}")
    if resp.status_code == 204:
        print("Deleted successfully")
    else:
        print(resp.text)

    print("\n=== Write suite complete ===")


if __name__ == "__main__":
    # asyncio.run(test_create_ticket())
    # asyncio.run(test_update_ticket())
    # asyncio.run(test_delete_ticket())
    # asyncio.run(test_get_ticket_by_id())
    # asyncio.run(test_list_service_items())
    # asyncio.run(test_get_requested_items())
    # asyncio.run(test_create_service_request())
    # asyncio.run(test_create_ticket_note())
    # asyncio.run(test_send_ticket_reply())
    # asyncio.run(test_list_all_ticket_conversation())
    # asyncio.run(test_update_ticket_conversation())
    # asyncio.run(test_get_all_products())
    # asyncio.run(test_get_products_by_id())
    # asyncio.run(test_create_product())
    # asyncio.run(test_update_product())
    # asyncio.run(test_create_requester())
    # asyncio.run(test_get_requester_id())
    # asyncio.run(test_update_requester())
    # asyncio.run(test_list_all_requester_fields())
    # asyncio.run(test_create_agent())
    # asyncio.run(test_get_agent())
    # asyncio.run(test_get_all_agents())
    # asyncio.run(test_update_agent())
    # asyncio.run(test_get_agent_fields())
    # asyncio.run(test_get_all_agent_groups())
    # asyncio.run(test_getAgentGroupById())
    # asyncio.run(test_create_group())
    # asyncio.run(test_update_group())
    # asyncio.run(test_update_requester_group())
    # asyncio.run(test_get_requester_groups_by_id())
    # asyncio.run(test_list_requester_group_members())
    # asyncio.run(test_create_requester_group())
    # asyncio.run(test_list_all_workspaces())
    # asyncio.run(test_get_workspace())
    # asyncio.run(test_get_all_canned_response())
    # asyncio.run(test_get_canned_response())
    # asyncio.run(test_list_all_canned_response_folder())
    # asyncio.run(test_get_all_solution_category())
    # asyncio.run(test_create_solution_category())
    # asyncio.run(test_update_solution_category())
    # asyncio.run(test_get_list_of_solution_folder())
    # asyncio.run(test_create_solution_folder())
    # asyncio.run(test_update_solution_folder())
    # asyncio.run(test_create_solution_article())
    # asyncio.run(test_update_solution_article()) 
    # asyncio.run(test_get_list_of_solution_article())
    # asyncio.run(test_get_solution_article())
    asyncio.run(test_filter_tickets())
    # asyncio.run(test_filter_requesters())
    # asyncio.run(test_filter_agents())
    # asyncio.run(test_publish_solution_article())
    # asyncio.run(test_add_requester_to_group())
    #
    # --- Journey tests (read-only) ---
    # asyncio.run(test_journey_read_only_suite())
    #
    # --- Journey tests (DESTRUCTIVE — confirm journey_id first!) ---
    # asyncio.run(test_journey_write_suite(
    #     journey_id=<SAFE_TEST_JOURNEY_ID>,
    #     initiator_data={"request_for": "mcp-test@example.com",
    #                      "custom_fields": {"cf_text": "MCP-TEST"}}
    # ))
    
    
    