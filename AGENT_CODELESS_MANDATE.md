# 🤖 AGENT CODELESS MANDATE (THE ADDENDUM)

**To the AI Assistant (GitHub Copilot):**

The user has explicitly requested a "Codeless Control" workflow. You are strictly forbidden from manually editing configuration files or running complex terminal commands on the user's behalf without first offering a reusable, interactive tool.

## 📜 THE RULES

1.  **Check the Registry First:**
    Before taking any action, check `CODELESS_CONTROL_REGISTRY.md`. Is there already a task for this?
    *   **YES:** Tell the user to run it. (e.g., "Please run the 'Adjust Settings' task.")
    *   **NO:** Proceed to Rule 2.

2.  **Create, Don't Just Do:**
    If the user asks for something new (e.g., "Lower the confidence threshold"), **DO NOT** just edit the code.
    *   **Step A:** Create a Python script in `scripts/` that performs the action interactively (asking for user input).
    *   **Step B:** Register this script as a VS Code Task in `.vscode/tasks.json`.
    *   **Step C:** Add the new task to `CODELESS_CONTROL_REGISTRY.md`.
    *   **Step D:** Tell the user: "I've created a new task called '[Task Name]' for you. You can run it now to adjust that setting."

3.  **Maintain the Registry:**
    You are responsible for keeping `CODELESS_CONTROL_REGISTRY.md` up to date. It is the user's manual.

4.  **Remember the User is NOT a Coder:**
    *   Do not ask them to edit JSON.
    *   Do not ask them to run `sed` commands.
    *   Do not ask them to remember flags.
    *   **DO** give them a simple menu or a single button click.

## 📝 Example Scenario

**User:** "Hey, change the max trades to 5."

**❌ Bad Response:** "Okay, I edited `charter.py` and changed `MAX_CONCURRENT_POSITIONS` to 5."

**✅ Good Response:** "I have a task for that. Please run the **'Adjust Settings'** task from the menu. It will ask you for the new number, and you can type '5'."

---
*This file is your instruction manual for interacting with this specific user.*
