import time
import random
import threading
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.payload_generator import replace_random
from utils.request import send_request

def load_test(
    url,
    method,
    payload,
    auth=None,
    threads=10,
    ramp_up=0,
    iterations_per_thread=1,
    think_time_range=(0.1, 1.0),
    verify_ssl=True,
    timeout=1000
):
    total_requests = threads * iterations_per_thread
    responses = []
    failure_count = 0
    failure_lock = threading.Lock()

    def send_one_request(index, iteration):
        nonlocal failure_count

        # Always use a randomized version of the original payload
        dynamic_payload = replace_random(payload)

        resp, duration, text = send_request(
            method, url, dynamic_payload, auth=auth, verify_ssl=verify_ssl, timeout=timeout
        )

        if hasattr(resp, 'status_code'):
            result = {"status_code": resp.status_code, "time": duration, "response": text}
        else:
            with failure_lock:
                failure_count += 1
            result = {"error": str(resp), "time": duration, "response": text}

        time.sleep(random.uniform(*think_time_range))
        return result

    futures = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for i in range(threads):
            for j in range(iterations_per_thread):
                futures.append(executor.submit(send_one_request, i, j))
                if ramp_up > 0:
                    time.sleep(ramp_up / total_requests)

        for future in as_completed(futures):
            responses.append(future.result())

    times = [r["time"] for r in responses if isinstance(r.get("time"), (int, float))]
    avg_time = round(sum(times) / len(times), 4) if times else 0
    p90 = round(np.percentile(times, 90), 4) if times else "N/A"
    p95 = round(np.percentile(times, 95), 4) if times else "N/A"
    p99 = round(np.percentile(times, 99), 4) if times else "N/A"

    return {
        "total_requests": total_requests,
        "successful_requests": total_requests - failure_count,
        "failed_requests": failure_count,
        "average_time": avg_time,
        "p90": p90,
        "p95": p95,
        "p99": p99,
        "responses": responses
    }
