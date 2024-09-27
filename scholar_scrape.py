import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import pickle
import time

# Search for a paper by title on Google Scholar
def search_scholar(title):
    search_url = "https://scholar.google.com/scholar"
    params = {"q": title}
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: {response.status_code}")
        return None

# Parse search results and get citation link
def parse_results_for_citation_link(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    citation_link = None

    # Parse the search results
    for entry in soup.select(".gs_r.gs_or.gs_scl"):
        citation_info = entry.select_one(".gs_fl a:nth-of-type(3)")
        if citation_info:
            citation_link = citation_info["href"]
            break  # Only take the first result for simplicity
    
    return citation_link

# Scrape titles and authors of citing papers
def scrape_citing_papers(citation_link):
    start_num=0
    found_cites=True
    citing_papers = []
    while found_cites:

        base_url = "https://scholar.google.com"
        full_citation_url = base_url + citation_link + '&start=' + str(start_num)
        headers = {"User-Agent": "Mozilla/5.0"}
        time.sleep(1.5)
        response = requests.get(full_citation_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            if len(soup.select(".gs_r.gs_or.gs_scl")) < 1:
                return citing_papers
            # Parse the titles and authors of citing papers
            for entry in soup.select(".gs_r.gs_or.gs_scl"):
                title_element = entry.select_one(".gs_rt a")
                author_element = entry.select_one(".gs_a")

                if title_element and author_element:
                    paper_title = title_element.text
                    paper_authors = author_element.text.split(' - ')[0]  # Extract authors from the author-info string
                    citing_papers.append({
                        "title": paper_title,
                        "authors": paper_authors.split('\xa0')[0]
                    })
        start_num +=10
    return citing_papers


def run_main():
    pub_data = pd.read_csv('Business_Faculty_Data.csv')
    titles = list(pub_data['Article'])
    cite_lst = []
    for paper_title in titles:
        #paper_title = "Base-stock policies are close to optimal for newsvendor networks"
        html_content = search_scholar(paper_title)

        if html_content:
            citation_link = parse_results_for_citation_link(html_content)
            
            if citation_link:
                citing_papers = scrape_citing_papers(citation_link)
                
                print(f"Papers citing '{paper_title}':")
                for i, paper in enumerate(citing_papers, 1):
                    print(f"{i}. Title: {paper['title']}")
                    print(f"   Authors: {paper['authors']}")
                    print("-" * 80)
                    cite_lst.append([paper_title, paper['title'], paper['authors']] )
                    with open("cite_lst", "wb") as fp:   #Pickling
                        pickle.dump(cite_lst, fp)
            else:
                print("No citation link found.")
        else:
            print("No search results found.")
    cite_df = pd.DataFrame(cite_lst, columns=['Paper Cited', 'Citing Paper ', 'Authors'])
    cite_df.to_csv('')
if __name__ == '__main__':
    run_main()
