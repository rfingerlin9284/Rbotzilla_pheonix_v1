# Strategy Protection Addendum

## IMMUTABLE RULE: Strategy Configuration Lock

**Effective Date:** December 1, 2025
**Applies To:** All Automated Agents, AI Assistants, and Sub-Systems

### 1. The Rule
No automated agent is permitted to:
- **Add** new strategies to `PhoenixV2/config/strategies.json`.
- **Disable** (turn off) existing strategies in `PhoenixV2/config/strategies.json`.
- **Modify** the parameters of existing strategies in `PhoenixV2/config/strategies.json`.

**WITHOUT EXPLICIT USER APPROVAL.**

### 2. The Mechanism
The `PhoenixV2/config/strategies.json` file now contains a `configuration_locked` flag.
- If `"configuration_locked": true`, the system is in **PROTECTED MODE**.
- Any attempt by an agent to modify the strategy list while this flag is true is a violation of this charter.

### 3. Enforcement
The `WolfPack` engine will respect this lock. While the engine itself reads the file, this document serves as the **primary directive** for any AI agent interacting with the codebase.

**YOU MUST ASK FOR PERMISSION BEFORE CHANGING THE STRATEGY CONFIGURATION.**
