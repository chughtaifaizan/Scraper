from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random
import os

# Change path to you desired path
PATH = ''


class scraper:
    company_name = ''
    all_elements = []
    found = False

    def __init__(self, path_to_webdriver):
        self.company_name = ''
        options = Options()
        prefs = {"download.default_directory": PATH}
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(executable_path=path_to_webdriver, chrome_options=options)
        self.driver.set_window_size(1060, 700)

    def get_all_agencies(self):
        driver = self.driver
        driver.get('https://itdashboard.gov/')
        driver.implicitly_wait(5)
        # Clicking dive in button
        driver.find_element_by_xpath('//*[@id="node-23"]/div/div/div/div/div/div/div/a').click()
        print('button clicked')
        driver.execute_script("window.scrollTo(0, 2000)")
        driver.implicitly_wait(15)
        time.sleep(5)
        scraped_agencies = driver.find_elements_by_xpath('//*[@id="agency-tiles-widget"]/div/div/div/div/div/div')
        # driver.implicitly_wait(2)
        # if os.path.exists('config.txt'):
        #     file = open('config.txt', 'r+')
        # else:
        #     file = open('config.txt', 'w')
        # if len(file.readline()) == 0:
        #     file.write('Agencies:\n')
        #     for i in range(len(agencies)):
        #         file.write('{}\n'.format(agencies[i]))
        #     file.write('\nSelected:\n')
        # else:
        #     temp = file.read().split('\n')
        #     num = random.randint(0, len(scraped_agencies)-1)
        #     if temp[-1] == 'Selected:':
        #         print('Select a Department from config.txt and write the exact name under Selected section or there can be a random one selected for testing purpose')
        #         self.company_name = scraped_agencies[num].text.split('\n')[0]
        #         scraped_agencies[num].click()
        #     else:
        #         # scraped_agencies[agencies.index(temp[-1])].click()
        #         self.company_name = scraped_agencies[num].text.split('\n')[0]
        #         scraped_agencies[num].click()
        master_fixture = [[agency.text.split('\n')[0], agency.text.split('\n')[-2]] for agency in scraped_agencies]
        agencies_data = pd.DataFrame(master_fixture, columns=['agencies', 'spendings'])
        agencies_data.to_csv('Agencies.csv')
        print(agencies_data)
        self.all_elements = scraped_agencies
        return print('Agencies.csv created.')

    def get_config(self):
        if os.path.exists('config.txt'):
            return print('config file exists.')
        else:
            file = open('config.txt', 'w+')
            file.write('Agencies:\n')
            import pandas as pd
            data = pd.read_csv('Agencies.csv')
            for name in data[['agencies']]:
                file.write(name + '\n')
            file.write('Selected:\n')
            file.close()
            return print('config file created.')

    def go_to_dept(self):
        elems = self.all_elements
        try:
            file = open('config.txt', 'r+')
            temp = file.read().split('\n')
            if temp[-2] == 'Selected:':
                print(
                    'Could not find a specific Department under Selected section \nA random Department will be selected')
                num = random.randint(0, len(elems) - 1)
                self.company_name = elems[num].text.split('\n')[0]
                elems[num].click()
            else:
                names = [name.text for name in elems]
                self.company_name = temp[-2]
                index = names.index(self.company_name)
                elems[index].click()

            file.close()
        except:
            import sys
            Exception('File not found')
            sys.exit()

    def individual_table(self, file_path=None):
        driver = self.driver
        # main_table = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td')
        driver.find_element_by_xpath('//*[@id="investments-table-object_length"]/label/select').click()
        driver.find_element_by_xpath('//*[@id="investments-table-object_length"]/label/select').send_keys('a')
        # Table Fetching
        UII = []
        total_entries = int(
            driver.find_element_by_xpath('//*[@id="investments-table-object_info"]').text.split(' ')[-2])
        print(total_entries)
        while len(UII) != total_entries:
            UII = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[1]')
            print('Loading table.....')
            time.sleep(3)
        print('Done Loading Table')

        Bureau = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[2]')
        Investment_title = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[3]')
        Total_spending = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[4]')
        type = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[5]')
        CIO_rating = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[6]')
        Projects = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[7]')

        # Collecting links
        print('Collecting Downloadable links.')
        links = driver.find_elements_by_xpath("//a[@href]")
        if 'read' in links[51].get_attribute('href'):
            links = links[52:len(links) - 8]
        else:
            links = links[51:len(links) - 8]
        print('Downloadable links collected.')
        Downloadables = [link.get_attribute('href') for link in links]
        individual_table = []
        for i in range(len(UII)):
            individual_table.append(
                [UII[i].text, Bureau[i].text, Investment_title[i].text, Total_spending[i].text, type[i].text,
                 CIO_rating[i].text, Projects[i].text])
        agency_table = pd.DataFrame(individual_table,
                                    columns=['UII', 'Bureau', 'Investment_title', 'Total_spending', 'type',
                                             'CIO_rating', 'Projects'])
        agency_table.to_csv(self.company_name + '.csv')

        for link in Downloadables:
            driver.get(link)
            driver.implicitly_wait(3)
            driver.find_element_by_xpath('//*[@id="business-case-pdf"]/a').click()
            time.sleep(5)

        driver.close()

        end = time.time()
        # print('time taken by scarper: ' ,end - start)

    def run(self):
        self.get_all_agencies()
        self.get_config()
        self.go_to_dept()
        self.individual_table()

