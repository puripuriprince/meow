from typing import List, Optional
import re
import tempfile
import os
from .base import ToolAdapter, ToolResult, which, run_command


class SqlmapAdapter(ToolAdapter):
    """Adapter for sqlmap SQL injection testing tool."""
    
    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "sqlmap"
    
    async def available(self) -> bool:
        """Check if sqlmap is available on the system."""
        return which("sqlmap") is not None or which("sqlmap.py") is not None
    
    async def run(self, cmd: List[str], **kwargs) -> ToolResult:
        """
        Run sqlmap with given parameters.
        
        Args:
            cmd: Command arguments to pass to sqlmap
            **kwargs: Additional arguments passed to run_command (timeout, cwd, etc.)
        
        Returns:
            ToolResult with parsed output if available
        """
        # Ensure sqlmap is the first argument
        if not cmd or (cmd[0] != "sqlmap" and cmd[0] != "sqlmap.py"):
            # Try sqlmap first, fallback to sqlmap.py
            sqlmap_cmd = "sqlmap" if which("sqlmap") else "sqlmap.py"
            cmd = [sqlmap_cmd] + cmd
            
        # Add batch mode if not specified to avoid interactive prompts
        if "--batch" not in cmd:
            cmd.append("--batch")
            
        # Add output directory for better result parsing
        output_dir = None
        if "--output-dir" not in cmd:
            output_dir = tempfile.mkdtemp(prefix="sqlmap_")
            cmd.extend(["--output-dir", output_dir])
        
        result = await run_command(cmd, **kwargs)
        
        # Try to parse sqlmap output
        if result.stdout:
            parsed_data = self._parse_output(result.stdout, output_dir)
            if parsed_data:
                result.parsed_data = parsed_data
        
        # Clean up temporary directory
        if output_dir and os.path.exists(output_dir):
            try:
                import shutil
                shutil.rmtree(output_dir)
            except OSError:
                pass
        
        return result
    
    def _parse_output(self, output: str, output_dir: Optional[str] = None) -> Optional[dict]:
        """Parse sqlmap text output into structured data."""
        parsed = {
            "target_url": None,
            "injectable_parameters": [],
            "databases": [],
            "vulnerabilities": [],
            "backend_dbms": None,
            "findings": []
        }
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Extract target URL
            if line.startswith("URL:") or "testing URL" in line:
                url_match = re.search(r'(https?://[^\s]+)', line)
                if url_match:
                    parsed["target_url"] = url_match.group(1)
            
            # Extract injectable parameters
            if "Parameter:" in line and "injectable" in line.lower():
                param_match = re.search(r"Parameter:\s*([^\s]+)", line)
                if param_match:
                    parsed["injectable_parameters"].append(param_match.group(1))
            
            # Extract backend DBMS
            if "back-end DBMS:" in line.lower():
                dbms_match = re.search(r"back-end DBMS:\s*([^\n]+)", line, re.IGNORECASE)
                if dbms_match:
                    parsed["backend_dbms"] = dbms_match.group(1).strip()
            
            # Extract databases
            if "available databases" in line.lower():
                # Databases are usually listed in subsequent lines
                continue
            
            # Look for SQL injection findings
            if any(keyword in line.lower() for keyword in ["injection", "vulnerable", "payload"]):
                parsed["findings"].append(line)
            
            # Extract vulnerability types
            if "injection point" in line.lower() or "injection type" in line.lower():
                parsed["vulnerabilities"].append(line)
        
        # Try to read additional data from output directory if available
        if output_dir and os.path.exists(output_dir):
            self._parse_output_files(output_dir, parsed)
        
        return parsed if any(parsed.values()) else None
    
    def _parse_output_files(self, output_dir: str, parsed: dict) -> None:
        """Parse additional data from sqlmap output files."""
        try:
            # Look for log files and session files
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.log'):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                                log_content = f.read()
                                # Extract additional information from logs
                                if "databases" in log_content.lower():
                                    db_matches = re.findall(r"database[s]?:\s*([^\n]+)", log_content, re.IGNORECASE)
                                    for match in db_matches:
                                        databases = [db.strip() for db in match.split(',')]
                                        parsed["databases"].extend(databases)
                        except (IOError, OSError):
                            continue
        except OSError:
            pass