import csv
import time
import sys
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException


# ============================================================
# GLOBALS
# ============================================================

CONFIG = {}
LOG_FILE = None


# ============================================================
# LOGGING
# ============================================================

def log(msg=""):
    print(msg)
    if LOG_FILE:
        LOG_FILE.write(msg + "\n")


# ============================================================
# CONFIG LOADER
# ============================================================

def load_config():
    cfg_path = "config/config.csv"
    default_cfg = {
        "stop_on_failure": "false",
        "wait_timeout": "10",
        "sleep_after_step": "0"
    }

    if not os.path.exists(cfg_path):
        return default_cfg

    with open(cfg_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row["key"].strip()
            default_cfg[key] = row["value"].strip()

    return default_cfg


# ============================================================
# CSV LOADING
# ============================================================

def load_steps(path):
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r)


def load_data(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = {k: (v or "") for k, v in row.items() if k is not None and k != ""}
            rows.append(clean)
    return rows


# ============================================================
# VARIABLE BINDING
# ============================================================

def bind_value(raw_value, testcase):
    """Replace ${var} with value from data row (handles BOM + trimming)."""
    if raw_value is None:
        return ""

    # Strip surrounding whitespace + BOM
    value = raw_value.strip().lstrip("\ufeff")

    for key, val in testcase.items():
        if not key or not key.strip():
            continue

        clean_key = key.strip().lstrip("\ufeff")
        pattern = "${" + clean_key + "}"

        value = value.replace(pattern, val.strip().lstrip("\ufeff"))

    return value



# ============================================================
# TARGET PARSER
# ============================================================

def parse_target(target):
    if not target:
        return None, None
    if "=" not in target:
        return None, target

    prefix, loc = target.split("=", 1)
    prefix = prefix.strip().lower()
    loc = loc.strip()

    by_map = {
        "css": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "id": By.ID,
        "name": By.NAME,
        "link": By.LINK_TEXT,
        "tag": By.TAG_NAME,
    }

    return by_map.get(prefix, None), loc


# ============================================================
# COMMANDS
# ============================================================

def cmd_open(driver, target, value):
    driver.get(target)
    return True


def cmd_click(driver, target, value):
    by, loc = parse_target(target)
    WebDriverWait(driver, int(CONFIG["wait_timeout"])).until(
        EC.element_to_be_clickable((by, loc))
    )
    driver.find_element(by, loc).click()
    return True


def cmd_type(driver, target, value):
    by, loc = parse_target(target)
    elem = WebDriverWait(driver, int(CONFIG["wait_timeout"])).until(
        EC.visibility_of_element_located((by, loc))
    )
    elem.clear()
    elem.send_keys(value)
    return True


def cmd_verifyText(driver, target, value):
    by, loc = parse_target(target)
    actual = driver.find_element(by, loc).text.strip()
    ok = (actual == value)
    log(f"   [VERIFY TEXT] expected='{value}' | actual='{actual}' | PASS={ok}")
    return ok


def cmd_verifyAlertText(driver, target, value):
    expected = value.strip()

    if expected == "":
        log(f"   [VERIFY ALERT] expected empty → PASS=True")
        return True

    actual = ""
    ok = False
    try:
        alert = WebDriverWait(driver, int(CONFIG["wait_timeout"])).until(
            EC.alert_is_present()
        )
        actual = alert.text.strip()
        alert.accept()
        ok = (actual == expected)
    except TimeoutException:
        ok = False

    log(f"   [VERIFY ALERT] expected='{expected}' | actual='{actual}' | PASS={ok}")
    return ok


def cmd_verifyFieldValue(driver, target, value):
    by, loc = parse_target(target)
    actual = driver.find_element(by, loc).get_attribute("value") or ""
    expected = value.strip()

    if expected == "":
        ok = (actual == "")
        log(f"   [VERIFY FIELD] expected='' | actual='{actual}' | PASS={ok}")
        return ok

    ok = (actual == expected)
    log(f"   [VERIFY FIELD] expected='{expected}' | actual='{actual}' | PASS={ok}")
    return ok


def cmd_acceptAlert(driver, target, value):
    try:
        alert = driver.switch_to.alert
        msg = alert.text
        alert.accept()
        log(f"   [ACCEPT ALERT] Text='{msg}' | PASS=True")
        return True
    except NoAlertPresentException:
        log(f"   [ACCEPT ALERT] No alert present → PASS=True")
        return True


# COMMAND TABLE
COMMANDS = {
    "open": cmd_open,
    "click": cmd_click,
    "type": cmd_type,
    "verifyText": cmd_verifyText,
    "verifyAlertText": cmd_verifyAlertText,
    "verifyFieldValue": cmd_verifyFieldValue,
    "acceptAlert": cmd_acceptAlert,
}


# ============================================================
# SUITE RESULT CLASS
# ============================================================

class SuiteResult:
    def __init__(self, name):
        self.name = name
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.start_time = time.time()
        self.end_time = None

    def record(self, ok):
        self.total += 1
        if ok:
            self.passed += 1
        else:
            self.failed += 1

    def finish(self):
        self.end_time = time.time()

    @property
    def duration(self):
        return round(self.end_time - self.start_time, 2)

    @property
    def status(self):
        return "PASS" if self.failed == 0 else "FAIL"


# ============================================================
# EXECUTION ENGINE
# ============================================================

def execute_step(driver, step, testcase):
    cmd = step["command"].strip()
    raw_target = step.get("target", "")
    raw_value = step.get("value", "")

    target = bind_value(raw_target, testcase)
    value = bind_value(raw_value, testcase)

    # 👉 Thêm dòng log này để thấy rõ từng step sau khi bind:
    log(f"   [STEP] cmd={cmd} | raw_target='{raw_target}' | raw_value='{raw_value}' | "
        f"bound_target='{target}' | bound_value='{value}'")

    func = COMMANDS.get(cmd)
    if not func:
        log(f"[ERROR] Unknown command: {cmd}")
        return False

    try:
        ok = func(driver, target, value)
        time.sleep(float(CONFIG["sleep_after_step"]))
        return ok
    except Exception as e:
        log(f"[ERROR] Step failed: {cmd} | {target} | {value} | {e}")
        return False



def run_testcase(steps, testcase, suite_name):
    log("\n------------------------------")
    log(f"TEST #{testcase['testcase_id']}")

    log("INPUT:")
    for key in ['first_name', 'last_name', 'post_code']:
        log(f"   {key.upper()}: '{testcase.get(key, '')}'")

    driver = webdriver.Chrome()
    result = True

    try:
        for step in steps:
            ok = execute_step(driver, step, testcase)
            if not ok:
                result = False
                if CONFIG["stop_on_failure"] == "true":
                    break

        log(f"OUTPUT: {'PASS' if result else 'FAIL'}")

    finally:
        driver.quit()

    return result


def run_suite(suite_name):
    log("\n====================================================")
    log(f"STARTING SUITE: {suite_name}")
    log("====================================================")

    suite_result = SuiteResult(suite_name)

    steps = load_steps(f"suites/{suite_name}/steps.csv")
    data = load_data(f"suites/{suite_name}/data.csv")

    for tc in data:
        ok = run_testcase(steps, tc, suite_name)
        suite_result.record(ok)

    suite_result.finish()

    log("\n===== SUITE SUMMARY =====")
    log(f"Suite: {suite_name}")
    log(f"Total: {suite_result.total}")
    log(f"Pass : {suite_result.passed}")
    log(f"Fail : {suite_result.failed}")
    log(f"Time : {suite_result.duration}s")
    log(f"Status: {suite_result.status}")
    log("=========================")

    return suite_result


# ============================================================
# REPORT CREATOR
# ============================================================

def make_and_write_report():
    global LOG_FILE
    if not os.path.exists("report"):
        os.makedirs("report")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE = open(f"report/report_{timestamp}.txt", "w", encoding="utf-8")


# ============================================================
# MAIN
# ============================================================

def main():
    global CONFIG
    CONFIG = load_config()

    make_and_write_report()

    log("===== DATA-DRIVEN TEST RUNNER =====")
    log(f"Loaded config: {CONFIG}")

    suites = sys.argv[1:] if len(sys.argv) > 1 else os.listdir("suites")
    suites = [s for s in suites if os.path.isdir(f"suites/{s}")]
    log(f"Suites to run: {', '.join(suites)}")

    suite_results = []
    for suite in suites:
        suite_results.append(run_suite(suite))

    log("\n===================== SUMMARY =====================")
    log("Suite          | Total | Pass | Fail | Time   | Status")
    log("----------------------------------------------------")

    total_all = passed_all = failed_all = time_all = 0

    for r in suite_results:
        total_all += r.total
        passed_all += r.passed
        failed_all += r.failed
        time_all += r.duration
        log(f"{r.name:14} | {r.total:5} | {r.passed:4} | {r.failed:4} | {r.duration:6}s | {r.status}")

    final_status = "PASS" if failed_all == 0 else "FAIL"

    log("----------------------------------------------------")
    log(f"TOTAL          | {total_all:5} | {passed_all:4} | {failed_all:4} | {round(time_all,2):6}s | {final_status}")
    log("====================================================")

    LOG_FILE.close()


if __name__ == "__main__":
    main()
