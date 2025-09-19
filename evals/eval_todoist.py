from arcade_tdk import ToolCatalog
from arcade_evals import (
    EvalRubric,
    EvalSuite,
    ExpectedToolCall,
    tool_eval,
)
from arcade_evals.critic import SimilarityCritic

import todoist
from todoist.tools.projects import list_projects, create_project

# Evaluation rubric
rubric = EvalRubric(
    fail_threshold=0.85,
    warn_threshold=0.95,
)

catalog = ToolCatalog()
catalog.add_module(todoist)

@tool_eval()
def todoist_eval_suite() -> EvalSuite:
    suite = EvalSuite(
        name="todoist Tools Evaluation",
        system_message=(
            "You are an AI assistant with access to todoist tools. "
            "Use them to help the user with their tasks."
        ),
        catalog=catalog,
        rubric=rubric,
    )

    suite.add_case(
        name="Create a project",
        user_message="Create a project called 'My Arcade Project'.",
        expected_tool_calls=[ExpectedToolCall(
            func=create_project, args={"name": "My Arcade Project"})],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="name", weight=0.5),
        ],
    )

    suite.add_case(
        name="List projects",
        user_message="List all of my projects.",
        expected_tool_calls=[ExpectedToolCall(
            func=list_projects, args={})],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="content", weight=0.5),
        ],
    )

    return suite
