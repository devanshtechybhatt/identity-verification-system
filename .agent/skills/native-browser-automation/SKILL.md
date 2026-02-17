---
name: native-browser-automation
description: Advanced web interaction using the agent's `browser_subagent`. Use this for deep research, navigating complex websites, testing web UIs, or extracting specific data from pages.
---

# Native Browser Automation Skill

This skill documents how to use the agent's native browser automation capabilities.

## Skill Location
`{project_path}/skills/native-browser-automation`

## Overview
The `browser_subagent` is a powerful tool that spawns a headless browser instance. Unlike simple web search, this tool can navigate, click, type, scrolls, and interact with dynamic web pages (SPAs).

## When to Use
- **Deep Research**: specific info hidden deep in documentation pages.
- **Visual Verification**: Checking how a deployed web page looks (via screenshots).
- **End-to-End Testing**: Simulating user flows (login, click button, submit form).
- **Data Extraction**: Scraping data from pages that require JavaScript execution.

## Usage Guide (For Agent)

### Tool: `browser_subagent`

**Parameters:**
- `TaskName`: A human-readable title for the session.
- `Task`: Detailed instructions for the subagent.
- `RecordingName`: Filename for the session video.

### Example Tasks

#### 1. Documentation Deep Dive
> **Task**: "Navigate to https://ui.shadcn.com/docs, click on 'Components', select 'Button', and extract the installation command and usage example code."

#### 2. UI Verification
> **Task**: "Go to http://localhost:3000, wait for the dashboard to load, scroll down to the footer, and take a screenshot to verify the layout."

## Capability Limits
- **Auth**: Can handle simple login, but be careful with credentials (use environment variables).
- **Download**: Cannot easily download files to the local file system; rely on text extraction.
- **Duration**: Sessions should be focused; minimize long, multi-step workflows if possible.
