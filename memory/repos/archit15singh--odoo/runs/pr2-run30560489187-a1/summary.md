## Review run pr2-run30560489187-a1
- Source: `archit15singh/odoo` PR #2
- Status: success
- Model: openai/gpt-5-mini
- Verdict: REQUEST CHANGES
- Blocking: - Add tests that cover the new `format` alias behavior for both integer and float fields (see suggestions). Currently the new behavior in:   - `addons/web/static/src/views/fields/float/float_field.js` (formatNumber)   - `addons/web/static/src/views/fields/integer/integer_field.js` (extractProps)   is not asserted by tests in this PR.
- Summary: This PR hardens getFieldsSpec to avoid crashes when activeFields references names missing from fields, and accepts the legacy options alias format => enable_formatting for integer/float fields. The changes are small, focused, and accompanied by tests for the getFieldsSpec crash paths.
- Trigger: @luffy review this pr
