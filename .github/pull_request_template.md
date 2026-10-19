## Why
<!-- What problem does this solve, or what need does it meet? -->

## What
<!-- Summary of the changes. Bullets are fine. -->

## Risk
<!-- What could break? Who would be affected? -->

## Review focus
<!-- Which files/areas should the reviewer look at most closely?
     Always list anything marked "Unrequested" in the commits. -->

## Testing
<!-- What was run or checked, and the result. Be honest about gaps. -->

---

### Reviewer checklist
- [ ] Changes match what was asked; no unexplained extra changes
- [ ] No hardcoded local paths, usernames, or machine-specific settings
- [ ] No secrets, credentials, or client/personal data
- [ ] Dependency changes (if any) are intentional and in the dependency file
- [ ] Logic makes sense for edge cases (empty input, missing values, odd formats)
- [ ] Outputs were sanity-checked, not just "it ran"
- [ ] CHANGELOG.md updated if users will notice the change
