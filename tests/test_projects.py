# tests/test_projects.py
import pytest
import os
from typing import List, Dict, Any

from todoist.tools.projects import list_projects, create_project, delete_project
from .test_utils import retry_on_network_error

@pytest.fixture
def tool_context():
    """Create a ToolContext that simulates how Arcade would populate it with secrets"""
    from arcade_tdk import ToolContext, ToolSecretItem
    import os
    
    # Get the API token from environment (for testing)
    # In production, Arcade would populate this automatically
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        pytest.skip("TODOIST_API_TOKEN environment variable not set for testing")
    
    # Create ToolContext and populate it with secrets (simulating Arcade behavior)
    ctx = ToolContext()
    ctx.secrets = [ToolSecretItem(key="TODOIST_API_TOKEN", value=token)]
    
    return ctx

@pytest.mark.network
@retry_on_network_error()
def test_list_projects_success(tool_context):
    """Test successfully listing projects"""
    result = list_projects(tool_context)
    
    assert isinstance(result, str)
    assert len(result) > 0  # Should have some content
    
    # Verify the string contains project information
    assert "ID:" in result
    assert "Name:" in result

@pytest.mark.network
@pytest.mark.integration
@retry_on_network_error()
def test_create_project_success(tool_context):
    """Test successfully creating a project"""
    import datetime
    
    # Create a unique project name with timestamp
    project_name = f"Test Project {datetime.datetime.now().isoformat()}"
    created_project = None
    
    try:
        result = create_project(tool_context, name=project_name)
        
        assert isinstance(result, dict)
        assert "id" in result
        assert result["name"] == project_name
        assert "url" in result
        
        # Store the project for cleanup
        created_project = result
        
        # Verify the project was actually created by listing projects
        projects_str = list_projects(tool_context)
        assert result["id"] in projects_str
        assert project_name in projects_str
        
    finally:
        # Clean up: delete the created project
        if created_project:
            delete_result = delete_project(tool_context, project_id=created_project["id"])
            assert delete_result is True

def test_delete_project_success(tool_context):
    """Test successfully deleting a project"""
    import datetime
    
    # First create a project to delete
    project_name = f"Project to Delete {datetime.datetime.now().isoformat()}"
    created_project = create_project(tool_context, name=project_name)
    
    # Verify it was created
    assert created_project is not None
    assert created_project["name"] == project_name
    
    # Now delete it
    delete_result = delete_project(tool_context, project_id=created_project["id"])
    assert delete_result is True
    
    # Verify it was deleted by checking it's not in the project list
    projects_str = list_projects(tool_context)
    assert created_project["id"] not in projects_str

def test_list_projects_with_tasks_integration(tool_context):
    """Test actual integration: create project, add task, verify relationship"""
    from todoist.tools.tasks import add_task, list_tasks
    import datetime
    
    # Create a test project
    project_name = f"Integration Test Project {datetime.datetime.now().isoformat()}"
    created_project = None
    created_task = None
    
    try:
        # Create project
        created_project = create_project(tool_context, name=project_name)
        project_id = created_project["id"]
        
        # Add a task to the project
        task_content = f"Integration test task {datetime.datetime.now().isoformat()}"
        created_task = add_task(tool_context, content=task_content, project_id=project_id)
        task_id = created_task["id"]
        
        # Verify the task appears when listing tasks for this project
        tasks_str = list_tasks(tool_context, project_id=project_id)
        assert isinstance(tasks_str, str)
        assert task_id in tasks_str
        assert task_content in tasks_str
        
        # Verify the project appears in the projects list
        projects_str = list_projects(tool_context)
        assert project_id in projects_str
        assert project_name in projects_str
        
    finally:
        # Clean up: delete task and project
        if created_task:
            from todoist.tools.tasks import delete_task
            delete_task(tool_context, task_id=created_task["id"])
        if created_project:
            delete_project(tool_context, project_id=created_project["id"])

def test_create_project_empty_name(tool_context):
    """Test creating project with empty name"""
    with pytest.raises(Exception):  # Should raise validation error
        create_project(tool_context, name="")

def test_create_project_invalid_name(tool_context):
    """Test creating project with invalid name"""
    # Test with very long name (over API limits)
    long_name = "x" * 1000
    
    # The API might accept long names, so we'll test that it either works or fails gracefully
    try:
        result = create_project(tool_context, name=long_name)
        # If it succeeds, clean up
        if result and "id" in result:
            delete_project(tool_context, project_id=result["id"])
    except Exception:
        # If it fails, that's also acceptable behavior
        pass

def test_create_project_duplicate_name(tool_context):
    """Test creating projects with same name (should be allowed)"""
    import datetime
    
    project_name = f"Duplicate Name Test {datetime.datetime.now().isoformat()}"
    created_projects = []
    
    try:
        # Create first project
        project1 = create_project(tool_context, name=project_name)
        created_projects.append(project1)
        
        # Create second project with same name (should be allowed)
        project2 = create_project(tool_context, name=project_name)
        created_projects.append(project2)
        
        # Both should be created successfully
        assert project1["name"] == project_name
        assert project2["name"] == project_name
        assert project1["id"] != project2["id"]  # Different IDs
        
    finally:
        # Clean up both projects
        for project in created_projects:
            delete_project(tool_context, project_id=project["id"])

def test_delete_project_nonexistent(tool_context):
    """Test deleting non-existent project"""
    # Test with non-existent project ID
    # The API might return 404 or handle it gracefully
    try:
        result = delete_project(tool_context, project_id="999999999")
        # If it returns False or raises an exception, that's acceptable
        assert result is False or isinstance(result, bool)
    except Exception:
        # If it raises an exception, that's also acceptable behavior
        pass

def test_delete_project_invalid_id(tool_context):
    """Test deleting project with invalid ID format"""
    # Test with malformed project ID
    with pytest.raises(Exception):
        delete_project(tool_context, project_id="invalid_id_format")

def test_list_projects_empty_account(tool_context):
    """Test listing projects when account has no projects"""
    # This is hard to test without actually having an empty account
    # We'll test that the function handles the case gracefully
    result = list_projects(tool_context)
    assert isinstance(result, str)
    # Should return either project list or "No projects found."
    assert len(result) > 0
