# SDRPilot plugin for Claude Code

Let Claude work inside your own SDRPilot workspace, and know what it is doing while it is there.

The plugin bundles three things:

1. **The connection.** The MCP server for your workspace, authenticated with your own API key.
2. **A skill.** The playbook Claude reads first: how SDRPilot is put together (your ICP, scoring, the connection queue, conversations), the common workflows step by step, and what it must ask you before doing.
3. **Live help docs.** The server gives Claude `docs_search`, `docs_read` and `docs_list`, which read the help site as it is today. When we ship a feature and document it, Claude can look it up the same day.

## Install

You need [Claude Code](https://claude.com/claude-code), an SDRPilot workspace and your API key. In SDRPilot, open Settings, then API and AI assistants.

```bash
claude plugin marketplace add sdrpilot/claude-plugin
claude plugin install sdrpilot@sdrpilot
```

Then give the plugin your key. Start `claude` and run:

```
/plugin configure sdrpilot@sdrpilot
```

Paste the key when it asks. It is stored in your system keychain, not in a file. Restart Claude Code afterwards so the connection picks it up.

Check that it works: start `claude`, run `/mcp` and look for the server marked connected, then ask something like "how is my outreach doing this week?".

## What to ask

- "How is my outreach doing this week, and is anything wrong with my account?"
- "My leads are off target. Show me what my ICP filters let through and suggest a tighter set."
- "Who is waiting in my connection queue, and which of them would you not send?"
- "Which conversations need me, and what would you reply?"
- "What is the difference between re-checking and re-scoring the queue?"

## What Claude will and will not do on its own

The skill tells Claude to preview before it applies, to show you what will change, and to get your explicit go before anything that reaches a real person on LinkedIn (a connection request, a message, accepting a request, publishing a post), anything that cannot be undone, and anything that spends credits. It is also told to put the safety of your LinkedIn account first: no switching off warm-up, no raising limits unless you ask.

Your API key is the access control: Claude can do what the key can do.

## Good to know

- **Claude Code only for now.** The plugin installs in the Claude Code terminal app. The Claude desktop and web apps are not supported yet.
- **No workspace yet?** The LinkedIn tools answer 403 until your account has SDRPilot access. See [Request Access and Sign In](https://help.sdrpilot.ai/get-started/request-access/).
- **Updates.** `claude plugin marketplace update sdrpilot`, then `claude plugin update sdrpilot@sdrpilot`. The help docs need no update, Claude reads them live.
- **Remove.** `claude plugin uninstall sdrpilot@sdrpilot`.

## Help

- Help docs: https://help.sdrpilot.ai

## For maintainers

```bash
python3 scripts/check.py --live                     # wording rules, every tool name the skill mentions exists on the live server
claude plugin validate . --strict                   # the marketplace
claude plugin validate ./plugins/sdrpilot --strict  # the plugin
```

Every statement in the skill must be backed by the help docs, and anything that can change (limits, prices, what is in beta) belongs in the docs, not in the skill. Bump `version` in `plugins/sdrpilot/.claude-plugin/plugin.json` when the skill or the MCP config changes, otherwise installed copies do not update.
