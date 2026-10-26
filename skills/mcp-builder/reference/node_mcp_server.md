# Node/TypeScript MCP Server Implementation Guide

## Overview

This document provides Node/TypeScript-specific best practices and examples for implementing MCP servers using the MCP TypeScript SDK v2 (`@modelcontextprotocol/server`), which implements spec revision 2026-07-28 and still serves 2025-era clients from the same code. It covers project structure, server setup, tool registration patterns, input validation with Zod, error handling, and complete working examples. Versions checked are in the table in SKILL.md.

**Why v2:** v2 is the SDK's stable line. The v1 package (`@modelcontextprotocol/sdk`) lives on the `v1.x` branch and receives bug and security fixes for at least six months after the v2 release on 2026-07-27. Use v1 only to maintain an existing v1 server; migrate with the codemod and the upgrade guide (`https://ts.sdk.modelcontextprotocol.io/v2/migration/upgrade-to-v2`).

**Requirements:** Node.js 20+, Zod 4.2+ (Zod 3 is not supported). The packages are ESM-first and also ship a CommonJS build.

---

## Quick Reference

### Key Imports
```typescript
import { McpServer, ResourceTemplate, createMcpHandler } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import { createMcpExpressApp } from "@modelcontextprotocol/express";
import { toNodeHandler } from "@modelcontextprotocol/node";
import * as z from "zod/v4";
```

### Server Initialization
```typescript
const server = new McpServer({
  name: "service-mcp-server",
  version: "1.0.0"
});
```

### Tool Registration Pattern
```typescript
server.registerTool(
  "tool_name",
  {
    title: "Tool Display Name",
    description: "What the tool does",
    inputSchema: z.object({ param: z.string() }),
    outputSchema: z.object({ result: z.string() })
  },
  async ({ param }) => {
    const output = { result: `Processed: ${param}` };
    return {
      content: [{ type: "text", text: JSON.stringify(output) }],
      structuredContent: output // Validated against outputSchema before it leaves the server
    };
  }
);
```

---

## MCP TypeScript SDK

The official MCP TypeScript SDK v2 is split into packages:
- `@modelcontextprotocol/server` - `McpServer`, `createMcpHandler` (Streamable HTTP), and `serveStdio` (from the `./stdio` subpath)
- `@modelcontextprotocol/client` - MCP clients
- `@modelcontextprotocol/node`, `@modelcontextprotocol/express`, `@modelcontextprotocol/hono`, `@modelcontextprotocol/fastify` - optional thin HTTP adapters

It provides:
- `registerTool` / `registerResource` / `registerPrompt` for registration
- Standard Schema validation (Zod 4, Valibot, ArkType) for tool inputs and outputs
- Type-safe handler arguments inferred from the input schema

**IMPORTANT - Use the v2 APIs:**
- **DO use**: `server.registerTool()`, `server.registerResource()`, `server.registerPrompt()`, `createMcpHandler()`, `serveStdio()`
- **DO NOT use**: `server.tool()`, `server.resource()`, `server.prompt()` (removed in v2), deep imports from `@modelcontextprotocol/sdk/...` (v1 package), or hand-wired `StreamableHTTPServerTransport` + `connect()` per request
- Pass `inputSchema` as a schema object (`z.object({...})`); raw `{ field: z.string() }` shapes are deprecated

**For complete SDK documentation, use WebFetch to load:**
`https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` and the guides at `https://ts.sdk.modelcontextprotocol.io/v2/`

## Server Naming Convention

Node/TypeScript MCP servers must follow this naming pattern:
- **Format**: `{service}-mcp-server` (lowercase with hyphens)
- **Examples**: `github-mcp-server`, `jira-mcp-server`, `stripe-mcp-server`

The name should be:
- General (not tied to specific features)
- Descriptive of the service/API being integrated
- Easy to infer from the task description
- Without version numbers or dates

## Project Structure

Create the following structure for Node/TypeScript MCP servers:

