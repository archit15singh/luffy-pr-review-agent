## 🏴‍☠️ Luffy Review — PR #3

**Verdict:** REQUEST CHANGES
**Confidence:** high
**Score:** 42/100
**Review effort:** 4/5

### Summary
The diagnosis in this PR is correct and valuable: the old `remove_control_characters` encoded a Unicode character class with `.encode()` and applied it as a **bytes** regex, which collapsed multi-byte ranges and let `U+FFFE`/`U+FFFF` survive into lxml. The new `str` path in `odoo/tools/xml_utils.py` genuinely fixes that, and `addons/account/tools/dict_to_xml.py` is correctly simplified. However, the new **bytes** path uses `errors='surrogatepass'`, which does *not* do what the code comment claims — it raises `UnicodeDecodeError` on exactly the legacy non-UTF-8 EDI payloads it says it protects. I reproduced this locally: it introduces a hard regression in `cleanup_xml_node`, and the PR's own new test `test_non_utf8_bytes_do_not_raise` fails. Not mergeable as-is; the `str` half is good and the `bytes` half needs a one-line codec change.

### Walkthrough
- `odoo/tools/xml_utils.py` / `_XML_ILLEGAL_CHAR_RE`: module-level precompiled negated XML 1.0 `Char` class, no longer `.encode()`d. Verified correct — strips `U+FFFE`/`U+FFFF`/`NUL`, preserves `\t\n\r`.
- `odoo/tools/xml_utils.py` / `remove_control_characters`: now type-dispatching; `str` → filter directly; `bytes`/`bytearray`/`memoryview` → decode with `surrogatepass`, filter, re-encode; anything else → `TypeError`.
- `remove_control_characters` added to `__all__`, making it public API.
- `addons/account/tools/dict_to_xml.py`: drops the `encode()→scrub→decode()` dance and passes `str` straight through. Correct.
- `odoo/addons/test_testing_utilities/tests/test_xml_tools.py`: new `TestRemoveControlCharacters` with 6 tests covering str/bytes, allowed controls, lxml assignment, `TypeError`, and non-UTF-8 bytes.

### Blocking
- **`odoo/tools/xml_utils.py` — `errors='surrogatepass'` cannot decode non-UTF-8 bytes and breaks `cleanup_xml_node`.** `surrogatepass` only permits *already-encoded lone surrogates* (the `\xed\xa0\x80` form); it does **not** tolerate arbitrary invalid bytes. The codec you want is `surrogateescape`. Trigger scenario: a partner sends a Latin-1/Windows-1252 encoded EDI/UBL document and any addon calls `cleanup_xml_node(payload_bytes)` (8 call sites in tree). Reproduced on this workspace:
  ```
  payload = '<?xml version="1.0" encoding="ISO-8859-1"?><Inv><Party>Société</Party></Inv>'.encode('latin-1')
  OLD (base 19.0): b'<Inv><Party>Soci&#233;t&#233;</Party></Inv>'   # works
  NEW (this PR):   UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 59: invalid continuation byte
  ```
  lxml's `recover=True` parser handles the declared `ISO-8859-1` encoding fine today; this PR makes it die before lxml is ever reached. That is a straight functional regression on the sanitizer's primary caller.
- **`odoo/addons/test_testing_utilities/tests/test_xml_tools.py` — `test_non_utf8_bytes_do_not_raise` fails against the code in this same PR.** I executed the new function against the exact test input: `remove_control_characters('café'.encode('latin-1'))` raises `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3: unexpected end of data`. The other 5 tests in the class pass. CI on this branch should be red — please confirm it was actually run, because a self-contradicting test suggests the `surrogatepass` claim was assumed rather than executed.
- **Naive `surrogateescape` swap silently destroys data — the surrogate range must be preserved through the filter.** Worth calling out so the fix isn't half-done: if you only change the codec, the `\udc80-\udcff` escapes land outside the allowed `Char` class and get stripped, turning `Société` into `Socit`. Verified: `surrogateescape` + unmodified regex yields `b'<Inv><Party>Socit</Party></Inv>'`. See the code suggestion below for the version I tested that round-trips byte-identically.

### Key findings

