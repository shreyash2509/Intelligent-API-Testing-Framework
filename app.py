import streamlit as st
import json
from urllib.parse import urljoin
from utils.request import send_request
from utils.load_Tester import load_test
from utils.Penetration_Tester import penetration_test
from utils.payload_generator import test_payloads_against_api
from utils.report_generator import generate_report
import time

st.set_page_config(page_title="API Testing Tool", layout="wide")
st.title("🔍 API Testing & Security Tool")

baseurl = st.text_input("Base URL", "https://perf.naehas.com/MendersQAPerfDashboard")
endpoint = st.text_input("Endpoint (e.g., /api/login)", "/api/test")
username = st.text_input("Username (optional)", "qaadmin@naehas.com")
password = st.text_input("Password (optional)", "naehas2016", type="password")
method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE"])
payload_type = st.selectbox("Payload Type", ["JSON"])
payload_input = st.text_area("Request Payload (as JSON)", '{"username": "random", "password": "random"}', height=150)
tests_to_run = st.multiselect("Select Tests to Run", ["Random Payload Test", "Load Test", "Penetration Test"])

if st.button("Run Tests"):
    try:
        payload = json.loads(payload_input)
    except Exception as e:
        st.error(f"Invalid JSON payload: {e}")
        st.stop()

    url = urljoin(baseurl.rstrip('/') + '/', endpoint.lstrip('/'))
    auth = (username, password) if username and password else None

    st.info("Sending Initial Request...")
    resp, duration, text = send_request(method, url, payload, auth=auth)
    initial_result = {"status_code": resp.status_code if hasattr(resp, 'status_code') else "N/A", "time": duration, "response": text}
    st.success(f"Initial Response: {initial_result['status_code']} in {initial_result['time']}s")

    payload_variants = []
    load_result = {}
    pen_results = []

    if "Random Payload Test" in tests_to_run:
        st.info("Generating and Testing Payload Variants...")
        payload_variants = test_payloads_against_api(url, method, payload, auth)
        st.success(f"Tested {len(payload_variants)} payload variants.")
    
    time.sleep(5)
    if "Load Test" in tests_to_run:
        st.info("Running Load Test...")
        load_result = load_test(url, method, payload, auth, threads=50)
        st.success("Load test completed.")

    time.sleep(5)
    
    if "Penetration Test" in tests_to_run:
        st.info("Running Penetration Tests...")
        pen_results = penetration_test(url, method, payload, auth)
        st.success(f"Tested {len(pen_results)} payloads in penetration test.")

    st.info("Generating Report...")
    json_path, html_path = generate_report(payload_variants, load_result, pen_results, initial_result)

    if json_path and html_path:
        st.success("Report generated successfully.")

        with open(json_path, "rb") as jf:
            st.download_button("📥 Download JSON Report", jf, file_name=json_path, mime="application/json")

        with open(html_path, "rb") as hf:
            st.download_button("📄 Download HTML Report", hf, file_name=html_path, mime="text/html")
    else:
        st.error("Failed to generate report.")
