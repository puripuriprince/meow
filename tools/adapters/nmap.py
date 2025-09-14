


# Check if the tool is installed (available).
# 
# Build the command for the tool (arguments etc).
# 
# Run the tool (via subprocess etc).
# 
# Collect output (stdout, stderr, exit code).
# 
# If it outputs JSON or structured output, parse it.

# Nmap (CLI)

# What it does: Network/port/service/OS detection; maps the stack behind a web app (e.g., 80/443/8443, versions).
# Common runs:
# 
# Quick web stack scan: nmap -sV -p 80,443,8080 target
# 
# Aggressive fingerprint: nmap -A target
# 
# Machine-parsable output: -oX nmap.xml (XML DTD documented).
# Outputs: Normal, greppable, XML—XML is best for adapters
