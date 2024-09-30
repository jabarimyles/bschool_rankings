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

# Ignore SSL certificate verification (for testing only)
ssl._create_default_https_context = ssl._create_unverified_context
# Initialize the WebDriver (using Chrome in this case)
# Make sure to replace 'chromedriver_path' with the actual path of your chromedriver
driver = uc.Chrome()

# Function to search a paper on Google Scholar
def search_google_scholar(paper_title):
    # Open Google Scholar
    driver.get("https://scholar.google.com/")
    time.sleep(random.uniform(3, 12))
    
    # Locate the search bar, input the paper title, and search
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(paper_title)
    search_box.send_keys(Keys.RETURN)
    
    # Wait for the search results to load
    time.sleep(random.uniform(3, 12))

# Function to retrieve citing papers (title and authors) and store in list of lists
def get_citing_papers(paper_title=''):
    citing_papers = []

    # Find the "Cited by" link for the first search result
    try:
        cited_by_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Cited by")
        cited_by_link.click()
        time.sleep(random.uniform(3, 12))
    except Exception as e:
        print(f"Error: {e}")
        return citing_papers
    
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

                # Append to the list of lists
                citing_papers.append([paper_title, title, authors])
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
    
    return citing_papers

# Function to perform the search and extraction for multiple paper titles
def search_and_extract_citing_papers(paper_titles):
    all_citing_papers = []

    # Loop through each paper title in the list
    for paper_title in paper_titles:
        time.sleep(300)
        # Search for the paper on Google Scholar
        print(f"Searching for: {paper_title}")
        search_google_scholar(paper_title)
        
        # Get the citing papers for the current paper
        citing_papers_list = get_citing_papers(paper_title)
        
        # Append results to the overall list
        all_citing_papers.extend(citing_papers_list)
    
    # Convert the list of lists to a pandas DataFrame
    citing_papers_df = pd.DataFrame(all_citing_papers, columns=["Paper Title", "Citing Title", "Authors"])

    return citing_papers_df

# Example usage
pub_data = pd.read_csv('Business_Faculty_Data.csv')
paper_titles = list(pub_data['Article'])

# Call the function to search and extract citing papers for all the paper titles
citing_papers_df = search_and_extract_citing_papers(paper_titles)

# Print the DataFrame
print(citing_papers_df)

# Close the browser once done
driver.quit()
