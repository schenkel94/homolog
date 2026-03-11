import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape job openings from InHire ATS
def scrape_jobs():
    url = 'https://www.inhire.com/jobs'  # Example URL (this should be the correct InHire jobs page)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    job_listings = []
    
    for job in soup.find_all('div', class_='job-listing'):  # Adjust selector based on real HTML structure
        title = job.find('h2').text.strip() if job.find('h2') else ''
        company = job.find('div', class_='company-name').text.strip() if job.find('div', class_='company-name') else ''
        location = job.find('div', class_='location').text.strip() if job.find('div', class_='location') else ''
        
        if 'data' in title.lower():  # Filter for data-related positions
            job_listings.append({'Title': title, 'Company': company, 'Location': location})
    
    return job_listings

# Streamlit application
def main():
    st.title("Job Openings in Startups")
    
    if st.button("Scrape Job Openings"):
        with st.spinner("Scraping job openings..."):
            job_listings = scrape_jobs()
        
        st.success(f"Found {len(job_listings)} job openings.")
        
        if job_listings:
            df = pd.DataFrame(job_listings)
            st.dataframe(df)

            # Export to Excel
            if st.button("Export to Excel"):
                df.to_excel("job_openings.xlsx", index=False)
                st.success("Exported to job_openings.xlsx")

if __name__ == "__main__":
    main()