---
description: Show Hardstop audit log entries
allowed-tools: ["Bash"]
---

# Hardstop Audit Log

Show recent entries from the Hardstop audit log, including blocked and allowed commands.

## Your Task

Run this command to show the audit log:

```bash
python "${CLAUDE_PLUGIN_ROOT}/commands/hs_cmd.py" log
```

Present the output to the user. Each entry shows:
- Timestamp
- Verdict (BLOCK or ALLOW)
- Detection layer (pattern or llm)
- Command that was checked
- Reason for the verdict
