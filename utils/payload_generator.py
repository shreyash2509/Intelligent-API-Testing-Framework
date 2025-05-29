import json
import random
import string
import openai
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from utils.request import send_request

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def replace_random(payload):
    def randomize(value):
        if isinstance(value, str) and value.lower() == "random":
            return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        elif isinstance(value, dict):
            return {k: randomize(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [randomize(v) for v in value]
        else:
            return value
    return randomize(payload)

def generate_payload_variants(sample_payload):
    prompt = (
        f"Given the following JSON payload:\n{json.dumps(sample_payload, indent=2)}\n\n"
        "Generate a list of at least 30 varied JSON payloads for API testing, covering the following cases:\n"
        "1. Valid/positive inputs\n"
        "2. Missing required fields\n"
        "3. Extra/unexpected fields\n"
        "4. Wrong data types (e.g., int instead of string, array instead of object)\n"
        "5. Boundary cases (empty string, very long string, 0, negative numbers, very large numbers)\n"
        "6. Null values\n"
        "7. SQL injection strings\n"
        "8. Script/HTML injection strings\n"
        "9. Enum violations (wrong value from expected options)\n"
        "10. Boolean confusion (e.g., \"true\", \"false\", 1, 0, yes, no)\n"
        "Return only a valid JSON list of objects, no markdown, no code fencing, no explanation."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        start = content.find('[')
        end = content.rfind(']')
        if start == -1 or end == -1:
            raise ValueError("No JSON array found in OpenAI response.")

        json_data = content[start:end + 1]
        variants = json.loads(json_data)

        if not isinstance(variants, list):
            raise ValueError("Expected a list of payloads.")
        
        print(f"\n{len(variants)} variants generated")

        return variants

    except Exception:
        return [sample_payload]

def test_payloads_against_api(url, method, sample_payload, auth=None, max_workers=5, verify_ssl=True, timeout=1000):
    payloads = generate_payload_variants(sample_payload)
    results = []

    def send_variant(payload, index):
        final_payload = replace_random(payload)
        try:
            
            resp, duration, text = send_request(method, url, final_payload, auth=auth, verify_ssl=verify_ssl, timeout=timeout)
            status_code = resp.status_code if hasattr(resp, 'status_code') else None
            return {
                "payload": final_payload,
                "status_code": status_code,
                "response_time": duration,
                "response": text
            }
        except Exception as e:
            return {
                "payload": final_payload,
                "status_code": None,
                "response_time": None,
                "error": str(e)
            }

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(send_variant, p, i): i for i, p in enumerate(payloads)}
        for future in as_completed(futures):
            results.append(future.result())

    return results
