# 🧪 Intelligent API Testing Framework

A robust and extensible Python-based API testing framework that automates functional testing, load testing, and penetration testing. This framework enables fast feedback cycles with dynamic payload mutation and insightful HTML+JSON reporting including key performance metrics like P90, P95, and P99.

---

## 🚀 Features

- 🖁️ Supports GET and POST API testing
- 🔒 Built-in penetration testing (e.g., SQL Injection patterns)
- 📈 Load testing with multithreaded request generation
- ⚡ Performance metrics: Average, P90, P95, P99 response times
- 📄 Auto-generated reports in JSON and HTML (with collapsible sections)
- 🤖 Dynamic payload mutation for realistic fuzz testing
- 🔧 Easily integrable into CI/CD pipelines

---

## 💪 Setup Instructions

1. Clone this repository:

```bash
git clone [https://github.com/your-username/api-testing-framework.git](https://github.com/shreyash2509/Intelligent-API-Testing-Framework.git)
cd Intelligent-API-Testing-Framework.git
```

2. (Optional but recommended) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

Note: If requirements.txt is not present, install manually:

```bash
pip install requests
```

---

## ⚙️ Usage

Run the app:

```bash
python app.py
```

You will be prompted to enter:

- Base URL (e.g., https://yourapi.com)
- Endpoint (e.g., /v1/test)
- Method (GET or POST)
- (Optional) Authorization token

After testing, the framework will generate:

- JSON report: api_test_report_YYYY-MM-DD_HH-MM-SS.json
- HTML report: api_test_report_YYYY-MM-DD_HH-MM-SS.html

Open the HTML file in a browser for an interactive overview.

---

## 📈 Example Output

HTML Report Sections:

- Initial Request Summary
- Load Test Results (collapsible)
- Penetration Test Results (collapsible)
- Payload Variants (collapsible)

---

## 📁 Folder Structure

```
├── app.py                  # Entry point
└── utils/
    ├── request.py          # API request logic
    └── payload_generator.py # Dynamic payload mutation
    └── report_generator.py     # HTML/JSON report generation
    └── penetration_tester.py   # Pen test logic
    └── load_tester.py          # Load testing logic

```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

Please make sure to update tests as appropriate.

---

## 📄 License

MIT License
