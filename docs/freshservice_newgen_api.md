# Freshservice New-Gen Projects & Project Tasks API Documentation

## IMPORTANT: These are NEW-GEN APIs
The following Project APIs are for new-gen project management and these are NOT compatible with the legacy project management module.

## Base URL Pattern
- Projects: /api/v2/pm/projects
- Project Tasks: /api/v2/pm/projects/{project_id}/tasks

---

## PROJECTS (New-Gen)

### Project Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| id | number | Unique identifier of the project. READ-ONLY |
| name | string | Name of the project. Max 255 characters. |
| description | string | Description in plain text or HTML format. |
| key | string | Project Key. Starts with letter, followed by letters/numbers. Max 10 chars. |
| status_id | number | Status of the project. |
| priority_id | number | Priority of the project. |
| project_type | number | Type: Business or Software. |
| manager_id | number | User ID of the project manager. |
| start_date | date | Format: yyyy-mm-dd |
| end_date | date | Format: yyyy-mm-dd |
| visibility | number | Public / Private. |
| sprint_duration | number | Sprint duration in days. |
| custom_fields | dictionary | Key value pairs of custom fields. |
| archived | boolean | Whether project is archived. READ-ONLY |
| created_at | datetime | Date/time of creation. READ-ONLY |
| updated_at | datetime | Date/time of last update. READ-ONLY |

### Project Properties (Enums)

Status: 1=Yet to start, 2=In Progress, 3=Completed
Priority: 1=Low, 2=Medium, 3=High, 4=Urgent
Project Type: 0=Software Project, 1=Business Project
Visibility: 0=Private, 1=Public

### Endpoints

- Create: POST /api/v2/pm/projects (mandatory: name, project_type) - scope: freshservice.projects.manage
- Create with attachment: POST /api/v2/pm/projects (Content-Type: multipart/form-data, attachments[] field)
- Update: PUT /api/v2/pm/projects/{id}
- View: GET /api/v2/pm/projects/{id} - scope: freshservice.projects.read OR .manage
- List All: GET /api/v2/pm/projects - paginated, returns {"projects": [...]}
- Delete: DELETE /api/v2/pm/projects/{id} - returns 204
- Archive: PUT /api/v2/pm/projects/{id}/archive - returns 204
- Restore: PUT /api/v2/pm/projects/{id}/restore - returns 204
- View Fields: GET /api/v2/pm/projects/fields
- View Templates: GET /api/v2/pm/project-templates
- Add Members: POST /api/v2/pm/projects/{id}/members - body: {"member_ids": [id1, id2]}
- Create Associations: POST /api/v2/pm/projects/{id}/associations - body: {"associations": [{"associatable_id": 123, "associatable_type": "Helpdesk::Ticket"}]}
- View Associations: GET /api/v2/pm/projects/{id}/associations
- Delete Association: DELETE /api/v2/pm/projects/{project_id}/associations/{association_id}
- Delete Attachment: DELETE /api/v2/pm/projects/{project_id}/attachments/{attachment_id}

associatable_type values: "Helpdesk::Ticket", "Helpdesk::Change", "Helpdesk::Asset"

Response format: {"project": {...}} for single, {"projects": [...]} for list

---

## PROJECT TASKS (New-Gen)

### Task Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| id | number | Unique identifier. READ-ONLY |
| title | string | Title. Max 255 chars. |
| description | string | Description in plain text or HTML. |
| project_id | number | Parent project ID. READ-ONLY |
| type_id | number | Task type ID. |
| reporter_id | number | Reporter user ID. |
| assignee_id | number | Assignee user ID. |
| status_id | number | Status. |
| priority_id | number | Priority. |
| story_points | number | Story points. |
| planned_start_date | date | Planned start date. |
| planned_end_date | date | Planned end date. |
| planned_effort | string | Planned effort e.g. "1:30" |
| planned_duration | number | Duration in seconds. |
| version_id | number | Version/release ID. |
| sprint_id | number | Sprint ID. |
| parent_id | number | Parent task ID for subtasks. |
| custom_fields | dictionary | Custom fields. |
| created_at | datetime | READ-ONLY |
| updated_at | datetime | READ-ONLY |

### Task Endpoints

- Create: POST /api/v2/pm/projects/{project_id}/tasks (mandatory: title)
- Update: PUT /api/v2/pm/projects/{project_id}/tasks/{id}
- View: GET /api/v2/pm/projects/{project_id}/tasks/{id}
- List All: GET /api/v2/pm/projects/{project_id}/tasks - paginated {"tasks": [...]}
- Filter: GET /api/v2/pm/projects/{project_id}/tasks/filter
- Delete: DELETE /api/v2/pm/projects/{project_id}/tasks/{id} - returns 204
- Task Type Fields: GET /api/v2/pm/projects/{project_id}/task-type-fields
- Task Types: GET /api/v2/pm/projects/{project_id}/task-types
- Task Priorities: GET /api/v2/pm/projects/{project_id}/task-priorities
- Task Statuses: GET /api/v2/pm/projects/{project_id}/task-statuses
- Versions: GET /api/v2/pm/projects/{project_id}/versions
- Sprints: GET /api/v2/pm/projects/{project_id}/sprints
- Memberships: GET /api/v2/pm/projects/{project_id}/members

### Task Associations
- Create: POST /api/v2/pm/projects/{project_id}/tasks/{task_id}/associations
- View: GET /api/v2/pm/projects/{project_id}/tasks/{task_id}/associations
- Delete: DELETE /api/v2/pm/projects/{project_id}/tasks/{task_id}/associations/{association_id}

### Task Notes
- Create: POST /api/v2/pm/projects/{project_id}/tasks/{task_id}/notes - body: {"body": "content"}
- View All: GET /api/v2/pm/projects/{project_id}/tasks/{task_id}/notes
- Update: PUT /api/v2/pm/projects/{project_id}/tasks/{task_id}/notes/{note_id}
- Delete: DELETE /api/v2/pm/projects/{project_id}/tasks/{task_id}/notes/{note_id}
- Delete Note Attachment: DELETE /api/v2/pm/projects/{project_id}/tasks/{task_id}/notes/{note_id}/attachments/{attachment_id}
- Delete Task Attachment: DELETE /api/v2/pm/projects/{project_id}/tasks/{task_id}/attachments/{attachment_id}
