# Antigravity Skills

By defining modular **Skills**, we empower the Agent with specialized capabilities in specific domains (such as full-stack development, complex logic planning, multimedia processing, etc.), enabling the Agent to solve complex problems systematically like a human expert.

## 📂 Directory Structure

```
.
├── .agent/
│   └── skills/             # Antigravity Skills Library
│       ├── skill-name/   # Independent skill directory
│       │   ├── SKILL.md    # Core skill definition and Prompt (Required)
│       │   ├── scripts/    # Scripts depended on by the skill (Optional)
│       │   ├── examples/   # Skill usage examples (Optional)
│       │   └── resources/  # Templates and resources depended on by the skill (Optional)
├── skill-guide/            # User manual and documentation guide
│   └── Antigravity_Skills_Manual_CN.md  # Chinese User Manual
└── README.md
```

## 📖 Quick Start
1. Copy the `.agent/` directory to your workspace:
```bash
cp -r .agent/ /path/to/your/workspace/
```
2. **Invoke a Skill**: Type `@[skill-name]` or `/skill-name` in the chat to invoke it, for example:
```text
/canvas-design Help me design a blog cover about "Deep Learning", elegant style, tech feel, size 16:9
```
3. **View Manual**: For detailed usage examples and parameter descriptions, please see [skill-guide/Antigravity_Skills_Manual_CN.md](skill-guide/Antigravity_Skills_Manual_CN.md).
4. **Environmental Dependencies**: Some Skills (like PDF, XLSX) depend on a Python environment. Please ensure `.venv` is activated or the corresponding libraries are installed on the system.


## 🚀 Integrated Skills

### 🔐 Security & Penetration Testing
These skills focus on security assessment, penetration testing, and vulnerability analysis.
- **`@[aws-penetration-testing]`**: AWS cloud security penetration testing
- **`@[ethical-hacking-methodology]`**: Ethical hacking methodology covering the complete penetration testing lifecycle
- **`@[pentest-checklist]`**: Penetration testing checklist for planning and executing security assessments
- **`@[top-web-vulnerabilities]`**: Web application vulnerability reference (100+ vulnerabilities), based on OWASP taxonomy

### 🎨 Creative & Design
These skills focus on visual presentation, UI/UX design, and artistic creation.
- **`@[algorithmic-art]`**: Create algorithmic and generative art using p5.js code
- **`@[canvas-design]`**: Create posters and artworks based on design philosophy (Output PNG/PDF)
- **`@[frontend-design]`**: Create high-quality, production-grade frontend interfaces and Web components
- **`@[ui-ux-pro-max]`**: Professional UI/UX design intelligence, offering full design schemes including color palettes, fonts, layouts, etc.
- **`@[web-artifacts-builder]`**: Build complex, modern Web applications (based on React, Tailwind, Shadcn/ui)
- **`@[theme-factory]`**: Generate matching themes for documents, slides, HTML, etc.
- **`@[brand-guidelines]`**: Apply official Anthropic brand design guidelines (colors, typography, etc.)
- **`@[slack-gif-creator]`**: Create high-quality GIFs specifically for Slack
- **`@[d3-viz]`**: Create interactive data visualizations using D3.js

### 🛠️ Development & Engineering
These skills cover the full lifecycle of coding, testing, debugging, and code review.
- **`@[backend-dev-guidelines]`**: Node.js/Express/TypeScript backend development guidelines
- **`@[frontend-dev-guidelines]`**: React/TypeScript frontend development guidelines (with MUI, TanStack Router)
- **`@[test-driven-development]`**: Test-Driven Development (TDD), writing tests before writing implementation code
- **`@[testing-patterns]`**: Jest testing patterns, factory functions, and mocking strategies
- **`@[test-fixing]`**: Run tests and systematically fix all failing tests
- **`@[systematic-debugging]`**: Systematic debugging for resolving bugs, test failures, or anomalous behavior
- **`@[webapp-testing]`**: Interactive testing and verification of local Web applications using Playwright
- **`@[playwright-skill]`**: Complete Playwright browser automation toolkit
- **`@[receiving-code-review]`**: Handle code review feedback, performing technical verification instead of blind modification
- **`@[requesting-code-review]`**: Proactively initiate code review to verify code quality before merging or completing tasks
- **`@[finishing-a-development-branch]`**: Guide the wrap-up of development branches (merge, PR, cleanup, etc.)
- **`@[subagent-driven-development]`**: Coordinate multiple sub-agents to execute independent development tasks in parallel
- **`@[react-ui-patterns]`**: Modern React UI patterns (loading states, error handling, data fetching)
- **`@[vercel-react-best-practices]`**: Vercel Engineering's React/Next.js performance optimization guide
- **`@[native-tool-usage]`**: Agent native tool usage best practices
- **`@[git-pushing]`**: Git commit and push workflow
- **`@[kaizen]`**: Continuous improvement, error-proofing, and standardization guide
- **`@[linux-shell-scripting]`**: Linux production environment shell script templates