| Severity | File | Issue | Trigger scenario |
|----------|------|-------|------------------|
| critical | `odoo/tools/xml_utils.py` | `surrogatepass` raises `UnicodeDecodeError` on non-UTF-8 bytes | `cleanup_xml_node()` on a Latin-1/CP1252 EDI or UBL payload — worked on `19.0`, now hard-fails before lxml's `recover=True` parser sees it |
| high | `odoo/addons/test_testing_utilities/tests/test_xml_tools.py` | `test_non_utf8_bytes_do_not_raise` fails against this PR's own implementation | Run `TestRemoveControlCharacters`; the `'café'.encode('latin-1')` case errors out |
| medium | `odoo/tools/xml_utils.py` | Stripping the surrogate range after a `surrogateescape` decode silently deletes accented characters | Applies to the obvious one-line fix for the above; `Société` → `Socit`, silent data loss on invoice party names |
| low | `odoo/tools/xml_utils.py` | Docstring promises "returns the **same type**" but `bytearray`/`memoryview` return `bytes` | Caller passes a `bytearray` buffer and relies on the documented contract; confirmed `bytearray` in → `bytes` out |

### Security audit
`No` — no injection, secrets, XSS, or authz concerns. `resolve_entities=False` is untouched, so XXE posture is unchanged, and the sanitizer becomes strictly *more* aggressive on the `str` path. Note the availability angle though: an attacker-influenced non-UTF-8 attachment can now trigger an unhandled `UnicodeDecodeError` in an EDI import path that previously degraded gracefully — a DoS-flavoured regression rather than a new vulnerability class.

### Suggestions
- Add a regression test that goes through `cleanup_xml_node` with a Latin-1 encoded XML document, not just `remove_control_characters` in isolation. The blocking bug lives at that boundary and the current unit-level tests would not have caught it even had they passed.
- Consider asserting byte-identity for the non-UTF-8 path (`assertEqual(clean, dirty)`) rather than only `assertIsInstance(..., bytes)` — the weaker assertion would still pass a version that silently strips accents.
- Since `remove_control_characters` is now in `__all__`, a one-line note in the docstring that the `bytes` path is lossless for undecodable bytes would help downstream addon authors.

### Code suggestions

#### Use `surrogateescape` and preserve the escape range through the filter (`odoo/tools/xml_utils.py`)
```diff
+# Lone surrogates U+DC80-U+DCFF are the `surrogateescape` representation of
+# undecodable bytes; they must survive the filter so non-UTF-8 input can be
+# re-encoded byte-identically. They can never appear in valid UTF-8 text.
+_XML_ILLEGAL_CHAR_RE_BYTES = re.compile(
+    '[^'
+    '\u0009\u000A\u000D'
+    '\u0020-\uD7FF'
+    '\uDC80-\uDCFF'          # surrogateescape placeholders
+    '\uE000-\uFFFD'
+    '\U00010000-\U0010FFFF'
+    ']'
+)
+
     if isinstance(byte_node, (bytes, bytearray, memoryview)):
         raw = bytes(byte_node)
-        # UTF-8 with surrogatepass: round-trip any byte sequence while still
-        # filtering illegal XML code points at the Unicode level. Strict
-        # UTF-8 would raise UnicodeDecodeError on legacy Latin-1 EDI bytes.
-        text_ = raw.decode('utf-8', errors='surrogatepass')
-        return _XML_ILLEGAL_CHAR_RE.sub('', text_).encode('utf-8', errors='surrogatepass')
+        # `surrogateescape` (not `surrogatepass`) is what tolerates arbitrary
+        # non-UTF-8 bytes; it maps them to lone surrogates that re-encode
+        # byte-for-byte, so legacy Latin-1 EDI payloads pass through unharmed
+        # while illegal XML code points are still stripped.
+        text_ = raw.decode('utf-8', errors='surrogateescape')
+        return _XML_ILLEGAL_CHAR_RE_BYTES.sub('', text_).encode('utf-8', errors='surrogateescape')
```
Why: `surrogatepass` raises on invalid bytes (verified), and keeping `U+DC80-U+DCFF` in the class is what stops the accent-eating data loss — I tested this exact version and the Latin-1 EDI document parses to `b'<Inv><P>Soci&#233;t&#233;</P></Inv>'` with `remove_control_characters('café'.encode('latin-1')) == 'café'.encode('latin-1')` byte-identical, while `U+FFFE`/`U+FFFF`/`NUL` are still stripped.

