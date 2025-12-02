# AI Agent Mandate: Visual Blueprint Generation Protocol

**Status:** MANDATORY - All AI agents working in R_H_UNI must follow this protocol  
**Effective Date:** October 10, 2025  
**Authority:** Project Owner Directive  
**Scope:** All work within `/home/ing/RICK/R_H_UNI/` and subdirectories

---

## 🎨 MANDATORY VISUAL BLUEPRINT REQUIREMENT

### When To Generate Blueprint

**TRIGGER EVENTS (Auto-generate blueprint after any of these):**

1. ✅ **Major integration complete** (ML models, new connectors, strategy modules)
2. ✅ **Structural changes** (new directories, renamed modules, reorganized code)
3. ✅ **Before extraction/deployment** (creating RICK_LIVE_DEPLOYMENT packages)
4. ✅ **Milestone completion** (Phase X complete, canary promotion, live activation)
5. ✅ **User explicitly requests** ("show me the blueprint", "visualize the system")
6. ✅ **Every 10 completed tasks** (check COMPLETED_TASKS/README.md)

---

## 📐 Blueprint Specification

### Required Format

- **File Type:** PNG image (high resolution, 300 DPI minimum)
- **Dimensions:** 1920x1080 minimum, scalable to 4K
- **Color Scheme:** 
  - Background: Dark (#0a0e27 - matches cyber dashboard)
  - Active Modules: **Green (#00ff41)** with glow effect
  - Inactive/Legacy: Gray (#404040)
  - Connections: Cyan (#00d4ff) arrows
  - Text: White (#ffffff) with drop shadow
- **Layout:** Hierarchical flowchart with clear node groupings

### Required Elements

Each blueprint MUST include:

1. **Header Section**
   - Project name: "RICK (RBOTzilla UNI)"
   - Date generated
   - System mode (Ghost/Canary/Live)
   - Total files indexed
   - Git branch + commit hash

2. **Color-Coded Nodes**
   - **GREEN nodes** = Active/Operational modules
   - **GRAY nodes** = Legacy/Inactive code
   - **YELLOW nodes** = In development/Testing
   - **RED nodes** = Critical/Safety systems

3. **Per-Node Information**
   ```
   [NODE: Foundation Layer]
   Color: GREEN
   ────────────────────────────
   Files:
   • rick_charter.py - PIN 841921 enforcement
   • immutable_rules.py - Trading constraints
   Size: 48 KB | Lines: 850
   Status: ACTIVE | Tested: ✅
   ```

4. **Connection Arrows**
   - Show data flow direction
   - Label with data type (e.g., "pricing data", "ML signals", "risk alerts")
   - Thickness indicates importance/frequency

5. **Index/Legend**
   - Color key
   - Icon meanings
   - File path conventions
   - Last updated timestamp

---

## 🤖 Blueprint Generation Tools

### Option 1: Graphviz (Recommended)

```python
#!/usr/bin/env python3
"""
RICK System Blueprint Generator
Automatically creates visual architecture diagram
"""

import graphviz
import os
from pathlib import Path
from datetime import datetime

def generate_blueprint():
    dot = graphviz.Digraph(
        'RICK_System_Blueprint',
        comment='RBOTzilla UNI Architecture',
        format='png',
        engine='dot'
    )
    
    # Graph styling
    dot.attr(
        bgcolor='#0a0e27',
        fontname='Courier New',
        fontsize='12',
        fontcolor='white'
    )
    
    # Node styling
    dot.attr(
        'node',
        shape='box',
        style='filled,rounded',
        fillcolor='#00ff41',
        fontcolor='black',
        fontname='Courier New',
        fontsize='10'
    )
    
    # Edge styling
    dot.attr(
        'edge',
        color='#00d4ff',
        fontcolor='white',
        fontsize='8'
    )
    
    # Define nodes (example structure)
    # Foundation Layer
    dot.node('foundation', 
             'FOUNDATION\n' +
             '─────────────\n' +
             'rick_charter.py\n' +
             'PIN 841921 gate\n' +
             '48 KB | ✅ Active',
             fillcolor='#00ff41')
    
    # Broker Layer
    dot.node('brokers',
             'BROKERS\n' +
             '─────────────\n' +
             'oanda_connector.py\n' +
             'coinbase_connector.py\n' +
             '68 KB | ✅ Active',
             fillcolor='#00ff41')
    
    # ML Layer
    dot.node('ml_learning',
             'ML MODELS\n' +
             '─────────────\n' +
             'ml_models.py (A/B/C)\n' +
             'pattern_learner.py\n' +
             'optimizer.py\n' +
             '92 KB | 🟡 Integrating',
             fillcolor='#ffff00',
             fontcolor='black')
    
    # Risk Layer
    dot.node('risk',
             'RISK MANAGEMENT\n' +
             '─────────────\n' +
             'session_breaker.py\n' +
             'oco_validator.py\n' +
             'risk_control_center.py\n' +
             '180 KB | ✅ Active',
             fillcolor='#ff4444')
    
    # Strategies Layer
    dot.node('wolf_packs',
             'STRATEGIES\n' +
             '─────────────\n' +
             'orchestrator.py\n' +
             'stochastic_config.py\n' +
             'extracted_oanda.py\n' +
             '36 KB | ✅ Active',
             fillcolor='#00ff41')
    
    # Ghost Engine
    dot.node('ghost_engine',
             'GHOST ENGINE\n' +
             '─────────────\n' +
             'live_ghost_engine.py\n' +
             '750ms polling\n' +
             'PID: 1543574 | ✅ Running',
             fillcolor='#00ff41')
    
    # Define edges (data flow)
    dot.edge('foundation', 'ghost_engine', 'Charter\nValidation')
    dot.edge('brokers', 'ghost_engine', 'Market\nPricing')
    dot.edge('ml_learning', 'wolf_packs', 'ML\nSignals')
    dot.edge('wolf_packs', 'ghost_engine', 'Trading\nSignals')
    dot.edge('risk', 'ghost_engine', 'Risk\nChecks')
    dot.edge('ghost_engine', 'risk', 'Trade\nEvents')
    
    # Add header
    dot.attr(label=f'RICK System Blueprint\\nGenerated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}\\nMode: Ghost | Branch: feat/complete-punchlist',
             labelloc='t',
             fontsize='16')
    
    # Render
    output_dir = Path('/home/ing/RICK/R_H_UNI/blueprints')
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f'RICK_Blueprint_{timestamp}'
    
    dot.render(output_file, cleanup=True)
    print(f"✅ Blueprint generated: {output_file}.png")
    
    return str(output_file) + '.png'

if __name__ == '__main__':
    generate_blueprint()
```

### Option 2: Python + Pillow (Manual Drawing)

For detailed custom layouts with exact positioning.

### Option 3: PlantUML

For UML-style component diagrams.

---

## 📋 Node Categorization Rules

### GREEN Nodes (Active/Operational)

**Criteria:**
- ✅ Code is tested and passing
- ✅ Integrated into ghost/canary/live engine
- ✅ Charter-compliant
- ✅ Used in current execution path

**Examples:**
- `foundation/rick_charter.py`
- `brokers/oanda_connector.py`
- `risk/session_breaker.py`
- `wolf_packs/orchestrator.py`

### YELLOW Nodes (In Development/Testing)

**Criteria:**
- 🟡 Code exists but not integrated yet
- 🟡 Tests passing but not in production
- 🟡 Awaiting shadow/canary validation

**Examples:**
- `ml_learning/ml_models.py` (before integration)
- `connectors/futures/venue_manager.py` (Phase 29)

### RED Nodes (Critical Safety Systems)

**Criteria:**
- 🔴 Safety-critical functionality
- 🔴 PIN-gated operations
- 🔴 Risk management systems
- 🔴 Charter enforcement

**Examples:**
- `foundation/rick_charter.py`
- `risk/session_breaker.py` (-5% daily halt)
- `risk/oco_validator.py` (stop-loss enforcement)

### GRAY Nodes (Legacy/Inactive)

**Criteria:**
- ⚫ Dead code (not called)
- ⚫ Legacy backup files
- ⚫ Deprecated modules

**Examples:**
- `brokers/oanda_connector.py::place_oco_order()` (dead method)
- `archive/` directory
- `extracted_legacy/` directory

---

## 🎯 Blueprint Update Frequency

### Auto-Generate After:

| Event | Blueprint Name | Priority |
|-------|---------------|----------|
| ML Integration Complete | `RICK_Blueprint_ML_Integrated_YYYYMMDD.png` | HIGH |
| Major Refactor | `RICK_Blueprint_Refactor_v{N}.png` | MEDIUM |
| Phase Completion | `RICK_Blueprint_Phase_{N}_Complete.png` | HIGH |
| Before Extraction | `RICK_Blueprint_Pre_Extract_YYYYMMDD.png` | CRITICAL |
| Every 10 Tasks | `RICK_Blueprint_Task_{N}.png` | LOW |
| User Request | `RICK_Blueprint_UserRequest_YYYYMMDD.png` | HIGH |

---

## 📁 Blueprint Storage

### Location

```
/home/ing/RICK/R_H_UNI/blueprints/
├── current/
│   └── RICK_Blueprint_Latest.png         ← Symlink to most recent
├── archive/
│   ├── RICK_Blueprint_20251010_Initial.png
│   ├── RICK_Blueprint_20251010_ML_Integrated.png
│   └── RICK_Blueprint_Phase_*.png
└── metadata/
    └── blueprint_index.json              ← Auto-generated index
```

### Metadata Format

`blueprints/metadata/blueprint_index.json`:
```json
{
  "blueprints": [
    {
      "filename": "RICK_Blueprint_20251010_ML_Integrated.png",
      "generated": "2025-10-10T18:30:00Z",
      "trigger": "ML_INTEGRATION_COMPLETE",
      "git_commit": "abc123def",
      "total_nodes": 25,
      "active_nodes": 18,
      "inactive_nodes": 7,
      "critical_nodes": 5,
      "file_count": 87,
      "total_code_size": "1.2 MB"
    }
  ]
}
```

---

## 🚨 AI Agent Compliance

### MANDATORY Actions for All AI Agents

When working in `/home/ing/RICK/R_H_UNI/`:

1. **Check COMPLETED_TASKS/README.md** before starting work
2. **Log every task** to COMPLETED_TASKS/README.md after completion
3. **Generate blueprint** if task count % 10 == 0
4. **Generate blueprint** if major integration/refactor
5. **Update blueprint metadata** after generation
6. **Reference latest blueprint** when explaining architecture

### Example Workflow

```python
# Pseudo-code for AI agent task completion

def complete_task(task_description, files_modified):
    # 1. Perform task
    result = execute_task()
    
    # 2. Log to COMPLETED_TASKS
    task_number = log_task_completion(
        description=task_description,
        files=files_modified,
        result=result
    )
    
    # 3. Check if blueprint needed
    if task_number % 10 == 0 or is_major_change(task_description):
        blueprint_path = generate_blueprint()
        update_blueprint_index(blueprint_path)
        print(f"📐 Blueprint generated: {blueprint_path}")
    
    # 4. Return completion message
    return f"✅ Task #{task_number} complete. Blueprint: {'generated' if blueprint_needed else 'not needed'}"
```

---

## 📊 Blueprint Content Requirements

### Minimum Information Per Node

Each node in the blueprint MUST display:

1. **Module Name** (e.g., "Foundation Layer")
2. **File List** (up to 5 most important files)
3. **Single-sentence description** (plain English, non-technical)
4. **Size** (KB or MB)
5. **Status** (✅ Active, 🟡 Testing, ⚫ Inactive, 🔴 Critical)
6. **Dependencies** (what this module requires)

### Example Node Format

```
┌─────────────────────────────────────┐
│  FOUNDATION LAYER                   │
│  ─────────────────────────────────  │
│                                     │
│  Files:                             │
│  • rick_charter.py                  │
│  • immutable_rules.py               │
│                                     │
│  Purpose:                           │
│  Enforces PIN 841921 and trading    │
│  rules (RR≥3.2, -5% daily halt)     │
│                                     │
│  Size: 48 KB | Lines: 850           │
│  Status: ✅ ACTIVE | Tests: PASS    │
│                                     │
│  Dependencies: None (base layer)    │
└─────────────────────────────────────┘
```

---

## 🔍 Blueprint Validation Checklist

Before finalizing any blueprint, verify:

- [ ] All active modules are colored GREEN
- [ ] Critical safety systems are colored RED
- [ ] Legacy/dead code is colored GRAY
- [ ] In-development modules are colored YELLOW
- [ ] All nodes have file lists
- [ ] All nodes have plain-English descriptions
- [ ] Data flow arrows are labeled
- [ ] Header includes date, mode, branch
- [ ] Legend/index is present
- [ ] PNG is high resolution (300+ DPI)
- [ ] File saved to `blueprints/` directory
- [ ] Metadata updated in `blueprint_index.json`

---

## 📝 Plain-English Description Guidelines

**DO:**
- ✅ "Stops trading if daily loss hits -5%"
- ✅ "Fetches live EUR/USD prices every 750ms"
- ✅ "Remembers which patterns win or lose money"

**DON'T:**
- ❌ "Implements AbstractTradeValidatorInterface"
- ❌ "Asyncio polling with backoff retry logic"
- ❌ "Stochastic gradient descent optimization"

**Rule:** If a 12-year-old can't understand it, rewrite it simpler.

---

## 🎨 Example Blueprint References

### Good Examples:

1. **AWS Architecture Diagrams** - Clear node groupings, color-coded
2. **Kubernetes Cluster Diagrams** - Hierarchical with labeled connections
3. **Network Topology Maps** - Shows data flow with arrows
4. **Game Engine Architecture** - Modular components with dependencies

### Style Inspiration:

- Cyberpunk aesthetic (dark backgrounds, neon accents)
- Matrix-style green terminals
- Futuristic HUD overlays
- Clean, professional flowcharts

---

## 🚀 Immediate Action Items

After ML integration completes:

1. ✅ **Generate first blueprint** showing ML models wired into ghost engine
2. ✅ **Create blueprints/ directory structure**
3. ✅ **Initialize blueprint_index.json**
4. ✅ **Generate baseline "before ML" snapshot** for comparison
5. ✅ **Generate "after ML" snapshot** showing integration

---

## 📌 Summary for AI Agents

**YOU MUST:**
1. Log every task to `COMPLETED_TASKS/README.md`
2. Generate blueprint after major changes or every 10 tasks
3. Use color-coded nodes (GREEN=active, RED=critical, GRAY=inactive, YELLOW=testing)
4. Include file lists and plain-English descriptions
5. Save to `blueprints/` with timestamped filename
6. Update `blueprint_index.json` metadata

**BLUEPRINT TRIGGERS:**
- ✅ ML integration complete
- ✅ Major refactor/restructure
- ✅ Phase completion
- ✅ Before extraction/deployment
- ✅ Every 10 completed tasks
- ✅ User explicitly requests

**NO EXCEPTIONS:** This is a mandatory protocol for all work in R_H_UNI.

---

*Addendum Status: ACTIVE*  
*Authority: Project Owner Mandate*  
*Effective: October 10, 2025*  
*Applies To: All AI agents (Claude, GPT-4, Copilot, etc.) working in /home/ing/RICK/R_H_UNI/*
