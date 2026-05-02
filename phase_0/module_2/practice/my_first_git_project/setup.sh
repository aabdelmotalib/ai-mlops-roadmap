#!/usr/bin/env bash
mkdir example_project
cd example_project
git init
git config user.name "abdelmotalib"
git config user.email "abdelmoteleeb@outlook.com"

cat > script.py << 'EOF'
# Simple calc program
def add(a, b):
    return a + b
print(add(5, 6))
EOF
git status
git add script.py
git commit -m "Add basic calc function"
git log --oneline
python script.py