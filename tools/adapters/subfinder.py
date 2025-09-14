

from __future__ import annotations

import json
from typing import List, Optional, Dict, Any
from tools.adapters.base import ToolAdapter, ToolResult, which, run_command


class SubfinderAdapter(ToolAdapter):
    """Adapter for Subfinder - Fast passive subdomain enumeration tool.
    
    Subfinder is a subdomain discovery tool that discovers valid subdomains for websites 
    using passive online sources. It has a simple, modular architecture and is optimized 
    for use during penetration testing.
    
    Features:
    - Fast passive subdomain enumeration
    - Multiple data sources (Certificate Transparency, DNS aggregators, etc.)
    - JSON output support
    - Rate limiting and threading control
    - Custom resolver support
    """

    @property
    def name(self) -> str:
        return "subfinder"

    async def available(self) -> bool:
        """Check if subfinder is available on the system."""
        return which("subfinder") is not None

    async def run(
        self,
        args: Optional[List[str]] = None,
        domain: Optional[str] = None,
        domains: Optional[List[str]] = None,
        wordlist: Optional[str] = None,
        sources: Optional[List[str]] = None,
        exclude_sources: Optional[List[str]] = None,
        timeout: float = 60.0,
        threads: Optional[int] = None,
        rate_limit: Optional[int] = None,
        resolvers: Optional[str] = None,
        output_file: Optional[str] = None,
        json_output: bool = True,
        silent: bool = True,
        verbose: bool = False,
        all_sources: bool = False,
        recursive: bool = False,
        max_time: Optional[int] = None,
        **kwargs
    ) -> ToolResult:
        """Run subfinder with specified parameters.
        
        Args:
            args: Raw command line arguments (if provided, other params are ignored)
            domain: Single domain to enumerate subdomains for
            domains: List of domains to enumerate subdomains for
            wordlist: Path to wordlist file for brute force
            sources: List of specific sources to use (e.g., ['certspotter', 'crtsh'])
            exclude_sources: List of sources to exclude
            timeout: Command timeout in seconds
            threads: Number of threads to use
            rate_limit: Rate limit requests per second
            resolvers: Path to custom resolver file
            output_file: Output file path
            json_output: Enable JSON output format
            silent: Enable silent mode (only results)
            verbose: Enable verbose output
            all_sources: Use all available sources
            recursive: Enable recursive subdomain discovery
            max_time: Maximum time to run in seconds
            **kwargs: Additional arguments passed to run_command
            
        Returns:
            ToolResult with subfinder output
        """
        if args is not None:
            # Use raw args if provided
            cmd = ["subfinder"] + args
        else:
            # Build command from parameters
            cmd = ["subfinder"]
            
            # Domain specification
            if domain:
                cmd.extend(["-d", domain])
            elif domains:
                for d in domains:
                    cmd.extend(["-d", d])
            else:
                raise ValueError("Either 'domain', 'domains', or 'args' must be provided")
            
            # Output format
            if json_output:
                cmd.append("-json")
            
            # Verbosity control
            if silent:
                cmd.append("-silent")
            elif verbose:
                cmd.append("-v")
            
            # Sources configuration
            if all_sources:
                cmd.append("-all")
            
            if sources:
                cmd.extend(["-sources", ",".join(sources)])
            
            if exclude_sources:
                cmd.extend(["-exclude-sources", ",".join(exclude_sources)])
            
            # Performance options
            if threads is not None:
                cmd.extend(["-t", str(threads)])
            
            if rate_limit is not None:
                cmd.extend(["-rl", str(rate_limit)])
            
            if max_time is not None:
                cmd.extend(["-max-time", str(max_time)])
            
            # File options
            if wordlist:
                cmd.extend(["-w", wordlist])
            
            if resolvers:
                cmd.extend(["-r", resolvers])
            
            if output_file:
                cmd.extend(["-o", output_file])
            
            # Advanced options
            if recursive:
                cmd.append("-recursive")

        # Execute command
        result = await run_command(cmd, timeout=timeout, **kwargs)
        
        # Parse JSON output if available and requested
        if json_output and result.stdout.strip():
            try:
                # Subfinder outputs one JSON object per line
                lines = result.stdout.strip().split('\n')
                parsed_results = []
                
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            parsed_results.append(json.loads(line))
                        except json.JSONDecodeError:
                            # If JSON parsing fails, treat as plain text result
                            parsed_results.append({"host": line})
                
                result.parsed_data = parsed_results
            except Exception:
                # If parsing fails completely, leave parsed_data as None
                pass
        elif result.stdout.strip() and not json_output:
            # Parse plain text output (one subdomain per line)
            subdomains = []
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('['):  # Skip log lines
                    subdomains.append(line)
            
            if subdomains:
                result.parsed_data = subdomains

        return result

    def parse_results(self, result: ToolResult) -> Dict[str, Any]:
        """Parse subfinder results into a structured format.
        
        Args:
            result: ToolResult from subfinder execution
            
        Returns:
            Dictionary with parsed results
        """
        parsed = {
            "subdomains": [],
            "total_found": 0,
            "sources_used": [],
            "errors": []
        }
        
        if result.parsed_data:
            if isinstance(result.parsed_data, list):
                if all(isinstance(item, dict) for item in result.parsed_data):
                    # JSON format results
                    for item in result.parsed_data:
                        if "host" in item:
                            subdomain_info = {
                                "subdomain": item["host"],
                                "source": item.get("source", "unknown")
                            }
                            parsed["subdomains"].append(subdomain_info)
                            
                            # Track sources
                            source = item.get("source", "unknown")
                            if source not in parsed["sources_used"]:
                                parsed["sources_used"].append(source)
                else:
                    # Plain text results
                    for subdomain in result.parsed_data:
                        parsed["subdomains"].append({
                            "subdomain": subdomain,
                            "source": "unknown"
                        })
        
        parsed["total_found"] = len(parsed["subdomains"])
        
        # Extract errors from stderr
        if result.stderr:
            for line in result.stderr.split('\n'):
                line = line.strip()
                if line and ('error' in line.lower() or 'failed' in line.lower()):
                    parsed["errors"].append(line)
        
        return parsed

    async def enumerate_subdomains(
        self,
        domain: str,
        sources: Optional[List[str]] = None,
        wordlist: Optional[str] = None,
        timeout: float = 300.0,
        max_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """High-level method to enumerate subdomains for a domain.
        
        Args:
            domain: Target domain
            sources: Specific sources to use
            wordlist: Wordlist for brute force
            timeout: Command timeout
            max_time: Maximum runtime in seconds
            
        Returns:
            Parsed results dictionary
        """
        result = await self.run(
            domain=domain,
            sources=sources,
            wordlist=wordlist,
            timeout=timeout,
            max_time=max_time,
            json_output=True,
            silent=True
        )
        
        return self.parse_results(result)

    async def get_version(self) -> Optional[str]:
        """Get subfinder version information.
        
        Returns:
            Version string or None if unavailable
        """
        try:
            result = await self.run(args=["-version"])
            if result.exit_code == 0 and result.stdout:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_available_sources(self) -> List[str]:
        """Get list of available subfinder sources.
        
        Returns:
            List of source names
        """
        # Common subfinder sources (as of latest versions)
        return [
            "alienvault",
            "anubis", 
            "bevigil",
            "binaryedge",
            "bufferover",
            "censys",
            "certspotter",
            "chaos",
            "chinaz",
            "crtsh",
            "dnsdumpster",
            "dnsrepo",
            "fofa",
            "fullhunt",
            "github",
            "hackertarget",
            "intelx",
            "passivetotal",
            "quake",
            "rapiddns",
            "redhuntlabs",
            "robtex",
            "securitytrails",
            "shodan",
            "spyse",
            "sublist3r",
            "threatbook",
            "threatminer",
            "urlscan",
            "virustotal",
            "waybackarchive",
            "zoomeye"
        ]


__all__ = ["SubfinderAdapter"]
