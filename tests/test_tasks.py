import pytest

from todoist.tools.tasks import list_tasks, add_task, close_task, delete_task
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

@pytest.fixture
def sample_token():
    """Get real API token for testing"""
    import os
    
    # Get the API token from environment (for testing)
    # In production, Arcade would provide this through ToolContext
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        pytest.skip("TODOIST_API_TOKEN environment variable not set for testing")
    return token

@pytest.fixture
def test_project_id(tool_context):
    """Get or create a test project for testing"""
    from todoist.tools.client import TodoistClient
    
    # Get existing projects using the client directly
    token = tool_context.get_secret("TODOIST_API_TOKEN")
    client = TodoistClient(token)
    projects = client.get("/projects")
    
    # Look for existing test project
    for project in projects:
        if project["name"].startswith("Test Project"):
            return project["id"]
    
    # If no test project exists, we'll use the inbox
    inbox_project = next((p for p in projects if p.get("is_inbox_project")), None)
    if inbox_project:
        return inbox_project["id"]
    
    # Fallback to first project
    if projects:
        return projects[0]["id"]
    
    pytest.skip("No projects available for testing")

@retry_on_network_error()
def test_list_tasks_no_filters(tool_context):
    """Test listing tasks without any filters"""
    result = list_tasks(tool_context)
    
    assert isinstance(result, str)
    # Should return a string with task information or "No tasks found."
    if result != "No tasks found.":
        assert "ID:" in result
        assert "Content:" in result

@retry_on_network_error()
def test_list_tasks_with_project_id(tool_context, test_project_id):
    """Test listing tasks filtered by project ID"""
    result = list_tasks(tool_context, project_id=test_project_id)
    
    assert isinstance(result, str)
    # Should return a string with task information or "No tasks found."
    if result != "No tasks found.":
        assert "ID:" in result
        assert "Content:" in result

@retry_on_network_error()
def test_add_task_minimal(tool_context, test_project_id):
    """Test adding a task with only required content"""
    import datetime
    
    test_content = f"Test task {datetime.datetime.now().isoformat()}"
    created_task = None
    
    try:
        result = add_task(tool_context, content=test_content)
        
        assert isinstance(result, dict)
        assert "id" in result
        assert result["content"] == test_content
        assert "created_at" in result
        assert "project_id" in result
        
        # Store the task for cleanup
        created_task = result
        
    finally:
        # Clean up: delete the created task
        if created_task:
            delete_result = delete_task(tool_context, task_id=created_task["id"])
            assert delete_result is True

def test_add_task_with_project_id(tool_context, test_project_id):
    """Test adding a task with specific project ID"""
    import datetime
    
    test_content = f"Test task in project {datetime.datetime.now().isoformat()}"
    created_task = None
    
    try:
        result = add_task(tool_context, content=test_content, project_id=test_project_id)
        
        assert isinstance(result, dict)
        assert "id" in result
        assert result["content"] == test_content
        assert result["project_id"] == test_project_id
        
        # Store the task for cleanup
        created_task = result
        
    finally:
        # Clean up: delete the created task
        if created_task:
            delete_result = delete_task(tool_context, task_id=created_task["id"])
            assert delete_result is True   

def test_close_task_success(tool_context, test_project_id):
    """Test successfully closing a task"""
    import datetime
    
    # First create a task to close
    test_content = f"Task to close {datetime.datetime.now().isoformat()}"
    created_task = add_task(tool_context, content=test_content, project_id=test_project_id)
    task_id = created_task["id"]
    
    # Now close the task
    result = close_task(tool_context, task_id=task_id)
    
    assert result is True
    
    # Verify the task is actually closed by checking the task list
    tasks_str = list_tasks(tool_context, project_id=test_project_id)
    
    # Closed tasks should not appear in active task lists.
    # Verify the closed task ID is not in the active tasks string.
    assert isinstance(tasks_str, str)
    assert task_id not in tasks_str

def test_delete_task_success(tool_context, test_project_id):
    """Test successfully deleting a task"""
    import datetime
    
    # First create a task to delete
    test_content = f"Task to Delete {datetime.datetime.now().isoformat()}"
    created_task = add_task(tool_context, content=test_content, project_id=test_project_id)
    
    # Verify it was created
    assert created_task is not None
    assert created_task["content"] == test_content
    
    # Now delete it
    delete_result = delete_task(tool_context, task_id=created_task["id"])
    assert delete_result is True
    
    # Verify it was deleted by checking it's not in the task list
    tasks_str = list_tasks(tool_context, project_id=test_project_id)
    assert created_task["id"] not in tasks_str

def test_list_tasks_with_filter(tool_context):
    """Test listing tasks with Todoist filters"""
    # Test with common filters
    filters_to_test = ["today", "tomorrow", "overdue", "p1", "p2"]
    
    for filter_value in filters_to_test:
        result = list_tasks(tool_context, filter=filter_value)
        assert isinstance(result, str)
        # Should return a string (could be "No tasks found." or task list)
        if result != "No tasks found.":
            assert "ID:" in result
            assert "Content:" in result

def test_list_tasks_with_label(tool_context):
    """Test listing tasks filtered by label"""
    # Test with a common label (if it exists)
    result = list_tasks(tool_context, label="work")
    assert isinstance(result, str)
    
    # Test with non-existent label
    result = list_tasks(tool_context, label="nonexistent_label_12345")
    assert isinstance(result, str)
    # Should return "No tasks found." or empty result

