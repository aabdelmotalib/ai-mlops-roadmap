import re
#  Extract structured data from a messy log line and transform it.
log_line = "2024-03-17 14:35:42 | User: alice_smith | Action: login | Status: SUCCESS"
# Extract each field
date_match = re.search(r"(\d{4}-\d{2}-\d{2})", log_line)
date = date_match.group(1) if date_match else "UNKNOWN"

user_match = re.search(r"User: (\w+)", log_line)
user = user_match.group(1) if user_match else "UNKNOWN"

action_match = re.search(r"Action: (\w+)", log_line)
action = action_match.group(1) if action_match else "UNKNOWN"

status_match = re.search(r"Status: (\w+)", log_line)
status = status_match.group(1) if status_match else "UNKNOWN"

# Format the output
output = f"[{date}] {user} performed {action} ({status})"
print(output)
