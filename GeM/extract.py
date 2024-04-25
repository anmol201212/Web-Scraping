# Import the necessary libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime



def startfun(): 

    options = Options()
    options.add_argument("--headless")

    browser = webdriver.Chrome(options=options)
    # browser = webdriver.Chrome()
    browser.get("https://bidplus.gem.gov.in/all-bids")
    
    
    # Wait for the page to fully load
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'card')))
    
    # Creating empty DataFrame with columns
    columns1 = ['Bid Number', 'RA Number', 'Items', 'Quantity', 'Department', 'Start Date', 'End Date']
    df1 = pd.DataFrame(columns=columns1)
    
    
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    total_no_of_pages = int(soup.find_all("a", class_="page-link")[-2].decode_contents())
    cards = None
    
    # for loop to iterage through the pages
    for i in range(2,10):
    # for i in range(2, total_no_of_pages):
    
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'card')))   
    
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        # Find all card elements
        cards = soup.find_all('div', class_='card')
    
        data = extract_data(cards)
    
        df1 = pd.concat([df1, data], ignore_index=True)
    
        # Find the button and click
        button = browser.find_element(By.LINK_TEXT, str(i))
        button.click()
    
    items = ["Transformer","Services","Generation","REPAIRS","MACHINE"]
    department = ["Ministry of Coal","Heavy Industries","Petroleum and Natural Gas","Civil Aviation","EducationDepartment"]
    df1['End Date'] = pd.to_datetime(df1['End Date'], format='%d-%m-%Y %I:%M %p')

    # Get current time
    current_time = datetime.now()

    # Filter DataFrame for rows where time is greater than current time
    filtered_df = df1[df1['End Date'] > current_time]
    filtered_df['End Date'] = filtered_df['End Date'].dt.strftime('%d-%m-%Y %I:%M %p')
    
    # Close the browser after the loop finishes
    browser.quit()

    return items,department,filtered_df


# Define a function to wait for the page to fully load

 
def extract_data(cards):
    # Initialize lists to store data
    bid_numbers = []
    ra_numbers = []
    items = []
    quantities = []
    departments = []
    start_dates = []
    end_dates = []
 
    # Extract data from each card
    for card in cards:
 
        bid_number = card.find('a', class_='bid_no_hover').text.strip()
        bid_numbers.append(bid_number)
       
 
        try:
            ra_number = card.find_all('a', class_='bid_no_hover')[1].text.strip()
            ra_numbers.append(ra_number)
        except:
            ra_numbers.append(0)
 
       
        temp = list(i['data-content'] for i in card.findAll("a", attrs={"data-content":True}))
        if temp!=[]:
            item = temp[0]
        else:
            item = card.findAll('div', class_="row")[1].get_text(strip=True).split(":")[1]
        items.append(item)
       
        quantity = card.find('strong', string='Quantity:').next_sibling.strip()
        quantities.append(quantity)
       
        department = card.find('strong', string='Department Name And Address:').find_next('div').text.strip()
        departments.append(department)
       
        start_date = card.find('strong', string='Start Date:').find_next_sibling().text.strip()
        start_dates.append(start_date)
       
        end_date = card.find('strong', string='End Date:').find_next_sibling().text.strip()
        end_dates.append(end_date)
 
    # Create a DataFrame
    data = {
        'Bid Number': bid_numbers,
        'RA Number': ra_numbers,
        'Items': items,
        'Quantity': quantities,
        'Department': departments,
        'Start Date': start_dates,
        'End Date': end_dates
    }
    df = pd.DataFrame(data)
 
    return df