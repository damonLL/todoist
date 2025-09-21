from typing import Optional, List, Dict, Any, Annotated, cast
import httpx
from arcade_tdk import tool, ToolContext
from arcade_tdk.auth import OAuth2
from todoist.tools.client import TodoistClient, resolve_todoist_token

@tool(requires_auth=OAuth2(id="todoist-oath-provider", scopes=["data:read_write"]))
def list_tasks(
    ctx: ToolContext,
    project_id: Annotated[Optional[str], "Filter by project ID"]=None,
    filter: Annotated[Optional[str], "Todoist filter (e.g., 'today' or 'p1')"]=None,
    label: Annotated[Optional[str], "Filter by label name"]=None,
    lang: Annotated[Optional[str], "IETF language tag for filter parsing"]=None,
) -> str:
    """
    List active tasks (REST v2). If `filter` is set, it takes precedence.
    Returns a formatted string listing all tasks with their details.
    """
    token = resolve_todoist_token(ctx)
    params = {k: v for k, v in dict(project_id=project_id, filter=filter, label=label, lang=lang).items() if v is not None}
    result = TodoistClient(token).get("/tasks", params=params)
    if not result:
        return "No tasks found."
    
    # Format the tasks as a readable string
    task_list = []
    # Type assertion: /tasks endpoint returns a list of dictionaries
    tasks = cast(List[Dict[str, Any]], result)
    for task in tasks:
        task_info = f"ID: {task.get('id', 'N/A')}, Content: {task.get('content', 'N/A')}"
        if task.get('due'):
            task_info += f", Due: {task.get('due', {}).get('date', 'N/A')}"
        if task.get('priority', 1) != 1:
            task_info += f", Priority: {task.get('priority', 1)}"
        task_list.append(task_info)
    
    return "\n".join(task_list)

@tool(requires_auth=OAuth2(id="todoist-oath-provider", scopes=["data:read_write"]))
def add_task(
    ctx: ToolContext,
    content: Annotated[str, "Task content (required)"],
    project_id: Annotated[Optional[str], "Project ID"]=None,
    due_string: Annotated[Optional[str], "Natural language due (e.g., 'tomorrow 5pm')"]=None,
    priority: Annotated[Optional[int], "1..4 (1=urgent,4=unimportant)"]=None,
    order: Annotated[Optional[int], "Order of the task in the project"]=None,
) -> Dict[str, Any]:
    """
    Create a task (REST v2) and return the created task.
    Returns the full task object including the task ID.
    """
    token = resolve_todoist_token(ctx)
    payload = {k: v for k, v in dict(content=content, project_id=project_id, due_string=due_string, order=order, priority=priority).items() if v is not None}
    
    try:
        result = TodoistClient(token).post("/tasks", json=payload)
        if not result or not isinstance(result, dict):
            raise ValueError(f"Unexpected response from Todoist API: {result}")
        if not result.get("id"):
            raise ValueError(f"Task created but no ID returned: {result}")
        return result
    except Exception as e:
        # Re-raise with more context
        raise RuntimeError(f"Failed to create task with payload {payload}: {e}") from e

@tool(requires_auth=OAuth2(id="todoist-oath-provider", scopes=["data:read_write"]))
def close_task(ctx: ToolContext, task_id: Annotated[str, "Task ID"]) -> bool:
    """
    Mark a task complete (REST v2). Returns True on 204 success.
    """
    token = resolve_todoist_token(ctx)
    return cast(bool, TodoistClient(token).post(f"/tasks/{task_id}/close"))


@tool(requires_auth=OAuth2(id="todoist-oath-provider", scopes=["data:read_write"]))
def delete_task(ctx: ToolContext, task_id: Annotated[str, "Task ID"]) -> bool:
    """
    Delete a task (REST v2). Returns True on 204 success.
    """
    token = resolve_todoist_token(ctx)
    # Use DELETE method instead of POST
    with httpx.Client(timeout=15) as c:
        r = c.delete(f"https://api.todoist.com/rest/v2/tasks/{task_id}", 
                    headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return True