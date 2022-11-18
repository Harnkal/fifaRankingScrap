# Loading required packages
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
import warnings


def recurring_click(web_driver, xpath):
    wait = WebDriverWait(web_driver, 20)
    count = 0
    while count < 10:
        try:
            wait.until(ec.element_to_be_clickable((By.XPATH, xpath))).click()
            return True
        except WebDriverException:
            time.sleep(0.5)
            count += 1


def get_drop_down_elements(web_driver):
    recurring_click(web_driver, '/html/body/div[1]/div/div[3]/main/section[1]/div/div/div[1]/div[2]/div/button/div')

    return web_driver.find_elements('xpath',
                                    '/html/body/div[1]/div/div[3]/main/section[1]/div/div/div[1]/div[2]/div/div/button')


def scrape_current_page(page_date, web_driver):
    df = pd.DataFrame(columns=['rank', 'country', 'points', 'date'])
    row_elements = web_driver.find_elements('xpath',
                                            "/html/body/div[1]/div/div[3]/main/section[2]/div/div/div[1]/table/tbody/tr")

    for elem in row_elements:
        rank = elem.text.split('\n')[0]
        country = elem.text.split('\n')[1]
        points = elem.text.split('\n')[2].split(' ')[0]
        df = df.append({'rank': rank, 'country': country, 'points': points, 'date': page_date}, ignore_index=True)

    return df


def next_page(web_driver):
    recurring_click(web_driver,
                    'html/body/div[1]/div/div[3]/main/section[2]/div/div/div[2]/div/div/div/div/div[3]/div/button')


if __name__ == "__main__":
    warnings.simplefilter(action='ignore', category=FutureWarning)
    # Setup
    home_page = 'https://www.fifa.com/fifa-world-ranking/men'  # Set home page
    options = webdriver.ChromeOptions()  # Set webdriver options
    options.add_argument('--no-sandbox')  # Set webdriver options
    options.add_argument('ignore-certificate-errors')  # Set webdriver options
    driver = webdriver.Chrome(options=options)  # Initiate webdriver
    driver.get(home_page)  # Get driver to retrieve homepage
    driver.implicitly_wait(3)  # Wait for page to load
    try:
        driver.find_element('xpath', '//*[@id="onetrust-accept-btn-handler"]').click()  # Accept cookies
    except WebDriverException:
        pass
    dropdown_size = len(get_drop_down_elements(driver))  # Get dropdown size
    data_list = []  # Data List
    master_df = pd.DataFrame(columns=['rank', 'country', 'points', 'date'])  # Create master df
    driver.get(home_page)  # Get driver to retrieve homepage

    # Getting data from all elements
    for i in range(dropdown_size):
        dd_elements = get_drop_down_elements(driver)
        date = dd_elements[i].text
        print(date)
        dd_elements[i].click()
        df_i = scrape_current_page(date, driver)
        master_df = pd.concat([master_df, df_i])
        next_page(driver)
        df_i2 = scrape_current_page(date, driver)
        while not df_i.equals(df_i2):
            df_i = df_i2
            master_df = pd.concat([master_df, df_i])
            next_page(driver)
            df_i2 = scrape_current_page(date, driver)

    master_df.to_csv("fifa_rankings.csv")