#### Cover the real regression surface (`odoo/addons/test_testing_utilities/tests/test_xml_tools.py`)
```diff
     def test_non_utf8_bytes_do_not_raise(self):
         # Latin-1 high bytes must not crash the sanitizer (EDI edge case).
         dirty = "café".encode("latin-1")  # b'caf\xe9'
         clean = remove_control_characters(dirty)
         self.assertIsInstance(clean, bytes)
-        # Result is still valid UTF-8 after surrogatepass round-trip.
-        clean.decode("utf-8")
+        # Undecodable bytes are preserved verbatim, not silently dropped.
+        self.assertEqual(clean, dirty)
+
+    def test_cleanup_xml_node_accepts_latin1_document(self):
+        payload = (
+            '<?xml version="1.0" encoding="ISO-8859-1"?>'
+            '<Inv><Party>Société</Party></Inv>'
+        ).encode("latin-1")
+        node = cleanup_xml_node(payload, indent_level=-1)
+        self.assertEqual(node.find("Party").text, "Société")
```
Why: the current assertion (`clean.decode("utf-8")`) both fails today and would still pass a lossy implementation, and nothing in the suite exercises the `cleanup_xml_node` boundary where the regression actually bites.

### Nits
- Stray double blank line introduced between `remove_control_characters` and `class odoo_resolver` (three blank lines total) — trivial, but it's in the diff.
- The parameter name `byte_node` is now misleading since `str` is the primary supported input; `node` or `value` would read better. Not worth a re-push on its own.

### Tests & risk
- Relevant tests added/updated: **yes** — but one of them fails against the implementation in the same PR.
- Coverage: good on the `str` path (`U+FFFE`/`U+FFFF`/`NUL` stripping, `\t\n\r` preservation, lxml assignment, `TypeError`). Gaps on the risky paths: nothing exercises `cleanup_xml_node` with bytes, which is the only in-tree consumer of the changed branch, and the non-UTF-8 assertion is both broken and too weak to catch silent data loss.
- Risk: **high** — shared sanitizer on EDI/UBL/export paths, and the bytes branch regresses a case that works on `19.0` today. Once the codec is fixed and the surrogate range preserved, risk drops to low/medium; the `str`-path behavior change (previously-kept illegal chars now stripped) is intentional and correct.
- Rollback: **easy** — three self-contained files, no schema or data migration.

### What I checked
- Full diff (not truncated, 6377 bytes) across all 3 files.
- `odoo/tools/xml_utils.py`: `_XML_ILLEGAL_CHAR_RE`, `remove_control_characters`, `__all__`, and the `cleanup_xml_node` call site that feeds `etree.fromstring(remove_control_characters(xml_node), parser=parser)` with `recover=True, resolve_entities=False`.
- `addons/account/tools/dict_to_xml.py` around the `element.text` assignment.
- All 6 new tests in `TestRemoveControlCharacters`, executed against the PR's real `remove_control_characters` (loaded in isolation with stubbed odoo imports): 5 pass, `test_non_utf8_bytes_do_not_raise` errors with `UnicodeDecodeError`.
- Empirically compared old vs. new behavior with `lxml` 6.1.1 installed: confirmed the old bytes regex left `b'a\xef\xbf\xbeb'` (the reported bug is real), confirmed `surrogatepass` raises on `b'caf\xe9'`/`b'\xff\xfe'`/`b'ok\x80bad'`, confirmed the Latin-1 XML document regression through `etree.fromstring`, and validated that `surrogateescape` + a surrogate-preserving class round-trips byte-identically while still stripping `U+FFFE`/`U+FFFF`/`NUL`.
- Grepped all 8 `cleanup_xml_node` and all `remove_control_characters` call sites to scope blast radius.

---
*Luffy · Hermes Agent · OpenRouter · memory-backed review*
