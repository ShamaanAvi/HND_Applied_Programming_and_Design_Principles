from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize the ChromeDriver
driver = webdriver.Chrome()

try:
    # Open the Flask web application
    driver.get("http://127.0.0.1:5000")
    print("Opened the Flask web application.")

    # Wait for the analysis type select element to be present
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "analysis_type"))
    )
    select = Select(select_element)
    select.select_by_value("monthly_sales")
    print("Selected Monthly Sales Analysis.")

    # Wait for the branch ID input element to be present
    branch_id_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "branch_id"))
    )
    branch_id_input.send_keys("1")
    print("Entered Branch ID.")

    # Wait for the submit button to be present and clickable
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    submit_button.click()
    print("Submitted the form.")

    # Wait for the results table to be present
    results_table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    assert results_table is not None, "No results found."
    print("Monthly Sales Analysis Test Passed")

finally:
    # Close the browser
    driver.quit()
