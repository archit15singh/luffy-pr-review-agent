<!-- luffy-review pr=2 run=30560489187 -->
## 🏴‍☠️ Luffy Review — PR #2

**Verdict:** REQUEST CHANGES  
**Confidence:** high

### Summary
This PR hardens getFieldsSpec to avoid crashes when activeFields references names missing from fields, and accepts the legacy options alias format => enable_formatting for integer/float fields. The changes are small, focused, and accompanied by tests for the getFieldsSpec crash paths.

### Blocking
- Add tests that cover the new `format` alias behavior for both integer and float fields (see suggestions). Currently the new behavior in:
  - `addons/web/static/src/views/fields/float/float_field.js` (formatNumber)
  - `addons/web/static/src/views/fields/integer/integer_field.js` (extractProps)
  is not asserted by tests in this PR.

### Suggestions
- Add unit tests that assert options={"format": false} (and options={"format": true}) result in the expected boolean for formatNumber/extractProps (both float and integer). This prevents regressions and ensures the legacy alias behaves as intended.
- Consider documenting (or normalizing) how string values are handled for these options. The current code uses Boolean(...) which treats non-empty strings like "false" as truthy. If options can be strings in practice, you may want to parse "False"/"true"/"0"/"1" explicitly (similar to how invisible uses `"True"` / `"1"` checks) so behavior matches expectations in XML/legacy cases.

### Nits
- Minor comment wording consistency: a short note in `float_field.js` / `integer_field.js` explaining the compatibility rationale and a reference to #275937 would help future readers.
- In `getFieldsSpec` (utils.js), consider adding a brief comment where you skip missing fields to say why activeFields can contain absent names (you already do this; maybe add a one-line pointer to the related issue #276570).

### Tests & risk
- Coverage: The PR adds tests covering:
  - `addons/web/static/tests/model/get_fields_spec.test.js` — verifies skipping of missing activeFields and relatedPropertyField handling.
  - Missing: tests for the newly-supported `format` alias in float/integer props.
- Risk: low — changes are narrowly scoped (guarding undefined accesses and adding a compatibility alias). The main risk is behavioral change if XML/legacy input uses string "false" which Boolean("false") will treat as true; add tests to clarify expected behavior.
- Rollback: easy — small, localized changes to a couple of files.

### What I checked
- Diff of getFieldsSpec changes: addons/web/static/src/model/relational_model/utils.js
  - Verified guard for missing `fields[fieldName]` (const field = fields[fieldName]; if (!field) continue;) and downstream use of `field.type`.
  - Verified safe access when building property-linked specs (fields[fieldName]?.definition_record).
- Diff of float field changes: addons/web/static/src/views/fields/float/float_field.js
  - Verified formatNumber IIFE that accepts `options.format` as alias of `enable_formatting`.
- Diff of integer field changes: addons/web/static/src/views/fields/integer/integer_field.js
  - Verified extractProps updated similarly to accept `options.format`.
- New tests: addons/web/static/tests/model/get_fields_spec.test.js
  - Confirmed tests for missing fields and relatedPropertyField skip behavior.
- Note: diff not truncated.

---
*Luffy · Hermes Agent · OpenRouter · memory-backed review*
