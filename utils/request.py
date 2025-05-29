import requests
import time

def send_request(method, url, payload, auth=None, verify_ssl=True, timeout=1000):
    try:
        print(f"\nSending {method} request to {url} with payload: {payload}")
        start = time.time()


        if method == 'GET':
            resp = requests.get(url, params=payload, auth=auth, timeout=timeout, verify=verify_ssl)
        elif method == 'POST':
            resp = requests.post(url, json=payload, auth=auth, timeout=timeout, verify=verify_ssl)
        elif method == 'PUT':
            resp = requests.put(url, json=payload, auth=auth, timeout=timeout, verify=verify_ssl)
        elif method == 'DELETE':
            resp = requests.delete(url, json=payload, auth=auth, timeout=timeout, verify=verify_ssl)
        else:
            return f"\nUnsupported HTTP method: {method}", 0, None

        end = time.time()
        print(f"\nReceived response with status {resp.status_code} in {round(end - start, 4)}s")
        return resp, round(end - start, 4), resp.text

    except Exception as e:
        print(f"\nRequest failed: {e}")
        return f"Request failed: {e}", 0, None
