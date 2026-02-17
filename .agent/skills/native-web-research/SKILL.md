---
name: native-web-research
description: Perform web research using the agent's internal `search_web` tool. Use this for finding documentation, libraries, news, or verifying facts without leaving the conversation.
---

# Native Web Research Skill

This skill documents how to use the agent's native web search capabilities.

## Skill Location
`{project_path}/skills/native-web-research`

## Overview
The agent has a built-in `search_web` tool that performs real-time Google searches. This enables the agent to act as a research assistant, fetching up-to-date information that is not in its training data.

## When to Use
- **Documentation**: Finding the latest API docs for a library (e.g., "latest Next.js features").
- **Debugging**: Searching for error messages or stack traces.
- **Market Research**: Finding competitor info or news.
- **Fact Checking**: Verifying user claims or data.

## Usage Guide (For Agent)

### Tool: `search_web`

**Parameters:**
- `query`: The search string.
- `domain` (Optional): Restrict search to a specific site (e.g., `github.com`, `stackoverflow.com`).

### Research Workflows

#### 1. Targeted Documentation Search
When a user asks about a specific library version or feature:
1. Construct a specific query including the version (e.g., "React 19 hooks list").
2. Call `search_web`.
3. Summarize findings with citations [Link Text](URL).

#### 2. Error Resolution
When the user provides an obscure error:
1. Search the exact error string in quotes.
2. Prioritize results from StackOverflow or GitHub Issues.
3. Synthesize the solution.

## Tips
- **Be Specific**: "python list comprehension syntax" vs "python lists".
- **Use Quotes**: For exact error messages.
- **Cite Sources**: Always provide the URL of the information source.
