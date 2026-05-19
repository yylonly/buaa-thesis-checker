# BUAA Thesis Checker Plugin

This plugin bundles the repository's BUAA thesis and document skills for Codex and Claude Code.

## Included Skills

| Skill | Purpose |
| --- | --- |
| `buaa-thesis-format-checking` | Check BUAA thesis formatting and generate JSON/HTML reports. |
| `buaa-thesis-content-checking` | Review academic contributions, innovations, experiments, and baselines. |
| `buaa-thesis-checking` | Run a combined thesis review and generate formal Chinese review comments. |
| `cn-to-en-translator` | Translate Chinese Word documents into polished English `.docx` files. |

## Codex

Codex plugin metadata lives at:

```text
.codex-plugin/plugin.json
```

The repository-level Codex marketplace entry is:

```text
.agents/plugins/marketplace.json
```

## Claude Code

Claude Code plugin metadata lives at:

```text
.claude-plugin/plugin.json
```

Test locally from the repository root:

```bash
claude --plugin-dir ./plugins/buaa-thesis-checker
```

The skills are namespaced in Claude Code, for example:

```text
/buaa-thesis-checker:buaa-thesis-checking
/buaa-thesis-checker:buaa-thesis-format-checking
/buaa-thesis-checker:buaa-thesis-content-checking
/buaa-thesis-checker:cn-to-en-translator
```

The repository also includes a Claude Code marketplace at:

```text
.claude-plugin/marketplace.json
```

For local marketplace testing:

```bash
claude plugin marketplace add .
claude plugin install buaa-thesis-checker@buaa-thesis-tools
```
