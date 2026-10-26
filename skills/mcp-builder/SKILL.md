---
name: mcp-builder
description: Builds MCP (Model Context Protocol) servers that expose an external API or service to LLMs as tools, in TypeScript (SDK v2) or Python (MCPServer), and evaluates them with Claude. Use when creating, extending, porting, or reviewing an MCP server, its tools, resources, transport, or auth, or packaging one for the MCP Registry or MCPB. Not for adding or configuring an existing MCP server in a client, or for Claude API tool use without MCP.
license: Complete terms in LICENSE.txt
---

# MCP Server Development Guide

## Overview

Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. The quality of an MCP server is measured by how well it enables LLMs to accomplish real-world tasks.

## Versions (checked 2026-10-26)

Every version-specific statement in this skill and its reference files follows this table. Re-check the sources before relying on it months later.

| Item | Current | Source |
|------|---------|--------|
| MCP spec revision | `2026-07-28` | `https://modelcontextprotocol.io/specification/2026-07-28/changelog.md` |
| TypeScript SDK | `@modelcontextprotocol/server` 2.4.0 (Node 20+, `zod` ^4.2.0); adapters `@modelcontextprotocol/express` 2.0.2, `@modelcontextprotocol/node` 2.1.2 | npm registry |
| TypeScript SDK v1 | `@modelcontextprotocol/sdk` 1.32.2, maintenance line on the `v1.x` branch | npm registry, SDK README |
| Python SDK | `mcp` 2.3.0 (released 2026-10-02), Python 3.10+; `FastMCP` is now `MCPServer` | PyPI, SDK migration guide |
| Eval harness | `anthropic` 2.3.0, `mcp` 2.3.0, `httpx2` (needs Python 3.11+); default model `claude-sonnet-5-5` | PyPI, `https://platform.claude.com/docs/en/about-claude/models/overview` |
| MCP Inspector | `@modelcontextprotocol/inspector` 2.12.0 (Node 22.19+) | npm registry |
| MCP Registry | Preview; `server.json` schema `2025-12-11` | `https://github.com/modelcontextprotocol/registry` |
| MCPB CLI | `@anthropic-ai/mcpb` 2.1.2 | npm registry |

---

# Process

## High-Level Workflow

Creating a high-quality MCP server involves five phases: research and planning, implementation, review and test, evaluation, and (optionally) distribution.

### Phase 1: Deep Research and Planning

#### 1.1 Understand Modern MCP Design

**API Coverage vs. Workflow Tools:**
Balance comprehensive API endpoint coverage with specialized workflow tools. Workflow tools can be more convenient for specific tasks, while comprehensive coverage gives agents flexibility to compose operations. Performance varies by client—some clients benefit from code execution that combines basic tools, while others work better with higher-level workflows. When uncertain, prioritize comprehensive API coverage.

**Tool Naming and Discoverability:**
Clear, descriptive tool names help agents find the right tools quickly. Use consistent prefixes (e.g., `github_create_issue`, `github_list_repos`) and action-oriented naming.

**Context Management:**
Agents benefit from concise tool descriptions and the ability to filter/paginate results. Design tools that return focused, relevant data. Some clients support code execution which can help agents filter and process data efficiently.

**Actionable Error Messages:**
Error messages should guide agents toward solutions with specific suggestions and next steps.

#### 1.2 Study MCP Protocol Documentation

**Navigate the MCP specification:**

Start with the documentation index: `https://modelcontextprotocol.io/llms.txt`

Then fetch specific pages with a `.md` suffix for markdown (e.g., `https://modelcontextprotocol.io/specification/2026-07-28/changelog.md`).

Key pages to review:
- The 2026-07-28 changelog (what changed from 2025-11-25)
- Transports (`basic/transports/streamable-http.md`, `basic/transports/stdio.md`)
- Tools, resources, and prompts (`server/tools.md`, `server/resources.md`, `server/prompts.md`)
- Authorization (`basic/authorization.md`) for remote servers

#### 1.3 Study Framework Documentation

**Recommended stack:**
- **Language**: TypeScript with `@modelcontextprotocol/server` v2 (high-quality SDK support and good compatibility in many execution environments, e.g. MCPB, which runs Node servers without extra installs. Plus AI models are good at generating TypeScript code, benefiting from its broad usage, static typing and good linting tools)
- **Transport**: Streamable HTTP for remote servers, stdio for local servers. Since spec 2026-07-28 the protocol is stateless: no `initialize` handshake, no sessions, no standalone GET stream, and every request is a self-contained POST, so a remote server scales horizontally without sticky sessions. Servers must implement `server/discover`; both SDKs do this for you and still serve 2025-era clients.

