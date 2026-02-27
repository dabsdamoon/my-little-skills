---
name: resume-project-summary
description: Generate portfolio-ready project summaries from codebases for resume/CV use. Use this skill when the user wants to create a project summary for their resume, portfolio, or job application. Analyzes repository structure, tech stack, features, and generates a structured markdown document with Background, Objective, Technical Decisions, and Features organized by user persona. Supports bilingual output (Korean/English).
license: MIT
---

# Resume Project Summary Generator

This skill generates comprehensive, portfolio-ready project summaries from codebases. The output is structured to showcase:

1. **Problem-Solution Narrative** - Why the project exists and what it solves
2. **Technical Competence** - Architecture decisions and tech stack choices
3. **Feature Implementation** - Concrete features organized by user persona
4. **Visual Evidence** - Screenshot placeholders for demonstration

## Workflow

### Phase 1: Repository Analysis

Use the **Explore** subagent to analyze the repository:

```
Task tool with subagent_type=Explore:
"Analyze this codebase comprehensively:
1. Read package.json, requirements.txt, or similar for tech stack
2. Explore src/ directory structure for architecture patterns
3. Find database schemas, types, or models
4. Identify user-facing features and user personas
5. Look for README, CLAUDE.md, or documentation
6. Find i18n files to understand supported languages
7. Identify deployment configuration (Vercel, Docker, etc.)

Provide a structured summary covering:
- Project purpose and domain
- Tech stack with rationale
- Main features grouped by user type
- Architecture patterns used
- Database design highlights"
```

### Phase 2: Feature Discovery

For each major feature area, use targeted exploration:

```
Task tool with subagent_type=Explore:
"Find all features related to [feature area]:
1. Components in src/components/[FeatureArea]/
2. Services or hooks related to this feature
3. API endpoints or database tables involved
4. User flows and interactions"
```

### Phase 3: Document Generation

Generate the summary using this template:

---

## Output Template

```markdown
# Project [PROJECT_NAME]

버전: v[VERSION]
설명: [One-line description in target language]
업무 속성: [Work types: 개발, 기획, 엔지니어링, 디자인, etc.]

# Background

- [Problem statement 1 - what pain point exists]
  - [Supporting detail or context]
- [Problem statement 2 - market gap or user need]

# Objective

- [Goal statement - what the project aims to achieve]
  - [Sub-goal for user type 1]
  - [Sub-goal for user type 2]

# Technical Stack

### Design
- [Design system/framework used]
  - [Rationale for choice]

### Database
- [Database technology]
  - [Key design decisions]

### Code Management
- [Deployment platform]
  - [CI/CD approach]
- [Development practices]
  - [Testing, code review, etc.]

# Features

### [User Persona 1] Dashboard

- **[Feature Name]**
  - [Description of what it does]
  - [Key implementation details]
  - screenshots
    - [PLACEHOLDER: Add screenshot of feature]

- **[Feature Name 2]**
  - [Description]
  - screenshots
    - [PLACEHOLDER: Add screenshot]

### [User Persona 2] Dashboard

[Repeat feature pattern...]

### [Additional Feature Areas]

[AI/ML features, integrations, etc.]

# Current Status

- [What's complete]
- [What's in progress]
- [Next steps/roadmap]
```

---

## Key Principles

### 1. Tell a Story
Start with the problem, then the solution, then the implementation. Hiring managers want to understand your thinking, not just the tech.

### 2. Organize by User Persona
Features grouped by user type (Admin, Customer, Provider, etc.) show product thinking, not just code skills.

### 3. Highlight Technical Decisions
Don't just list technologies - explain WHY you chose them:
- "Supabase - vibe coding friendly with Lovable integration"
- "Claude Code subagents - parallel code review workflow"

### 4. Be Specific About Your Contributions
Use active voice: "Implemented X", "Designed Y", "Architected Z"

### 5. Include Visual Placeholders
Mark where screenshots should go with clear labels. Screenshots add credibility.

### 6. Support Bilingual Output
If the project serves international users, consider generating summaries in multiple languages (Korean/English).

---

## Feature Categories to Look For

When analyzing a codebase, look for these common feature patterns:

### Authentication & Authorization
- Login methods (email, SSO, OAuth)
- User types and roles
- Registration flows

### Dashboards
- Overview/summary views
- Analytics and metrics
- Quick actions

### CRUD Operations
- List views with filtering/sorting
- Detail views with editing
- Batch operations

### Workflows
- Multi-step forms
- Approval processes
- Status transitions

### Communication
- Email/SMS notifications
- In-app messaging
- Chatbots/AI assistants

### Data Management
- Import/export functionality
- Reporting and analytics
- Data visualization

### Integrations
- Third-party APIs
- Payment processing
- External services

---

## Example: Extracting Features from Code

When you find a component like `ProviderInvoiceBuilder.tsx`:

1. **Identify the feature**: Invoice generation for healthcare providers
2. **Find related code**:
   - Services: `invoiceService.ts`
   - Database: `billing_invoices`, `billing_invoice_lines` tables
   - UI: `invoice/` component directory
3. **Describe the feature**:
   - "Invoice Management: Create, edit, and send medical invoices with billing code lookup and automated calculations"
4. **Note technical highlights**:
   - PDF generation with pdf-lib
   - Billing code management system
   - Audit logging for compliance

---

## Usage

When the user asks to create a project summary:

1. First, explore the repository using the Explore subagent
2. Identify user personas from routes, dashboards, or role-based components
3. Group features by persona
4. Extract technical decisions from config files and CLAUDE.md
5. Generate the markdown document following the template
6. Ask user about:
   - Preferred language (Korean/English/both)
   - Which screenshots they want to add
   - Any features to highlight or de-emphasize

---

## Screenshot Guidance

Suggest screenshots for:
- **Login/Registration** - Shows onboarding flow
- **Main Dashboard** - First impression of the product
- **Key Feature Screens** - Core value proposition
- **Data Visualization** - Charts, graphs, analytics
- **Mobile/Responsive Views** - If applicable

For each screenshot placeholder, include:
```markdown
- screenshots
  - ![Description of what to capture](path/to/image.png)
```
