#!/usr/bin/env python3
"""Checks that keep the plugin honest. Run before every push:

    python3 scripts/check.py            # offline checks
    python3 scripts/check.py --live     # also check every tool name against the live MCP server

1. Skill text follows the house rules: no dashes used as punctuation, nothing
   about models or infrastructure.
2. The MCP config takes the key from user config, never a literal.
3. --live: every `tool_name` the skill mentions exists on the server the plugin
   connects to (tools/list needs a key header but not a valid key).
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = "sdrpilot"
URL = "https://mcp.sdrpilot.ai/mcp"
SKILL = f"plugins/{PLUGIN}/skills/{PLUGIN}/SKILL.md"
BANNED = re.compile(r"—|–| - |\b(gpt|claude-|gemini|qwen|llama|self.?host|gpu|postgres|firestore|hetzner|proxy vendor)\b", re.I)
NOT_TOOLS = {"verb_object", "linkedin_verb_object", "sub_account_id"}
failures = []


def tools_on(url):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}).encode()
    headers = {"X-API-Key": "check", "Content-Type": "application/json", "Accept": "application/json, text/event-stream", "User-Agent": "claude-plugin-check/1.0"}
    raw = urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers), timeout=60).read().decode()
    for line in raw.splitlines():
        if line.startswith("data: "):
            raw = line[6:]
            break
    return {t["name"] for t in json.loads(raw)["result"]["tools"]}


text = (ROOT / SKILL).read_text()
for number, line in enumerate(text.splitlines(), 1):
    hit = BANNED.search(line)
    if hit:
        failures.append(f"{SKILL}:{number}: banned wording {hit.group(0)!r}")
if len(text.splitlines()) > 500:
    failures.append(f"{SKILL}: over 500 lines")

checked = 0
if "--live" in sys.argv:
    live = tools_on(URL)
    named = set(re.findall(r"`((?:linkedin_)?[a-z]+(?:_[a-z0-9]+)+)`", text))
    checked = len(named)
    for name in sorted(named - live - NOT_TOOLS):
        failures.append(f"{SKILL}: `{name}` is not a tool on {URL}")

for manifest in [".claude-plugin/marketplace.json", f"plugins/{PLUGIN}/.claude-plugin/plugin.json", f"plugins/{PLUGIN}/.mcp.json"]:
    raw = (ROOT / manifest).read_text()
    json.loads(raw)
    if manifest.endswith(".mcp.json") and "${user_config.api_key}" not in raw:
        failures.append(f"{manifest}: the key must come from user config, never a literal")

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("ok: skill checked" + (f", {checked} tool names verified against {URL}" if checked else ""))
