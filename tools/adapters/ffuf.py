from typing import List, Optional
from .base import ToolAdapter, ToolResult, which, run_command


class FfufAdapter(ToolAdapter):
    """Adapter for ffuf (Fuzz Faster U Fool) web fuzzer."""
    
    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "ffuf"
    
    async def available(self) -> bool:
        """Check if ffuf is available on the system."""
        return which("ffuf") is not None
    
    async def run(self, cmd: List[str], **kwargs) -> ToolResult:
        """
        Run ffuf with given parameters.
        
        Args:
            cmd: Command arguments to pass to ffuf
            **kwargs: Additional arguments passed to run_command (timeout, cwd, etc.)
        
        Returns:
            ToolResult with parsed JSON output if available
        """
        # Ensure ffuf is the first argument
        if not cmd or cmd[0] != "ffuf":
            cmd = ["ffuf"] + cmd
            
        # Add JSON output format if not already specified
        if "-o" not in cmd and "-of" not in cmd:
            # Check if JSON format is requested, if not add it for bette+r parsing
            if "-of" not in cmd:
                cmd.extend(["-of", "json"])
        
        result = await run_command(cmd, **kwargs)
        
        # Try to parse JSON output if available
        if result.stdout and result.exit_code == 0:
            parsed = result.parse_json()
            if parsed:
                result.parsed_data = parsed
        
        return result



# ffuf (CLI)
# 
# What it does: Very fast fuzzing of paths, parameters, vhosts, headers, bodies; excellent filters and output formats
# Key flags: -w (wordlist), -u (URL with FUZZ), -X/-d (method/body), filters -fc/-fs/-fw, threads -t, auto-calibration -ac, JSON/CSV/HTML/Markdown outputs via -o + -of.
# 
# Common runs:
# 
# Directory brute-force: ffuf -w WORDS.txt -u https://site/FUZZ -o out.json -of json -t 100 -ac
# Param name fuzz: ffuf -w params.txt -u "https://site/search?FUZZ=value" -o out.json -of json
# 
# VHost fuzz: ffuf -w subs.txt -H "Host: FUZZ.site.com" -u https://site -o hosts.json -of json
# 
# Outputs: JSON (newline or file), CSV, HTML, MD—easy to parse for hits (status/size/words
