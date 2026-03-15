#!/usr/bin/env bash
# =============================================================================
# setup_roadmap.sh
# Creates the full folder structure for "The AI & MLOps Engineer Roadmap"
# MkDocs Material project.
#
# Usage:
#   chmod +x setup_roadmap.sh
#   ./setup_roadmap.sh
#
# What it does:
#   - Creates docs/ structure with all phase and module folders
#   - Creates placeholder .md files (ready for AI-generated content)
#   - Creates empty practice/, exercises/, mini_projects/,
#     diagrams/, and code_snippets/ folders per module
#   - Creates mkdocs support files (extra.css, extra.js, tags.md, index.md)
# =============================================================================

set -e  # Exit immediately if any command fails

# ─── Color output helpers ────────────────────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No color

log()    { echo -e "${GREEN}✔${NC}  $1"; }
header() { echo -e "\n${BLUE}━━━  $1  ━━━${NC}"; }
note()   { echo -e "${YELLOW}→${NC}  $1"; }

# =============================================================================
# PHASE & MODULE DEFINITIONS
# Format: "phase_X|Module Title|topic1,topic2,topic3,topic4,topic5"
# =============================================================================
declare -A PHASE_TITLES=(
  [0]="Baseline Setup"
  [1]="Data Collection & Storage"
  [2]="Data Pipelines & Automation"
  [3]="AI and ML Basics"
  [4]="Automation & Workflow Integration"
  [5]="Analytics & Monitoring"
  [6]="MLOps & Deployment"
)

declare -A PHASE_MODULES=(
  [0]="Python Essentials|Git & Version Control|Docker Basics|Linux CLI|PostgreSQL Basics"
  [1]="REST APIs in Python|Web Scraping|Database Schema Design|Data Cleaning & Normalization|CSV & JSON Files"
  [2]="Apache Airflow|dbt Transformations|Data Validation & Error Handling|Connecting Databases to ETL|Workflow Orchestration"
  [3]="ML Concepts & Workflows|Feature Engineering|Pre-trained Models & Embeddings|Scikit-learn|Integrating ML with Python Apps"
  [4]="Background Tasks with Celery and RQ|Message Queues Redis and RabbitMQ|Scheduling & Retries|Logging Monitoring & Error Handling|Integrating Multiple Services"
  [5]="SQL for Analytics|Building Dashboards|Tracking Pipeline Metrics|System Monitoring & Logging|Visualizing Results & Trends"
  [6]="Docker Compose|Containerizing Applications|CI/CD Pipelines|Experiment Tracking with MLflow|Production Monitoring & Error Handling"
)

# Subfolders created inside each module directory (left empty for you to fill)
MODULE_SUBFOLDERS=("practice" "exercises" "mini_projects" "diagrams" "code_snippets")

# =============================================================================
# START
# =============================================================================
header "The AI & MLOps Engineer Roadmap — Project Setup"
note "This script will create the full MkDocs project structure."
echo ""

# Root-level mkdocs support dirs
mkdir -p docs/assets
mkdir -p docs/stylesheets
mkdir -p docs/javascripts
log "Created docs/assets, docs/stylesheets, docs/javascripts"

# ─── Root index.md ───────────────────────────────────────────────────────────
cat > docs/index.md << 'EOF'
---
tags:
  - Beginner
---

# 👋 Welcome to The AI & MLOps Engineer Roadmap

This is your **complete, beginner-friendly learning journey** from Python basics all the way to deploying production AI systems.

Each module is written as if a senior engineer is sitting next to you — explaining the *why*, not just the *what*.

---

## 🗺️ Roadmap Overview

| Phase | Topic | What You'll Learn |
|-------|-------|-------------------|
| **Phase 0** | Baseline Setup | Python, Git, Docker, Linux, PostgreSQL |
| **Phase 1** | Data Collection & Storage | APIs, Scraping, Schema Design, Cleaning |
| **Phase 2** | Data Pipelines & Automation | Airflow, dbt, ETL, Validation |
| **Phase 3** | AI / ML Basics | ML Concepts, Scikit-learn, Embeddings |
| **Phase 4** | Automation & Workflows | Celery, Redis, Scheduling, Logging |
| **Phase 5** | Analytics & Monitoring | SQL, Dashboards, Metrics, Grafana |
| **Phase 6** | MLOps & Deployment | Docker Compose, CI/CD, MLflow |

---

## ✅ How to Use This Site

1. Start at **Phase 0** and work through modules in order.
2. Each module has a concept explanation → step-by-step guide → code examples → exercises.
3. Use the **Tags** page to jump to any topic.
4. Toggle 🌙 dark mode top-right.

!!! tip "Beginner tip"
    Don't skip phases — each one builds on the last.

