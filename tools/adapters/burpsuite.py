#



# Check if the tool is installed (available).
# 
# Build the command for the tool (arguments etc).
# 
# Run the tool (via subprocess etc).
# 
# Collect output (stdout, stderr, exit code).
# 
# If it outputs JSON or structured output, parse it.



# 
# Burp Suite (GUI; special case)
# 
# What it does: Intercept/proxy traffic, manual replay, and (Pro) active scanning; core panels include Proxy (HTTP history), Repeater, and Intruder.
# How to interact: Primarily GUI. Launchable via command line (Java JAR) with startup options (e.g., memory, config); automation via Burp Extender (Montoya API) or BApp extensions (e.g., Headless Burp for command-line spider/scanner).
# Inputs: Browser-through-proxy traffic; imported requests; scope settings.
# Outputs (export):
# 
# Proxy HTTP history / items → XML via “Save items”.
# Scanner issues → HTML/PDF reports; XML issue data export (good for programmatic parsing).
# Adapter tips: If you need programmatic results, prefer “Export issue data (XML)” or saved HTTP history XML; drive headless scans only if you install a headless/REST extension.
# 



