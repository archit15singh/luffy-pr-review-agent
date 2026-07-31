<!-- luffy-review pr=1 run=30559624590 -->
## 🏴‍☠️ Luffy Review — PR #1

**Verdict:** REQUEST CHANGES  
**Confidence:** high

### Summary
This PR hardens Cloudflare Turnstile form callbacks in addons/website_cf_turnstile/static/src/interactions/turnstile.js by adding safer handling around visibility and validation. The intention is correct and the changes mostly improve robustness, but there is a remaining race that can still throw in the success callback.

### Blocking
- In addons/website_cf_turnstile/static/src/interactions/turnstile.js, the success callback assigned to globalThis[successCbName] (around lines 34–50) does:
  const form = turnstileContainer.closest("form") || turnstileContainer.parentElement;
  If turnstileContainer is null/undefined (e.g. removed or not created due to a race), calling .closest(...) will throw. Please add an early guard to avoid this crash. Example fixes (pick one):
  - Early return:
    if (!turnstileContainer) { return; }
  - Or use optional chaining:
    const form = turnstileContainer?.closest("form") || turnstileContainer?.parentElement;
  This is blocking because it can cause an uncaught exception when the remote script invokes the callback after the DOM changed.

### Suggestions
- Consider checking for existence of inputValidation before calling setAttribute / setting required (defensive), though you already guard presence via if (inputValidation) — this is fine. The primary fix is the turnstileContainer guard described above.
- You already guard turnstileContainer in becomeVisibleCb; mirror that same defensive pattern in the success callback for consistency.
- Minor: script1El is created (line ~58) but never populated/used — either populate or remove to avoid confusion.

### Nits
- Prefer setting styles via element.style.display = 'none' instead of assigning a string to style (line ~70), e.g. inputValidation.style.display = 'none'; (styling string works but is less idiomatic and can overwrite other inline styles).
- Consider scoping the global callbacks more narrowly (or documenting) since they mutate globalThis (throwTurnstileErrorCode and dynamic globalThis[...]) — acceptable here but worth noting for future maintenance.

### Tests & risk
- Coverage: No unit/integration tests included for DOM race conditions. A simple browser test (or JS unit test simulating callback invocation after container removal) would help prevent regressions.
- Risk: low — change is small and focused to avoid a runtime exception, but failing to add the guard leaves a crash possibility.
- Rollback: easy — revert the single-file change.

### What I checked
- File: addons/website_cf_turnstile/static/src/interactions/turnstile.js
  - Inspected constructor and the two global callbacks: globalThis[successCbName] (lines ~34–50) and globalThis[becomeVisibleCbName] (lines ~52–56).
  - Confirmed becomeVisibleCb already guards turnstileContainer; successCb currently does not guard before calling .closest.
- Diff was available and not truncated.

---
*Luffy · Hermes Agent · OpenRouter · memory-backed review*
