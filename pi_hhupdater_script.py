import pickle
import sys
from datetime import datetime
from random import uniform
from time import sleep

import requests
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config


def browser_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # don't need images
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.add_argument("--headless")
    return options


def wait_12sec(driver, by, selector):
    return WebDriverWait(driver, 12).until(EC.element_to_be_clickable((by, selector)))


def try_finding_captcha(driver: webdriver.Chrome):
    try:
        driver.find_element(By.CSS_SELECTOR, ".HH-Supernova-NaviLevel2-Link")
    except NoSuchElementException:
        telegram_message(f'{datetime.now()}: Captcha found')
        print(f'{datetime.now()}: Captcha found')
        # closing and quiting just to be sure.
        driver.close()
        driver.quit()
        sys.exit()


def login(driver: webdriver.Chrome):
    """Tries if there is a password field"""
    wait_12sec(driver, By.LINK_TEXT, "Войти").click()
    print(f'{datetime.now()}: Enter button pressed')

    try:
        driver.find_element(By.XPATH, "//input[@type='password']")
    except NoSuchElementException:
        print(f'{datetime.now()}: No password field found')
        driver.find_element(By.XPATH, "//span[@class='bloko-link-switch']").click()

    # Login
    login_input = driver.find_element(
        By.XPATH,
        "//div[@class='bloko-form-item']//input[@type='text']"
    )
    # login_input.clear()
    login_input.send_keys(Keys.CONTROL + "a")
    login_input.send_keys(Keys.DELETE)
    login_input.send_keys(config.user_name)
    print(f'{datetime.now()}: Ввел номер телефона или почту')
    sleep(uniform(1.0, 3.5))

    # Password
    password_input = driver.find_element(By.XPATH, "//input[@type='password']")
    password_input.send_keys(config.password)
    print(f'{datetime.now()}: Ввел пароль')

    # Enter
    try:
        # New button
        driver.find_element(By.CSS_SELECTOR, '.account-login-actions > button:nth-child(1)').click()
    except NoSuchElementException:
        driver.find_elements(By.CLASS_NAME, 'bloko-form-row')[1].click()
    sleep(1)
    print(f'{datetime.now()}: Нажал кнопку "Войти"')

    try_finding_captcha(driver)
    try_finding_resumes(driver)


def load_pickle_cookies(driver: webdriver.Chrome) -> bool:
    """Load cookies. If there's none -> proceed to login"""
    try:
        with open("/home/pi/hh_resume_updater_Selenium/cookies.pkl", "rb") as pkl:
            cookies = pickle.load(pkl)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print(f'{datetime.now()}: Cookies added')
            return True

    except FileNotFoundError:
        print(f'{datetime.now()}: No cookies found')
        return False


def try_finding_resumes(driver: webdriver.Chrome):
    try:
        resumes = driver.find_element(By.CSS_SELECTOR, ".HH-Supernova-NaviLevel2-Link")
        resumes.click()
        print(f'{datetime.now()}: Зашел во вкладку "Мои резюме"')
    except NoSuchElementException:
        login(driver)
    except ElementClickInterceptedException:
        pass


def update_resumes(driver: webdriver.Chrome):
    """Поднимает в поиске все резюме"""
    resume_titles = driver.find_elements(By.XPATH, "//*[@data-qa='resume-title']")
    update_buttons = driver.find_elements(By.XPATH, "//*[@data-qa='resume-update-button']")

    for title, j in zip(resume_titles, update_buttons):
        try:
            if j.text == 'Поднимать автоматически':
                continue
            j.click()
            responses = telegram_message(f'Поднял резюме {title.text} в поиске')
            for response in responses:
                print(f'{datetime.now()}: Поднял резюме {title.text} в поиске {response}')
            sleep(2)
        except ElementClickInterceptedException:
            print(f'{datetime.now()}: Еще рано! кнопка недоступна!')
        except StaleElementReferenceException:
            pass


def telegram_message(message: str) -> list:
    responses = []
    for chat_id in config.CHAT_IDS:
        bot_api_token = config.BOT_API_TOKEN
        url = config.telegram_url

        params = {'chat_id': chat_id, 'text': message}
        responses.append(requests.get(url + bot_api_token + '/sendMessage', params=params))
    return responses


def main():
    print(f'Приступаю к работе: {datetime.now()}')

    with webdriver.Chrome(
            options=browser_options(),
            service=Service('/usr/lib/chromium-browser/chromedriver')
    ) as driver:
        driver.get('https://hh.ru/')
        print(f'{datetime.now()}: Открыл браузер')

        if load_pickle_cookies(driver):
            wait_12sec(driver, By.LINK_TEXT, "Войти").click()
            print(f'{datetime.now()}: Enter button pressed')
        else:
            login(driver)

        try_finding_resumes(driver)

        with open("cookies.pkl", "wb") as pkl:
            pickle.dump(driver.get_cookies(), pkl)
            print(f'{datetime.now()}: Cookies saved')

        update_resumes(driver)

        # Close
        print(f'{datetime.now()}: Выключил браузер')


if __name__ == '__main__':
    main()
