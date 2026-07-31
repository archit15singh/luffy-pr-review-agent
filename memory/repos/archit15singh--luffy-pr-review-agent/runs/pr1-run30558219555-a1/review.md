<!-- luffy-review pr=1 run=30558219555 -->
## 🏴‍☠️ Luffy Review — PR #1

**Verdict:** REQUEST CHANGES  
**Confidence:** high

### Summary
This PR adds a tiny demo module at demo/hello.py with two functions: greet(name: str) and greet_many(names). The intent is clear, but both functions have correctness and API/typing issues that should be fixed before merging.

### Blocking
- demo/hello.py:greet (lines 3–5) — do not call name.upper() without validating the input. As written it will crash on None and will produce surprising results for non-str inputs. Either:
  - validate the argument and raise a clear TypeError if name is not a str, or
  - explicitly coerce None -> "" if that is the desired behavior. Document the choice in the function docstring/comments.
- demo/hello.py:greet_many (lines 8–12) — add type hints and stop mutating the input list. Current implementation mutates the caller-supplied list (names[i] = ...). Change to return a new list (e.g. list comprehension) and give a precise signature like def greet_many(names: Sequence[str]) -> list[str] or def greet_many(names: Iterable[str]) -> list[str].
- Add unit tests that cover:
  - greet with normal strings, empty string, None (or invalid types) and assert the chosen behaviour,
  - greet_many with an empty list, list containing None (if supported), and confirm the original input is not mutated.
  Tests should be included in the repo (e.g. tests/test_hello.py) and run by CI or `pytest`.

### Suggestions
- For greet, prefer explicit validation:
  - Example behaviour (non-blocking suggestion): raise TypeError("name must be a str") if not isinstance(name, str). This keeps the API consistent with the type annotation.
  - Alternatively, if this is intentionally permissive, coerce with name = "" if name is None, then use name.upper().
- For greet_many, implement without side-effects, e.g.:
  - return [greet(n) for n in names]
  - annotate parameter and return type to make the API clear.
- Add a short docstring for each function describing input expectations and behavior on edge cases.
- Consider adding a simple __main__ demo or a README note if this file is meant to be used for e2e testing, so its intended semantics are explicit.

### Nits
- demo/hello.py: add type hints for greet_many (line 8 comment already notes missing hints).
- The module-level docstring is fine but could mention expected behavior for None/empty strings.
- Minor style: prefer "Hello" capitalization if human-facing, but keep consistent with repo conventions.

### Tests & risk
- Coverage: none present in this PR — demo/hello.py is untested.
- Risk: low — changes are small and confined to a demo module, but the current runtime crash potential (greet(None)) makes it unsafe to merge as-is.
- Rollback: easy — revert the single file change.

### What I checked
- demo/hello.py (full contents)
  - greet at lines 3–5
  - greet_many at lines 8–12
- Diff appears small (1 file, +9/-1); I inspected the full file contents shown in the workspace.

---
*Luffy · Hermes Agent · OpenRouter · memory-backed review*
