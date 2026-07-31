# Luffy review memory — `archit15singh/odoo`

Cumulative notes from Luffy PR reviews (hub-ingested).

## Review run pr1-run30558836212-a1
- Source: `archit15singh/odoo` PR #1
- Status: success
- Model: openai/gpt-5-mini
- Verdict: REQUEST CHANGES
- Blocking: - Please add a guard for turnstileContainer at the top of the success callback (globalThis[successCbName]). Right now the callback does:   const form = turnstileContainer.closest("form") || turnstileContainer.parentElement;   If turnstileContainer is null/removed before this callback runs, that line will throw. Either:   - return early if turnstileContainer is falsy, or   - use optional chaining when resolving form (e.g. turnstileContainer?.closest(...)).    File / symbol to change: addons/websi
- Summary: This PR hardens the Cloudflare Turnstile callbacks in addons/website_cf_turnstile/static/src/interactions/turnstile.js by guarding against null form/input races and fixes a comment typo (fingerprinting). The changes are small, focused, and move the callbacks toward safer runtime behavior when DOM elements vanish due to races.
- Trigger: @luffy review this pr

## Review run pr1-run30559624590-a1
- Source: `archit15singh/odoo` PR #1
- Status: success
- Model: openai/gpt-5-mini
- Verdict: REQUEST CHANGES
- Blocking: - In addons/website_cf_turnstile/static/src/interactions/turnstile.js, the success callback assigned to globalThis[successCbName] (around lines 34–50) does:   const form = turnstileContainer.closest("form") || turnstileContainer.parentElement;   If turnstileContainer is null/undefined (e.g. removed or not created due to a race), calling .closest(...) will throw. Please add an early guard to avoid this crash. Example fixes (pick one):   - Early return:     if (!turnstileContainer) { return; }   -
- Summary: This PR hardens Cloudflare Turnstile form callbacks in addons/website_cf_turnstile/static/src/interactions/turnstile.js by adding safer handling around visibility and validation. The intention is correct and the changes mostly improve robustness, but there is a remaining race that can still throw in the success callback.
- Trigger: @luffy review this pr

## Review run pr2-run30560489187-a1
- Source: `archit15singh/odoo` PR #2
- Status: success
- Model: openai/gpt-5-mini
- Verdict: REQUEST CHANGES
- Blocking: - Add tests that cover the new `format` alias behavior for both integer and float fields (see suggestions). Currently the new behavior in:   - `addons/web/static/src/views/fields/float/float_field.js` (formatNumber)   - `addons/web/static/src/views/fields/integer/integer_field.js` (extractProps)   is not asserted by tests in this PR.
- Summary: This PR hardens getFieldsSpec to avoid crashes when activeFields references names missing from fields, and accepts the legacy options alias format => enable_formatting for integer/float fields. The changes are small, focused, and accompanied by tests for the getFieldsSpec crash paths.
- Trigger: @luffy review this pr

## Review run pr3-run30572964204-a1
- Source: `archit15singh/odoo` PR #3
- Status: success
- Model: openai/gpt-5-mini
- Verdict: REQUEST CHANGES
- Blocking: - `odoo/tools/xml_utils.py` — bytes decoding handling: If a caller passes `bytes` that are not valid UTF‑8 (for example: legacy Latin‑1 payload, or ill-formed byte sequences), the new implementation will attempt to decode to `str` (presumably with strict UTF‑8) and raise `UnicodeDecodeError`. Trigger scenario: an EDI/export pipeline that previously passed non-UTF-8 bytes into `cleanup_xml_node` / `remove_control_characters` will now raise and fail the export. Either: 1) explicitly document and e
- Summary: This PR replaces a broken bytes-based regex approach with a Unicode-aware sanitizer for XML illegal chars (`odoo/tools/xml_utils.py`), makes `remove_control_characters` preserve input type (str/bytes), updates `addons/account/tools/dict_to_xml.py` to pass strings, and adds regression tests in `odoo/addons/test_testing_utilities/tests/test_xml_tools.py`. Implementation and tests look solid for the common UTF‑8 paths and the explicit allowed controls (`\t\n\r`) are preserved. There is one important compatibility/behavioral gap around how `bytes` inputs are decoded and one portability edge worth addressing before merge.
- Trigger: @luffy review this pr

Complex fix for odoo/odoo#271153 — Unicode-level XML Char sanitizer, dict_to_xml str path, regression tests. Please deep-review correctness, encoding edge cases, and test covera

## Review 2026-07-30T19:22:59Z · archit15singh/odoo PR #3 · [FIX] tools: strip non-XML characters at Unicode level (#271153)

- Verdict: REQUEST CHANGES
- Blocking notes: - **`odoo/tools/xml_utils.py` — `errors='surrogatepass'` cannot decode non-UTF-8 bytes and breaks `cleanup_xml_node`.** `surrogatepass` only permits *already-encoded lone surrogates* (the `\xed\xa0\x80` form); it does **not** tolerate arbitrary invalid bytes. The codec you want is `surrogateescape`. Trigger scenario: a partner sends a Latin-1/Windows-1252 encoded EDI/UBL document and any addon calls `cleanup_xml_node(payload_bytes)` (8 call sites in tree). Reproduced on this workspace:; - **`odoo/addons/test_testing_utilities/tests/test_xml_tools.py` — `test_non_utf8_bytes_do_not_raise` fails against the code in this same PR.** I executed the new function against the exact test input: `remove_control_characters('café'.encode('latin-1'))` raises `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3: unexpected end of data`. The other 5 tests in the class pass. CI on this branch should be red — please confirm it was actually run, because a self-contradicting test suggests the `surrogatepass` claim was assumed rather than executed.; - **Naive `surrogateescape` swap silently destroys data — the surrogate range must be preserved through the filter.** Worth calling out so the fix isn't half-done: if you only change the codec, the `\udc80-\udcff` escapes land outside the allowed `Char` class and get stripped, turning `Société` into `Socit`. Verified: `surrogateescape` + unmodified regex yields `b'<Inv><Party>Socit</Party></Inv>'`. See the code suggestion below for the version I tested that round-trips byte-identically.
- (Auto-distilled; refine manually if needed)

