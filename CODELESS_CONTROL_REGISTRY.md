# 🎛️ CODELESS CONTROL REGISTRY

**"I don't want to code. I want to control."**

This document is the central registry for all "Codeless" control mechanisms in the RICK Phoenix V2 system. 
**Agent Mandate:** If the user asks to change a setting or perform an action, check this list first. If a tool exists, tell the user to run it. If not, create the tool, add it here, and THEN tell the user to run it.

---

## 🚀 1. Start & Stop System

| Action | Command / Task | Description |
| :--- | :--- | :--- |
| **Start System** | `Start Phoenix` (Task) | Launches the full system (Orchestrator, Surgeon, etc.) |
| **Stop System** | `Stop Phoenix` (Task) | Safely shuts down all processes. |
| **Restart System** | `Force Restart` (Task) | Kills everything and starts fresh. |

## ⚙️ 2. Configuration & Tuning

| Action | Command / Task | Description |
| :--- | :--- | :--- |
| **Adjust Settings** | `Adjust Settings` (Task) | **Interactive Menu** to change Max Positions, Confidence, Sharpe Ratio. |
| **Toggle WolfPack** | `Toggle WolfPack` (Task) | Enable/Disable specific strategies without code. |
| **Approve Strategy** | `Approve Strategy` (Task) | Manually approve a strategy for live trading. |

## 📺 3. Monitoring & Visibility

| Action | Command / Task | Description |
| :--- | :--- | :--- |
| **Live Narration** | `Rick Narration Stream` (Task) | Real-time "Play-by-Play" of what the bot is doing. |
| **System Status** | `Monitor Status` (Task) | Quick health check of all components. |
| **Ask Rick** | `Ask Rick` (Task) | Plain English interface to query the system state. |

## 🛠️ 4. Maintenance & Repair

| Action | Command / Task | Description |
| :--- | :--- | :--- |
| **Snapshot Memory** | `Snapshot Memory` (Task) | Backup the current state of the AI memory. |
| **Run Diagnostics** | `Run Diagnostics` (Task) | Check for broken connections or errors. |

---

## 🤖 Agent Instructions (The "Addendum")

**To the AI Assistant:**

1.  **Never** manually edit `charter.py` or config files unless the user explicitly forbids scripts.
2.  **Always** direct the user to the `Adjust Settings` task for tuning.
3.  **If a requested action has no script:**
    *   **STOP.** Do not just do it.
    *   **CREATE** a script in `scripts/` that performs the action interactively.
    *   **REGISTER** the script in `.vscode/tasks.json`.
    *   **UPDATE** this file (`CODELESS_CONTROL_README.md`).
    *   **TELL** the user: "I've created a new task for that. Run 'Task Name' to do it."

---
*Last Updated: December 2, 2025*
