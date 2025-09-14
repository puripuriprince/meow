
from typing import List, Optional
import json
from .base import ToolAdapter, ToolResult, which, run_command


class NucleiAdapter(ToolAdapter):
    """Adapter for nuclei vulnerability scanner."""
    
    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "nuclei"
    
    async def available(self) -> bool:
        """Check if nuclei is available on the system."""
        return which("nuclei") is not None
    
    async def run(self, cmd: List[str], **kwargs) -> ToolResult:
        """
        Run nuclei with given parameters.
        
        Args:
            cmd: Command arguments to pass to nuclei
            **kwargs: Additional arguments passed to run_command (timeout, cwd, etc.)
        
        Returns:
            ToolResult with parsed JSONL output if available
        """
        # Ensure nuclei is the first argument
        if not cmd or cmd[0] != "nuclei":
            cmd = ["nuclei"] + cmd
            
        # Add JSONL output format if not already specified
        if "-o" not in cmd and "-jsonl" not in cmd:
            # Add JSONL format for better parsing
            cmd.append("-jsonl")
        
        result = await run_command(cmd, **kwargs)
        
        # Try to parse JSONL output if available
        if result.stdout and result.exit_code == 0:
            parsed_lines = self._parse_jsonl(result.stdout)
            if parsed_lines:
                result.parsed_data = parsed_lines
        
        return result
    
    def _parse_jsonl(self, output: str) -> Optional[List[dict]]:
        """Parse JSONL (JSON Lines) output - each line is a separate JSON object."""
        try:
            lines = []
            for line in output.strip().split('\n'):
                line = line.strip()
                if line:  # Skip empty lines
                    lines.append(json.loads(line))
            return lines if lines else None
        except json.JSONDecodeError:
            return None

# What it does: High-speed, template-driven vuln & misconfig scanner; huge community YAML templates; great for low-noise checks and CI.
# Key flags:
# 
# Targets from list: -l urls.txt (supports inputs like burp exports, OpenAPI, etc. with -im)
# Template selection: -t cves/ or filter by -tags, -severity critical,high.
# Output: -o results.jsonl -jsonl, -silent, Markdown export, even SARIF.
# 
# Common run: nuclei -l urls.txt -tags cve -severity critical,high -o findings.jsonl -jsonl
# 
# Outputs: JSONL / SARIF / Markdown—excellent for programmatic pipelines.