---

*Happy learning! 🚀*
EOF
log "Created docs/index.md"

# ─── tags.md ─────────────────────────────────────────────────────────────────
cat > docs/tags.md << 'EOF'
# 🏷️ Tags Index

Browse all modules and exercises by topic.

[TAGS]
EOF
log "Created docs/tags.md"

# ─── extra.css ───────────────────────────────────────────────────────────────
cat > docs/stylesheets/extra.css << 'EOF'
/* ============================================================
   extra.css — Custom styles for The AI & MLOps Engineer Roadmap
   ============================================================ */

/* Slightly wider content area */
.md-grid {
  max-width: 1400px;
}

/* Phase overview cards (used in phase index pages) */
.phase-card {
  border-left: 4px solid var(--md-primary-fg-color);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  background: var(--md-code-bg-color);
}

/* Module progress tag */
.progress-tag {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  background: var(--md-accent-fg-color);
  color: white;
}

/* Inline keyboard key styling enhancement */
kbd {
  background: var(--md-code-bg-color);
  border: 1px solid var(--md-default-fg-color--lighter);
  border-radius: 4px;
  padding: 1px 5px;
  font-size: 0.85em;
}
EOF
log "Created docs/stylesheets/extra.css"

# ─── extra.js ────────────────────────────────────────────────────────────────
cat > docs/javascripts/extra.js << 'EOF'
/* ============================================================
   extra.js — Custom JavaScript for The AI & MLOps Engineer Roadmap
   ============================================================ */

// Initialize Mermaid diagrams with current theme
document$.subscribe(function () {
  const isDark = document.body.getAttribute("data-md-color-scheme") === "slate";
  mermaid.initialize({
    startOnLoad: true,
    theme: isDark ? "dark" : "default",
  });
});
EOF
log "Created docs/javascripts/extra.js"

# ─── Placeholder asset files ──────────────────────────────────────────────────
touch docs/assets/logo.png
touch docs/assets/favicon.png
note "Placeholder logo.png and favicon.png created in docs/assets/ — replace with your own images."

# =============================================================================
# PHASE + MODULE LOOP
# =============================================================================
for phase_num in 0 1 2 3 4 5 6; do
  phase_dir="docs/phase_${phase_num}"
  phase_title="${PHASE_TITLES[$phase_num]}"
  header "Phase ${phase_num}: ${phase_title}"

  mkdir -p "$phase_dir"

  # Phase index page
  cat > "${phase_dir}/index.md" << EOF
---
tags:
  - Beginner
---

# Phase ${phase_num}: ${phase_title}

Welcome to Phase ${phase_num}. Work through each module below in order.

## Modules

| # | Module | Status |
|---|--------|--------|
EOF

  # Split modules by pipe character
  IFS='|' read -ra modules <<< "${PHASE_MODULES[$phase_num]}"
  module_num=1

  for module_title in "${modules[@]}"; do
    module_dir="${phase_dir}/module_${module_num}"

    # Add row to phase index table
    echo "| ${module_num} | ${module_title} | 🔲 Not started |" >> "${phase_dir}/index.md"

    # Create module directory and subfolders
    mkdir -p "$module_dir"
    for subfolder in "${MODULE_SUBFOLDERS[@]}"; do
      mkdir -p "${module_dir}/${subfolder}"
      # Drop a .gitkeep so git tracks the empty folder
      touch "${module_dir}/${subfolder}/.gitkeep"
    done

    # ── Main module .md file ──────────────────────────────────────────────────
    cat > "${module_dir}/module_${module_num}.md" << EOF
---
tags:
  - Beginner
  - Phase ${phase_num}
---

# Module ${module_num}: ${module_title}

> **Phase ${phase_num} — ${phase_title}**

---

<!-- ============================================================
  AI PROMPT — paste the prompt below into your AI of choice
  to generate the full content for this module.
  ============================================================ -->

<!--
PROMPT START
============================================================
You are a senior software engineer and patient mentor teaching
a complete beginner. Write the full learning module for:

  Module ${module_num}: ${module_title}
  Phase ${phase_num}: ${phase_title}

STRICT RULES — follow every one:

1. TONE & STYLE
   - Write as if sitting next to the student, explaining out loud.
   - Use plain English. Avoid jargon — if you must use a technical
     term, define it immediately in one sentence.
   - Use real-world analogies to introduce every new concept before
     showing any code.
   - Never assume prior knowledge beyond what was covered in
     earlier modules of this roadmap.

