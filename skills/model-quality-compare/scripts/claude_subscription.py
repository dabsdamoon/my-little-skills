"""Native Claude subscription adapter; no SDK, --bare, API keys, or model fallback."""
import json
import subprocess
import uuid


def host_map(models, claude_models):
    if set(claude_models) - set(models):
        raise ValueError('--claude-models must be a subset of --models')
    return {m: 'claude' if m in claude_models else 'codex' for m in models}


def preflight(args, design, env):
    hosts = {}
    for host in sorted(set(design.get('providers', {m: 'codex' for m in design['models']}).values())):
        executable = args.claude if host == 'claude' else args.codex
        cmd = [executable, 'auth', 'status', '--json'] if host == 'claude' else [executable, 'login', 'status']
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if host == 'claude':
            try: auth = json.loads(result.stdout)
            except ValueError: raise ValueError('Claude subscription auth status is unavailable')
            if result.returncode or not auth.get('loggedIn') or auth.get('authMethod') != 'claude.ai' or auth.get('apiProvider') != 'firstParty':
                raise ValueError('Claude.ai subscription login required; API/third-party auth refused')
            receipt = {'authentication': 'claude.ai subscription', 'auth_method': 'claude.ai'}
        else:
            if result.returncode or 'Logged in using ChatGPT' not in result.stdout + result.stderr:
                raise ValueError('ChatGPT subscription login required; no API fallback')
            receipt = {'authentication': 'ChatGPT subscription'}
        receipt['cli_version'] = subprocess.run([executable, '--version'], env=env, check=True,
                                               capture_output=True, text=True).stdout.strip()
        hosts[host] = receipt
    version = ' / '.join(v['cli_version'] for v in hosts.values())
    return hosts, version


def command(executable, model, effort, instructions, artifact=False):
    tools = 'Bash,Read,Write,Edit' if artifact else ''
    settings = {'availableModels': [model], 'availableModelsMatch': 'exact', 'enforceAvailableModels': True,
                'fallbackModel': [], 'autoMemoryEnabled': False,
                'ultracode': False, 'env': {'CLAUDE_CODE_DISABLE_ULTRATHINK': '1'},
                'permissions': {'blockReadsOutsideWorkingDirectories': True}}
    if artifact:
        settings['sandbox'] = {'enabled': True, 'failIfUnavailable': True, 'autoAllowBashIfSandboxed': True,
                               'allowUnsandboxedCommands': False, 'network': {'allowedDomains': []}}
    cmd = [executable, '--print', '--safe-mode', '--restricted', '--no-session-persistence',
           '--session-id', str(uuid.uuid4()), '--setting-sources', '', '--settings', json.dumps(settings),
           '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--disable-slash-commands',
           '--no-chrome', '--prompt-suggestions', 'false', '--permission-mode', 'dontAsk',
           '--permission-prompts', 'none', '--tools', tools, '--model', model, '--effort', effort,
           '--system-prompt', instructions, '--output-format', 'stream-json', '--verbose']
    if artifact:
        cmd += ['--allowedTools', tools]
    return cmd


