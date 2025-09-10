from typing import List, Dict, Any, Optional, Annotated, cast
import httpx
from arcade_tdk import tool, ToolContext
from todoist.tools.client import TodoistClient

@tool(requires_secrets=["TODOIST_API_TOKEN"])
def list_projects(ctx: ToolContext) -> str:
    """
    Return the user's Todoist projects.
    Returns a formatted string listing all projects with their IDs and names.
    Requires secret: TODOIST_API_TOKEN
    """
    token = ctx.get_secret("TODOIST_API_TOKEN")
    result = TodoistClient(token).get("/projects")
    if not result:
        return "No projects found."
    
    # Format the projects as a readable string
    project_list = []
    # Type assertion: /projects endpoint returns a list of dictionaries
    projects = cast(List[Dict[str, Any]], result)
    for project in projects:
        project_info = f"ID: {project.get('id', 'N/A')}, Name: {project.get('name', 'N/A')}"
        project_list.append(project_info)
    
    return "\n".join(project_list)

@tool(requires_secrets=["TODOIST_API_TOKEN"])
def create_project(
    ctx: ToolContext,
    name: Annotated[str, "The name of the project (required)"],
) -> Dict[str, Any]:
    """
    Create a new project in Todoist.
    Returns the created project object including the project ID.
    Use the 'id' field from the response to add tasks to this project.
    
    Example:
        project = create_project("My New Project")
        project_id = project["id"]  # Use this ID to add tasks
        add_task("Task content", project_id=project_id)
    
    Requires secret: TODOIST_API_TOKEN
    """
    token = ctx.get_secret("TODOIST_API_TOKEN")
    payload = {k: v for k, v in dict(
        name=name
    ).items() if v is not None}
    result = TodoistClient(token).post("/projects", json=payload)
    
    # Handle case where API returns boolean (204 status) instead of JSON
    if isinstance(result, bool):
        # If we get a boolean, it means success but no content returned
        # This shouldn't happen for project creation, but handle it gracefully
        raise RuntimeError("Project creation succeeded but no project data was returned")
    
    return result

@tool(requires_secrets=["TODOIST_API_TOKEN"])
def delete_project(ctx: ToolContext, project_id: Annotated[str, "The ID of the project to delete"]) -> bool:
    """
    Delete a project in Todoist.
    Requires secret: TODOIST_API_TOKEN
    """
    token = ctx.get_secret("TODOIST_API_TOKEN")
    # Use DELETE method instead of POST
    with httpx.Client(timeout=15) as c:
        r = c.delete(f"https://api.todoist.com/rest/v2/projects/{project_id}", 
            headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return True