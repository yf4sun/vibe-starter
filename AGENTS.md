# AGENTS.md

Instructions for AI coding assistants (Claude Code, Copilot, Cursor, Codex, etc.)
working in this repository. Humans should read this too.

---

## Project overview

<!-- Fill this in for each project. Keep it short. -->

- **Purpose:** <what this tool does and who uses it>
- **Owner:** <name / team>
- **Language(s):** <e.g. Python 3.11>
- **How to run:** <command, e.g. `python main.py --input data.csv`>
- **How to test:** <command, or "manual: run on files in /samples">
- **Key folders:**
  - `src/` – <what lives here>
  - `tests/` – <what lives here>
  - `samples/` – <test inputs, no real/client data>

### Things that must not change without discussion

<!-- e.g. output file format other tools depend on, config file names, public function signatures -->
- <item>

---

## Working rules

1. **Stay in scope.** Only change what was asked. If you think something else
   should change (refactors, renames, dependency upgrades, formatting sweeps),
   suggest it and wait for approval rather than doing it.
2. **Small steps.** Make one logical change at a time. When a change works,
   commit it before starting the next one.
3. **Never commit secrets.** No passwords, API keys, tokens, connection strings,
   or personal/client data in code, config, sample files, or commit messages.
   Use environment variables or a git-ignored config file instead.
4. **No silent dependency changes.** If you add, remove, or upgrade a package,
   say so explicitly and update the dependency file (`requirements.txt`,
   `pyproject.toml`, `package.json`, etc.).
5. **Explain anything non-obvious.** If code exists to work around a specific
   problem (a quirk in another tool, a known bug, an odd data format), leave a
   short comment saying why.
6. **Update the changelog** for any change a user of the tool would notice
   (see below).

---

## Commit messages

Every commit must follow this format. When asked to commit, write the message
yourself using the full context of the session.

```
<Summary line: imperative, under 72 characters>

Goal: <what problem this solves or what it adds, in plain language>

Prompt: <short summary of what the user asked for; paraphrase, do not paste
long transcripts>

Changes: <what was changed, briefly>

Unrequested: <anything changed that the user did NOT ask for, or "None">

Tested: <what was actually run or checked, and the result>
Not tested: <known gaps, or "None known">

Assisted-by: <AI tool name, e.g. Claude Code>
```

### Rules for commit messages

- **The `Unrequested` line is mandatory.** If you refactored, reformatted,
  renamed, or touched any file beyond the request, list it here. If nothing,
  write `None`.
- **Be honest in `Tested`.** "Not run" is an acceptable answer. Never claim
  something was tested if it wasn't.
- **Scrub the prompt summary.** Remove file paths containing usernames, client
  names, pasted credentials, and personal data. Summarize rather than quote
  when in doubt.
- **Summarize long sessions.** If the work took many prompts, describe the
  final intent, not every step.
- **One logical change per commit.** If a message needs two unrelated `Goal`
  lines, it should be two commits.

### Example

```
Handle locked Excel files during export

Goal: Export crashed with PermissionError when the output file was
open in Excel. It now warns the user and saves a timestamped copy.

Prompt: User asked to stop the crash when the Excel file is open and
save somewhere else instead, with a message to the user.

Changes: Added try/except around workbook save in export.py; new
helper make_fallback_path().

Unrequested: Moved logging setup into its own function (logging_setup.py).

Tested: Exported with output file open and closed; both succeeded.
Not tested: Network drive paths.

Assisted-by: Claude Code
```

---

## Changelog

For user-visible changes, add an entry to the top of `CHANGELOG.md` in plain
language that a non-programmer can understand:

```
## [1.3.0] - YYYY-MM-DD
### Fixed
- Export no longer crashes if the output file is open in Excel; it saves a copy instead.
```

Use the headings `Added`, `Changed`, `Fixed`, `Removed`. Internal-only changes
(refactors, test updates) do not need a changelog entry.

---

## Pull requests

When preparing a pull request description, include:

- **Why:** the problem or need behind the change
- **What:** a summary of the commits
- **Risk:** what could break, and who would be affected
- **Review focus:** which files or areas a reviewer should look at most closely
  (always include anything listed under `Unrequested` in the commits)
- **Testing:** what was tested overall