```
{service}-mcp-server/
├── package.json
├── tsconfig.json
├── README.md
├── src/
│   ├── index.ts          # Entry point: createServer() factory plus stdio/HTTP startup
│   ├── types.ts          # TypeScript type definitions and interfaces
│   ├── tools/            # Tool implementations (one file per domain)
│   ├── services/         # API clients and shared utilities
│   ├── schemas/          # Zod validation schemas
│   └── constants.ts      # Shared constants (API_URL, CHARACTER_LIMIT, etc.)
└── dist/                 # Built JavaScript files (entry point: dist/index.js)
```

## Tool Implementation

### Tool Naming

Use snake_case for tool names (e.g., "search_users", "create_project", "get_channel_info") with clear, action-oriented names.

**Avoid Naming Conflicts**: Include the service context to prevent overlaps:
- Use "slack_send_message" instead of just "send_message"
- Use "github_create_issue" instead of just "create_issue"
- Use "asana_list_tasks" instead of just "list_tasks"

### Tool Structure

Tools are registered using the `registerTool` method with the following requirements:
- Use Zod schemas for runtime input validation and type safety
- The `description` field must be explicitly provided - JSDoc comments are NOT automatically extracted
- Explicitly provide `title`, `description`, `inputSchema`, and `annotations`
- The `inputSchema` must be a schema object such as `z.object({...})` (not a JSON schema)
- `.describe()` text on each field becomes that argument's description in the advertised JSON Schema
- Type all parameters and return values explicitly

```typescript
import { McpServer } from "@modelcontextprotocol/server";
import * as z from "zod/v4";

const server = new McpServer({
  name: "example-mcp-server",
  version: "1.0.0"
});

// Zod schema for input validation
const UserSearchInputSchema = z.strictObject({
  query: z.string()
    .min(2, "Query must be at least 2 characters")
    .max(200, "Query must not exceed 200 characters")
    .describe("Search string to match against names/emails"),
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip for pagination"),
  response_format: z.enum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
});

// Type definition from Zod schema
type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

server.registerTool(
  "example_search_users",
  {
    title: "Search Example Users",
    description: `Search for users in the Example system by name, email, or team.

This tool searches across all user profiles in the Example platform, supporting partial matches and various search filters. It does NOT create or modify users, only searches existing ones.

Args:
  - query (string): Search string to match against names/emails
  - limit (number): Maximum results to return, between 1-100 (default: 20)
  - offset (number): Number of results to skip for pagination (default: 0)
  - response_format ('markdown' | 'json'): Output format (default: 'markdown')

Returns:
  For JSON format: Structured data with schema:
  {
    "total": number,           // Total number of matches found
    "count": number,           // Number of results in this response
    "offset": number,          // Current pagination offset
    "users": [
      {
        "id": string,          // User ID (e.g., "U123456789")
        "name": string,        // Full name (e.g., "John Doe")
        "email": string,       // Email address
        "team": string,        // Team name (optional)
        "active": boolean      // Whether user is active
      }
    ],
    "has_more": boolean,       // Whether more results are available
    "next_offset": number      // Offset for next page (if has_more is true)
  }

Examples:
  - Use when: "Find all marketing team members" -> params with query="team:marketing"
  - Use when: "Search for John's account" -> params with query="john"
  - Don't use when: You need to create a user (use example_create_user instead)

