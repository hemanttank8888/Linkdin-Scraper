from datetime import datetime
import pandas as pd
import os
import logging
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from bs4 import BeautifulSoup
from lxml import etree


class LinkedInSearcher:
    def __init__(self, 
                headless,
                output_directory,
                input_file,
                sheet_name,
                driver = None
                ):
        """
        Initialize Selenium WebDriver with advanced configuration and progress tracking

        Args:
            headless (bool): Run browser in headless mode
            max_workers (int): Maximum number of concurrent searches
            progress_file (str): Path to save extraction progress
            output_file (str): Path to save LinkedIn URLs
        """
        self.input_file = input_file 
        self.sheet_name = sheet_name 
        self.output_directory = output_directory
        self.driver = driver
        self.success_output_file = []
        self.not_successful_searches = []
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    def linkdin_window(self):
        self.driver.execute_script("window.open('https://www.google.com', '_blank');")
        windows = self.driver.window_handles
        print("Window handles:", windows)

        # Switch to the new window (index 1 since it's the second window)
        self.driver.switch_to.window(windows[1])
        self.driver.get('https://www.linkedin.com/')
        time.sleep(5)
        sign_in_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Sign in with email")]'))
        )

        sign_in_button.click()
        email_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@aria-label="Email or phone"]'))
        )
        email_input.send_keys('#######################################')
        time.sleep(random.randint(5, 10))
        password_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@aria-label="Password"]'))
        )
        password_input.send_keys('####################################')
        time.sleep(random.randint(5, 10))
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Sign in"]'))
        )
        login_button.click()
        # Get the list of window handles
        return self.driver, windows
        
    def setup_chrome_options(self):
        """
        Configure Chrome options with enhanced stealth and performance
        
        Returns:
            Configured Chrome Options
        """
        chrome_options = Options()
        
        # Expanded user agent rotation with more recent versions
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
            # "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.6; rv:92.0) Gecko/20100101 Firefox/92.0"
        ]
        chrome_options.add_argument(f"user-agent={user_agents[0]}")

        # Enhanced performance and anti-detection options
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        # Advanced stealth options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        # chrome_options.add_argument("--headless")

        return chrome_options
    
    def get_linkdin_url(self):
        df_pdf_data = pd.read_excel(self.input_file, sheet_name='Sheet1')
        if 'Website' not in df_pdf_data.columns:
            if 'Website' not in df_pdf_data.columns:
                raise ValueError("Excel file must contain a 'Website' column")
        chrome_options = self.setup_chrome_options()
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver, windows = self.linkdin_window()
        self.driver.switch_to.window(windows[0])

        for index, row in df_pdf_data[:].iterrows():
            website = str(row['Website'])
            print(website)
            time.sleep(random.uniform(15, 20))
            search_query = f'site:linkedin.com "{website}"'
            self.driver.get("https://www.google.com")
            time.sleep(random.uniform(3, 6))
            search_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            dict_data = {"Website": website, "LinkedIn URL": "Url Not Found", "industry": "industry Not font"}
            # url_xpath = "//*[@id='rso']/div[1]/div/div/div/div[1]/div/div/span/a"
            url_xpath = "//*[@id='rso']/div[1]/div/div/div/div[1]/div/div//span/a"
            try:
                url_element = self.driver.find_element(By.XPATH, url_xpath)
                linkedin_url = url_element.get_attribute('href')
                dict_data["LinkedIn URL"] = linkedin_url
            except NoSuchElementException:
                self.logger.warning(f"No LinkedIn URL found for {website}")
            # if dict_data['LinkedIn URL'] != "Url Not Found":
            #     successful_searches.append(dict_data)
            #     df = pd.DataFrame(successful_searches)
            #     df.to_excel(file_path_output, index=False, sheet_name='Sheet1')
            if dict_data["LinkedIn URL"] == "Url Not Found":
                self.not_successful_searches.append(dict_data)
                model_dir_path = os.path.join(self.output_directory, "url_not_found")
                if not os.path.exists(model_dir_path):
                    os.makedirs(model_dir_path)
                not_found_output_data = os.path.join(model_dir_path,  "not found output_data.xlsx")
                df = pd.DataFrame(self.not_successful_searches)
                df.to_excel(not_found_output_data, index=False, sheet_name='Sheet1')
            else:
                    try:
                        dict_data["LinkedIn URL"] = str(dict_data["LinkedIn URL"])
                        time.sleep(random.randint(4, 8))
                        self.driver.get(dict_data["LinkedIn URL"])
                        time.sleep(random.randint(4, 8))
                        print(dict_data["LinkedIn URL"])
                        dict_data["LinkedIn URL"] = dict_data["LinkedIn URL"].split("?")[0]
                    except Exception as e:
                        self.logger.warning(f"pliting linkdin url  {e}")
                    tree = ""
                    try:
                        about_url = dict_data["LinkedIn URL"] + "/about/"
                        print(about_url)
                        self.driver.get(about_url)
                        time.sleep(random.randint(4, 8))
                        page_source = self.driver.page_source
                        soup = BeautifulSoup(page_source, 'html.parser')
                        tree = etree.HTML(str(soup))
                    except Exception as e:
                        self.logger.warning(f"error in request fire about page  {e}")
                    dict_data['industry'] = ""
                    try:
                        dict_data['industry'] = tree.xpath('//h3[contains(text(), "Industry")]/parent::dt/following-sibling::dd[1]')
                    except Exception as e:
                        print(f"error in industry {e}")
                    try:
                        if dict_data['industry']:
                            dict_data['industry'] = dict_data['industry'][0].text.strip()
                        else:
                            print(f"industry not found.")
                            dict_data['industry'] = ""
                    except Exception as e:
                        self.logger.warning(f"error in industry get {e}")
                    print(dict_data['industry'])
                    # with open(f'{index}page_source.html', 'w', encoding='utf-8') as file:
                    #     file.write(page_source)
                    if dict_data['industry'] != "":
                        self.success_output_file.append(dict_data)
                        time.sleep(random.randint(5, 10))
                        
                        model_dir_path = os.path.join(self.output_directory, "found_url")
                        if not os.path.exists(model_dir_path):
                            os.makedirs(model_dir_path)
                        current_date = datetime.now().strftime('%Y-%m-%d')
                        output_data = os.path.join(model_dir_path,  f"found output_data {current_date}.xlsx")
                        df = pd.DataFrame(self.success_output_file)
                        df.to_excel(output_data, index=False)


def main():
    if not os.path.exists("output_file"):
        os.makedirs("output_file")
    output_directory = os.path.join(os.getcwd(), 'output_file')
    searcher = LinkedInSearcher(
        headless=False,
        output_directory=output_directory,
        input_file=r"C:\Users\HemantTank\Downloads\ziippiiing\ziippiiing\testing.xlsx",
        sheet_name= "Sheet1",
        driver=None
    )

    try:
        searcher.get_linkdin_url()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
