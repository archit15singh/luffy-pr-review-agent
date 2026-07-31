#!/usr/bin/env python3
"""Capture a detailed Hermes agentic-loop package for Luffy traces.

Reads HERMES_HOME (state.db, logs/agent.log) + optional usage JSON and
writes a redacted showcase package:

  agent-loop/
    agent-loop.json   # structured steps, messages, tool calls, usage
    agent-loop.md     # human-readable walkthrough
    agent.log         # truncated redacted agent log
    usage.json        # token/cost if present
    sessions-export/  # raw message rows if available

Never copies .env / API keys; redacts sk-or- / Bearer tokens.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REDACT = [
    (re.compile(r"sk-or-v1-[A-Za-z0-9_-]+"), "[OPENROUTER_KEY_REDACTED]"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[API_KEY_REDACTED]"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.I), "Bearer [REDACTED]"),
    (re.compile(r"OPENROUTER_API_KEY\s*=\s*\S+"), "OPENROUTER_API_KEY=[REDACTED]"),
]


def redact_text(s: str) -> str:
    if not s:
        return s
    out = s
    for pat, repl in REDACT:
        out = pat.sub(repl, out)
    return out


def redact_obj(o: Any) -> Any:
    if isinstance(o, str):
        return redact_text(o)
    if isinstance(o, list):
        return [redact_obj(x) for x in o]
    if isinstance(o, dict):
        return {k: redact_obj(v) for k, v in o.items()}
    return o


def load_usage(path: Path | None) -> dict:
    if not path or not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def query_messages(db_path: Path, session_id: str | None) -> list[dict]:
    if not db_path.is_file():
        return []
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
    except Exception:
        return []
    try:
        # Discover columns
        cols = {r[1] for r in conn.execute("PRAGMA table_info(messages)").fetchall()}
        if "session_id" not in cols:
            return []
        select_cols = ["id", "session_id", "role", "content", "timestamp"]
        for optional in ("tool_name", "tool_calls", "tool_call_id", "name"):
            if optional in cols:
                select_cols.append(optional)
        col_sql = ", ".join(select_cols)
        if session_id:
            rows = conn.execute(
                f"SELECT {col_sql} FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
        else:
            # Latest session with most messages
            row = conn.execute(
                "SELECT session_id, COUNT(*) c FROM messages "
                "GROUP BY session_id ORDER BY c DESC LIMIT 1"
            ).fetchone()
            if not row:
                return []
            session_id = row[0]
            rows = conn.execute(
                f"SELECT {col_sql} FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
        out = []
        for r in rows:
            d = {k: r[k] for k in r.keys()}
            # Decode tool_calls JSON if string
            tc = d.get("tool_calls")
            if isinstance(tc, str) and tc.strip().startswith(("[", "{")):
                try:
                    d["tool_calls"] = json.loads(tc)
                except Exception:
                    pass
            content = d.get("content")
            if isinstance(content, str) and content.startswith("\x00json:"):
                try:
                    d["content"] = json.loads(content[len("\x00json:") :])
                except Exception:
                    pass
            out.append(d)
        return out
    except Exception as e:
        return [{"_error": f"state.db read failed: {e}"}]
    finally:
        conn.close()


def steps_from_messages(messages: list[dict]) -> list[dict]:
    steps = []
    n = 0
    for m in messages:
        if m.get("_error"):
            steps.append({"step": n, "kind": "error", "detail": m["_error"]})
            n += 1
            continue
        role = m.get("role") or "unknown"
        content = m.get("content")
        preview = content if isinstance(content, str) else json.dumps(content, default=str)
        preview = (preview or "")[:2000]
        step: dict[str, Any] = {
            "step": n,
            "kind": role,
            "role": role,
            "timestamp": m.get("timestamp"),
            "content_preview": redact_text(preview),
            "content_bytes": len(preview.encode("utf-8", errors="replace")),
        }
        if m.get("tool_name"):
            step["tool_name"] = m["tool_name"]
            step["kind"] = "tool_result"
        tc = m.get("tool_calls")
        if tc:
            step["kind"] = "assistant_tool_calls"
            # normalize list of calls
            calls = tc if isinstance(tc, list) else [tc]
            simplified = []
            for c in calls:
                if not isinstance(c, dict):
                    simplified.append({"raw": str(c)[:500]})
                    continue
                fn = c.get("function") or c
                simplified.append(
                    {
                        "id": c.get("id"),
                        "name": fn.get("name") if isinstance(fn, dict) else c.get("name"),
                        "arguments_preview": redact_text(
                            str((fn.get("arguments") if isinstance(fn, dict) else c.get("arguments")) or "")[
                                :1500
                            ]
                        ),
                    }
                )
            step["tool_calls"] = simplified
        steps.append(step)
        n += 1
    return steps


def render_markdown(pkg: dict) -> str:
    lines = [
        "# Hermes agentic loop (captured)",
        "",
        f"- **Captured at:** {pkg.get('captured_at')}",
        f"- **Model:** `{pkg.get('model')}`",
        f"- **Provider:** `{pkg.get('provider')}`",
        f"- **Session id:** `{pkg.get('session_id') or 'unknown'}`",
        f"- **API calls:** {pkg.get('usage', {}).get('api_calls', 'n/a')}",
        f"- **Tokens (in/out/total):** "
        f"{pkg.get('usage', {}).get('input_tokens', '?')} / "
        f"{pkg.get('usage', {}).get('output_tokens', '?')} / "
        f"{pkg.get('usage', {}).get('total_tokens', '?')}",
        f"- **Estimated cost USD:** {pkg.get('usage', {}).get('estimated_cost_usd', 'n/a')}",
        f"- **Message count:** {len(pkg.get('messages') or [])}",
        f"- **Tool call turns:** {pkg.get('tool_call_turns', 0)}",
        "",
        "## Loop steps",
        "",
    ]
    for s in pkg.get("steps") or []:
        kind = s.get("kind")
        lines.append(f"### Step {s.get('step')} · `{kind}`")
        if s.get("tool_name"):
            lines.append(f"- **tool:** `{s['tool_name']}`")
        if s.get("tool_calls"):
            lines.append("- **tool_calls:**")
            for c in s["tool_calls"]:
                lines.append(
                    f"  - `{c.get('name')}` args: `{c.get('arguments_preview', '')[:400]}`"
                )
        prev = s.get("content_preview") or ""
        if prev.strip():
            lines.append("")
            lines.append("```")
            lines.append(prev[:3000])
            lines.append("```")
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "Prompts, tool arguments, and model outputs are redacted for secrets. "
        "Full (redacted) rows live in `agent-loop.json`. Raw Hermes file log: `agent.log`."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    hermes_home = Path(os.environ.get("HERMES_HOME", "")).expanduser()
    out_dir = Path(os.environ.get("OUT_DIR", ".luffy-out")).expanduser()
    loop_dir = Path(os.environ.get("AGENT_LOOP_DIR", str(out_dir / "agent-loop")))
    usage_path = Path(os.environ.get("HERMES_USAGE_FILE", str(out_dir / "hermes-usage.json")))
    model = os.environ.get("LUFFY_MODEL") or os.environ.get("OPENROUTER_MODEL") or "unknown"
    provider = os.environ.get("LUFFY_PROVIDER") or "openrouter"

    loop_dir.mkdir(parents=True, exist_ok=True)
    usage = load_usage(usage_path if usage_path.is_file() else None)
    session_id = usage.get("session_id")

    db_path = hermes_home / "state.db" if hermes_home else Path()
    messages = query_messages(db_path, session_id) if hermes_home else []
    messages = redact_obj(messages)
    steps = steps_from_messages(messages if isinstance(messages, list) else [])
    tool_turns = sum(1 for s in steps if s.get("kind") == "assistant_tool_calls")

    # Copy / truncate agent.log
    log_src = hermes_home / "logs" / "agent.log" if hermes_home else None
    log_dest = loop_dir / "agent.log"
    log_excerpt = ""
    if log_src and log_src.is_file():
        raw = log_src.read_text(errors="replace")
        # keep last 200k chars
        raw = raw[-200_000:]
        log_excerpt = redact_text(raw)
        log_dest.write_text(log_excerpt)

    if usage:
        (loop_dir / "usage.json").write_text(
            json.dumps(redact_obj(usage), indent=2) + "\n"
        )

    # Also grab errors.log tail if present
    err_src = hermes_home / "logs" / "errors.log" if hermes_home else None
    if err_src and err_src.is_file():
        err = redact_text(err_src.read_text(errors="replace")[-50_000:])
        (loop_dir / "errors.log").write_text(err)

    # List sessions dir files (names only + small jsonl copies)
    sessions_meta = []
    sess_dir = hermes_home / "sessions" if hermes_home else None
    if sess_dir and sess_dir.is_dir():
        export_dir = loop_dir / "sessions-export"
        export_dir.mkdir(exist_ok=True)
        for p in sorted(sess_dir.rglob("*"))[:50]:
            if p.is_file() and p.stat().st_size < 2_000_000:
                rel = str(p.relative_to(sess_dir))
                sessions_meta.append({"path": rel, "bytes": p.stat().st_size})
                try:
                    data = p.read_bytes()
                    # text-ish
                    if p.suffix in {".json", ".jsonl", ".md", ".txt", ".log"} or b"{" in data[:20]:
                        text = redact_text(data.decode("utf-8", errors="replace"))
                        (export_dir / p.name).write_text(text[:500_000])
                except Exception:
                    pass

    pkg = {
        "schema_version": 1,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": model,
        "provider": provider,
        "session_id": session_id,
        "hermes_home": str(hermes_home) if hermes_home else None,
        "usage": redact_obj(usage),
        "tool_call_turns": tool_turns,
        "message_count": len(messages) if isinstance(messages, list) else 0,
        "steps": steps,
        "messages": messages,
        "agent_log_bytes": len(log_excerpt.encode("utf-8")),
        "agent_log_sha256": hashlib.sha256(log_excerpt.encode("utf-8")).hexdigest()
        if log_excerpt
        else None,
        "sessions_files": sessions_meta,
    }

    (loop_dir / "agent-loop.json").write_text(json.dumps(pkg, indent=2, default=str) + "\n")
    (loop_dir / "agent-loop.md").write_text(render_markdown(pkg))
    print(loop_dir)
    print(
        f"captured steps={len(steps)} messages={pkg['message_count']} "
        f"tool_turns={tool_turns} session={session_id}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
