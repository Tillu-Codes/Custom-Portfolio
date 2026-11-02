<!-- codeledger:start -->
## CodeLedger - AI decision log (managed section)

This repository uses CodeLedger ("git blame for AI-written code").

1. At the **start of every session**, read `.ledger/CAPSULE.md` for context.
   If it does not exist, run `ledger capsule` to generate it.
2. After **every code change** you make, run `ledger log` and record the
   prompt/model/tool, the files touched, the decision, and every approach
   you considered and rejected. Non-interactive form:
   `ledger log --prompt "..." --model "..." --tool "..." --files a.py
   --decision "..." --rejected "approach::reason"`.
3. **Never repeat an approach listed under "Don't do this again"** in the
   capsule unless an entry explains why the situation has changed.
4. Ship tests together with source changes: the pre-commit hook runs
   `ledger gate` and blocks AI source changes that have no tests. Bypass
   only deliberately with `LEDGER_SKIP_GATE=1` (recorded as "bypassed").
5. The raw log is `.ledger/decisions.jsonl` - one JSON object per line.
<!-- codeledger:end -->