Error Handling:
  - Returns "Error: Rate limit exceeded" if too many requests (429 status)
  - Returns "No users found matching '<query>'" if search returns empty`,
    inputSchema: UserSearchInputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  },
  async (params: UserSearchInput) => {
    try {
      // Input validation is handled by the Zod schema before this runs
      const data = await makeApiRequest<UserSearchResponse>(
        "users/search",
        "GET",
        undefined,
        {
          q: params.query,
          limit: params.limit,
          offset: params.offset
        }
      );

      const users = data.users ?? [];
      const total = data.total ?? 0;

      if (!users.length) {
        return {
          content: [{
            type: "text",
            text: `No users found matching '${params.query}'`
          }]
        };
      }

      // Prepare structured output
      const output = {
        total,
        count: users.length,
        offset: params.offset,
        users: users.map(user => ({
          id: user.id,
          name: user.name,
          email: user.email,
          ...(user.team ? { team: user.team } : {}),
          active: user.active ?? true
        })),
        has_more: total > params.offset + users.length,
        ...(total > params.offset + users.length ? {
          next_offset: params.offset + users.length
        } : {})
      };

      // Format text representation based on requested format
      let textContent: string;
      if (params.response_format === ResponseFormat.MARKDOWN) {
        const lines = [`# User Search Results: '${params.query}'`, "",
          `Found ${total} users (showing ${users.length})`, ""];
        for (const user of users) {
          lines.push(`## ${user.name} (${user.id})`);
          lines.push(`- **Email**: ${user.email}`);
          if (user.team) lines.push(`- **Team**: ${user.team}`);
          lines.push("");
        }
        textContent = lines.join("\n");
      } else {
        textContent = JSON.stringify(output, null, 2);
      }

      return {
        content: [{ type: "text", text: textContent }],
        structuredContent: output
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: handleApiError(error)
        }],
        isError: true
      };
    }
  }
);
```

Arguments that fail the schema never reach the handler: the SDK returns an `isError: true` tool result describing the problem, so the model can retry. A handler that throws is also converted to an `isError: true` result.

## Zod Schemas for Input Validation

Zod 4 provides runtime type validation. Zod 4.2+ is required so the SDK can convert schemas (and `.describe()` text) to JSON Schema:

```typescript
import * as z from "zod/v4";

// Basic schema with validation
const CreateUserSchema = z.strictObject({  // strictObject forbids extra fields
  name: z.string()
    .min(1, "Name is required")
    .max(100, "Name must not exceed 100 characters"),
  email: z.email("Invalid email format"),
  age: z.number()
    .int("Age must be a whole number")
    .min(0, "Age cannot be negative")
    .max(150, "Age cannot be greater than 150")
});

// Enums: z.enum accepts a TypeScript enum (z.nativeEnum is deprecated in Zod 4)
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

const SearchSchema = z.object({
  response_format: z.enum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format")
});

// Optional fields with defaults
const PaginationSchema = z.object({
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip")
});
```

## Response Format Options

Support multiple output formats for flexibility:

```typescript
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

const inputSchema = z.object({
  query: z.string(),
  response_format: z.enum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
});
```

**Markdown format**:
- Use headers, lists, and formatting for clarity
- Convert timestamps to human-readable format
- Show display names with IDs in parentheses
- Omit verbose metadata
- Group related information logically

**JSON format**:
- Return complete, structured data suitable for programmatic processing
- Include all available fields and metadata
- Use consistent field names and types

## Pagination Implementation

For tools that list resources:

```typescript
const ListSchema = z.object({
  limit: z.number().int().min(1).max(100).default(20),
  offset: z.number().int().min(0).default(0)
});

async function listItems(params: z.infer<typeof ListSchema>) {
  const data = await apiRequest(params.limit, params.offset);

  const response = {
    total: data.total,
    count: data.items.length,
    offset: params.offset,
    items: data.items,
    has_more: data.total > params.offset + data.items.length,
    next_offset: data.total > params.offset + data.items.length
      ? params.offset + data.items.length
      : undefined
  };

  return JSON.stringify(response, null, 2);
}
```

## Character Limits and Truncation

Add a CHARACTER_LIMIT constant to prevent overwhelming responses:

```typescript
// At module level in constants.ts
export const CHARACTER_LIMIT = 25000;  // Maximum response size in characters

async function searchTool(params: SearchInput) {
  let result = generateResponse(data);

  // Check character limit and truncate if needed
  if (result.length > CHARACTER_LIMIT) {
    const truncatedData = data.slice(0, Math.max(1, data.length / 2));
    response.data = truncatedData;
    response.truncated = true;
    response.truncation_message =
      `Response truncated from ${data.length} to ${truncatedData.length} items. ` +
      `Use 'offset' parameter or add filters to see more results.`;
    result = JSON.stringify(response, null, 2);
  }

  return result;
}
```

## Error Handling

Provide clear, actionable error messages. Return them as `isError: true` tool results so the model can read and react to them:

```typescript
class ApiError extends Error {
  constructor(readonly status: number) {
    super(`API request failed with status ${status}`);
  }
}

