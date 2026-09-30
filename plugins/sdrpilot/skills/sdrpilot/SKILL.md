---
name: sdrpilot
description: How SDRPilot works and how to run LinkedIn outreach through its MCP tools (the ones prefixed linkedin_). Use when the user wants to check or change their ICP, leads, lead scoring, the connection queue, pending invitations, LinkedIn conversations, the outreach agent, daily limits and active hours, LinkedIn posts, the profile optimizer or outreach analytics, asks why they are getting few or poor leads, or asks how an SDRPilot feature works.
---

# SDRPilot

SDRPilot runs LinkedIn outreach for a connected LinkedIn account. It collects leads from several sources, scores them against the user's ideal customer profile, sends connection requests within daily limits, and an AI agent handles the conversations that follow until it hands a thread to a person.

Its tools are the ones prefixed `linkedin_`. Work with those. The server also lists unprefixed tools: they belong to the DM Champ account the workspace is signed in with, and the only ones you need here are the agent and knowledge base tools, because that is where the conversation agent's wording and knowledge are stored.

This file is the map. The help docs are the territory, and you can read them live.

## 1. Read the docs before you act

- `docs_search`: find the section that answers a question (add `product: "sdrpilot"` to stay inside the SDRPilot docs). Use it before you explain a feature or use a kind of tool for the first time in a conversation.
- `docs_read`: read the whole page. `docs_list`: the table of contents.
- The page `/api/api-and-mcp/` has worked examples for the queue, the ICP filters and re-scoring. Read it before the first write in those areas.
- When the docs and this file disagree, the docs win. Not every tool maps to a feature that is switched on for the account: if the docs say a feature is not available yet, tell the user that instead of trying the tool.
- A 403 on every `linkedin_` tool means the account has no SDRPilot workspace yet. The docs page `/get-started/request-access/` explains how access works.

## 2. The model in one page

**Workspace and seat.** The workspace belongs to a DM Champ account. One connected LinkedIn account is a seat, with its own limits, its own agents and its own inbox. Each seat runs on the clock of the country it connects from.

**ICP (ideal customer profile).** Two halves:
- a written profile, built from the customers the user marks or imports,
- hard filters (countries, languages, industries, roles, exclusions, score thresholds and more).

Every rebuild or edit is a version, and a restore creates a new version.

**Scoring.** The hard filters run first. A lead that passes gets an AI score from 0 to 100 with a reasoning note, and must reach the minimum score for its source.

**Lead sources.** Incoming connection requests, profile viewers, post engagement, content search and people search. Incoming requests are always on. The others can be switched on or off, and their order is set per agent.

**Connection queue.** Approved requests that have not been sent yet. They wait for the daily budget, the active hours window and their turn. Nothing in the queue has touched LinkedIn, so it can still be pulled back.

- In semi-auto mode requests stop in "Needs approval" with the drafted note. In full auto they skip that step.
- **Re-check (rescreen)** runs the hard filters only. It is a preview first and an apply second, and costs nothing.
- **Re-score** asks the AI to judge again. It spends AI credits, has no preview, and withdraws requests that no longer pass.
- Tightening a filter affects new leads. It does not reach back into the queue by itself: that is what the re-check is for.

**Pending invitations.** Sending pauses while too many sent invitations are unanswered. Old unanswered invitations are withdrawn automatically, a few at a time.

**Conversations.** A conversation belongs to either the AI or a human. Take over stops the AI on that thread. Hand back returns it, optionally with a note the agent reads first. The agent hands a thread over by itself when it cannot answer or the lead asks for a person. Those sit under Attention.

**The agent.** Each agent belongs to one seat and only one agent runs per sender. New agents are created paused. What the agent says comes from the linked DM Champ agent: its business context, knowledge base and FAQs. Edits there go to a draft first and are then published.

**Content.** Posts can be drafted, scheduled, published now, edited and removed.

**Profile optimizer.** Reads the user's own LinkedIn profile, scores it and writes suggestions. Nothing is written to LinkedIn until the user confirms it.

**Customers.** Marking a lead as a customer removes it from outreach and makes it evidence for the ICP.

## 3. Picking a tool

- Names read `linkedin_verb_object`. Search the tool list by the object: "icp", "queue", "lead", "conversation", "agent", "content", "analytics".
- A JSON request body goes in the single `body` argument.
- Start with the state: `linkedin_get_linkedin_status` and `linkedin_list_linkedin_accounts` (is the seat connected), `linkedin_get_ops_insights` (what the system thinks is wrong right now), `linkedin_get_outreach_stats` (sends against the seat limits), `linkedin_get_usage`.

