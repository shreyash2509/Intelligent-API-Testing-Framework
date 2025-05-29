import json
from datetime import datetime
from collections import defaultdict
import html

def generate_report(payload_variants, load_result, pen_test_results, initial_response):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename_json = f"api_test_report_{timestamp}.json"
    filename_html = f"api_test_report_{timestamp}.html"

    report = {
        "initial_response_time": initial_response["time"],
        "initial_status_code": initial_response["status_code"],
        "initial_response_body": initial_response["response"],
        "payload_test_results": payload_variants,
        "load_test_result": load_result,
        "penetration_test_results": pen_test_results
    }

    try:
        with open(filename_json, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"\nJSON report saved as {filename_json}")

        with open(filename_html, 'w') as f:
            f.write("""
<html>
<head>
<title>API Test Report</title>
<style>
    body { font-family: Arial; margin: 20px; background: #f0f2f5; color: #333; }
    h1 { color: #222; }
    h2 { color: #1a73e8; margin-top: 30px; }
    pre { background: #fff; padding: 10px; border: 1px solid #ccc; border-radius: 5px; overflow-x: auto; }
    .success { color: green; font-weight: bold; }
    .fail { color: red; font-weight: bold; }
    details summary { cursor: pointer; margin-bottom: 10px; }
</style>
</head>
<body>
""")
            f.write(f"<h1>API Test Report - {timestamp}</h1>")
            f.write(f"<h2>Initial Request</h2><pre>Status Code: {initial_response['status_code']}\nResponse Time: {initial_response['time']}s\nResponse Body:\n{html.escape(str(initial_response['response']))}</pre>")

            # Payload Variants Section
            if payload_variants:
                f.write("<details><summary><h2>Payload Variant Results</h2></summary>")
                for i, r in enumerate(payload_variants):
                    status = r.get('status_code', 'N/A')
                    flag_class = 'success' if status == 200 else 'fail'
                    f.write(f"<details><summary class='{flag_class}'>Variant {i+1} - Status: {status}</summary>")
                    f.write(f"<pre class='{flag_class}'>Payload: {html.escape(json.dumps(r.get('payload', {}), indent=2))}\nStatus Code: {status}\nResponse Time: {r.get('response_time', 'N/A')}s\nResponse: {html.escape(str(r.get('response', 'N/A')))}\nError: {html.escape(str(r.get('error', 'N/A')))}</pre></details>")
                f.write("</details>")

            # Load Test Section
            if load_result and isinstance(load_result, dict) and load_result.get("total_requests"):
                f.write("<details><summary><h2>Load Test Results</h2></summary>")
                f.write(f"<pre>Total Requests: {load_result.get('total_requests', 'N/A')}\nAverage Time: {load_result.get('average_time', 'N/A')}s\nSuccessful Requests: {load_result.get('successful_requests', 'N/A')}\nFailed Requests: {load_result.get('failed_requests', 'N/A')}\nP90: {load_result.get('p90', 'N/A')}\nP95: {load_result.get('p95', 'N/A')}\nP99: {load_result.get('p99', 'N/A')}</pre>")
                for i, r in enumerate(load_result.get('responses', [])):
                    flag_class = 'success' if r.get('status_code', 0) == 200 else 'fail'
                    f.write(f"<details><summary class='{flag_class}'>Response {i+1} - Status: {r.get('status_code', 'N/A')}</summary>")
                    f.write(f"<pre class='{flag_class}'>{html.escape(json.dumps(r, indent=2))}</pre></details>")
                f.write("</details>")

            # Penetration Test Section
            if pen_test_results:
                f.write("<details><summary><h2>Penetration Test Results (SQLi, XSS, Command Injection, SSRF, LFI, RFI, Path Traversal, XXE, LDAP Injection)</h2></summary>")
                grouped_results = defaultdict(list)
                for r in pen_test_results:
                    grouped_results[r.get("category", "Unknown")].append(r)

                for category, results in grouped_results.items():
                    f.write(f"<details><summary><strong>{html.escape(category)} tests</strong></summary>")
                    for i, r in enumerate(results):
                        flag_class = 'fail' if r.get('flag', '').startswith('✅') else 'success'
                        parameter = html.escape(str(r.get('parameter', 'N/A')))
                        injection = html.escape(str(r.get('injection', '')))
                        status = r.get('status_code', 'N/A')
                        time_taken = r.get('time', 'N/A')
                        response = html.escape(str(r.get('response', '')))
                        flag = html.escape(str(r.get('flag', 'N/A')))
                        payload_str = html.escape(json.dumps(r.get('payload', {}), indent=2))

                        f.write(f"<details><summary class='{flag_class}'>#{i+1} - injection: <code>{injection}</code> | Status: {status}</summary>")
                        f.write(f"<pre class='{flag_class}'>"
                                f"Category: {html.escape(category)}\n"
                                f"Parameter: {parameter}\n"
                                f"Injection: {injection}\n"
                                f"Status Code: {status}\n"
                                f"Response Time: {time_taken}s\n"
                                f"Flag: {flag}\n"
                                f"Payload:\n{payload_str}\n\n"
                                f"Response Body:\n{response}"
                                f"</pre></details>")
                    f.write("</details>")
                f.write("</details>")

            f.write("</body></html>")

        print(f"HTML report saved as {filename_html}")
        return filename_json, filename_html

    except Exception as e:
        print(f"Failed to save report: {e}")
        return None, None
