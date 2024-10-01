import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager
import time
import undetected_chromedriver as uc
import ssl
import csv
import os

# Ignore SSL certificate verification (for testing only)
ssl._create_default_https_context = ssl._create_unverified_context
# Initialize the WebDriver (using Chrome in this case)
# Make sure to replace 'chromedriver_path' with the actual path of your chromedriver
driver = uc.Chrome()

# Function to search a paper on Google Scholar
def search_google_scholar(paper_title):
    # Open Google Scholar
    driver.get("https://scholar.google.com/")
    driver.execute_script("window.scrollTo(0, 50)")
    time.sleep(random.uniform(100, 120))  # Sleep to mimic human behavior
    
    # Locate the search bar, input the paper title, and search
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(paper_title)
    search_box.send_keys(Keys.RETURN)
    
    # Wait for the search results to load
    time.sleep(random.uniform(3, 12))

# Function to retrieve citing papers (title and authors) and directly append to CSV
def get_citing_papers(paper_title='', csv_writer=None):
    # Find the "Cited by" link for the first search result
    try:
        cited_by_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Cited by")
        cited_by_link.click()
        driver.execute_script("window.scrollTo(0, 50)")
        time.sleep(random.uniform(3, 12))
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Now we are on the page listing all citing papers
    # Extract titles and authors from the results
    while True:
        # Get all the result elements on the page
        results = driver.find_elements(By.CLASS_NAME, "gs_ri")

        for result in results:
            try:
                # Extract the title
                title = result.find_element(By.TAG_NAME, "h3").text
                
                # Extract the authors
                authors = result.find_element(By.CLASS_NAME, "gs_a").text

                # Append directly to the CSV
                csv_writer.writerow([paper_title, title, authors])
            except Exception as e:
                print(f"Error parsing result: {e}")
        
        # Check if there's a 'Next' button to go to the next page of results
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next")
            next_button.click()
            time.sleep(random.uniform(3, 12))
        except:
            # No more pages
            break

# Function to perform the search and extraction for multiple paper titles
def search_and_extract_citing_papers(paper_titles, output_file):
    # Check if the file is empty by attempting to read it briefly
    file_exists = os.path.exists(output_file)
    is_file_empty = not file_exists or os.path.getsize(output_file) == 0
    
    # Open CSV file in append mode
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        # Write the header only if the file is empty or does not exist
        if is_file_empty:
            csv_writer.writerow(["Paper Title", "Citing Title", "Authors"])
        
        # Loop through each paper title in the list
        for paper_title in paper_titles:
            time.sleep(5)
            # Search for the paper on Google Scholar
            print(f"Searching for: {paper_title}")
            search_google_scholar(paper_title)
            
            # Get the citing papers for the current paper and append to CSV
            get_citing_papers(paper_title, csv_writer)

# Example usage
pub_data = pd.read_csv('Business_Faculty_Data.csv')
paper_titles = list(pub_data['Article'])

# Call the function to search and extract citing papers for all the paper titles, saving directly to CSV
output_csv = 'citing_papers_output.csv'
search_and_extract_citing_papers(paper_titles, output_csv)

# Close the browser once done
driver.quit()