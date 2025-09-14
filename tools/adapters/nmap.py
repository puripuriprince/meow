

from typing import List, Optional
import xml.etree.ElementTree as ET
import tempfile
import os
from .base import ToolAdapter, ToolResult, which, run_command


class NmapAdapter(ToolAdapter):
    """Adapter for nmap network scanner."""
    
    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "nmap"
    
    async def available(self) -> bool:
        """Check if nmap is available on the system."""
        return which("nmap") is not None
    
    async def run(self, cmd: List[str], **kwargs) -> ToolResult:
        """
        Run nmap with given parameters.
        
        Args:
            cmd: Command arguments to pass to nmap
            **kwargs: Additional arguments passed to run_command (timeout, cwd, etc.)
        
        Returns:
            ToolResult with parsed XML output if available
        """
        # Ensure nmap is the first argument
        if not cmd or cmd[0] != "nmap":
            cmd = ["nmap"] + cmd
            
        # Add XML output format if not already specified
        xml_file = None
        if "-oX" not in cmd and "-oA" not in cmd:
            # Create temporary file for XML output
            xml_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
            xml_file.close()
            cmd.extend(["-oX", xml_file.name])
        
        result = await run_command(cmd, **kwargs)
        
        # Try to parse XML output if available
        if xml_file and result.exit_code == 0:
            try:
                with open(xml_file.name, 'r') as f:
                    xml_content = f.read()
                parsed_data = self._parse_xml(xml_content)
                if parsed_data:
                    result.parsed_data = parsed_data
                # Clean up temporary file
                os.unlink(xml_file.name)
            except (IOError, OSError):
                pass
        
        return result
    
    def _parse_xml(self, xml_content: str) -> Optional[dict]:
        """Parse nmap XML output into structured data."""
        try:
            root = ET.fromstring(xml_content)
            
            scan_data = {
                "scanner": root.get("scanner", "nmap"),
                "version": root.get("version"),
                "start_time": root.get("start"),
                "hosts": []
            }
            
            # Parse each host
            for host in root.findall(".//host"):
                host_data = {
                    "status": host.find("status").get("state") if host.find("status") is not None else "unknown",
                    "addresses": [],
                    "hostnames": [],
                    "ports": []
                }
                
                # Parse addresses
                for address in host.findall("address"):
                    host_data["addresses"].append({
                        "addr": address.get("addr"),
                        "addrtype": address.get("addrtype")
                    })
                
                # Parse hostnames
                for hostname in host.findall(".//hostname"):
                    host_data["hostnames"].append({
                        "name": hostname.get("name"),
                        "type": hostname.get("type")
                    })
                
                # Parse ports
                for port in host.findall(".//port"):
                    port_data = {
                        "protocol": port.get("protocol"),
                        "portid": port.get("portid"),
                        "state": port.find("state").get("state") if port.find("state") is not None else "unknown"
                    }
                    
                    # Parse service information
                    service = port.find("service")
                    if service is not None:
                        port_data["service"] = {
                            "name": service.get("name"),
                            "product": service.get("product"),
                            "version": service.get("version"),
                            "extrainfo": service.get("extrainfo")
                        }
                    
                    host_data["ports"].append(port_data)
                
                scan_data["hosts"].append(host_data)
            
            return scan_data
            
        except ET.ParseError:
            return None

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
