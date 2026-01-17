# 🛑 Hardstop

**The Emergency Brake for Claude Code, Claude Desktop & Cowork.**

Hardstop is a defense-in-depth safety layer that catches dangerous commands before they execute: even when soft guardrails fail.

![Version](https://img.shields.io/badge/version-1.0.0--beta-orange) ![License](https://img.shields.io/badge/license-CC_BY_4.0-blue) ![Platform](https://img.shields.io/badge/platform-macOS_%7C_Linux_%7C_Windows-lightgrey)

[Installation](#-installation) • [How It Works](#%EF%B8%8F-how-it-works) • [Commands](#%EF%B8%8F-controls) • [Report Issue](https://github.com/frmoretto/hardstop/issues)

---

## ⚡️ Why Hardstop?

You trust your AI, but you shouldn't trust it with `rm -rf /`. Hardstop sits between the LLM and your terminal, enforcing a strict **Fail-Closed** policy on dangerous operations.

- **🛡️ Pattern Matching:** Instant regex-based detection for known threats (fork bombs, reverse shells)
- **🧠 LLM Analysis:** Semantic analysis for edge cases and obfuscated attacks
- **⛓️ Chain Awareness:** Scans every link in a command chain (`&&`, `|`, `;`)

---

## 🚀 Quick Demo

Claude tries to ruin your day? **Hardstop says no.**

```bash
# Claude attempts a home directory deletion
$ rm -rf ~/
🛑 BLOCKED: Deletes home directory

# You check the status
$ /hs status
Hardstop v1.0.0
  Status:      🟢 Enabled
  Fail mode:   Fail-closed

# One-time bypass for a command you trust
$ /hs skip
⏭️  Next command will skip safety check

# View recent security decisions
$ /hs log
2025-01-15 10:30:45 🛑 [pattern] rm -rf ~/
                     └─ Deletes home directory
```

---

## ⚙️ How It Works

Hardstop uses a two-layer verification system to ensure speed and safety.

```mermaid
graph TD
    A[Command Arrives] --> B{Layer 1: Patterns};
    B -- Dangerous Pattern --> C[🛑 BLOCK];
    B -- Safe Pattern --> D[✅ ALLOW];
    B -- Unknown --> E{Layer 2: LLM Analysis};
    E -- Risky --> C;
    E -- Safe --> D;
    C --> F[Log to Audit];
    D --> G[Execute Command];
```

---

## 📦 Installation

### macOS / Linux

```bash
git clone https://github.com/frmoretto/hardstop.git && cd hardstop && ./install.sh
```

### Windows

```powershell
git clone https://github.com/frmoretto/hardstop.git
cd hardstop
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Verify

**Restart Claude Code / Desktop / Cowork**, then:

```
/hs status
```

---

## 🕹️ Controls

Control Hardstop directly from the chat prompt.

| Command | Action |
|---------|--------|
| `/hs on` | Enable protection (Default) |
| `/hs off` | Disable temporarily |
| `/hs skip` | Bypass checks for the very next command only |
| `/hs status` | Check system health |
| `/hs log` | View recent security decisions |

---

## 🛡️ Protection Scope

<details>
<summary><strong>🐧 Unix (macOS/Linux) Triggers</strong></summary>

- **Annihilation:** `rm -rf ~/`, `rm -rf /`, `mkfs`, `shred`
- **Malware:** Fork bombs, Reverse shells (`/dev/tcp`, `nc -e`)
- **Theft:** Exfiltration via `curl`/`wget` of `.ssh`, `.aws` credentials
- **Trickery:** Encoded payloads, Pipe-to-shell (`curl | bash`)
- **System damage:** `chmod 777 /`, recursive permission changes
- **Dangerous sudo:** `sudo rm -rf /`, `sudo dd`

</details>

<details>
<summary><strong>🪟 Windows Triggers</strong></summary>

- **Destruction:** `rd /s /q`, `format C:`, `bcdedit /delete`
- **Registry:** `reg delete HKLM`, Persistence via Run keys
- **Credential theft:** `mimikatz`, `cmdkey /list`, SAM database access
- **Download cradles:** PowerShell IEX, `certutil`, `bitsadmin`, `mshta`
- **Encoded payloads:** `powershell -e <base64>`
- **Privilege escalation:** `net user /add`, `net localgroup administrators`

</details>

---

## 📋 Audit Logging

All decisions are logged to `~/.hardstop/audit.log` in JSON-lines format:

```json
{"timestamp": "2025-01-15T10:30:45", "version": "1.0.0", "command": "rm -rf ~/", "cwd": "/home/user", "verdict": "BLOCK", "reason": "Deletes home directory", "layer": "pattern"}
```

View recent entries with `/hs log`.

---

## 📁 State Files

| File | Purpose |
|------|---------|
| `~/.hardstop/state.json` | Enabled/disabled state |
| `~/.hardstop/skip_next` | One-time bypass flag |
| `~/.hardstop/audit.log` | Decision audit log |

---

## ⚠️ Beta Disclaimer

**This is v1.0.0-beta.** Hardstop is a robust safety net, but it is **not a guarantee**.

- Sophisticated obfuscation may bypass detection
- Always review commands before execution
- Use at your own risk

---

## 🤝 Community & Feedback

Found a bypass? Have a new pattern? Ideas for improvement?

[Report an Issue](https://github.com/frmoretto/hardstop/issues) • [View License](LICENSE) • **Author:** Francesco Marinoni Moretto