**Load framework documentation:**

- **MCP Best Practices**: [View Best Practices](./reference/mcp_best_practices.md) - Core guidelines, transports, and auth for spec 2026-07-28

**For TypeScript (recommended):**
- **TypeScript SDK**: Use WebFetch to load `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` (the `main` branch is v2), then the guides at `https://ts.sdk.modelcontextprotocol.io/v2/`
- [TypeScript Guide](./reference/node_mcp_server.md) - TypeScript patterns and examples

**For Python:**
- **Python SDK**: Use WebFetch to load `https://py.sdk.modelcontextprotocol.io/` (servers written for 1.x need the migration guide at `https://py.sdk.modelcontextprotocol.io/migration/`)
- [Python Guide](./reference/python_mcp_server.md) - Python patterns and examples

#### 1.4 Plan Your Implementation

**Understand the API:**
Review the service's API documentation to identify key endpoints, authentication requirements, and data models. Use web search and WebFetch as needed.

**Tool Selection:**
Prioritize comprehensive API coverage. List endpoints to implement, starting with the most common operations.

---

### Phase 2: Implementation

#### 2.1 Set Up Project Structure

See language-specific guides for project setup:
- [TypeScript Guide](./reference/node_mcp_server.md) - Project structure, package.json, tsconfig.json
- [Python Guide](./reference/python_mcp_server.md) - Module organization, dependencies

#### 2.2 Implement Core Infrastructure

Create shared utilities:
- API client with authentication (credentials read from the environment, never hardcoded)
- Error handling helpers
- Response formatting (JSON/Markdown)
- Pagination support

#### 2.3 Implement Tools

For each tool:

**Input Schema:**
- Use Zod 4 (TypeScript) or Pydantic (Python)
- Include constraints and clear descriptions
- Add examples in field descriptions

**Output Schema:**
- Define `outputSchema` where possible for structured data
- Return `structuredContent` alongside text `content` (TypeScript), or annotate a structured return type (Python)
- Helps clients understand and process tool outputs

**Tool Description:**
- Concise summary of functionality
- Parameter descriptions
- Return type schema

**Implementation:**
- Async/await for I/O operations
- Proper error handling with actionable messages, returned as `isError: true` tool results
- Support pagination where applicable
- Return both text content and structured data when using modern SDKs
- Ask the user for confirmation through the SDK's era-portable elicitation (TypeScript `inputRequired(...)`, Python `Resolve`/`Elicit`); never elicit secrets in a form

**Annotations:**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

**Avoid deprecated features:** Logging, Sampling, and Roots are Deprecated in spec 2026-07-28. Log to stderr, call LLM APIs directly, and take paths as tool parameters.

---

### Phase 3: Review and Test

#### 3.1 Code Quality

Review for:
- No duplicated code (DRY principle)
- Consistent error handling
- Full type coverage
- Clear tool descriptions
- No secrets in code, logs, or tool output

#### 3.2 Build and Test

**TypeScript:**
- Run `npm run build` to verify compilation
- Test with MCP Inspector: `npx @modelcontextprotocol/inspector node dist/index.js` (the Inspector needs Node 22.19+)

**Python:**
- Verify syntax: `python3 -m py_compile your_server.py`
- Test with MCP Inspector: `uv run mcp dev your_server.py` (needs the `mcp[cli]` extra)

See language-specific guides for detailed testing approaches and quality checklists.

---

### Phase 4: Create Evaluations

After implementing your MCP server, create comprehensive evaluations to test its effectiveness.

**Load [Evaluation Guide](./reference/evaluation.md) for complete evaluation guidelines.**

#### 4.1 Understand Evaluation Purpose

Use evaluations to test whether LLMs can effectively use your MCP server to answer realistic, complex questions.

#### 4.2 Create 10 Evaluation Questions

To create effective evaluations, follow the process outlined in the evaluation guide:

1. **Tool Inspection**: List available tools and understand their capabilities
2. **Content Exploration**: Use READ-ONLY operations to explore available data
3. **Question Generation**: Create 10 complex, realistic questions
4. **Answer Verification**: Solve each question yourself to verify answers

