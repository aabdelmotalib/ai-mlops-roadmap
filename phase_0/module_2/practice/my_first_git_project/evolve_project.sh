#!/usr/bin/env bash
set -e 
mkdir -p example_project
cd example_project

if [ ! -d ".git" ]; then
    git init
fi 

git config user.name 
git config user.email

# -------------------------------
# Version 1
# -------------------------------
cat > math_tools.py << 'EOF'
# Version one 
def add(a, b):
    return a + b
EOF

git add math_tools.py 
git commit -m "Add addition function"

# -------------------------------
# Version 2
# -------------------------------
cat > math_tools.py << 'EOF'
# Version two
def add(a, b):
    return a + b

def sub(a, b):
    return a - b

EOF

git add math_tools.py
git commit -m "ADD sub function"

# -------------------------------
# Version 3
# -------------------------------
cat > math_tools.py << 'EOF'
# Version 3: Basic arithmetic operations
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
def multiply(a, b):
    return a * b
EOF

git add math_tools.py
git commit -m "Add multi function"

git log --oneline 
git status
git branch
