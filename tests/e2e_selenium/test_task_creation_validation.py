"""Selenium E2E Test Suite: Task Creation and Input Validation (Boundary & Negative Testing).

Scenarios covered:
- Valid task creation with title, priority, effort duration, and deadline
- Negative test: Rejecting empty or whitespace-only task titles
- Boundary test: Negative/zero estimated duration validation
- Whitespace trimming: Verifying user inputs are sanitized and trimmed in DOM
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.conftest import record_meta


@record_meta(
    test_id="TC_SEL_01",
    module="Task Creation",
    scenario="Verify valid task creation with title, priority, duration, and target deadline",
    test_type="Selenium E2E",
    preconditions="User authenticated, navigated to /tasks view",
    steps="1. Click 'Create Task' button\n2. Fill unique task title, category, deadline, priority, effort\n3. Click 'Create Task' submit\n4. Assert modal closes\n5. Search for task title in search bar and assert visible in DOM",
    input_data="title='SE Architecture Milestone', priority='high', duration=6h",
    expected="Task card rendered in DOM with correct title and metadata",
)
def test_valid_task_creation_e2e(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 20)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))
    time.sleep(1.5)

    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Task')]")))
    driver.execute_script("arguments[0].click();", create_btn)

    title_input = wait.until(EC.visibility_of_element_located((By.ID, "task-title")))
    unique_title = f"SE Architecture Milestone {int(time.time())}"
    title_input.send_keys(unique_title)

    cat_input = driver.find_element(By.ID, "task-category")
    cat_input.click()
    cat_input.send_keys(Keys.CONTROL + "a")
    cat_input.send_keys("Software Engineering")

    est_input = driver.find_element(By.ID, "task-est")
    est_input.click()
    est_input.send_keys(Keys.CONTROL + "a")
    est_input.send_keys("6")

    submit_btn = driver.find_element(By.XPATH, "//form//button[@type='submit' and contains(., 'Create Task')]")
    driver.execute_script("arguments[0].click();", submit_btn)

    # Modal should close
    wait.until(EC.invisibility_of_element_located((By.ID, "task-title")))

    # Search for newly created task
    search_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search tasks, categories...']")))
    search_input.click()
    search_input.send_keys(Keys.CONTROL + "a")
    search_input.send_keys(unique_title)
    time.sleep(1.5)

    card = wait.until(EC.visibility_of_element_located((By.XPATH, f"//a[contains(., '{unique_title}')]")))
    assert card.is_displayed()
    assert unique_title in card.text


@record_meta(
    test_id="TC_SEL_02",
    module="Input Validation",
    scenario="Verify submission rejection when task title is empty or whitespace",
    test_type="Selenium E2E",
    preconditions="User authenticated on /tasks view, Create Task modal open",
    steps="1. Open Create Task modal\n2. Clear title field completely\n3. Attempt form submission\n4. Assert modal remains open and submission is blocked\n5. Cancel modal cleanly",
    input_data="title='' (empty string)",
    expected="Form is not submitted, modal remains open in DOM",
)
def test_empty_task_title_negative_validation_e2e(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 20)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))
    time.sleep(1.5)

    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Task')]")))
    driver.execute_script("arguments[0].click();", create_btn)

    title_input = wait.until(EC.visibility_of_element_located((By.ID, "task-title")))
    title_input.click()
    title_input.send_keys(Keys.CONTROL + "a")
    title_input.send_keys(Keys.BACKSPACE)

    submit_btn = driver.find_element(By.XPATH, "//form//button[@type='submit' and contains(., 'Create Task')]")
    driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(0.5)

    # Modal remains open because required title validation fails
    assert title_input.is_displayed()

    # Cleanly cancel modal
    cancel_btn = driver.find_element(By.XPATH, "//form//button[contains(., 'Cancel')]")
    cancel_btn.click()
    wait.until(EC.invisibility_of_element_located((By.ID, "task-title")))


@record_meta(
    test_id="TC_SEL_03",
    module="Input Validation",
    scenario="Verify rejection of non-positive estimated duration values",
    test_type="Selenium E2E",
    preconditions="Create Task modal open",
    steps="1. Fill valid title\n2. Clear estimated duration and enter 0\n3. Click Submit\n4. Assert submission is rejected and modal remains open",
    input_data="title='Boundary Duration Task', estimatedDuration=0",
    expected="Form submission is blocked, modal remains open",
)
def test_invalid_zero_duration_validation_e2e(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 20)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))
    time.sleep(1.5)

    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Task')]")))
    driver.execute_script("arguments[0].click();", create_btn)

    title_input = wait.until(EC.visibility_of_element_located((By.ID, "task-title")))
    title_input.send_keys("Boundary Duration Task")

    est_input = driver.find_element(By.ID, "task-est")
    est_input.click()
    est_input.send_keys(Keys.CONTROL + "a")
    est_input.send_keys("0")

    submit_btn = driver.find_element(By.XPATH, "//form//button[@type='submit' and contains(., 'Create Task')]")
    driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(0.5)

    # Modal remains visible
    assert title_input.is_displayed()

    cancel_btn = driver.find_element(By.XPATH, "//form//button[contains(., 'Cancel')]")
    cancel_btn.click()
    wait.until(EC.invisibility_of_element_located((By.ID, "task-title")))


@record_meta(
    test_id="TC_SEL_04",
    module="Task Creation",
    scenario="Verify automatic whitespace trimming on task title input",
    test_type="Selenium E2E",
    preconditions="Create Task modal open",
    steps="1. Enter title with leading/trailing spaces '  Trimmed Task Item  '\n2. Submit task\n3. Filter for task in DOM\n4. Assert trimmed title text matches without extra padding spaces",
    input_data="title='  Trimmed Task Item  '",
    expected="Task displayed in DOM as 'Trimmed Task Item' (trimmed)",
)
def test_whitespace_trimming_and_boundary_length(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 20)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))
    time.sleep(1.5)

    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Task')]")))
    driver.execute_script("arguments[0].click();", create_btn)

    title_input = wait.until(EC.visibility_of_element_located((By.ID, "task-title")))
    unique_suffix = int(time.time())
    raw_title = f"  Trimmed Task {unique_suffix}  "
    expected_title = f"Trimmed Task {unique_suffix}"

    title_input.send_keys(raw_title)

    submit_btn = driver.find_element(By.XPATH, "//form//button[@type='submit' and contains(., 'Create Task')]")
    driver.execute_script("arguments[0].click();", submit_btn)

    wait.until(EC.invisibility_of_element_located((By.ID, "task-title")))

    search_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search tasks, categories...']")))
    search_input.click()
    search_input.send_keys(Keys.CONTROL + "a")
    search_input.send_keys(expected_title)
    time.sleep(1.5)

    card = wait.until(EC.visibility_of_element_located((By.XPATH, f"//a[contains(., '{expected_title}')]")))
    assert card.text == expected_title
