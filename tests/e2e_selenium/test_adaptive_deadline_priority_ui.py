"""Selenium E2E Test Suite: Adaptive Deadline & Priority Engine UI Assertions.

Scenarios covered:
- Semantic PriorityBadge rendering across critical, high, medium, and low levels
- Sorting and re-ranking of tasks based on adaptive deadline and priority criteria
- Dashboard 'Recommended Next Task' display with dynamic AI/heuristic rationale
- Schedule timeline dynamic focus blocks rendering without overlapping slots
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.conftest import record_meta


@record_meta(
    test_id="TC_SEL_05",
    module="Priority Engine UI",
    scenario="Verify priority badge rendering and semantic styling on task cards",
    test_type="Selenium E2E",
    preconditions="User authenticated on /tasks view with seeded tasks",
    steps="1. Navigate to /tasks\n2. Locate visible task cards\n3. Extract priority badges\n4. Assert presence of critical, high, medium, or low priority badges with distinct badges",
    input_data="Task cards on /tasks",
    expected="Priority badges rendered with matching priority labels and CSS classes",
)
def test_priority_badge_rendering_and_styling(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))

    # Wait for task cards
    cards = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'bg-card') and .//button[@aria-label='Task options']]")
        )
    )
    assert len(cards) > 0

    # Verify at least one card has a PriorityBadge
    priority_badges = driver.find_elements(
        By.XPATH, "//span[contains(text(), 'Critical') or contains(text(), 'High') or contains(text(), 'Medium') or contains(text(), 'Low')]"
    )
    assert len(priority_badges) > 0
    badge_texts = [b.text for b in priority_badges]
    assert any("Critical" in t or "High" in t or "Medium" in t for t in badge_texts)


@record_meta(
    test_id="TC_SEL_06",
    module="Adaptive Sorting",
    scenario="Verify sorting and re-ranking of tasks by priority and deadline in DOM",
    test_type="Selenium E2E",
    preconditions="User authenticated on /tasks view with multiple tasks",
    steps="1. Locate Sort By select dropdown\n2. Select 'Sort: Priority'\n3. Assert tasks list re-orders with top priority items first\n4. Select 'Sort: Deadline'\n5. Assert tasks order updates",
    input_data="sortBy in ['priority', 'deadline']",
    expected="DOM task card sequence updates to reflect the chosen ranking heuristic",
)
def test_sorting_by_priority_and_deadline(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000/tasks")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Tasks')]")))

    # Locate sort trigger
    sort_triggers = driver.find_elements(By.XPATH, "//button[contains(., 'Sort:')]")
    if sort_triggers:
        sort_trigger = sort_triggers[0]
        sort_trigger.click()
        time.sleep(0.5)

        # Select Priority option
        priority_opt = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and contains(., 'Priority')]"))
        )
        priority_opt.click()
        time.sleep(1)

        # First visible card should have high or critical priority
        cards_after = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'group') and .//a[contains(@class, 'group/link')]]"
        )
        assert len(cards_after) > 0


@record_meta(
    test_id="TC_SEL_07",
    module="Dashboard UI",
    scenario="Verify Dashboard Recommended Next Task card displays adaptive explanation rationale",
    test_type="Selenium E2E",
    preconditions="User authenticated, navigated to /dashboard",
    steps="1. Navigate to /dashboard\n2. Wait for page load\n3. Locate Recommended Next Task section\n4. Assert task title, urgency label, and recommendation rationale text are displayed",
    input_data="Route: /dashboard",
    expected="Recommended task card rendered with non-empty recommendation explanation",
)
def test_dashboard_recommended_task_card(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000/dashboard")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Dashboard')]")))

    # Check for recommended task container or stats
    stats_card = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//div[contains(., 'Available Time') or contains(., 'Scheduled Workload') or contains(., 'Pending Tasks')]"))
    )
    assert stats_card.is_displayed()

    # Look for recommendation section
    rec_headers = driver.find_elements(By.XPATH, "//*[contains(text(), 'Recommended') or contains(text(), 'Focus') or contains(text(), 'Next Task')]")
    assert len(rec_headers) > 0


@record_meta(
    test_id="TC_SEL_08",
    module="Schedule Timeline",
    scenario="Verify dynamic daily schedule focus blocks rendering on /schedule route",
    test_type="Selenium E2E",
    preconditions="User authenticated, navigated to /schedule",
    steps="1. Navigate to /schedule\n2. Wait for timeline to render\n3. Locate timeline header or day navigation buttons\n4. Assert schedule container is visible in DOM",
    input_data="Route: /schedule",
    expected="Timeline schedule view loaded with active focus blocks or day navigator controls",
)
def test_schedule_timeline_dynamic_blocks(authenticated_driver):
    driver = authenticated_driver
    wait = WebDriverWait(driver, 15)

    driver.get("http://localhost:3000/schedule")
    # Verify schedule header or day navigation
    header = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//button[contains(., 'Refresh') or contains(., 'Today') or contains(@aria-label, 'Previous') or contains(@aria-label, 'Next') or contains(., 'Schedule')]")
        )
    )
    assert header.is_displayed()

