"""Pytest configuration, Selenium WebDriver fixtures, and automated test execution reporter.

Manages:
1. Environment setup and backend module imports.
2. Headless Chrome WebDriver initialization with standard options.
3. Authenticated session fixtures for Next.js frontend UI testing.
4. Execution metrics collection for TEST_EXECUTION_REPORT.md.
"""

import os
import sys
import time
import json
import socket
import pytest
from pathlib import Path
from typing import Dict, List, Any

# Ensure backend modules are on sys.path and backend environment is loaded
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ------------------------------------------------------------------------------
# Test Result Collector for TEST_EXECUTION_REPORT.md
# ------------------------------------------------------------------------------

TEST_RECORDS: List[Dict[str, Any]] = []


def is_port_open(port: int, host: str = "127.0.0.1") -> bool:
    """Check if local TCP port is open and accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


@pytest.fixture(scope="session", autouse=True)
def verify_services_ready():
    """Verify that backend (port 8000) and frontend (port 3000) are responsive."""
    backend_up = is_port_open(8000)
    frontend_up = is_port_open(3000)
    if not backend_up:
        print("[WARNING] Backend API on port 8000 does not appear to be open.")
    if not frontend_up:
        print("[WARNING] Frontend on port 3000 does not appear to be open.")


@pytest.fixture(scope="function")
def chrome_driver():
    """Yield a cleanly configured headless Chrome WebDriver instance."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1440,900")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)
    try:
        yield driver
    finally:
        try:
            driver.quit()
        except Exception:
            pass


@pytest.fixture(scope="function")
def authenticated_driver(chrome_driver):
    """Yield a Chrome WebDriver that is pre-authenticated with the active session."""
    driver = chrome_driver
    auth_token_file = REPO_ROOT / "auth_token.json"

    # Try instant token injection first
    if auth_token_file.exists():
        try:
            with open(auth_token_file, "r", encoding="utf-8") as f:
                auth_data = f.read().strip()
            if auth_data:
                driver.get("http://localhost:3000/login")
                driver.execute_script(
                    "window.localStorage.setItem('sb-yzkfguqgusupoyfzxrsl-auth-token', arguments[0]);",
                    auth_data,
                )
                driver.get("http://localhost:3000/tasks")
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]"))
                )
                yield driver
                return
        except Exception:
            pass

    # Fallback to UI-based login
    driver.get("http://localhost:3000/login")
    wait = WebDriverWait(driver, 25)
    demo_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Fill demo credentials')]"))
    )
    demo_btn.click()
    time.sleep(0.5)

    sign_in = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Sign in')]"))
    )
    sign_in.click()

    wait.until(lambda d: "/dashboard" in d.current_url or "/tasks" in d.current_url)

    # Cache token for next test runs
    try:
        val = driver.execute_script("return window.localStorage.getItem('sb-yzkfguqgusupoyfzxrsl-auth-token');")
        if val:
            with open(auth_token_file, "w", encoding="utf-8") as f:
                f.write(val)
    except Exception:
        pass

    yield driver


# ------------------------------------------------------------------------------
# Pytest Hooks to Record Test Execution Metrics
# ------------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture individual test outcome and timing for documentation reporting."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        test_meta = getattr(item.function, "_test_meta", None)
        doc = item.function.__doc__ or ""
        test_id = item.name
        scenario = doc.strip().split("\n")[0] if doc else item.name
        test_type = "Selenium E2E" if "selenium" in item.nodeid else "Unit"
        module_name = item.module.__name__.split(".")[-1]

        execution_time_ms = round(report.duration * 1000, 2)
        status = "PASS" if report.passed else "FAIL"

        record = {
            "test_id": test_meta.get("id", test_id) if test_meta else test_id,
            "module": test_meta.get("module", module_name) if test_meta else module_name,
            "scenario": test_meta.get("scenario", scenario) if test_meta else scenario,
            "test_type": test_meta.get("test_type", test_type) if test_meta else test_type,
            "preconditions": test_meta.get("preconditions", "Services active") if test_meta else "Services active",
            "steps": test_meta.get("steps", "Execute test assertions") if test_meta else "Execute test assertions",
            "input_data": test_meta.get("input_data", "Standard parameters") if test_meta else "Standard parameters",
            "expected_result": test_meta.get("expected", "Assertions pass") if test_meta else "Assertions pass",
            "actual_result": "Assertions passed successfully" if report.passed else f"Failure: {str(report.longrepr)[:80]}",
            "execution_time_ms": execution_time_ms,
            "status": status,
        }
        TEST_RECORDS.append(record)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Write execution summary report to TEST_EXECUTION_REPORT.md in root."""
    if not TEST_RECORDS:
        return

    report_path = REPO_ROOT / "TEST_EXECUTION_REPORT.md"
    total_tests = len(TEST_RECORDS)
    passed_tests = sum(1 for r in TEST_RECORDS if r["status"] == "PASS")
    failed_tests = total_tests - passed_tests
    total_time_s = round(sum(r["execution_time_ms"] for r in TEST_RECORDS) / 1000, 2)

    lines = [
        "# Software Engineering Automated Test Execution Report",
        "",
        f"**Repository:** SE - Adaptive Task and Deadline Management  ",
        f"**Test Framework:** Pytest 8.4.2 + Selenium WebDriver (Headless Chrome)  ",
        f"**Execution Summary:** {total_tests} Total Tests | **{passed_tests} PASSED** | **{failed_tests} FAILED** | Total Duration: {total_time_s}s  ",
        "",
        "## Formal Test Case Execution Matrix",
        "",
        "| Test_ID | Module | Test_Scenario | Test_Type (Unit/Selenium) | Preconditions | Test_Steps | Input_Data | Expected_Result | Actual_Result | Execution_Time_ms | Status (PASS/FAIL) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |",
    ]

    for r in TEST_RECORDS:
        # Sanitize pipe characters and newlines for clean Markdown table rendering
        def clean(val: Any) -> str:
            s = str(val).replace("|", "\\|").replace("\n", "<br>")
            return s.strip()

        line = (
            f"| {clean(r['test_id'])} "
            f"| {clean(r['module'])} "
            f"| {clean(r['scenario'])} "
            f"| {clean(r['test_type'])} "
            f"| {clean(r['preconditions'])} "
            f"| {clean(r['steps'])} "
            f"| {clean(r['input_data'])} "
            f"| {clean(r['expected_result'])} "
            f"| {clean(r['actual_result'])} "
            f"| {r['execution_time_ms']} "
            f"| **{r['status']}** |"
        )
        lines.append(line)

    lines.append("")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[INFO] Generated TEST_EXECUTION_REPORT.md at {report_path}")


def record_meta(test_id: str, module: str, scenario: str, test_type: str, preconditions: str, steps: str, input_data: str, expected: str):
    """Decorator to attach formal test case metadata to a test function."""
    def decorator(func):
        func._test_meta = {
            "id": test_id,
            "module": module,
            "scenario": scenario,
            "test_type": test_type,
            "preconditions": preconditions,
            "steps": steps,
            "input_data": input_data,
            "expected": expected,
        }
        return func
    return decorator

