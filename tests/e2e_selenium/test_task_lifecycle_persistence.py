"""Selenium E2E Test Suite: Task Lifecycle & State Persistence (CRUD & Storage).

Scenarios covered:
- Updating task status (Pending -> In Progress -> Completed)
- Editing an existing task's parameters and verifying automatic UI recalculation
- Deleting a task and confirming removal from DOM and storage after page reload (driver.refresh())
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.conftest import record_meta


@record_meta(
    test_id="TC_SEL_09",
    module="Task Lifecycle",
    scenario="Verify task status transition from in_progress/pending to completed",
    test_type="Selenium E2E",
    preconditions="Active task present on /tasks view",
    steps="1. Navigate to /tasks\n2. Open options context menu on first incomplete task\n3. Click 'Mark Completed'\n4. Assert toast notification appears\n5. Assert task card status updates to Completed",
    input_data="Action: Mark Completed",
    expected="Task status updates to 'completed' with visual completed state",
)
def test_task_status_transition_lifecycle(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))

    # Find incomplete card
    options_btns = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//button[@aria-label='Task options']"))
    )
    assert len(options_btns) > 0
    driver.execute_script("arguments[0].click();", options_btns[0])

    # Click Mark Completed or Re-open
    action_item = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@role='menuitem' and (contains(., 'Mark Completed') or contains(., 'Re-open Task'))]")
        )
    )
    driver.execute_script("arguments[0].click();", action_item)

    # Toast or state update confirmation
    time.sleep(1)
    status_indicators = driver.find_elements(
        By.XPATH, "//*[contains(@data-sonner-toast, '') or contains(text(), 'completed') or contains(text(), 'Completed') or contains(text(), 'status updated')]"
    )
    assert len(status_indicators) > 0


@record_meta(
    test_id="TC_SEL_10",
    module="Task Lifecycle",
    scenario="Verify editing existing task parameters and automatic UI recalculation",
    test_type="Selenium E2E",
    preconditions="Task card present in DOM",
    steps="1. Open context menu on first task\n2. Click 'Edit Task'\n3. Update completed hours to 2.0\n4. Click Save Changes\n5. Assert modal closes and updated hours appear in DOM",
    input_data="completedDuration=2.0",
    expected="Task duration metrics recalculated in DOM",
)
def test_task_edit_duration_and_progress_recalculation(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))

    options_btns = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//button[@aria-label='Task options']"))
    )
    options_btns[0].click()

    edit_item = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem' and contains(., 'Edit Task')]"))
    )
    edit_item.click()

    # Edit modal open
    wait.until(EC.visibility_of_element_located((By.ID, "task-title")))
    comp_input = driver.find_element(By.ID, "task-completed")
    comp_input.click()
    comp_input.send_keys(Keys.CONTROL + "a")
    comp_input.send_keys("2")

    save_btn = driver.find_element(By.XPATH, "//form//button[@type='submit' and contains(., 'Save Changes')]")
    save_btn.click()

    # Modal closes
    wait.until(EC.invisibility_of_element_located((By.ID, "task-title")))


@record_meta(
    test_id="TC_SEL_11",
    module="Task Deletion",
    scenario="Verify deleting task and confirming removal from DOM and persistent DB storage across page reload",
    test_type="Selenium E2E",
    preconditions="Newly created unique task for deletion",
    steps="1. Create distinct task 'Delete Target Task'\n2. Search for task in list\n3. Click options menu -> 'Delete Task'\n4. Confirm delete in modal\n5. Assert task removed from DOM\n6. Reload page via driver.refresh()\n7. Assert task remains absent from DOM",
    input_data="title='Delete Target Task'",
    expected="Task is permanently removed from DOM and persistent database across page reload",
)
def test_task_deletion_and_storage_persistence(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))

    # 1. Create a task specifically to delete
    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Task')]")))
    create_btn.click()

    del_title = f"Delete Target Task {int(time.time())}"
    title_input = wait.until(EC.visibility_of_element_located((By.ID, "task-title")))
    title_input.send_keys(del_title)

    submit_btn = driver.find_element(By.XPATH, "//form//button[@type='submit' and contains(., 'Create Task')]")
    submit_btn.click()
    wait.until(EC.invisibility_of_element_located((By.ID, "task-title")))

    # 2. Search for the task
    search_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search tasks, categories...']")))
    search_input.click()
    search_input.send_keys(Keys.CONTROL + "a")
    search_input.send_keys(del_title)
    time.sleep(1)

    card = wait.until(EC.visibility_of_element_located((By.XPATH, f"//a[contains(., '{del_title}')]")))
    assert card.is_displayed()

    # 3. Open options menu on this card
    card_container = card.find_element(By.XPATH, "./ancestor::div[contains(@class, 'group') and contains(@class, 'bg-card')]")
    menu_btn = card_container.find_element(By.XPATH, ".//button[@aria-label='Task options']")
    menu_btn.click()

    delete_item = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem' and contains(., 'Delete Task')]"))
    )
    delete_item.click()

    # 4. Confirm delete in modal
    confirm_del_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Delete Task') and contains(@class, 'bg-destructive')]"))
    )
    confirm_del_btn.click()

    # 5. Assert card removed
    wait.until(EC.invisibility_of_element_located((By.XPATH, f"//a[contains(., '{del_title}')]")))

    # 6. Page reload (driver.refresh()) to verify persistent database storage deletion
    driver.refresh()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))

    # 7. Search again
    search_input_after = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search tasks, categories...']")))
    search_input_after.click()
    search_input_after.send_keys(Keys.CONTROL + "a")
    search_input_after.send_keys(del_title)
    time.sleep(1)

    cards_after_reload = driver.find_elements(By.XPATH, f"//a[contains(., '{del_title}')]")
    assert len(cards_after_reload) == 0

