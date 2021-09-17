from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random
# Change path to you desired path
PATH = ''

company_name = ''
options = Options()
prefs={"download.default_directory": PATH}
options.add_experimental_option("prefs",prefs)


driver = webdriver.Chrome(executable_path='drivers/chromedriver.exe', chrome_options= options)
driver.set_window_size(1060, 700)
start = time.time()
driver.get('https://itdashboard.gov/')
driver.implicitly_wait(5)

# Clicking dive in button
driver.find_element_by_xpath('//*[@id="node-23"]/div/div/div/div/div/div/div/a').click()
print('button clicked')
driver.execute_script("window.scrollTo(0, 4500)")
driver.implicitly_wait(15)
time.sleep(5)
scraped_agencies = driver.find_elements_by_xpath('//*[@id="agency-tiles-widget"]/div/div/div/div/div/div')
print(len(scraped_agencies))
driver.implicitly_wait(2)
spendings= []
agencies = []
master_fixture = []
file = open('config.txt', 'r+')

for i in scraped_agencies:
    agencies.append(i.text.split('\n')[0])
    spendings.append(i.text.split('\n')[-2])
    master_fixture.append([i.text.split('\n')[0],i.text.split('\n')[-2]])

print(master_fixture)
agencies_data= pd.DataFrame(master_fixture, columns=['agencies', 'spendings'])
agencies_data.to_csv('Agencies.csv')
if len(file.readline()) == 0:
    file.write('Agencies:\n')
    for i in range(len(agencies)):
        file.write('{}\n'.format(agencies[i]))
    file.write('\nSelected:\n')
else:
    temp = file.read().split('\n')
    num = random.randint(0, len(scraped_agencies)-1)
    if temp[-1] == 'Selected:':
        print('Select a Department from config.txt and write the exact name under Selected section or there can be a random one selected for testing purpose')
        company_name = scraped_agencies[num].text.split('\n')[0]
        scraped_agencies[num].click()
    else:
        # scraped_agencies[agencies.index(temp[-1])].click()
        company_name = scraped_agencies[num].text.split('\n')[0]
        scraped_agencies[num].click()

file.close()


time.sleep(15)
# main_table = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td')
driver.find_element_by_xpath('//*[@id="investments-table-object_length"]/label/select').click()
driver.find_element_by_xpath('//*[@id="investments-table-object_length"]/label/select').send_keys('a')
time.sleep(10)
# Table Fetching
UII = []
total_entries = int(driver.find_element_by_xpath('//*[@id="investments-table-object_info"]').text.split(' ')[-2])
print(total_entries)
while len(UII) != total_entries:
    UII = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[1]')
    print('Loading table.....')
    time.sleep(3)
print('Done Loading Table')

Bureau  =   driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[2]')
Investment_title = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[3]')
Total_spending = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[4]')
type = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[5]')
CIO_rating = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[6]')
Projects = driver.find_elements_by_xpath('//*[@id="investments-table-object"]/tbody/tr/td[7]')

# Collecting links
Downloadables = []
links = driver.find_elements_by_xpath("//a[@href]")
if 'read' in links[51].get_attribute('href'):
    links= links[52:len(links)-8]
else:
    links= links[51:len(links)-8]

for link in links:
    Downloadables.append(link.get_attribute('href'))



individual_table = []
for i in range(len(UII)):
    individual_table.append([UII[i].text,Bureau[i].text,Investment_title[i].text,Total_spending[i].text,type[i].text,CIO_rating[i].text,Projects[i].text])
agency_table = pd.DataFrame(individual_table, columns=['UII','Bureau','Investment_title','Total_spending','type','CIO_rating','Projects'])
agency_table.to_csv('individual table for a department.csv')

for link in Downloadables:
    driver.get(link)
    driver.implicitly_wait(3)
    driver.find_element_by_xpath('//*[@id="business-case-pdf"]/a').click()
    time.sleep(5)



driver.close()




end = time.time()
print('time taken by scarper: ' ,end - start)