## 4. Core workflows

**Health check: "how is my outreach doing?"**
1. `linkedin_get_linkedin_status`, `linkedin_get_ops_insights`.
2. `linkedin_get_analytics_overview`, `linkedin_get_lead_source_analytics`, `linkedin_get_outreach_stats`.
3. `linkedin_list_queued_connections` for what is waiting, `linkedin_list_conversations` with the attention filter for threads that need a person.

**Review the connection queue**
1. `linkedin_list_queued_connections` (filter by status, country, score, source).
2. Show the user who is waiting and the drafted notes.
3. On their decision: `linkedin_approve_queued_connections` or `linkedin_withdraw_queued_connections`, by id or by filter. The note that gets sent is the approved one, word for word.

**Lead quality is off: tune the ICP**
1. `linkedin_list_icp_profiles`, `linkedin_get_icp_profile` to see the written profile and the effective filters.
2. `linkedin_propose_icp_filters` turns a plain-language request into a filter proposal. Show it.
3. `linkedin_get_icp_impact` replays filters over a sample. Show what would change.
4. On a yes: `linkedin_update_icp_filters`. The body is the COMPLETE rule set, not a patch: a rule you leave out is switched off. Read the current filters first and send them back with the change.
5. `linkedin_rescreen_queued_connections` without `apply` for the preview, show it, then with `apply` on a yes.
6. If the written profile changed (new customers, a rebuild with `linkedin_rebuild_icp_profile`): `linkedin_rescore_queued_connections` for the queue and `linkedin_rescore_leads` for rejected leads. Both spend AI credits, so say so first.

**Handle replies**
1. `linkedin_list_conversations`, `linkedin_get_conversation`.
2. `linkedin_suggest_conversation_replies` drafts options. Suggestions never send by themselves.
3. To answer as the user: `linkedin_take_over_lead`, then `linkedin_send_conversation_message` with wording the user approved. `linkedin_hand_back_lead` returns the thread to the agent.

**Change how the agent talks**
The words live on the DM Champ agent: `linkedin_get_dmchamp_linkedin_agent` shows which one. Change it there (see the DM Champ docs on agents: edits are a draft until published). `linkedin_simulate_agent` dry-runs the agent on a sample conversation and sends nothing.

**Publish a post**
`linkedin_create_content` saves a draft. `linkedin_schedule_content` or `linkedin_publish_content` only after the user has read the final text.

## 5. Guardrails

Get the user's explicit OK in the conversation, stating exactly what will happen, before any of these:

- **Anything that reaches a real person on LinkedIn**: a connection request (`linkedin_connect_to_lead`, approving the queue), a message, accepting an incoming request, publishing a post, replying to a comment, applying a profile suggestion.
- **Anything that cannot be undone**: an invitation that was already sent cannot be changed, accepting an incoming request is not reversible on LinkedIn's side, deleting an agent cannot be undone, removing a LinkedIn account deletes it (signing out keeps the data).
- **Anything that spends credits**: re-scoring, and whatever the docs list as charged.

Account safety comes first. A restricted LinkedIn account is the worst outcome:

- Do not switch off warm-up to go faster. The docs call it the one setting that can get an account restricted on its own.
- Do not raise daily limits or widen active hours unless the user asks, and read `/settings/limits-and-active-hours/` first. An account that only ever acts in the middle of the night where it connects from is a pattern LinkedIn restricts accounts for.
- Never write or send outreach in bulk on your own initiative. Volume is the platform's job, inside the limits. Your job is targeting, review and the user's decisions.
- Never ask for, print or store the user's LinkedIn password or the API key.

## 6. Work that finishes later

Most operations are queued and return at once: connecting a seat, enriching a lead, building an ICP, queue operations, sending, content and scraping. Read the result with the matching get or list tool a little later, do not repeat the call. A few calls (simulate, analyze a website, large imports, the filter proposal) can take up to about two minutes.

## 7. Where things are in the docs

| Area | Docs path |
|---|---|
| Access, connecting LinkedIn, onboarding, dashboard | `/get-started/` |
| Leads, ICP, connection queue, searches, incoming requests | `/leads/` |
| Agents and the conversation agent | `/agents/` |
| Inbox | `/inbox/` |
| Posts and engagement | `/content/` |
| Profile optimizer | `/profile/` |
| Limits, active hours, session, safety | `/settings/` |
| Analytics | `/analytics/` |
| API and MCP | `/api/` |
