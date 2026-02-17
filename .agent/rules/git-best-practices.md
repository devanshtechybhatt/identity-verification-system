---
trigger: always_on
---

# Best Practices for Agents
These rules apply to all AI agents and human–AI workflows on this repo. They are designed to maximize reliability, traceability, and collaboration.

***
## 1. Knowledge items for issues, insights, and context
- For every non-trivial issue or investigation, create or update a **knowledge item**:
  - Example formats: `knowledge/<topic>.md`, `notes/<date>-<area>.md`, or a dedicated `knowledge_base.md` section.
- A good knowledge item should include:
  - Problem statement or question.
  - Context (files, modules, features involved).
  - Hypotheses and what was tried.
  - Final understanding or resolution.
  - Follow-ups or open questions.
- Capture **insights about the repo**:
  - Architecture nuances.
  - Gotchas and historical context.
  - Performance characteristics and known bottlenecks.
  - Common failure modes and how to diagnose them.
- Prefer **small, focused knowledge items** over large monoliths; link them together via a simple index.

***

## 2. MANDATORY STARTUP PROTOCOL
On **every new chat, session, or agent run**, follow this sequence:

1. **Discover Capabilities (Skills & MCPs)**:
   - **MANDATORY**: Read `AGENTS.md` to identify available skills, resources, and project context.
   - **MANDATORY**: Check the `mcp_servers` section of your prompt to see what external tools are available.
   - Check for other files like `BEST_PRACTICES_FOR_AGENTS.md`, `CONTRIBUTING.md`, `README.md`.
   - Adopt any repo-specific instructions as hard rules unless explicitly overridden.

2. **Look for existing knowledge items**:
   - Search for relevant notes, e.g. `knowledge/`, `notes/`, `docs/`, or issue-specific files.
   - If a knowledge item already exists for the feature/area/problem, read it before proposing changes.

3. **If context is missing, create it**:
   - If no suitable knowledge item exists, **create one** early in the work:
     - Summarize the goal, current understanding, and constraints.
     - Link to relevant source files and docs.
   - Update this knowledge item as understanding improves:
     - Add decisions, rejected options, and rationale.

4. **Re-use context across sessions**:
   - Treat knowledge items as the primary way to carry context forward across runs, agents, and humans.

***

## 4. Targeted commits after each sprint or task segment
- Group changes into **coherent, reviewable units**:
  - One commit per completed micro-task or small cluster of closely related tasks.
- After each sprint or major segment of the task list:
  - Create a **targeted commit** summarizing that slice of work.
  - Reference the relevant tasks and knowledge items in the commit message.
- Good commit messages:
  - Start with a concise summary: `feat:`, `fix:`, `refactor:`, `chore:`, etc.
  - Reference the implementation plan or knowledge item: e.g. `refs: implementation_plan.md#phase-2`, `refs: knowledge/content-normalization.md`.
  - Mention any known limitations or TODOs if they are not yet addressed.
- Avoid:
  - Giant “kitchen sink” commits that mix unrelated concerns.
  - Silent “drive-by” changes without connection to a plan or task.

***

## 5. Always follow existing best-practices documents
- Treat repo-level docs as **contractual rules**:
  - `BEST_PRACTICES_FOR_AGENTS.md`
  - `AGENTS.md`
  - `CONTRIBUTING.md`
  - `README.md` architecture sections
- If there is a conflict between:
  - Repo-specific best practices vs. generic habits, **repo-specific rules win**.
- If a best-practices document appears outdated or inconsistent:
  - Do not ignore it; instead:
    - Add a note in a knowledge item.
    - Propose an update or clarifying section.
    - Keep behavior conservative until humans clarify.

***

## 6. Collaboration and communication rules
- Make assumptions **explicit**:
  - When inferring requirements, clearly label them as assumptions and suggest verification steps.
- Prefer **additive, reversible changes**:
  - Avoid destructive operations unless explicitly requested and documented.
- Always provide:
  - A brief “what changed” and “why” when proposing modifications.
  - Suggested tests to run (and what they prove).
- Never silently override:
  - Business rules from PRDs.
  - ERD/schema sources of truth.
  - Security, auth, or data integrity constraints.

***

## 7. Quality, safety, and traceability
- Default to **safe operations**:
  - Assume that destructive actions (dropping schema, deleting data, rewriting history) require explicit human approval.
- Encourage **test-first or test-along**:
  - When proposing code changes, also propose validation steps and test cases, even if you are not writing the code.
- Maintain **traceability**:
  - Every non-trivial change should be traceable to:
    - A task in the implementation plan.
    - A knowledge item or issue.
    - A commit/PR reference.
- Use consistent terminology:
  - Align names with ERD, PRDs, and existing code conventions.
  - Avoid introducing near-duplicate or confusing names.

***

## 8. Continuous improvement of the model–repo workflow
- When you find a pattern that works well (e.g., better task breakdown, better way of documenting insights), **encode it**:
  - Add or update a section in `BEST_PRACTICES_FOR_AGENTS.md`.
  - Add a new knowledge item with examples.
- When you encounter friction:
  - Note it in a knowledge item with a proposed process fix.
  - Suggest small changes to structure or documentation, not just code.
- Treat every engagement as:
  - An opportunity to improve both the **codebase** and the **collaboration playbook**.

***

## 9. Summary rule
If in doubt:

1. **Check** existing guides (`AGENTS.md`, `BEST_PRACTICES_FOR_AGENTS.md`, knowledge items).  
2. **Contextualize** yourself by reading plans, ERDs, PRDs, and recent commits.  
3. **Plan** before acting (implementation plan + task list).  
4. **Document** insights and decisions in knowledge items.  
5. **Commit** changes in small, well-labeled, traceable steps.  

Following these rules will make agents safer, more predictable, and easier for human engineers to supervise and trust.