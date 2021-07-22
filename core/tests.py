from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Create your tests here.

def test():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get('https://choosemypc.net/build/?budget=1170&oc=false')

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

        print(
            cpu.text + '\n' + mobo.text + '\n' + ram.text + '\n' + ssd.text + hdd.text + '\n' + gpu.text + '\n' + case.text + '\n' + power.text)
    finally:
        driver.quit()


test()
