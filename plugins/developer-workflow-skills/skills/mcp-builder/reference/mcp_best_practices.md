# MCP Server Best Practices

## Quick Reference

### Server Naming
- **Python**: `{service}_mcp` (e.g., `slack_mcp`)
- **Node/TypeScript**: `{service}-mcp-server` (e.g., `slack-mcp-server`)

### Tool Naming
- Use snake_case with service prefix
- Format: `{service}_{action}_{resource}`
- Example: `slack_send_message`, `github_create_issue`

### Response Formats
- Support both JSON and Markdown formats
- JSON for programmatic processing
- Markdown for human readability

### Pagination
- Always respect `limit` parameter
- Return `has_more`, `next_offset`, `total_count`
- Default to 20-50 items

### Transport
- **Streamable HTTP**: For remote servers, multi-client scenarios
- **stdio**: For local integrations, command-line tools
- Avoid HTTP+SSE (Deprecated in spec 2026-07-28)
- Do not build on Logging, Sampling, or Roots (Deprecated in spec 2026-07-28)

---

## Server Naming Conventions

Follow these standardized naming patterns:

**Python**: Use format `{service}_mcp` (lowercase with underscores)
- Examples: `slack_mcp`, `github_mcp`, `jira_mcp`

**Node/TypeScript**: Use format `{service}-mcp-server` (lowercase with hyphens)
- Examples: `slack-mcp-server`, `github-mcp-server`, `jira-mcp-server`

The name should be general, descriptive of the service being integrated, easy to infer from the task description, and without version numbers.

---

## Tool Naming and Design

### Tool Naming

1. **Use snake_case**: `search_users`, `create_project`, `get_channel_info`
2. **Include service prefix**: Anticipate that your MCP server may be used alongside other MCP servers
   - Use `slack_send_message` instead of just `send_message`
   - Use `github_create_issue` instead of just `create_issue`
3. **Be action-oriented**: Start with verbs (get, list, search, create, etc.)
4. **Be specific**: Avoid generic names that could conflict with other servers

### Tool Design

- Tool descriptions must narrowly and unambiguously describe functionality
- Descriptions must precisely match actual functionality
- Provide tool annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
- Keep tool operations focused and atomic

---

## Response Formats

All tools that return data should support multiple formats:

### JSON Format (`response_format="json"`)
- Machine-readable structured data
- Include all available fields and metadata
- Consistent field names and types
- Use for programmatic processing

### Markdown Format (`response_format="markdown"`, typically default)
- Human-readable formatted text
- Use headers, lists, and formatting for clarity
- Convert timestamps to human-readable format
- Show display names with IDs in parentheses
- Omit verbose metadata

---

## Pagination

For tools that list resources:

- **Always respect the `limit` parameter**
- **Implement pagination**: Use `offset` or cursor-based pagination
- **Return pagination metadata**: Include `has_more`, `next_offset`/`next_cursor`, `total_count`
- **Never load all results into memory**: Especially important for large datasets
- **Default to reasonable limits**: 20-50 items is typical

Example pagination response:
```json
{
  "total": 150,
  "count": 20,
  "offset": 0,
  "items": [...],
  "has_more": true,
  "next_offset": 20
}
```

---

## Transport Options

This section follows spec revision 2026-07-28 (changelog: `https://modelcontextprotocol.io/specification/2026-07-28/changelog.md`). Both current SDKs also serve clients on 2025-11-25 and earlier from the same server code.

### What changed in 2026-07-28

- **Stateless protocol.** The `initialize` / `notifications/initialized` handshake is removed. Every request carries its protocol version and client capabilities in `_meta`.
- **`server/discover` is required.** Servers MUST implement it to advertise supported versions, capabilities, and identity. The SDKs implement it for you.
- **No sessions.** Streamable HTTP drops protocol-level sessions and the `Mcp-Session-Id` header. Keep cross-call state in explicit handles passed as ordinary tool arguments.
- **No GET stream.** The standalone HTTP GET stream and `resources/subscribe` are replaced by `subscriptions/listen`, a long-lived POST response stream for opted-in change notifications. SSE resumability (`Last-Event-ID`) is gone.
- **No server-initiated requests.** Elicitation, sampling, and roots requests travel inside an `InputRequiredResult` and the client retries the original request with the answers (Multi Round-Trip Requests). Use your SDK's era-portable form rather than pushing a request mid-call.
- **Deprecated:** Logging, Sampling, and Roots (log to stderr or OpenTelemetry instead; call LLM provider APIs directly instead of Sampling; take paths as tool parameters instead of Roots), and the HTTP+SSE transport.

### Streamable HTTP

**Best for**: Remote servers, web services, multi-client scenarios

**Characteristics**:
- One MCP endpoint (e.g. `/mcp`) that accepts POST; every JSON-RPC message is its own POST
- Each response is a single JSON object or an SSE stream scoped to that request (progress, then the result)
- Stateless on 2026-07-28: any instance can serve any request, so it scales horizontally without sticky sessions
- Request bodies are capped (both SDKs default to 4 MiB)

**Use when**:
- Serving multiple clients simultaneously
- Deploying as a cloud service
- Integration with web applications

### stdio