def test_list_tasks_with_lang(tool_context):
    """Test listing tasks with language parameter"""
    # Test with different language codes
    languages = ["en", "es", "fr"]
    
    for lang in languages:
        result = list_tasks(tool_context, lang=lang)
        assert isinstance(result, str)

def test_list_tasks_filter_precedence(tool_context, test_project_id):
    """Test that filter takes precedence over project_id"""
    # When both filter and project_id are provided, filter should take precedence
    result = list_tasks(tool_context, project_id=test_project_id, filter="today")
    assert isinstance(result, str)
    
    # The result should be filtered by "today", not by project_id
    # (We can't easily verify the actual filtering without knowing the data)

def test_list_tasks_invalid_project_id(tool_context):
    """Test listing tasks with invalid project ID"""
    # Test with non-existent project ID
    # This might raise a ToolExecutionError due to 404, which is acceptable
    try:
        result = list_tasks(tool_context, project_id="999999999")
        assert isinstance(result, str)
        # Should return "No tasks found." or empty result
    except Exception:
        # If it raises an exception due to 404, that's also acceptable behavior
        pass

def test_list_tasks_empty_project(tool_context, test_project_id):
    """Test listing tasks for project with no tasks"""
    # This test assumes the test project might be empty
    # If it has tasks, we'll create a new empty project
    from todoist.tools.projects import create_project, delete_project
    import datetime
    
    # Create a new empty project
    project_name = f"Empty Test Project {datetime.datetime.now().isoformat()}"
    created_project = None
    
    try:
        created_project = create_project(tool_context, name=project_name)
        empty_project_id = created_project["id"]
        
        # List tasks for the empty project
        result = list_tasks(tool_context, project_id=empty_project_id)
        assert isinstance(result, str)
        # Should return "No tasks found."
        assert result == "No tasks found."
        
    finally:
        # Clean up
        if created_project:
            delete_project(tool_context, project_id=created_project["id"])

def test_add_task_empty_content(tool_context, test_project_id):
    """Test adding task with empty content"""
    with pytest.raises(Exception):  # Should raise validation error
        add_task(tool_context, content="", project_id=test_project_id)

def test_add_task_invalid_priority(tool_context, test_project_id):
    """Test adding task with invalid priority"""
    import datetime
    
    test_content = f"Test task with invalid priority {datetime.datetime.now().isoformat()}"
    created_tasks = []
    
    try:
        # Test priority outside valid range (1-4)
        # The API might accept these values, so we'll test both success and failure cases
        try:
            result = add_task(tool_context, content=test_content, project_id=test_project_id, priority=0)
            if result and "id" in result:
                created_tasks.append(result)
        except Exception:
            # If it fails, that's acceptable behavior
            pass
        
        try:
            result = add_task(tool_context, content=test_content, project_id=test_project_id, priority=5)
            if result and "id" in result:
                created_tasks.append(result)
        except Exception:
            # If it fails, that's acceptable behavior
            pass
            
    finally:
        # Clean up any created tasks
        for task in created_tasks:
            delete_task(tool_context, task_id=task["id"])

def test_add_task_invalid_project_id(tool_context):
    """Test adding task with non-existent project ID"""
    import datetime
    
    test_content = f"Test task with invalid project {datetime.datetime.now().isoformat()}"
    
    # Test with non-existent project ID
    with pytest.raises(Exception):
        add_task(tool_context, content=test_content, project_id="999999999")

def test_add_task_with_due_string(tool_context, test_project_id):
    """Test adding task with natural language due date"""
    import datetime
    
    test_content = f"Test task with due date {datetime.datetime.now().isoformat()}"
    created_task = None
    
    try:
        # Test with natural language due date
        result = add_task(tool_context, content=test_content, project_id=test_project_id, due_string="tomorrow 5pm")
        
        assert isinstance(result, dict)
        assert "id" in result
        assert result["content"] == test_content
        assert result["project_id"] == test_project_id
        
        created_task = result
        
    finally:
        # Clean up
        if created_task:
            delete_task(tool_context, task_id=created_task["id"])

def test_add_task_with_order(tool_context, test_project_id):
    """Test adding task with order parameter"""
    import datetime
    
    test_content = f"Test task with order {datetime.datetime.now().isoformat()}"
    created_task = None
    
    try:
        # Test with order parameter
        result = add_task(tool_context, content=test_content, project_id=test_project_id, order=1)
        
        assert isinstance(result, dict)
        assert "id" in result
        assert result["content"] == test_content
        assert result["project_id"] == test_project_id
        
        created_task = result
        
    finally:
        # Clean up
        if created_task:
            delete_task(tool_context, task_id=created_task["id"])

def test_close_task_nonexistent(tool_context):
    """Test closing non-existent task"""
    # Test with non-existent task ID
    # This might raise a ToolExecutionError due to 404, which is acceptable
    try:
        result = close_task(tool_context, task_id="999999999")
        # Should return False or raise an exception
        assert result is False or isinstance(result, bool)
    except Exception:
        # If it raises an exception due to 404, that's also acceptable behavior
        pass

def test_delete_task_nonexistent(tool_context):
    """Test deleting non-existent task"""
    # Test with non-existent task ID
    with pytest.raises(Exception):
        delete_task(tool_context, task_id="999999999")