def normalize(events, expected_model, artifact=False, legacy_plugins=False, expected_session=None):
    """Retain native evidence separately; normalize only final text, tools and usage."""
    init = next((e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init'), {})
    final = next((e for e in reversed(events) if e.get('type') == 'result'), {})
    models = set(final.get('modelUsage', {}))
    if init.get('model'): models.add(init['model'])
    output, violations, tools = [], [], []
    server_tools = []
    for event in events:
        if event.get('type') != 'assistant': continue
        message = event.get('message', {})
        if message.get('model'): models.add(message['model'])
        for block in message.get('content', []):
            if block.get('type') == 'server_tool_use': server_tools.append(block.get('name'))
            if block.get('type') != 'tool_use': continue
            name, value = block.get('name'), block.get('input', {})
            allowed = artifact and name in {'Bash', 'Read', 'Write', 'Edit'}
            kind = 'file_change' if name in {'Write', 'Edit'} else 'command_execution'
            if not allowed: kind = 'host_control_violation'
            item = {'type': kind, 'host_tool': name, 'native_input': value,
                    'command': value.get('command', name + ' ' + str(value.get('file_path', '')))}
            tools.append(item)
            output.append({'type': 'item.completed', 'item': item})
    if not init: violations.append('missing native session initialization')
    if not models or models != {expected_model}: violations.append('reported model differs from requested model')
    expected_tools = {'Bash', 'Read', 'Write', 'Edit'} if artifact else set()
    if set(init.get('tools') or []) != expected_tools:
        violations.append('native tool inventory differs from declared controls')
    if init.get('permissionMode') != 'dontAsk': violations.append('unexpected native permission mode')
    if init.get('apiKeySource') != 'none': violations.append('unexpected native API authentication source')
    if expected_session is not None and not (expected_session == init.get('session_id') == final.get('session_id')):
        violations.append('native session ID differs from launch UUID')
    counts = (final.get('usage') or {}).get('server_tool_use') or {}
    external_count = sum(counts.get(k, 0) or 0 for k in ['web_search_requests', 'web_fetch_requests'])
    external_count += sum((v.get('webSearchRequests', 0) or 0)+(v.get('webFetchRequests', 0) or 0)
                          for v in final.get('modelUsage', {}).values())
    if server_tools or external_count: violations.append('undeclared server-side tool use')
    for key in ['skills', 'mcp_servers']:
        if init.get(key): violations.append('unexpected native context: ' + key)
    core_names = {'cc-plugin-sec-default', 'cc-plugin-agents-md', 'cc-plugin-telemetry',
                  'cc-plugin-privacy', 'cc-plugin-plugin-authoring'}
    builtins, custom = [], []
    for plugin in init.get('plugins', []):
        known_core = (isinstance(plugin, dict) and plugin.get('name') in core_names
                      and plugin.get('path') == 'builtin'
                      and plugin.get('source') == plugin['name'] + '@builtin')
        (builtins if known_core else custom).append(plugin)
    if custom or (legacy_plugins and init.get('plugins')):
        violations.append('unexpected native context: plugins')
    if violations:
        output.append({'type': 'item.completed', 'item': {'type': 'host_control_violation', 'message': '; '.join(violations)}})
    text = final.get('result', '')
    if not isinstance(text, str): text = ''
    if final.get('subtype') == 'success' and not final.get('is_error') and not final.get('permission_denials'):
        usage = final.get('usage', {})
        normalized = {'input_tokens': sum(usage.get(k, 0) for k in ['input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens']),
                      'cached_input_tokens': usage.get('cache_read_input_tokens', 0),
                      'cache_write_input_tokens': usage.get('cache_creation_input_tokens', 0),
                      'output_tokens': usage.get('output_tokens', 0)}
        output += [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': text}},
                   {'type': 'turn.completed', 'usage': normalized}]
    else:
        output.append({'type': 'turn.failed'})
    metadata = {'reported_models': sorted(models), 'native_session_id': init.get('session_id'),
                'native_requested_session_id': expected_session, 'native_result_session_id': final.get('session_id'),
                'native_permission_mode': init.get('permissionMode'), 'native_api_key_source': init.get('apiKeySource'),
                'native_server_tools': server_tools, 'native_external_tool_requests': external_count,
                'native_tools': init.get('tools'), 'native_skills': init.get('skills', []),
                'native_plugins': init.get('plugins', []), 'native_builtin_plugins': builtins,
                'native_user_plugins': custom, 'native_mcp_servers': init.get('mcp_servers', []),
                'native_normalization_version': 2,
                'native_usage': final.get('usage'), 'native_num_turns': final.get('num_turns'),
                'permission_denials': final.get('permission_denials', []), 'context_violations': violations}
    return output, text, metadata
