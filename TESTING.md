# Testing Guide

This file documents possible issues you might encounter when running the "make test" target in this toolkit.

## Handling 503 Service Unavailable Errors

The Todoist API occasionally returns 503 (Service Unavailable) errors, which can cause flaky tests. I've implemented a retry mechanism to address this.

### Retry Mechanism

All critical tests are decorated with `@retry_on_network_error()` which:

- **Automatically retries** on 503, 502, 504, timeout, and other network errors
- **Uses exponential backoff** with jitter to avoid overwhelming the API
- **Configurable** via environment variables
- **Logs retry attempts** so you can see what's happening

### Configuration

You can control the retry behavior with environment variables:

```bash
# Number of retry attempts (default: 3)
export TEST_RETRY_MAX_ATTEMPTS=5

# Initial delay between retries in seconds (default: 1)
export TEST_RETRY_DELAY=2

# Backoff multiplier (default: 2)
export TEST_RETRY_BACKOFF=1.5
```

### Example Output

When a 503 error occurs, you'll see output like:

```
503/Service Unavailable error on attempt 1, retrying in 1.23s...
503/Service Unavailable error on attempt 2, retrying in 2.45s...
503/Service Unavailable error on attempt 3, retrying in 4.67s...
```

### Running Tests

```bash
# Run all tests with default retry settings
make test

# Run tests with custom retry settings
TEST_RETRY_MAX_ATTEMPTS=5 TEST_RETRY_DELAY=2 make test

# Run only fast tests (skip network-dependent tests)
pytest -m "not network"

# Run tests with verbose output to see retry attempts
pytest -v
```

### Test Categories

Tests are marked with categories:

- `@pytest.mark.network` - Tests that require network access
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Tests that take longer to run

### Best Practices

1. **Don't disable retries** - The 503 errors are real and need to be handled
2. **Monitor retry frequency** - If you see many retries, the API might be having issues
3. **Use appropriate timeouts** - Don't make tests wait too long for retries
4. **Clean up resources** - Always clean up created projects/tasks in `finally` blocks

### Troubleshooting

If tests are still flaky:

1. **Check API status** - Visit [Todoist's status page](https://status.todoist.com/)
2. **Increase retry attempts** - Set `TEST_RETRY_MAX_ATTEMPTS=5`
3. **Increase delays** - Set `TEST_RETRY_DELAY=2`
4. **Run tests individually** - `pytest tests/test_projects.py::test_create_project_success -v`

### CI/CD Considerations

In CI environments:

- Set `TEST_RETRY_MAX_ATTEMPTS=5` for more resilience
- Set `TEST_RETRY_DELAY=2` for longer delays
- Consider running tests multiple times if they're still flaky
- Monitor test results over time to identify patterns
