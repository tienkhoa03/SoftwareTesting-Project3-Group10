import csv
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException

class TestFileResult:
    def __init__(self, name):
        self.name = name
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.start_time = time.time()
        self.end_time = None
    
    def add_pass(self):
        self.total += 1
        self.passed += 1
    
    def add_fail(self):
        self.total += 1
        self.failed += 1

    def finish(self):
        self.end_time = time.time()

    @property
    def duration(self):
        return round(self.end_time - self.start_time, 2)

    @property
    def status(self):
        return "PASS" if self.failed == 0 else "FAIL"

class SummaryReport:
    def __init__(self):
        self.files = []
    
    def add(self, file_result):
        self.files.append(file_result)

    def print_summary(self):
        print("\n===================== SUMMARY =====================")
        print("File           | Total | Pass | Fail | Time  | Status")
        print("----------------------------------------------------")
        
        total, passed, failed, t = 0, 0, 0, 0

        for fr in self.files:
            total += fr.total
            passed += fr.passed
            failed += fr.failed
            t += fr.duration
            print(f"{fr.name:14} | {fr.total:5} | {fr.passed:4} | {fr.failed:4} | {fr.duration:5}s | {fr.status}")

        print("----------------------------------------------------")
        print(f"TOTAL          | {total:5} | {passed:4} | {failed:4} | {round(t,2)}s | {'PASS' if failed == 0 else 'FAIL'}")
        print("====================================================")

# =========================================
# CONFIGURATION for SLEEP TIME
# Bug when reach 0.2s or lower, 
# higher number takes more time

stableTime = 0.5
isStable = True

# Default times (when run not OK)
# Else change isStable to False
if (isStable):
    sleepTime = 0.5
    allertTime = 0.5
    deleteTime = 0.5

# =========================================
# MAP CSV NAMES
# =========================================
CSV_MAP = {
    "BVA": "BVA.csv",
    "ECP": "ECP.csv",
    "DT":  "DecTable.csv",
    "UCT": "UseCase.csv"
}


# =========================================
# DELETE ALL CUSTOMERS
# =========================================
def delete_all_customers(driver):
    driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject/#/manager/list")
    time.sleep(1)

    try:
        driver.find_element(By.XPATH, "//button[contains(text(),'Customers')]").click()
        time.sleep(deleteTime)
    except:
        pass

    while True:
        try:
            btn = driver.find_element(By.XPATH, "//table/tbody/tr[1]/td[5]/button")
            btn.click()
            time.sleep(deleteTime)
        except:
            break


# =========================================
# ACCEPT ALERT IF EXISTS
# =========================================
def accept_alert_if_exists(driver):
    try:
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(allertTime)
    except NoAlertPresentException:
        pass


# =========================================
# PRINT UTILS
# =========================================
def line():
    print("-" * 70)


def log_test_result(idx, inp, exp, act):
    print(f"TEST #{idx}")
    print(f" Input: FN='{inp['fn']}', LN='{inp['ln']}', PC='{inp['pc']}'")
    print("")
    print(f"  PASS={exp['fn'] == act['fn']}  | FN: expect='{exp['fn']}' | actual='{act['fn']}' ")
    print(f"  PASS={exp['ln'] == act['ln']}  | LN: expect='{exp['ln']}' | actual='{act['ln']}' ")
    print(f"  PASS={exp['pc'] == act['pc']}  | PC: expect='{exp['pc']}' | actual='{act['pc']}' ")
    print("")

    final = (exp['fn'] == act['fn'] and exp['ln'] == act['ln'] and exp['pc'] == act['pc'])
    print(f"  FINAL RESULT: {'PASS' if final else 'FAIL'}")
    line()

# =========================================
# RUN A SINGLE CSV TEST FILE
# =========================================
def run_test_file(csv_path, driver):
    
    result = TestFileResult(csv_path)
    delete_all_customers(driver)
    
    print(f"\n>>> Running file: {csv_path}")
    line()


    # Load CSV
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} tests")
    line()

    for idx, row in enumerate(rows, start=1):
        fn_in = row["first_name"]
        ln_in = row["last_name"]
        pc_in = row["post_code"]

        exp_fn = row["expected_f_name"]
        exp_ln = row["expected_l_name"]
        exp_pc = row["expected_post_code"]

        # Go to Add Customer page
        driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject/#/manager/addCust")
        time.sleep(sleepTime)

        fn_field = driver.find_element(By.CSS_SELECTOR, "input[ng-model='fName']")
        ln_field = driver.find_element(By.CSS_SELECTOR, "input[ng-model='lName']")
        pc_field = driver.find_element(By.CSS_SELECTOR, "input[ng-model='postCd']")

        fn_field.clear()
        ln_field.clear()
        pc_field.clear()

        fn_field.send_keys(fn_in)
        ln_field.send_keys(ln_in)
        pc_field.send_keys(pc_in)

        # Submit
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(sleepTime)

        # Handle alert
        accept_alert_if_exists(driver)
        time.sleep(sleepTime)

        # Read values back
        fn_act = fn_field.get_attribute("value")
        ln_act = ln_field.get_attribute("value")
        pc_act = pc_field.get_attribute("value")

        # log result
        input_data = {"fn": fn_in, "ln": ln_in, "pc": pc_in}
        expected = {"fn": exp_fn, "ln": exp_ln, "pc": exp_pc}
        actual = {"fn": fn_act, "ln": ln_act, "pc": pc_act}

        log_test_result(idx, input_data, expected, actual)
        
        # Update result class
        if fn_act == exp_fn and ln_act == exp_ln and pc_act == exp_pc:
            result.add_pass()
        else:
            result.add_fail()
    
    result.finish()
    return result


# =========================================
# RUN ALL CSV FILES
# =========================================
def run_all(driver):
    summary = SummaryReport()
    for key in ["BVA", "ECP", "DT", "UCT"]:
        r = run_test_file(CSV_MAP[key], driver)
        summary.add(r)
    summary.print_summary()

# =========================================
# MAIN
# =========================================
def main():
    driver = webdriver.Chrome()

    if len(sys.argv) > 1:
        arg = sys.argv[1].upper()
        
        if arg in CSV_MAP:
            runRes = run_test_file(CSV_MAP[arg], driver)
            summary = SummaryReport()
            summary.add(runRes)
            summary.print_summary()
        
        else:
            print(f"Unknown argument: {arg}. Running ALL instead.")
            run_all(driver)
    
    else:
        run_all(driver)

    driver.quit()


# =========================================
# EXECUTE
# =========================================
if __name__ == "__main__":
    main()
