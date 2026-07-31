## Review run pr3-run30572964204-a1
- Source: `archit15singh/odoo` PR #3
- Status: success
- Model: openai/gpt-5-mini
- Verdict: REQUEST CHANGES
- Blocking: - `odoo/tools/xml_utils.py` — bytes decoding handling: If a caller passes `bytes` that are not valid UTF‑8 (for example: legacy Latin‑1 payload, or ill-formed byte sequences), the new implementation will attempt to decode to `str` (presumably with strict UTF‑8) and raise `UnicodeDecodeError`. Trigger scenario: an EDI/export pipeline that previously passed non-UTF-8 bytes into `cleanup_xml_node` / `remove_control_characters` will now raise and fail the export. Either: 1) explicitly document and e
- Summary: This PR replaces a broken bytes-based regex approach with a Unicode-aware sanitizer for XML illegal chars (`odoo/tools/xml_utils.py`), makes `remove_control_characters` preserve input type (str/bytes), updates `addons/account/tools/dict_to_xml.py` to pass strings, and adds regression tests in `odoo/addons/test_testing_utilities/tests/test_xml_tools.py`. Implementation and tests look solid for the common UTF‑8 paths and the explicit allowed controls (`\t\n\r`) are preserved. There is one important compatibility/behavioral gap around how `bytes` inputs are decoded and one portability edge worth addressing before merge.
- Trigger: @luffy review this pr

Complex fix for odoo/odoo#271153 — Unicode-level XML Char sanitizer, dict_to_xml str path, regression tests. Please deep-review correctness, encoding edge cases, and test covera
