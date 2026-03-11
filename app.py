import time
from selenium import webdriver

# Set up the Selenium WebDriver
# Make sure to set the path to your WebDriver executable
browser = webdriver.Chrome(executable_path='/path/to/chromedriver')

# Navigate to the web page
browser.get('http://example.com')

# Wait for JavaScript to render
time.sleep(5)  # Adjust as necessary for the content to load

# Use browser.page_source or other Selenium methods
rendered_content = browser.page_source

# Remember to close the browser
browser.quit()