2. STRUCTURE — use exactly this order:
   a) ## 🎯 What You Will Learn  (bullet list of outcomes)
   b) ## 🧠 Concept Explained    (theory + analogy, no code yet)
   c) ## 🔍 How It Works         (deeper explanation, ASCII or
                                   Mermaid diagram required)
   d) ## 🛠️ Step-by-Step Guide   (numbered steps, one action each)
   e) ## 💻 Code Examples        (full, runnable code blocks)
   f) ## 📝 Inline Comments Rule (every line of code must have
                                   a comment explaining WHY,
                                   not just what)
   g) ## ⚠️ Common Mistakes      (at least 3 mistakes beginners make)
   h) ## ✅ Exercises            (3 graded: easy / medium / hard)
   i) ## 🏗️ Mini Project         (1 small project using this module)
   j) ## 🔗 What's Next          (link to next module)

3. CODE QUALITY
   - Every code block must be complete and runnable as-is.
   - Every single line must have an inline comment.
   - Use Python unless the module is specifically about another tool.
   - Show expected output after each code block in a separate
     code block labeled \`# Expected output\`.

4. DIAGRAMS
   - Include at least one Mermaid diagram OR ASCII diagram.
   - Diagrams must show data flow, not just boxes with names.

5. ADMONITIONS — use MkDocs Material admonitions:
   - !!! tip     for shortcuts and best practices
   - !!! warning for things that often break
   - !!! note    for important context
   - !!! danger  for things that can cause data loss or bugs

6. CROSS-LINKS
   - Reference earlier modules when building on prior concepts.
   - Example: "Remember virtual environments from Module 1?"

7. LENGTH
   - Do not summarise. Be thorough.
   - Each section should be detailed enough that a beginner
     can follow without searching anything else.
============================================================
PROMPT END
-->

!!! note "Module content coming soon"
    Use the AI prompt in the comment above to generate the full
    content for this module. Paste it into Claude, ChatGPT, or
    any AI assistant.

EOF

    # ── Placeholder files inside subfolders ──────────────────────────────────

    # practice/
    cat > "${module_dir}/practice/README.md" << EOF
# Practice — Module ${module_num}: ${module_title}

Step-by-step practice exercises for this module.
Add your practice files here as you work through the module.

Suggested files:
- \`step_01_<topic>.py\`
- \`step_02_<topic>.py\`
- etc.
EOF

    # exercises/
    cat > "${module_dir}/exercises/README.md" << EOF
# Exercises — Module ${module_num}: ${module_title}

Coding problems for this module (Easy / Medium / Hard).

Suggested files:
- \`exercise_1_easy.py\`
- \`exercise_2_medium.py\`
- \`exercise_3_hard.py\`
- \`solutions/\` (create this folder for your solutions)
EOF

    # mini_projects/
    cat > "${module_dir}/mini_projects/README.md" << EOF
# Mini Project — Module ${module_num}: ${module_title}

A small project that puts this module's concepts into practice.

Suggested files:
- \`project_description.md\` (copy from the module's mini project section)
- \`main.py\` (your implementation)
- \`requirements.txt\`
- \`README.md\` (how to run the project)
EOF

    # diagrams/
    cat > "${module_dir}/diagrams/README.md" << EOF
# Diagrams — Module ${module_num}: ${module_title}

Architecture, workflow, and concept diagrams for this module.

Suggested files:
- \`concept_diagram.md\` (Mermaid source)
- \`workflow_diagram.md\`
- \`data_flow.md\`
EOF

    # code_snippets/
    cat > "${module_dir}/code_snippets/README.md" << EOF
# Code Snippets — Module ${module_num}: ${module_title}

Reusable, standalone code examples from this module.

Suggested files:
- \`snippet_01_<name>.py\`
- \`snippet_02_<name>.py\`
EOF

    log "Phase ${phase_num} / Module ${module_num}: ${module_title}"
    ((module_num++))
  done

  # Close the phase index table
  echo "" >> "${phase_dir}/index.md"
  echo "---" >> "${phase_dir}/index.md"
  echo "" >> "${phase_dir}/index.md"
  echo "!!! tip" >> "${phase_dir}/index.md"
  echo "    Work through modules in order — each one builds on the last." >> "${phase_dir}/index.md"

done

# =============================================================================
# PRINT SUMMARY
# =============================================================================
header "Done! Here is your project structure"
echo ""
find docs -type f -name "*.md" | sort
echo ""
header "Next steps"
note "1.  Copy mkdocs.yml to the root of your project folder."
note "2.  Install dependencies:"
echo "        pip install mkdocs-material mkdocs-glightbox"
note "3.  Serve locally:"
echo "        mkdocs serve"
note "4.  Open http://127.0.0.1:8000 in your browser."
note "5.  For each module, copy the AI prompt from the .md comment"
echo "    and paste it into Claude or ChatGPT to generate the content."
echo ""
echo -e "${GREEN}Happy learning! 🚀${NC}"
echo ""
