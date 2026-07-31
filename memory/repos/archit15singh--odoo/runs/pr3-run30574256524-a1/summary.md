## Review run pr3-run30574256524-a1
- Source: `archit15singh/odoo` PR #3
- Status: success
- Model: anthropic/claude-opus-5
- Verdict: REQUEST CHANGES
- Blocking: - **`odoo/tools/xml_utils.py` — `errors='surrogatepass'` cannot decode non-UTF-8 bytes and breaks `cleanup_xml_node`.** `surrogatepass` only permits *already-encoded lone surrogates* (the `\xed\xa0\x80` form); it does **not** tolerate arbitrary invalid bytes. The codec you want is `surrogateescape`. Trigger scenario: a partner sends a Latin-1/Windows-1252 encoded EDI/UBL document and any addon calls `cleanup_xml_node(payload_bytes)` (8 call sites in tree). Reproduced on this workspace:   ```   p
- Summary: The diagnosis in this PR is correct and valuable: the old `remove_control_characters` encoded a Unicode character class with `.encode()` and applied it as a **bytes** regex, which collapsed multi-byte ranges and let `U+FFFE`/`U+FFFF` survive into lxml. The new `str` path in `odoo/tools/xml_utils.py` genuinely fixes that, and `addons/account/tools/dict_to_xml.py` is correctly simplified. However, the new **bytes** path uses `errors='surrogatepass'`, which does *not* do what the code comment claims — it raises `UnicodeDecodeError` on exactly the legacy non-UTF-8 EDI payloads it says it protects. I reproduced this locally: it introduces a hard regression in `cleanup_xml_node`, and the PR's own new test `test_non_utf8_bytes_do_not_raise` fails. Not mergeable as-is; the `str` half is good and t
- Trigger: @luffy review this pr

Re-run with Claude Opus 5 + full agentic-loop capture (tool calls, session messages, usage, agent.log) for README showcase.
