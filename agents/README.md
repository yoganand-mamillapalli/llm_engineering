# Agent Orchestration Demos

These examples teach three ways to organize LangChain agents around one
question: fixed context stages, an explicitly orchestrated team, and a
supervisor that delegates to subagents. They are not benchmarks and do not
prove that using more agents improves an answer.

Run from the directory above `llm_engineering`:

```powershell
python -m llm_engineering.agents.multi_agent_context_demo
python -m llm_engineering.agents.team_agents_demo
python -m llm_engineering.agents.subagent_demo
```

Choose a provider in `.env` as described in the project README. All three demos use
the shared `create_model()` provider helper and keep their example context in
Python dictionaries, so no external data service is needed.

## Context-Aware Specialist Workflow

`multi_agent_context_demo.py` explores how context can be selected and passed
between specialist steps:

1. A context specialist receives the question and recent conversation notes,
   and can retrieve matching facts from the project context tool.
2. An answer specialist receives the context specialist's output and drafts an
   answer using known facts.
3. A reviewer checks the candidate answer against those facts and returns its
   review as the final output.

The example is meant to make context flow explicit: conversation notes and
retrieved project facts are supplied to later steps instead of assuming every
agent remembers earlier calls. `conversation_history` is an in-memory Python
list that retains notes for the full process lifetime and is searched by topic
using substring matching. It is not persisted, so restarting the process clears
it; passing the full history can also increase prompt size over time. The review
is another model response, not a formal correctness check, and the code does
not ask the answer agent to revise its draft after review.

Pay attention to:

- How `build_agent()` gives each agent a role-specific system prompt and tool
  set.
- How `get_project_context()` performs simple substring matching, not semantic
  search or database retrieval.
- How `remember_context()` and the prompt text pass session notes between
  turns and agent calls.
- What information each step receives, and what it must infer from prior
  output rather than shared hidden state.
- The extra model calls' effect on latency and cost, and how to evaluate each
  stage against a single-agent baseline.

## Team Decision Workflow

`team_agents_demo.py` models a product question handled by support and
engineering:

1. A coordinator summarizes the relevant roles and team context.
2. Support produces a customer-facing policy or access perspective.
3. Engineering identifies technical risks or constraints.
4. A final agent combines both responses into one answer.

This demonstrates role specialization, parallel execution, and synthesis. The
coordinator runs first; support and engineering then run concurrently with
`asyncio.gather()` using the coordinator summary; the final agent waits for both
responses before combining them. Although the coordinator is asked to identify
which teams should answer, the Python workflow currently calls both specialists
for every question. Routing is therefore illustrative, not dynamic. This is
application-managed orchestration, not a framework-managed subagent handoff.

Pay attention to:

- How role prompts constrain each specialist's responsibility.
- How the coordinator summary and team context are explicitly included in
  both parallel specialist prompts.
- How parallel calls may reduce latency while increasing concurrent provider
  requests and potentially encountering rate limits.
- How specialist answers can overlap, conflict, or introduce unsupported
  claims before synthesis.
- How `remember_decision()` stores notes only in process memory, and how only
  the latest three notes are included in the coordinator prompt.
- Whether a question needs both specialists, and whether the final answer
  preserves uncertainty and the source team's boundaries.

## Supervisor and Subagent Workflow

`subagent_demo.py` gives a supervisor agent two specialist agents through
async tool wrappers:

1. The supervisor receives the user's question.
2. It chooses the support subagent, the engineering subagent, or both by calling
  their respective tools.
3. Each tool invokes its specialist agent and returns that agent's answer to
  the supervisor.
4. The supervisor synthesizes the delegated results into the user-facing answer.

This is the subagent pattern: a parent agent delegates bounded work to child
agents, and only the parent responds to the user. Delegation is model-directed
through tool selection, while the wrapper code explicitly invokes each child;
there is no separate automatic handoff protocol.

Pay attention to:

- How the tool descriptions tell the supervisor when each subagent is useful.
- How the child agents receive their own role instructions and context tool.
- Whether the supervisor calls only the specialists needed for a question.
- The extra model calls and tool latency caused by delegation.

## Compare and Extend

Try the same questions with all three demos and a single-agent baseline. Check
factual grounding, missed context, unsupported claims, response consistency,
latency, and approximate model cost. More agents add prompt and coordination
work, so keep them only when they measurably help.

The distinction is that the context demo always runs fixed stages, the team
demo's Python code always calls both specialists (in parallel), and the
subagent demo lets the supervisor choose which specialist tools to call.
Useful next experiments are adding structured outputs to delegated results and
tests with questions whose answers are absent from the supplied context. Add
explicit limits for retries, tool calls, context size, and total run time
before turning these teaching examples into production workflows.