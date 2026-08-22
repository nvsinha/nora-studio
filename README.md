<!-- pyml disable no-inline-html,first-line-heading -->
<img src="https://raw.githubusercontent.com/nvsinha/nora-studio/main/docs/images/logo.svg"
     alt="" width="72" height="72" />

<!-- pyml enable no-inline-html,first-line-heading -->

# Nora Studio

**Author, run, and evaluate declarative agent networks.**

Nora Studio is the workbench for the [Nora Fleet](https://github.com/nvsinha/nora-fleet)
runtime. It ships a CLI, a library of ready-to-run agent networks, and the tooling to design,
test and export your own — all declared in HOCON, so building one is configuration rather than
code.

<!-- pyml disable no-inline-html -->
<p align="center">
  <img src="https://img.shields.io/github/stars/nvsinha/nora-studio?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/nvsinha/nora-studio?style=social" alt="GitHub forks">
  <img src="https://img.shields.io/github/watchers/nvsinha/nora-studio?style=social" alt="GitHub watchers">
  <br>
  <img src="https://img.shields.io/github/last-commit/nvsinha/nora-studio" alt="Last commit">
  <img src="https://img.shields.io/github/issues/nvsinha/nora-studio" alt="Issues">
  <img src="https://img.shields.io/github/issues-pr/nvsinha/nora-studio" alt="Pull requests">
  <br>
  <a href="https://github.com/nvsinha/nora-fleet"><img alt="Nora Fleet repository"
  src="https://img.shields.io/badge/GitHub-Repo-green.svg" /></a>
  <img src="https://img.shields.io/github/commit-activity/m/nvsinha/nora-fleet" alt="Nora Fleet commit activity">
</p>
<!-- pyml enable no-inline-html -->

## What Nora Fleet is

[**Nora Fleet**](https://github.com/nvsinha/nora-fleet) is an open-source, data-driven
framework for orchestrating multiple agents. Its purpose is to shorten the distance between an
idea for a collaborative AI system and a working one — for machine learning engineers and
business domain experts alike, since networks are declared in HOCON configuration rather than
written in code.

The reason for using several agents instead of one is that no single model holds all the
expertise or context a multifaceted problem needs. A network of LLM-powered agents can divide
such a problem between them, delegating subtasks to each other as the work reveals what it
actually requires.

Nora Fleet is open source, and is meant to be picked up and prototyped with immediately, in
any industry vertical.

<!-- TODO: the walkthrough videos still show the pre-rename UI, so they were
     dropped rather than left to mislead. Re-recording them needs a screen
     capture of a live session, which is a manual step. -->

### Key features

- **Data-driven configuration.** A whole agent network is declared in HOCON files, which puts
  designing agent interactions within reach of technical and non-technical people alike.
- **Adaptive communication.** Agents decide for themselves how to delegate, following the
  [AAOSA protocol](https://arxiv.org/abs/cs/9812015), so interactions stay fluid and
  decision-making stays decentralized.
- **Sly data.** Sensitive values move between agents through a separate channel, never exposed
  to a language model.
- **A designer that is itself an agent.** The Agent Network Designer is a meta-agent: give it
  a high-level description of a use case and it generates a custom agent network for it. It
  ships with Nora Fleet as an example.
- **Flexible tool integration.** Custom Python coded tools, APIs, databases and external agent
  ecosystems — Agentforce, Agentspace, CrewAI, MCP, A2A agents, LangChain tools and others —
  all plug into a workflow.
- **Traceability.** Logging, tracing and session-level metrics, for transparency while
  debugging and for monitoring once running.
- **Extensible and cloud-agnostic.** Works with OpenAI, Anthropic, Azure, Ollama and other
  providers, and deploys to a laptop, a container or a cloud equally well.

### Use cases

A sample of what has been built with Nora Fleet. There are more in
[docs/examples.md](docs/examples.md).

<!-- pyml disable line-length -->

| Agent network | Use case | What it does |
| --- | --- | --- |
| **Agent Network Designer** | Generating multi-agent HOCON configurations | Turns natural language into a complete multi-agent configuration, so intricate workflows do not have to be written by hand. |
| **Airline Policy Assistance** | Customer support for airline policies | Interprets and explains policy, handling questions about baggage allowances, cancellations and other travel concerns. |
| **Banking Operations and Compliance** | Financial operations and regulatory compliance | Monitors transactions, detects fraud and produces compliance reporting, keeping routine operations efficient and within the rules. |
| **Consumer Packaged Goods** | Market analysis and product development | Gathers and analyzes market trends, customer feedback and sales data to inform product development and marketing strategy. |
| **Insurance Agents** | Claims processing and risk assessment | Evaluates claims, weighs risk factors and checks policy compliance, improving both handling time and customer satisfaction. |
| **Intranet Agents** | Internal knowledge management and employee support | Gives employees quick access to policy, HR and IT support, improving internal communication and how easily resources are found. |
| **Retail Operations and Customer Service** | Retail experience and operational efficiency | Fields customer inquiries, manages inventory and supports the sales process. |
| **Telco Network Support** | Technical support and network issue resolution | Diagnoses network problems, walks users through troubleshooting and escalates what it cannot resolve, reducing downtime. |
| **Therapy Vignette Supervision** | Producing a treatment plan for a therapy vignette | A clear demonstration of several expert agents working toward a single plan. |

<!-- pyml enable line-length -->

## Architecture

![Nora architecture: the web UI calls the orchestration server, which loads this repository's agent networks][arch]

[arch]: https://raw.githubusercontent.com/nvsinha/nora-studio/main/docs/images/architecture.svg

<!-- Edit docs/images/architecture.svg; it is what this renders. -->

## Getting started

These commands are written for Linux and macOS. Adjust as needed on Windows.

### Install uv

[`uv`](https://docs.astral.sh/uv/) is a fast Python package and project manager from Astral.
Its own
[installation guide](https://docs.astral.sh/uv/getting-started/installation/) covers every
platform.

### Create a project

```bash
mkdir my_project
cd my_project
```

Initialize the project, create a virtual environment and add Nora Studio. It is not published
to PyPI, so it comes from the repository:

```bash
uv init
uv venv
source .venv/bin/activate
uv add "nora-studio @ git+https://github.com/nvsinha/nora-studio@v0.1.2"
```

### Initialize it

`nora init` sets up a Nora Studio project. (`nora-studio` is the same command spelled out in
full.) It will:

- ask which LLM provider you want
- create a `config` folder holding your model choices and plugin configuration
- create an `mcp` folder listing MCP tools
- create a `registries` folder containing a simple agent network

```bash
nora init
```

```text
Which LLM providers do you want to enable?

#  Provider       Default model
1  OpenAI         gpt-5.2 (default)
2  Anthropic      claude-sonnet
3  Google Gemini  gemini-3-flash

Enter numbers separated by commas (default: 1):
```

`nora --help` describes the command in full.

### Set your API keys

Set the key for your provider — `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` and so
on — or put it in a `.env` file in the working directory. [docs/api_key.md](docs/api_key.md)
covers the details and the other providers.

```bash
export OPENAI_API_KEY="XXX"
```

Confirm the keys are picked up:

```bash
nora check-llm-keys
```

Then confirm `config/llm_config.hocon` itself works. A valid configuration answers with a
`hello` from each configured model:

```bash
nora check-config
```

### Import agent networks

`nora import` brings in the agent networks that ship with Nora Studio. Run without arguments
it prompts interactively; [docs/cli/import.md](docs/cli/import.md) documents the rest.

```bash
nora import
```

```text
[info]  Discovering available agent networks...

? What do you want to import? (Use arrow keys)
   Basic (17)
   Experimental (9)
   Industry (22)
 » Root (6)
   Tools (28)
   ---------------
   Custom selection
   All (82)
```

Choose `Root` and press Enter, then confirm with `Y`. That group includes the Agent Network
Designer, which is what you will use to build networks of your own.

From `Experimental`, also import these two:

```text
   ● cruse_theme_agent
 » ● cruse_widget_agent
```

They enable CRUSE, an interface that adapts itself to what the user and the agents are doing.

### Start the developer UI

`nora run` starts a Nora Fleet server together with the Nora Flow UI:

```bash
nora run
```

| | Address |
| --- | --- |
| Nora Fleet server | `localhost:8080` |
| Nora Flow UI | [http://localhost:4173/](http://localhost:4173/) |

Logs are written under `logs/` — `server.log`, `nora_flow.log` and `thinking_dir/`.

![Nora Flow UI snapshot](https://raw.githubusercontent.com/nvsinha/nora-flow/main/docs/snapshot01.png)

## Building a network with the Designer

From the Nora Flow UI, click **NEW** at the top center of the screen.

![The NEW button in the Nora Flow header](https://raw.githubusercontent.com/nvsinha/nora-studio/main/docs/images/agent_network_designer_new_button.png)

A new window opens with a text box in the bottom right. Describe what you want. The Agent
Network Designer will:

- create the agents
- link them together
- write instructions for each one
- generate a few sample queries you can put to the finished network
- save the network in `registries/generated`

When it replies in the chat window, you can keep going — ask for changes and it will revise
the design.

Once it looks right, test it: the blue **Launch** button at the top center opens a window
where you can chat with the network. If something needs changing, return to the editor window
and ask. Any network can also be edited directly by clicking the pen icon beside its name in
the main window.

## Sharing networks

A network and everything it depends on can be bundled into a single file:

```bash
nora export my_project.hocon
```

The same `import` command takes a path, accepting either a `.hocon` file or a `.zip`:

```bash
nora import ~/Downloads/my_project.hocon
```

See [docs/cli/export.md](docs/cli/export.md) for the details.

## Command reference

<!-- pyml disable line-length -->

| Command | Purpose | Key flags |
| --- | --- | --- |
| `nora init` | Scaffold a starter project in the current directory. | `--providers openai,anthropic,google` |
| `nora run` | Start the Nora Fleet server and the Nora Flow UI. | `--server-host`, `--server-http-port`, `--nora_flow-port`, `--log-level`, `--client-only`, `--server-only` |
| `nora chat` | Chat with an agent network directly, without a server. | Positional: agent name. `--connection`, `--host`, `--port`, `--one-shot`, `--list` |
| `nora import` | Import agent networks into the current project. | Positional: space-separated group names, network names, or `all`; or local `.hocon` / `.zip` paths — do not mix the two. `--force` overwrites. Omit arguments for interactive mode. |
| `nora export` | Bundle a network from the current project into a shareable file. | Positional: network name, such as `music_nerd` or `basic/music_nerd`. `-o` / `--output` sets the output path. Omit arguments for an interactive picker. |
| `nora check-llm-keys` | Validate LLM API keys and environment variables. | `--tier 1` (placeholder), `--tier 2` (format), `--tier 3` (live API call, the default) |
| `nora check-config` | Validate the LLM configuration in a HOCON file. | `--hocon-path`, defaulting to `config/llm_config.hocon` |

<!-- pyml enable line-length -->

`nora <command> --help` gives the full flag list for any subcommand.

## Documentation

- [User guide](docs/user_guide.md) — a detailed tour of the Nora Fleet library and what it can do
- [Tutorial](docs/tutorial.md) — a worked introduction
- [Examples](docs/examples.md) — the full library of agent networks
- [Developer guide](docs/dev_guide.md) — for working on Nora Studio itself

## Utilities

- [Nora Fleet Slack app](./apps/slack/README.md) — a Slack integration for talking to Nora
  Fleet from your workspace