function handleApiError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 404:
        return "Error: Resource not found. Please check the ID is correct.";
      case 403:
        return "Error: Permission denied. You don't have access to this resource.";
      case 429:
        return "Error: Rate limit exceeded. Please wait before making more requests.";
      default:
        return `Error: API request failed with status ${error.status}`;
    }
  }
  if (error instanceof DOMException && error.name === "TimeoutError") {
    return "Error: Request timed out. Please try again.";
  }
  return `Error: Unexpected error occurred: ${error instanceof Error ? error.message : String(error)}`;
}
```

## Shared Utilities

Extract common functionality into reusable functions. Node 20+ ships `fetch`, so no HTTP client dependency is needed:

```typescript
// Shared API request function
async function makeApiRequest<T>(
  endpoint: string,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  body?: unknown,
  params?: Record<string, string | number>
): Promise<T> {
  const url = new URL(`${API_BASE_URL}/${endpoint}`);
  for (const [key, value] of Object.entries(params ?? {})) {
    url.searchParams.set(key, String(value));
  }

  const response = await fetch(url, {
    method,
    body: body === undefined ? undefined : JSON.stringify(body),
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    signal: AbortSignal.timeout(30_000)
  });
  if (!response.ok) {
    throw new ApiError(response.status);
  }
  return (await response.json()) as T;
}
```

## Async/Await Best Practices

Always use async/await for network requests and I/O operations:

```typescript
// Good: Async network request
async function fetchData(resourceId: string): Promise<ResourceData> {
  const response = await fetch(`${API_URL}/resource/${resourceId}`);
  return (await response.json()) as ResourceData;
}

// Bad: Promise chains
function fetchData(resourceId: string): Promise<ResourceData> {
  return fetch(`${API_URL}/resource/${resourceId}`)
    .then(response => response.json());  // Harder to read and maintain
}
```

## TypeScript Best Practices

1. **Use Strict TypeScript**: Enable strict mode in tsconfig.json
2. **Define Interfaces**: Create clear interface definitions for all data structures
3. **Avoid `any`**: Use proper types or `unknown` instead of `any`
4. **Zod for Runtime Validation**: Use Zod schemas to validate external data
5. **Type Guards**: Create type guard functions for complex type checking
6. **Error Handling**: Always use try-catch with proper error type checking
7. **Null Safety**: Use optional chaining (`?.`) and nullish coalescing (`??`)

```typescript
// Good: Type-safe with Zod and interfaces
interface UserResponse {
  id: string;
  name: string;
  email: string;
  team?: string;
  active: boolean;
}

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.email(),
  team: z.string().optional(),
  active: z.boolean()
});

type User = z.infer<typeof UserSchema>;

async function getUser(id: string): Promise<User> {
  const data = await apiCall(`/users/${id}`);
  return UserSchema.parse(data);  // Runtime validation
}