#### 4.3 Evaluation Requirements

Ensure each question is:
- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requiring multiple tool calls and deep exploration
- **Realistic**: Based on real use cases humans would care about
- **Verifiable**: Single, clear answer that can be verified by string comparison
- **Stable**: Answer won't change over time

#### 4.4 Output Format

Create an XML file with this structure:

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

#### 4.5 Run the Harness

Set `SKILL_DIR` to this skill directory, then run `python3 "$SKILL_DIR/scripts/evaluation.py" evaluation.xml -t stdio -c python3 -a your_server.py`. The script reads `ANTHROPIC_API_KEY` from its environment; supply it through the repo's secrets wrapper (e.g. `scripts/with-secrets.sh`) rather than exporting it. Setup, flags, and secret forwarding are in the [Evaluation Guide](./reference/evaluation.md#running-evaluations).

---

### Phase 5: Distribute (Optional)

**MCP Registry** (`https://registry.modelcontextprotocol.io`): a metadata registry that MCP clients read, like an app store for MCP servers. It is in **preview**: breaking changes or data resets may occur before general availability. Publishing happens through the `mcp-publisher` CLI from your project, not through pull requests to the registry repo.

1. Publish the package itself (npm, PyPI, NuGet, OCI, or MCPB) and add the ownership marker: `"mcpName": "io.github.<user>/<server>"` in `package.json` for npm, or an `mcp-name: <server-name>` line in the README for PyPI.
2. Run `mcp-publisher init` to generate `server.json` (`$schema` `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`). Its `name` must match `mcpName`. Mark API-key environment variables with `"isSecret": true`. A remote-only server lists a `remotes` entry (`"type": "streamable-http"`, public `url`) instead of `packages`.
3. Run `mcp-publisher login github` (names under `io.github.<user>/`; DNS or HTTP verification covers your own domain), then `mcp-publisher publish`.

The registry verifies that you control the namespace in `name`, not that you control a remote URL. Install `mcp-publisher` from the registry's GitHub releases or Homebrew per the publishing quickstart (`https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx`).

**MCP Bundles (MCPB, formerly DXT):** a `.mcpb` file is a zip of a local MCP server plus a `manifest.json`, installable with one click in Claude for macOS and Windows. The `@anthropic-ai/mcpb` CLI creates the manifest (`mcpb init`) and the bundle (`mcpb pack`); the manifest spec is `MANIFEST.md` in `https://github.com/modelcontextprotocol/mcpb`. Prefer Node servers, which run on the Node.js that ships with Claude's desktop apps; Python bundles can use `server.type = "uv"` so the host manages Python and dependencies.

---

# Reference Files

## Documentation Library

Load these resources as needed during development:

### Core MCP Documentation (Load First)
- **MCP Protocol**: Start with `https://modelcontextprotocol.io/llms.txt`, then fetch specific pages with a `.md` suffix
- [MCP Best Practices](./reference/mcp_best_practices.md) - Universal MCP guidelines including:
  - Server and tool naming conventions
  - Response format guidelines (JSON vs Markdown)
  - Pagination best practices
  - Transport selection (streamable HTTP vs stdio) and the 2026-07-28 changes
  - Authorization, security, and error handling standards

### SDK Documentation (Load During Phase 1/2)
- **Python SDK**: Fetch `https://py.sdk.modelcontextprotocol.io/`
- **TypeScript SDK**: Fetch `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` and `https://ts.sdk.modelcontextprotocol.io/v2/`

### Language-Specific Implementation Guides (Load During Phase 2)
- [Python Implementation Guide](./reference/python_mcp_server.md) - Complete Python/MCPServer guide with:
  - Server initialization patterns
  - Pydantic model examples
  - Tool registration with `@mcp.tool`
  - Complete working examples
  - Quality checklist

- [TypeScript Implementation Guide](./reference/node_mcp_server.md) - Complete TypeScript guide with:
  - Project structure
  - Zod schema patterns
  - Tool registration with `server.registerTool`
  - Complete working examples
  - Quality checklist

### Evaluation Guide (Load During Phase 4)
- [Evaluation Guide](./reference/evaluation.md) - Complete evaluation creation guide with:
  - Question creation guidelines
  - Answer verification strategies
  - XML format specifications
  - Example questions and answers
  - Running an evaluation with the provided scripts
