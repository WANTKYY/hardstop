# Changelog

All notable changes to Hardstop will be documented in this file.

## [1.0.0] - 2025-01-17

First public release.

### Core Features
- **Two-layer defense** — Pattern matching (instant) + LLM analysis (semantic)
- **Fail-closed design** — If safety check fails, command is blocked (not allowed)
- **Cross-platform** — Unix (Bash) + Windows (PowerShell) pattern detection
- **Command chaining** — Analyzes all parts of piped/chained commands (`&&`, `||`, `;`, `|`)
- **Audit logging** — All decisions logged to `~/.hardstop/audit.log`
- **Skill command** — `/hs` for status, on/off, skip, and log viewing

### Pattern Coverage
- Home/root deletion, fork bombs, reverse shells
- Credential exfiltration (`.ssh`, `.aws`, `.config`)
- Disk destruction, encoded payloads, pipe-to-shell
- Windows: Registry manipulation, LOLBins, PowerShell download cradles

### Installation
- `install.sh` for macOS/Linux
- `install.ps1` for Windows (uses Python for reliable JSON handling)
- `uninstall.sh` and `uninstall.ps1` for clean removal
- Automatic hook configuration in `~/.claude/settings.json`
- Skill installation to `~/.claude/skills/hs/`

### Reliability
- Atomic state writes (prevents corruption)
- Atomic skip flag (prevents race conditions)
- Windows CLI detection (`claude.cmd` via `cmd /c`)
- Full-command matching for safe patterns (prevents substring bypass)
- Path expansion at install time (fixes `~` not working on Windows)

---

## Development History (Pre-release)

The following documents the development process leading to v1.0.0.

### 2025-01-17 — Final Polish

**Bug Fixes:**
- Fixed PowerShell JSON handling (ConvertFrom-Json fails on nested objects; now uses Python)
- Fixed path expansion (`~` and `%USERPROFILE%` don't expand in Windows hook commands)
- Fixed skill directory name (`hs` not `hs-hardstop-plugin` — directory name = command name)
- Fixed double naming bug (`hs-hardstop-plugin-hardstop-plugin`)

**Improvements:**
- Added uninstall scripts (`uninstall.ps1`, `uninstall.sh`)
- Added uninstall detection in hook with friendly confirmation message
- Added strong restart warnings for VS Code, CLI, and Cowork users
- Added beta disclaimer and feedback call-to-action
- Cleaned up `/hardstop` and `/hard` alias references (kept only `/hs`)

**Lessons Learned:**
1. Directory name = skill command name (not the `name` field in SKILL.md)
2. `aliases` field in SKILL.md doesn't create additional slash commands
3. `~` doesn't expand in Windows hook commands — must use full paths
4. `%USERPROFILE%` also doesn't expand — use Python `os.path.expanduser()`
5. PowerShell's `ConvertFrom-Json | ConvertTo-Json` breaks nested objects
6. Hooks are snapshotted at startup — restart required after changes
7. Hardstop can block its own uninstall — need skip or custom detection

### 2025-01-16 — Structure Refactor

- Changed plugin name from "hardstop" to "hs" in plugin.json
- Improved Windows console encoding handling in hs_cmd.py
- Added debug logging for hook invocation
- Created command documentation files (`hs.md`, `on.md`, `off.md`, `skip.md`, `status.md`, `log.md`)
- Updated installation scripts for new structure

### 2025-01-15 — Initial Development

- Implemented two-layer defense (pattern + LLM)
- Created pattern databases for Unix and Windows
- Implemented fail-closed error handling
- Added command chaining analysis
- Created `/hs` skill interface
- Added audit logging system
- Wrote test suite (82 tests)

---

## License

CC BY 4.0 — Francesco Marinoni Moretto