// Bad: Using any
async function getUser(id: string): Promise<any> {
  return await apiCall(`/users/${id}`);  // No type safety
}
```

## Package Configuration

### package.json

Ranges below match the published v2 packages and the toolchain the SDK itself builds with (checked 2026-10-26; see SKILL.md). Drop the Express and Node adapter packages if the server only speaks stdio.

```json
{
  "name": "{service}-mcp-server",
  "version": "1.0.0",
  "description": "MCP server for {Service} API integration",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "clean": "rm -rf dist"
  },
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "@modelcontextprotocol/express": "^2.0.2",
    "@modelcontextprotocol/node": "^2.1.2",
    "@modelcontextprotocol/server": "^2.4.0",
    "express": "^5.2.1",
    "zod": "^4.2.0"
  },
  "devDependencies": {
    "@types/express": "^5.0.6",
    "@types/node": "^24.10.1",
    "tsx": "^4.16.5",
    "typescript": "^5.9.3"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Complete Example

The server is built by a `createServer()` factory. `serveStdio` calls it once per stdio connection; `createMcpHandler` calls it once per HTTP request, so register everything inside the factory and keep shared resources (pools, caches) at module scope.

```typescript
#!/usr/bin/env node
/**
 * MCP Server for Example Service.
 *
 * This server provides tools to interact with Example API, including user search,
 * project management, and data export capabilities.
 */

import { McpServer, createMcpHandler } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import { createMcpExpressApp } from "@modelcontextprotocol/express";
import { toNodeHandler } from "@modelcontextprotocol/node";
import * as z from "zod/v4";

// Constants
const API_BASE_URL = "https://api.example.com/v1";
const CHARACTER_LIMIT = 25000;

// Enums
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

// Zod schemas
const UserSearchInputSchema = z.strictObject({
  query: z.string()
    .min(2, "Query must be at least 2 characters")
    .max(200, "Query must not exceed 200 characters")
    .describe("Search string to match against names/emails"),
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip for pagination"),
  response_format: z.enum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
});

type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

interface UserSearchResponse {
  total?: number;
  users?: { id: string; name: string; email: string; team?: string; active?: boolean }[];
}

// Shared utilities: ApiError, makeApiRequest, and handleApiError as shown above

// Server factory
function createServer(): McpServer {
  const server = new McpServer({
    name: "example-mcp-server",
    version: "1.0.0"
  });

  server.registerTool(
    "example_search_users",
    {
      title: "Search Example Users",
      description: `[Full description as shown above]`,
      inputSchema: UserSearchInputSchema,
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: true
      }
    },
    async (params: UserSearchInput) => {
      // Implementation as shown above
    }
  );

  return server;
}

if (!process.env.EXAMPLE_API_KEY) {
  console.error("ERROR: EXAMPLE_API_KEY environment variable is required");
  process.exit(1);
}

if (process.env.TRANSPORT === "http") {
  // Streamable HTTP (remote). createMcpExpressApp validates Host and Origin on localhost binds.
  const handler = createMcpHandler(createServer);
  const app = createMcpExpressApp();
  const node = toNodeHandler(handler);
  app.all("/mcp", (req, res) => void node(req, res, req.body));

  const port = Number(process.env.PORT ?? 3000);
  app.listen(port, "127.0.0.1", () => {
    console.error(`MCP server running on http://127.0.0.1:${port}/mcp`);
  });
} else {
  // stdio (local). stdout carries the protocol, so log with console.error only.
  serveStdio(createServer);
  console.error("MCP server running via stdio");
}
```

---

## Advanced MCP Features

### Resource Registration

Expose data as resources for efficient, URI-based access. `registerResource` takes a name, a URI or `ResourceTemplate`, metadata (pass `{}` if you have none), and a read callback:

```typescript
import { ResourceTemplate } from "@modelcontextprotocol/server";

// Fixed URI
server.registerResource(
  "app-config",
  "config://app",
  {
    title: "Application Config",
    description: "Application configuration data",
    mimeType: "text/plain"
  },
  async uri => ({
    contents: [{ uri: uri.href, text: await loadConfig() }]
  })
);

// URI template; the list callback makes instances appear in resources/list
server.registerResource(
  "document",
  new ResourceTemplate("file://documents/{name}", {
    list: async () => ({
      resources: (await getAvailableDocuments()).map(doc => ({
        uri: `file://documents/${doc.name}`,
        name: doc.name,
        mimeType: "text/plain",
        description: doc.description
      }))
    })
  }),
  {
    title: "Document Resource",
    description: "Access documents by name",
    mimeType: "text/plain"
  },
  async (uri, { name }) => ({
    contents: [{ uri: uri.href, mimeType: "text/plain", text: await loadDocument(String(name)) }]
  })
);
```

Pass `{ list: undefined }` when a template's instances cannot be enumerated. Validate template variables before using them as file paths.

**When to use Resources vs Tools:**
- **Resources**: For data access with simple URI-based parameters
- **Tools**: For complex operations requiring validation and business logic
- **Resources**: When data is relatively static or template-based
- **Tools**: When operations have side effects or complex workflows

### Transport Options

The TypeScript SDK supports two main transport mechanisms:

#### Streamable HTTP (Recommended for Remote Servers)

```typescript
import { createMcpHandler } from "@modelcontextprotocol/server";
import { createMcpExpressApp } from "@modelcontextprotocol/express";
import { toNodeHandler } from "@modelcontextprotocol/node";

// The factory runs once per HTTP request; the handler keeps no state between requests
const handler = createMcpHandler(createServer);

