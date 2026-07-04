# MCP Server

Paper Format Agent ships an optional [Model Context Protocol](https://modelcontextprotocol.io)
server, so an agent runtime (Claude Code, Codex CLI, or any MCP client) can call
the same local, content-guarded formatting pipeline the CLI uses.

The MCP SDK requires Python >= 3.10.

## Install

```bash
pip install "paper-format-agent[mcp]"
```

## Run

```bash
paper-format-agent-mcp
```

This starts the server on the stdio transport. Point your MCP client at that
command.

### Claude Code / Codex CLI config example

```json
{
  "mcpServers": {
    "paper-format-agent": {
      "command": "paper-format-agent-mcp"
    }
  }
}
```

## Tools

| Tool | What it does | Writes files? |
| --- | --- | --- |
| `format_paper` | Reformats a paper DOCX to match a format guide and writes the outputs. Content-guarded: if the body/table text changes, it fails instead of writing. | Yes (into `out_dir`) |
| `extract_format_rules` | Returns the structured formatting rules parsed from a guide. | No |
| `score_paper` | Scores a paper against a guide and returns penalties and diagnostics. | No |

### `format_paper`

Arguments:

- `format_file` — path to the formatting guide (`.docx`, `.doc`, or `.txt`).
- `paper_file` — path to the paper to format (`.docx`).
- `out_dir` — directory for outputs (created if missing).
- `engine` — post-process engine, default `python` (the fully content-guarded
  path). `auto`/`word-com`/`libreoffice` run a post-processor after the guard
  check, e.g. to refresh the table of contents.
- `strict_required_sections` — enforce the guide's required sections, default
  `true`.

Returns a summary including `score_before`, `score_after`, `content_changed`,
`content_guard_enforced`, and both `content_fingerprint_before` /
`content_fingerprint_after`. The full report is written to
`<out_dir>/format_report.json`.

## Privacy

Every tool runs entirely on the local machine. No document content is uploaded.
