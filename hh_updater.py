import os
import pickle
from itertools import zip_longest
from random import uniform
from time import sleep

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from utils import config
from utils.telegram_message import send_telegram_message

logger.add('updater.log', format='{time} {level} {message}',
           level='DEBUG', retention='5 days')


def browser_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # don't need images
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    # options.add_argument("--headless")
    return options


def try_finding_captcha(driver: webdriver.Chrome):
    try:
        driver.find_element(By.XPATH, "//*[@data-qa='mainmenu_myResumes']")
    except NoSuchElementException:
        logger.debug('Captcha found. Pass it and push the button')
        sleep(12)
        logger.info('Залогинился на сайт')


def login(driver: webdriver.Chrome):
    """Tries to find if there is a password field"""
    driver.find_element(By.LINK_TEXT, "Войти").click()
    logger.info('Enter button pressed')

    try:
        driver.find_element(By.XPATH, "//input[@type='password']")
    except NoSuchElementException:
        logger.info('No password field found')
        driver.find_element(By.XPATH,
                            "//div[@class='account-login-actions']//button[@class='bloko-link bloko-link_pseudo']") \
            .click()

    # Login
    login_input = driver.find_element(
        By.XPATH,
        "//div[@class='bloko-form-item']//input[@type='text']"
    )
    # login_input.clear()
    login_input.send_keys(Keys.CONTROL + "a")
    login_input.send_keys(Keys.DELETE)
    login_input.send_keys(config.user_name)
    logger.info('Ввел номер телефона или почту')
    sleep(uniform(1.0, 3.5))

    # Password
    password_input = driver.find_element(By.XPATH, "//input[@type='password']")
    password_input.send_keys(config.password)
    logger.info('Ввел пароль')

    # Enter
    try:
        # New button
        driver.find_element(By.CSS_SELECTOR, '.account-login-actions > button:nth-child(1)').click()
    except NoSuchElementException:
        driver.find_elements(By.CLASS_NAME, 'bloko-form-row')[1].click()
    sleep(1)
    logger.info('Нажал кнопку "Войти"')

    try_finding_captcha(driver)
    try_finding_resumes(driver)


@logger.catch
def load_pickle_cookies(driver: webdriver.Chrome) -> bool:
    """Loads cookies. If there's none, proceeds to log in"""
    try:
        with open("cookies.pkl", "rb") as pkl:
            cookies = pickle.load(pkl)
            for cookie in cookies:
                driver.add_cookie(cookie)
            logger.info('Cookies added')
            return True

    except FileNotFoundError:
        logger.info('No cookies found')
        return False


def try_finding_resumes(driver: webdriver.Chrome) -> None:
    try:
        resumes = driver.find_element(By.XPATH, "//a[contains(text(),'Мои резюме')]")
        resumes.click()
        logger.info('Зашел во вкладку "Мои резюме"')
    except NoSuchElementException:
        login(driver)
    except ElementClickInterceptedException:
        pass


def update_resumes(driver: webdriver.Chrome):
    """Поднимает в поиске все резюме"""
    resume_titles = driver.find_elements(By.XPATH, "//*[@data-qa='resume-title']")
    update_buttons = driver.find_elements(By.XPATH, "//button[@data-qa='resume-update-button']")

    print(f"{len(resume_titles)=}, {len(update_buttons)=}")

    for title, button in zip_longest(resume_titles, update_buttons, fillvalue='resume'):
        try:
            if button.text == 'Поднимать автоматически':
                continue
            button.click()
            try:
                response = send_telegram_message(f'Поднял резюме {title.text} в поиске')
                logger.info(f'Поднял резюме {title.text} в поиске {response}')
                sleep(2)
            except AttributeError:
                logger.debug(title, button)
        except ElementClickInterceptedException:
            logger.debug('Еще рано! кнопка недоступна!')
        except StaleElementReferenceException:
            pass


@logger.catch
def main():
    logger.info('Приступаю к работе')
    s = Service(ChromeDriverManager().install())

    with webdriver.Chrome(
            options=browser_options(),
            service=s
    ) as driver:
        driver.get('https://hh.ru/')
        logger.info('Открыл браузер')
        driver.implicitly_wait(12)

        if load_pickle_cookies(driver):
            driver.find_element(By.LINK_TEXT, "Войти").click()
            logger.info('Enter button pressed')
        else:
            login(driver)

        try_finding_resumes(driver)

        with open("cookies.pkl", "wb") as pkl:
            pickle.dump(driver.get_cookies(), pkl)
            logger.info('Cookies saved')

        update_resumes(driver)

        # Manual check if all is OK
        sleep(10)

        # Close
        logger.info('Выключил браузер')


if __name__ == '__main__':

    user_input = 'y'
    # user_input = input('Do you want to log in as last user: y/N?/n').lower()

    if user_input in ('y', 'yes', 'да', 'д'):
        pass
    else:
        try:
            logger.debug('Removing cookies if there are any')
            os.remove('cookies.pkl')
        except FileNotFoundError:
            logger.debug('no cookies found')
    main()