const app = createMcpExpressApp();  // express.json() plus Host/Origin validation
const node = toNodeHandler(handler);
app.all("/mcp", (req, res) => void node(req, res, req.body));

app.listen(3000, "127.0.0.1");
```

- `createMcpHandler(factory)` returns `{ fetch, close, notify, bus }`. On Workers, Deno, or Bun, `export default handler` is the whole mount; Node frameworks wrap it once with `toNodeHandler`.
- The bare handler validates no `Host` or `Origin` header and verifies no token. `createMcpExpressApp()` adds the header checks on localhost binds; when binding `0.0.0.0`, pass `createMcpExpressApp({ host: "0.0.0.0", allowedHosts: ["api.example.com"] })`.
- For auth, verify the bearer token in front of the handler (`requireBearerAuth` from `@modelcontextprotocol/express`); tool handlers read the result as `ctx.http.authInfo`.
- Responses are a single JSON body unless a handler emits progress first; `createMcpHandler(factory, { responseMode: "json" })` pins JSON and drops mid-call notifications.
- The same handler serves 2025-era clients statelessly by default.

#### stdio (For Local Integrations)

```typescript
import { serveStdio } from "@modelcontextprotocol/server/stdio";

const handle = serveStdio(createServer);
process.on("SIGINT", () => void handle.close());
```

**Transport selection:**
- **Streamable HTTP**: Web services, remote access, multiple clients
- **stdio**: Command-line tools, local development, subprocess integration

### Notification Support

Notify clients when server state changes:

```typescript
// Registration handles notify for you
const report = server.registerTool("run_report", { description: "Run the weekly report" }, async () => ({
  content: [{ type: "text", text: "report queued" }]
}));
report.update({ description: "Run the weekly report and email it" });  // sends tools/list_changed
report.disable();                                                       // sends tools/list_changed

// Explicit notifications for changes the registration API cannot see
server.sendToolListChanged();
server.sendResourceListChanged();

// Behind createMcpHandler the instance is per-request, so publish through the handler
handler.notify.toolsChanged();
handler.notify.resourceUpdated("config://app");
```

On 2026-07-28 connections, change notifications reach only clients that opened a `subscriptions/listen` stream asking for them. Use notifications sparingly - only when server capabilities genuinely change.

### Progress

Every handler receives a context as its second argument. Request-scoped helpers live on `ctx.mcpReq`:

```typescript
async ({ files }, ctx) => {
  const progressToken = ctx.mcpReq._meta?.progressToken;
  for (let i = 0; i < files.length; i++) {
    // ... process files[i] ...
    if (progressToken !== undefined) {
      await ctx.mcpReq.notify({
        method: "notifications/progress",
        params: { progressToken, progress: i + 1, total: files.length }
      });
    }
  }
  return { content: [{ type: "text", text: `Processed ${files.length} files` }] };
}
```

MCP Logging is Deprecated in spec 2026-07-28; log to stderr (`console.error`) or OpenTelemetry instead.

### Asking the User (Elicitation)

Return the question instead of pushing it. On 2026-07-28 connections the client answers and retries the call; for older clients the SDK's legacy shim (on by default) sends a real `elicitation/create` request and re-enters the handler, so one handler serves both:

```typescript
import type { CallToolResult, InputRequiredResult } from "@modelcontextprotocol/server";
import { acceptedContent, inputRequired } from "@modelcontextprotocol/server";

const confirmationSchema = z.object({ confirm: z.boolean() });

