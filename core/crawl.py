from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def chrome_crawl(budget):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    # budget = request.GET.get('budget')
    driver.get('https://choosemypc.net/build/?budget=' + budget + '&oc=false')

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'buildTable')))
        cpu = driver.find_element_by_xpath('//*[@id="cpu"]/td[3]/a')
        mobo = driver.find_element_by_xpath('//*[@id="mobo"]/td[3]/a')
        ram = driver.find_element_by_xpath('//*[@id="ram"]/td[3]/a')
        ssd = driver.find_element_by_xpath('//*[@id="ssd"]/td[3]/a')
        hdd = driver.find_element_by_xpath('//*[@id="hdd"]/td[3]/a')
        gpu = driver.find_element_by_xpath('//*[@id="gpu"]/td[3]/a')
        case = driver.find_element_by_xpath('//*[@id="case"]/td[3]/a')
        power = driver.find_element_by_xpath('//*[@id="psu"]/td[3]/a')
    finally:
        driver.quit()

    args = {'cpu': cpu.text, 'mobo': mobo.text, 'ram': ram.text, 'ssd': ssd.text, 'hdd': hdd.text,
            'gpu': gpu.text, 'case': case.text, 'power': power.text}
    return args