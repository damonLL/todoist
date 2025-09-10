<div style="display: flex; justify-content: center; align-items: center;">
  <img
    src="https://docs.arcade.dev/images/logo/arcade-logo.png"
    style="width: 250px;"
  >
</div>

<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">
  <img src="https://img.shields.io/github/v/release/damonll/todoist" alt="GitHub release" style="margin: 0 2px;">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python version" style="margin: 0 2px;">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" style="margin: 0 2px;">
  <img src="https://img.shields.io/pypi/v/todoist" alt="PyPI version" style="margin: 0 2px;">
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <a href="https://github.com/damonll/todoist" target="_blank">
    <img src="https://img.shields.io/github/stars/damonll/todoist" alt="GitHub stars" style="margin: 0 2px;">
  </a>
  <a href="https://github.com/damonll/todoist/fork" target="_blank">
    <img src="https://img.shields.io/github/forks/damonll/todoist" alt="GitHub forks" style="margin: 0 2px;">
  </a>
</div>


<br>
<br>

# Arcade todoist Toolkit

Manages Todoist projects and tasks

## Features

- **Project Management**: Create, list, and delete Todoist projects
- **Task Management**: Create, list, close, and delete tasks with due dates and priorities
- **LangGraph Integration**: Ready-to-use workflow for AI-powered task planning

## Project planning workflow

The toolkit includes a complete example workflow that demonstrates how to use the Todoist toolkit with LangGraph to create a project and tasks for a user-defined project.

### Quick Start

1. **Create a Todoist account**
  - Visit [Todoist](https://app.todoist.com/auth/signup) to create an account
  - Click on your user profile in the upper left.
  - Settings -> Integrations
  - Click on the 'Developer' tab
  - Create or copy your API_TOKEN

2. **Set up environment variables**:
   ```sh
   export ARCADE_API_KEY="your_arcade_api_key"
   export OPENAI_API_KEY="your_openai_api_key"
   export TODOIST_API_TOKEN="your_todoist_api_token"
   export ARCADE_USER_ID="your_email@example.com"
   ```

3. **Setup environment** (if not already setup):
    ```sh
    # clone repository
    git clone https://github.com/damonll/todoist.git
    cd todoist
    # install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH=$PATH:$HOME/.local/bin
    # Install project dependencies
    uv sync

4. **Start the local environment**

    ```sh
    source .venv/bin/activate
    arcade serve --reload
    ```

5. **Add worker access**:

This allows arcade.dev to access your locally running environment. For more information

Follow Step 7 from the [Create a Toolkit page](https://docs.arcade.dev/home/build-tools/create-a-toolkit) to setup access to your worker. Make sure to copy the publicly accessible URL from ngrok and enter it into the `URL` field. It will look like `https://random_numbers_letters.ngrok-free.app`

6. **Open the Todoist web interface**

Keep the [Todoist web interface](https://app.todoist.com/app/inbox) open in a window to the side of your terminal so watch the updates as they happen.

7. **Run the LangGraph workflow**:
   ```sh
   python project_workflow.py
   ```


### What the workflow does

When you run the workflow with the prompt similar to "I need a project and some tasks to manage my upcoming trip to Barcelona with my family", the AI agent will:

1. **Create a new project** called something like "Barcelona Family Trip"
2. **Add relevant tasks** such as:
   - Book flights to Barcelona
   - Research and book accommodation
   - Create itinerary for family activities
   - Book tickets for Sagrada Familia
   - Research family-friendly restaurants
   - Pack suitcases for family
3. **Set appropriate priorities and due dates** for each task, working backwards from due date

### Files

- `project_workflow.py` - Main LangGraph workflow script
- `todoist/tools/` - Core toolkit implementation

## Development

Read the docs on how to create a toolkit [here](https://docs.arcade.dev/home/build-tools/create-a-toolkit)