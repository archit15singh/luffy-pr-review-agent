<!-- luffy-review pr=3 run=30572964204 -->
## 🏴‍☠️ Luffy Review — PR #3

**Verdict:** REQUEST CHANGES  
**Confidence:** high  
**Score:** 88/100  
**Review effort:** 3/5

### Summary
This PR replaces a broken bytes-based regex approach with a Unicode-aware sanitizer for XML illegal chars (`odoo/tools/xml_utils.py`), makes `remove_control_characters` preserve input type (str/bytes), updates `addons/account/tools/dict_to_xml.py` to pass strings, and adds regression tests in `odoo/addons/test_testing_utilities/tests/test_xml_tools.py`. Implementation and tests look solid for the common UTF‑8 paths and the explicit allowed controls (`\t\n\r`) are preserved. There is one important compatibility/behavioral gap around how `bytes` inputs are decoded and one portability edge worth addressing before merge.

### Walkthrough
- Compiles and applies the illegal-character class at Unicode/code-point level (`odoo/tools/xml_utils.py::remove_control_characters`) instead of encoding the pattern to bytes.
- `remove_control_characters` now accepts `str` or `bytes` and returns the same type (backwards compatibility for callers that pass bytes).
- `addons/account/tools/dict_to_xml.py` changed to pass `str` directly to sanitizer rather than encode→scrub→decode.
- Tests added in `odoo/addons/test_testing_utilities/tests/test_xml_tools.py` cover: str/bytes inputs, allowed controls (`\t\n\r`), assignment to lxml text, and type errors.

### Blocking
- `odoo/tools/xml_utils.py` — bytes decoding handling: If a caller passes `bytes` that are not valid UTF‑8 (for example: legacy Latin‑1 payload, or ill-formed byte sequences), the new implementation will attempt to decode to `str` (presumably with strict UTF‑8) and raise `UnicodeDecodeError`. Trigger scenario: an EDI/export pipeline that previously passed non-UTF-8 bytes into `cleanup_xml_node` / `remove_control_characters` will now raise and fail the export. Either: 1) explicitly document and enforce that callers must pass UTF‑8, or 2) handle bytes robustly (decode with a defined error policy such as `surrogatepass` and re-encode), and add a regression test for non-UTF-8 bytes. Concrete trigger: send a Latin‑1 encoded invoice bytes payload into `account.tools.dict_to_xml` and observe an unhandled `UnicodeDecodeError` / export failure. This is blocking until behavior is documented or code is adjusted.

### Key findings

| Severity | File | Issue | Trigger scenario |
|----------|------|-------|------------------|
| high | `odoo/tools/xml_utils.py` | `bytes` input decoding/compatibility | Passing non-UTF-8 `bytes` into `remove_control_characters` (used via `cleanup_xml_node` / `dict_to_xml`) raises `UnicodeDecodeError`, breaking export/EDI paths that previously operated on raw bytes. |
| medium | `odoo/tools/xml_utils.py` | Unicode-range / regex portability for >U+FFFF ranges | On obscure Python builds or older/embedded regex engines, range handling for `\U00010000-\U0010FFFF` can behave differently (surrogate handling). Trigger: platform with narrow Unicode build or regex oddity that matches surrogate pairs unexpectedly and leaves illegal chars unfiltered. |
| low | `addons/account/tools/dict_to_xml.py` | Behavioral change is intentional but should be documented | Callers that relied on previous implicit bytes->bytes scrub behavior may be surprised by the stricter Unicode-based sanitization. Trigger: internal code expecting previous (buggy) behavior for some rare code points. |

### Security audit
No security issues found. No injection, secrets, or auth problems introduced by the new sanitizer itself. The sanitizer reduces risk by correctly removing illegal XML code points. Note: if callers silently re-encode with a permissive errors policy, unexpected replacement characters could appear in XML output — that’s a correctness/robustness, not a direct security flaw.

### Suggestions
- Add an explicit statement in the `remove_control_characters` docstring explaining expected input encoding for `bytes` (e.g., "if bytes are passed they must be UTF‑8 encoded; otherwise a UnicodeDecodeError is raised" OR "we decode with 'utf-8' using surrogatepass and re-encode to bytes to preserve non‑UTF8 sequences").
- Add a unit test that passes non-UTF8 `bytes` (e.g., Latin-1 encoded bytes containing high‑bit bytes) to assert the intended behavior (raise vs. lossy-sanitized output). This makes the compatibility decision explicit.
- Add a short comment near the compiled regex explaining that ranges include `\U00010000-\U0010FFFF` and why (XML 1.0 Char production), and note assumptions about Python's Unicode/regex handling.

### Code suggestions
If you want to preserve maximal backward compatibility for `bytes` while still performing Unicode-level sanitization, consider decoding with `surrogatepass` and re-encoding. Example change suggestion:

#### Decode `bytes` with surrogatepass (`odoo/tools/xml_utils.py`)
```diff
-    if isinstance(value, bytes):
-        s = value.decode('utf-8')
+    if isinstance(value, bytes):
+        # Decode using surrogatepass so we can round-trip any non-decodable bytes
+        # and still remove illegal XML code points at the Unicode level.
+        s = value.decode('utf-8', errors='surrogatepass')
...
-    if isinstance(value, bytes):
-        return cleaned.encode('utf-8')
+    if isinstance(value, bytes):
+        return cleaned.encode('utf-8', errors='surrogatepass')
```
Why: preserves round-trip of raw bytes while allowing Unicode-level filtering; avoids raising for non-UTF8 byte sequences. Alternatively, document/require UTF‑8 strictly.

### Nits
- Add/adjust the `remove_control_characters` docstring to state exact behavior (allowed chars, input types, encoding expectations).
- Consider adding a small comment in `addons/account/tools/dict_to_xml.py` about why we now pass `str` to the sanitizer (clarifies intent to future readers).
- `None` for other trivial style suggestions.

### Tests & risk
- Relevant tests added/updated: yes — `TestRemoveControlCharacters` in `odoo/addons/test_testing_utilities/tests/test_xml_tools.py`.
- Coverage: Tests cover str/bytes happy paths, allowed controls (`\t\n\r`), lxml assignment, and type errors. Missing: explicit test for non-UTF8 `bytes` behavior and for characters above U+10000 on platforms with different regex behavior (if you want to be exhaustive).
- Risk: medium — this touches a shared XML sanitizer used across export/EDI paths; behavior change is intentional (fixes bug where invalid code points survived). The main operational risk is the bytes-decoding compatibility gap described above.
- Rollback: moderate — revertable change set, but exports/EDI relying on old behavior could break until callers are updated or behavior documented.

### What I checked
- `odoo/tools/xml_utils.py` — confirm Unicode-level regex approach and type-preserving behavior described in PR summary.  
- `addons/account/tools/dict_to_xml.py` — confirm change to pass `str` rather than bytes round-trip.  
- `odoo/addons/test_testing_utilities/tests/test_xml_tools.py` — confirm tests added for str/bytes, allowed controls, lxml assignment, and type errors.  
- Diff not truncated; reviewed the new code and tests in the PR.

---
*Luffy · Hermes Agent · OpenRouter · memory-backed review*
