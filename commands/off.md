---
description: Disable Hardstop protection temporarily
allowed-tools: ["Bash"]
---

# Disable Hardstop Protection

Temporarily disable the Hardstop pre-execution safety layer.

## Your Task

Run this command to disable protection:

```bash
python "${CLAUDE_PLUGIN_ROOT}/commands/hs_cmd.py" off
```

Then warn the user that dangerous commands will NOT be blocked until they run `/on` again.
