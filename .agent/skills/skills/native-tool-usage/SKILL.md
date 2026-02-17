---
name: native-tool-usage
description: Best practices for using native agent tools (write_to_file, replace_file_content, run_command, etc.). Use this skill when you need to understand how to interact with the file system or environment efficiently and safely.
---

# Native Tool Usage Guidelines

This skill documents best practices for using the native tools available to Antigravity agents.

## Core Principles

1.  **Absolute Paths**: ALWAYS use absolute paths for file operations (`e:\git\auth-dash\README.md`).
2.  **Safety First**: Check file contents (`view_file`) before replacing them.
3.  **Atomic Operations**: Prefer atomic writes/replacements over complex multi-step edits when possible.

## Tool-Specific Guidelines

### `write_to_file`
- **Use for**: Creating NEW files or completely Overwriting existing ones.
- **Critical Arguments**:
    - `TargetFile`: Absolute path.
    - `Overwrite`: Set to `true` if you intend to replace the whole file.
- **Tip**: Do not use this for small edits to large files; it consumes excessive tokens.

### `replace_file_content`
- **Use for**: Single, contiguous block edits in an existing file.
- **Critical Arguments**:
    - `TargetContent`: MUST be unique in the file. Include surrounding context lines if needed to ensure uniqueness.
    - `ReplacementContent`: The new content.
- **Best Practice**: `view_file` first to get the exact `TargetContent`. Whitespace matters!

### `multi_replace_file_content`
- **Use for**: Multiple, non-contiguous edits in the same file.
- **Critical Arguments**:
    - `ReplacementChunks`: Array of {`TargetContent`, `ReplacementContent`, `StartLine`, `EndLine`}.
- **Best Practice**: Efficient for refactoring a file in one pass. Avoid overlapping chunks.

### `run_command`
- **Use for**: Executing shell commands (PowerShell on Windows).
- **Critical Arguments**:
    - `Cwd`: Always specify the current working directory explicitly.
    - `SafeToAutoRun`: Set `true` ONLY for read-only/safe commands (e.g., `ls`, `grep`). Set `false` for destructive commands or running scripts.
- **Constraint**: No interactive commands (e.g., `top`, `vim`). Capture output via `command_status`.

### `task_boundary`
- **Use for**: Managing task state and updating the UI.
- **Rule**: MUST be the **FIRST** tool call in any turn where it is used.
- **Best Practice**: Break work into "Phases" (Planning, Execution, Verification). Update status frequently (every ~5 loops).

### `view_file` vs `read_url_content`
- **view_file**: For local files. Supports line ranges (`StartLine`, `EndLine`).
- **read_url_content**: For fetching web pages (docs, references).

## Common Patterns

### "The Safe Edit"
1. `view_file` (check context)
2. `replace_file_content` (make edit)
3. `run_command` (verify, e.g., `npm run test` or linter)

### "The New Feature"
1. `task_boundary` (Planning)
2. `write_to_file` (Create implementation plan)
3. `notify_user` (Get approval)
4. `task_boundary` (Execution)
5. `write_to_file` (Create code files)

### `generate_image`
- **Use for**:Creating UI mockups (`login_page_mockup`), assets, or visual demonstrations.
- **Critical Arguments**:
    - `Prompt`: Detailed description of the visual.
    - `ImageName`: Snake_case name (e.g., `dashboard_v2`).
- **Best Practice**: Use for frontend tasks to "show" the user what you plan to build before writing code.

### `browser_subagent`
- **Use for**: Interacting with live websites, verifying deployments, or taking screenshots of complex states.
- **Critical Arguments**:
    - `Task`: Detailed instructions for the subagent.
    - `TaskName`: Summary of the action.
- **Limitations**: Cannot access local localhost unless explicitly networked (hybrid setup).

### `search_web`
- **Use for**: finding external documentation, resolving errors, or researching libraries.
- **Tip**: Combine with `read_url_content` to ingest specific documentation pages found via search.

### `find_by_name` & `grep_search`
- **Use for**: Navigating the codebase.
- **Best Practice**:
    - start with `list_dir` to understand structure.
    - use `find_by_name` to locate specific files.
    - use `grep_search` to find code patterns or usage.