server.registerTool(
  "example_delete_project",
  {
    description: "Delete a project after the user confirms",
    inputSchema: z.object({ project_id: z.string() }),
    annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: true }
  },
  async ({ project_id }, ctx): Promise<CallToolResult | InputRequiredResult> => {
    const answer = acceptedContent(ctx.mcpReq.inputResponses, "confirm", confirmationSchema);
    if (answer?.confirm !== true) {
      return inputRequired({
        inputRequests: {
          confirm: inputRequired.elicit({
            message: `Delete project ${project_id}? This cannot be undone.`,
            requestedSchema: confirmationSchema
          })
        }
      });
    }
    await makeApiRequest(`projects/${project_id}`, "DELETE");
    return { content: [{ type: "text", text: `Deleted project ${project_id}` }] };
  }
);
```

`ctx.mcpReq.elicitInput` is the 2025-era push form and throws on 2026-07-28 requests. Elicitation schemas must be flat objects of primitive fields. Never collect passwords, API keys, or payment details through form elicitation; use URL mode or an out-of-band flow.

---

## Code Best Practices

### Code Composability and Reusability

Your implementation MUST prioritize composability and code reuse:

1. **Extract Common Functionality**:
   - Create reusable helper functions for operations used across multiple tools
   - Build shared API clients for HTTP requests instead of duplicating code
   - Centralize error handling logic in utility functions
   - Extract business logic into dedicated functions that can be composed
   - Extract shared markdown or JSON field selection & formatting functionality

2. **Avoid Duplication**:
   - NEVER copy-paste similar code between tools
   - If you find yourself writing similar logic twice, extract it into a function
   - Common operations like pagination, filtering, field selection, and formatting should be shared
   - Authentication/authorization logic should be centralized

## Building and Running

Always build your TypeScript code before running:

```bash
# Build the project
npm run build

# Run the server
npm start

# Development with auto-reload
npm run dev
```

Always ensure `npm run build` completes successfully before considering the implementation complete.

## Quality Checklist

Before finalizing your Node/TypeScript MCP server implementation, ensure:

### Strategic Design
- [ ] Tools enable complete workflows, not just API endpoint wrappers
- [ ] Tool names reflect natural task subdivisions
- [ ] Response formats optimize for agent context efficiency
- [ ] Human-readable identifiers used where appropriate
- [ ] Error messages guide agents toward correct usage

### Implementation Quality
- [ ] FOCUSED IMPLEMENTATION: Most important and valuable tools implemented
- [ ] All tools registered using `registerTool` with complete configuration
- [ ] All tools include `title`, `description`, `inputSchema`, and `annotations`
- [ ] Annotations correctly set (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
- [ ] All tools use Zod 4 schema objects for input validation, with `z.strictObject` where extra fields must be rejected
- [ ] All Zod schemas have proper constraints and descriptive error messages
- [ ] All tools have comprehensive descriptions with explicit input/output types
- [ ] Descriptions include return value examples and complete schema documentation
- [ ] Error messages are clear, actionable, and educational

### TypeScript Quality
- [ ] TypeScript interfaces are defined for all data structures
- [ ] Strict TypeScript is enabled in tsconfig.json
- [ ] No use of `any` type - use `unknown` or proper types instead
- [ ] All async functions have explicit Promise<T> return types
- [ ] Error handling uses proper type guards (e.g., `instanceof ApiError`, `z.ZodError`)

### Advanced Features (where applicable)
- [ ] Resources registered for appropriate data endpoints
- [ ] Appropriate transport configured (`serveStdio` or `createMcpHandler`), with Host/Origin validation in front of HTTP
- [ ] Notifications implemented for dynamic server capabilities
- [ ] Type-safe with SDK interfaces

### Project Configuration
- [ ] Package.json depends on `@modelcontextprotocol/server` v2 and `zod` ^4.2, with no `@modelcontextprotocol/sdk` imports left
- [ ] Build script produces working JavaScript in dist/ directory
- [ ] Main entry point is properly configured as dist/index.js
- [ ] Server name follows format: `{service}-mcp-server`
- [ ] tsconfig.json properly configured with strict mode

### Code Quality
- [ ] Pagination is properly implemented where applicable
- [ ] Large responses check CHARACTER_LIMIT constant and truncate with clear messages
- [ ] Filtering options are provided for potentially large result sets
- [ ] All network operations handle timeouts and connection errors gracefully
- [ ] Common functionality is extracted into reusable functions
- [ ] Return types are consistent across similar operations

### Testing and Build
- [ ] `npm run build` completes successfully without errors
- [ ] dist/index.js created and executable
- [ ] Server lists and calls tools in the MCP Inspector: `npx @modelcontextprotocol/inspector node dist/index.js`
- [ ] All imports resolve correctly
- [ ] Sample tool calls work as expected