**Best for**: Local integrations, command-line tools

**Characteristics**:
- Newline-delimited JSON-RPC over the standard streams of a client-launched subprocess
- Simple setup, no network configuration needed
- Credentials come from the environment the client launches the server with

**Use when**:
- Building tools for local development environments
- Integrating with desktop applications
- Single-user scenarios

**Note**: stdio servers must NOT write anything but protocol messages to stdout (log to stderr)

### Transport Selection

| Criterion | stdio | Streamable HTTP |
|-----------|-------|-----------------|
| **Deployment** | Local | Remote |
| **Clients** | Single | Multiple |
| **Complexity** | Low | Medium |
| **Auth** | Environment credentials | OAuth 2.1 (spec authorization) |

---

## Security Best Practices

### Authentication and Authorization

Authorization is optional in MCP. HTTP-based servers that support it SHOULD follow the spec's authorization section (`https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization.md`); stdio servers SHOULD NOT, and read credentials from the environment instead. For an HTTP server that requires auth, the spec says:

- **Protected Resource Metadata is required.** MCP servers MUST implement OAuth 2.0 Protected Resource Metadata (RFC 9728) so clients can discover the authorization server.
- **Validate the audience.** MCP servers MUST validate that each access token was issued specifically for them as the intended audience (RFC 8707 Section 2), and answer invalid or expired tokens with HTTP 401. Clients MUST send RFC 8707 resource indicators naming the server's canonical URI.
- **No token passthrough.** MCP servers MUST NOT accept or transit tokens issued for anything else, and MUST NOT forward the token they received to upstream APIs. Call upstream APIs with a separate token issued by the upstream authorization server.
- **Client registration.** Clients and authorization servers SHOULD support OAuth Client ID Metadata Documents. Dynamic Client Registration (RFC 7591) is Deprecated and kept only for backward compatibility. Pre-registration is the third option.
- **Tokens stay out of URLs.** Access tokens MUST NOT appear in the URI query string.

Both SDKs ship helpers for the resource-server side (bearer-token verification and the metadata endpoint); see their authorization docs rather than hand-rolling token checks.

**API Keys** (for the upstream service the server wraps):
- Read keys from the environment at startup, never from code or committed config files
- Have the launcher supply them on demand (e.g. a `scripts/with-secrets.sh` wrapper that fetches from a secret manager) instead of exporting them in shell profiles
- Never log or echo key values, and fail at startup with a message that names the missing variable
- Never ask for a secret through form-mode elicitation: the spec forbids requesting passwords, API keys, access tokens, or payment credentials that way. Use URL-mode elicitation or server configuration

### Input Validation

- Sanitize file paths to prevent directory traversal
- Validate URLs and external identifiers
- Check parameter sizes and ranges
- Prevent command injection in system calls
- Use schema validation (Pydantic/Zod) for all inputs

### Error Handling

- Don't expose internal errors to clients
- Log security-relevant errors server-side
- Provide helpful but not revealing error messages
- Clean up resources after errors

### DNS Rebinding Protection

For Streamable HTTP servers:
- Servers MUST validate the `Origin` header on all incoming connections
- When running locally, bind to `127.0.0.1` rather than `0.0.0.0`
- Python's `streamable_http_app()` and the TypeScript framework apps (`createMcpExpressApp`, Hono, Fastify) validate `Host` and `Origin` by default on localhost binds; the bare TypeScript `createMcpHandler` does not, so put the checks in front of it. Behind a real hostname, configure an explicit allowlist instead of turning the check off

---

## Tool Annotations

Provide annotations to help clients understand tool behavior:

| Annotation | Type | Default | Description |
|-----------|------|---------|-------------|
| `readOnlyHint` | boolean | false | Tool does not modify its environment |
| `destructiveHint` | boolean | true | Tool may perform destructive updates |
| `idempotentHint` | boolean | false | Repeated calls with same args have no additional effect |
| `openWorldHint` | boolean | true | Tool interacts with external entities |

**Important**: Annotations are hints, not security guarantees. Clients should not make security-critical decisions based solely on annotations.

---

## Error Handling

- Use standard JSON-RPC error codes
- Report tool errors within result objects (not protocol-level errors)
- Provide helpful, specific error messages with suggested next steps
- Don't expose internal implementation details
- Clean up resources properly on errors

Example error handling:
```typescript
try {
  const result = performOperation();
  return { content: [{ type: "text", text: result }] };
} catch (error) {
  return {
    isError: true,
    content: [{
      type: "text",
      text: `Error: ${error.message}. Try using filter='active_only' to reduce results.`
    }]
  };
}
```

---

## Testing Requirements

Comprehensive testing should cover:

- **Functional testing**: Verify correct execution with valid/invalid inputs
- **Integration testing**: Test interaction with external systems
- **Security testing**: Validate auth, input sanitization, rate limiting
- **Performance testing**: Check behavior under load, timeouts
- **Error handling**: Ensure proper error reporting and cleanup

---

## Documentation Requirements

- Provide clear documentation of all tools and capabilities
- Include working examples (at least 3 per major feature)
- Document security considerations
- Specify required permissions and access levels
- Document rate limits and performance characteristics
