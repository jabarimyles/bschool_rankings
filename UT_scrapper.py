from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium import webdriver
import pandas as pd

# List of schools to search
schools = [
    "North Carolina State University",
    "University of Texas at Austin",
    "Stanford University"
    # Add more schools as needed
]


for school in schools:
    driver = webdriver.Chrome()
    # Refresh the page before each new search
    driver.get("https://jsom.utdallas.edu/the-utd-top-100-business-school-research-rankings/search#collaboration")

    # Wait for the search box to be present
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "as-input"))
    )

    # Input the school name into the search box
    search_box.clear()  # Clear any previous input
    search_box.send_keys(school)

    # Wait for the results dropdown to appear
    result_dropdown = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "as-results"))
    )

    # Locate and click the appropriate result
    result_items = driver.find_elements(By.CLASS_NAME, "as-result-item")
    for item in result_items:
        if school in item.text:
            actions = ActionChains(driver)
            actions.move_to_element(item).click().perform()
            break
    
    time.sleep(1)

    # Wait for the year dropdown to be present
    year_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "fromDate"))
    )

    # Create a Select object to interact with the dropdown
    select = Select(year_dropdown)

    # Select the option with value "1990"
    select.select_by_value("1990")

    time.sleep(8)

    # Wait for the "Select All" link to be clickable
    select_all_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Select All"))
    )

    # Click the "Select All" link
    select_all_link.click()

    time.sleep(2)

    # Wait for the "Search" button to be clickable
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "button4"))
    )

    # Click the "Search" button
    search_button.click()
    time.sleep(8)

    # Wait for the results to load, specifically waiting for the tables to appear
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
    )

    # Locate the tables
    tables = driver.find_elements(By.TAG_NAME, "table")
    time.sleep(2)

    # Extract data from the "Publications by Business School Faculty" table
    if len(tables) > 0:
        business_table = tables[0]
        business_rows = business_table.find_elements(By.TAG_NAME, "tr")
        
        # Initialize lists to store column data
        business_journals = []
        business_articles = []
        business_authors = []
        business_years = []
        business_volumes = []

        # Loop through each row and extract the data
        for row in business_rows[1:]:  # Skip the header row
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 5:  # Ensure there are 5 columns
                business_journals.append(cells[0].text)
                business_articles.append(cells[1].text)
                business_authors.append(cells[2].text)
                business_years.append(cells[3].text)
                business_volumes.append(cells[4].text)

        # Create a DataFrame for Business School Faculty
        df_business = pd.DataFrame({
            'Journal': business_journals,
            'Article': business_articles,
            'Author': business_authors,
            'Year': business_years,
            'Volume': business_volumes
        })

        # Save the DataFrame to a CSV file
        business_csv_filename = f'{school.replace(" ", "_").replace(",", "")}_Business_Faculty.csv'
        df_business.to_csv(business_csv_filename, index=False)
        print(f"Business School Faculty data for {school} saved to {business_csv_filename}")

    
    if len(tables) > 1:
        time.sleep(1)
        # Extract data from the "Publications by Non-Business School Faculty" table
        non_business_table = tables[1]
        non_business_rows = non_business_table.find_elements(By.TAG_NAME, "tr")
        
        # Initialize lists to store column data
        non_business_journals = []
        non_business_articles = []
        non_business_authors = []
        non_business_years = []
        non_business_volumes = []

        # Loop through each row and extract the data
        for row in non_business_rows[1:]:  # Skip the header row
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 5:  # Ensure there are 5 columns
                non_business_journals.append(cells[0].text)
                non_business_articles.append(cells[1].text)
                non_business_authors.append(cells[2].text)
                non_business_years.append(cells[3].text)
                non_business_volumes.append(cells[4].text)

        # Create a DataFrame for Non-Business School Faculty
        df_non_business = pd.DataFrame({
            'Journal': non_business_journals,
            'Article': non_business_articles,
            'Author': non_business_authors,
            'Year': non_business_years,
            'Volume': non_business_volumes
        })

        # Save the DataFrame to a CSV file
        non_business_csv_filename = f'{school.replace(" ", "_").replace(",", "")}_Non_Business_Faculty.csv'
        df_non_business.to_csv(non_business_csv_filename, index=False)
        print(f"Non-Business School Faculty data for {school} saved to {non_business_csv_filename}")

    # Optional: Add a short delay to avoid overwhelming the server
    time.sleep(2)

    # Close the browser
    driver.quit()