### 📄 Documentation & Office
These skills are used for handling various formats of professional documents and office needs.
- **`@[doc-coauthoring]`**: Guide users in collaborative writing of structured documents (proposals, technical specifications, etc.)
- **`@[docx]`**: Create, edit, and analyze Word documents
- **`@[xlsx]`**: Create, edit, and analyze Excel spreadsheets (supports formulas, charts)
- **`@[pptx]`**: Create and modify PowerPoint presentations
- **`@[pdf]`**: Process PDF documents, including extracting text/tables, merging/splitting, and filling forms
- **`@[internal-comms]`**: Draft various internal enterprise communication documents (weekly reports, announcements, FAQs, etc.)
- **`@[notebooklm]`**: Query Google NotebookLM notebooks to provide exact answers based on documents
- **`@[content-creator]`**: Create SEO-optimized marketing content and social media templates

### 📅 Planning & Workflow
These skills help optimize workflows, task planning, and execution efficiency.
- **`@[brainstorming]`**: Conduct brainstorming before starting any work to clarify requirements and design
- **`@[writing-plans]`**: Write detailed execution plans (Specs) for complex multi-step tasks
- **`@[planning-with-files]`**: File-based planning system suitable for complex tasks (Manus-style)
- **`@[executing-plans]`**: Execute existing implementation plans, including checkpoints and review mechanisms
- **`@[using-git-worktrees]`**: Create isolated Git worktrees for parallel development or task switching
- **`@[verification-before-completion]`**: Run verification commands before declaring task completion to ensure solid evidence
- **`@[using-superpowers]`**: Guide users to discover and use these advanced skills
- **`@[file-organizer]`**: Intelligent file organization, including deduplication and directory structure optimization
- **`@[prompt-engineering]`**: Prompt engineering best practices and optimization techniques

### 🏗️ Architecture & Product
These skills focus on system design, architecture decisions, and product management.
- **`@[senior-architect]`**: Comprehensive software architecture skills supporting system design across multiple tech stacks
- **`@[senior-fullstack]`**: Full-stack development skills covering project scaffolding and code quality analysis
- **`@[software-architecture]`**: Quality-oriented software architecture guide
- **`@[product-manager-toolkit]`**: Product manager toolkit (RICE prioritization, PRD templates, user interview analysis)
- **`@[app-store-optimization]`**: Mobile app store optimization (ASO) toolkit
- **`@[web-design-guidelines]`**: Web interface design guidelines compliance review
- **`@[core-components]`**: Core component library and design system patterns

### 🧩 System Extension
These skills allow me to extend my own capability boundaries.
- **`@[mcp-builder]`**: Build MCP (Model Context Protocol) servers to connect external tools and data
- **`@[skill-creator]`**: Create new skills or update existing ones to extend my knowledge base and workflow
- **`@[skill-developer]`**: Create and manage skills following Anthropic best practices
- **`@[writing-skills]`**: A toolset for assisting in writing, editing, and verifying skill files
- **`@[dispatching-parallel-agents]`**: Dispatch parallel tasks to multiple Agents for processing
- **`@[loki-mode]`**: Multi-Agent autonomous entrepreneurship system (requires --dangerously-skip-permissions)

## 📚 Reference Documentation
- [Anthropic Skills](https://github.com/anthropic/skills)
- [UI/UX Pro Max Skills](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [Superpowers](https://github.com/obra/superpowers)
- [Planning with Files](https://github.com/OthmanAdi/planning-with-files)
- [NotebookLM](https://github.com/PleasePrompto/notebooklm-skill)
