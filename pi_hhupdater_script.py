from datetime import datetime
from random import uniform
from sys import exit
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException)

import config


def browser_options():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # don't need images
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")
    return options


def main():
    print(f'Приступаю к работе: {datetime.now()}')
    with webdriver.Chrome(options=browser_options(), executable_path='/usr/lib/chromium-browser/chromedriver') as driver:
        # Start
        driver.get('https://hh.ru/')
        print(f'Открыл браузер: {datetime.now()}')
        # Enter
        driver.find_element_by_link_text('Войти').click()
        print(f'Нажал кнопку "Войти": {datetime.now()}')
        sleep(uniform(1.0, 3.5))  # some random for good measure
        try:
            # Tries if there is a password field
            driver.find_elements_by_class_name('bloko-input')[2]
        except IndexError:
            driver.find_element_by_css_selector('span.bloko-link-switch').click()
        # Login
        login = driver.find_elements_by_class_name('bloko-input')
        login[1].send_keys(config.user_name)
        print(f'Ввел номер телефона или почту: {datetime.now()}')
        sleep(uniform(1.0, 3.5))
        # Password
        login[2].send_keys(config.password)
        print(f'Ввел пароль: {datetime.now()}')
        sleep(uniform(1.0, 3.5))
        # Enter
        try:
            # New button
            driver.find_element_by_css_selector('.account-login-actions > button:nth-child(1)').click()
        except NoSuchElementException:
            driver.find_elements_by_class_name('bloko-form-row')[1].click()
        enter = driver.find_elements_by_class_name('bloko-form-row')
        enter[1].click()
        print(f'Залогинился на сайт: {datetime.now()}')
        sleep(3)
        # Enter resume
        try:
            driver.find_element_by_css_selector(".HH-Supernova-NaviLevel2-Link").click()
            print(f'Зашел во вкладку "Мои резюме": {datetime.now()}')
            sleep(2)
        except ElementClickInterceptedException:
            print(f"Something ain't right: {datetime.now()}\nShutting down")
            exit()
        # driver.find_element_by_link_text("Мои резюме").click()
        # Поднимает в поиске резюме. Цикл для того, чтобы поднимать несколько резюме.
        for i in driver.find_elements_by_css_selector(".applicant-resumes-update-button"):
            try:
                i.click()
                print(f'Поднял резюме в поиске: {datetime.now()}')
                sleep(2)
            except ElementClickInterceptedException:
                print(f'Еще рано! кнопка недоступна!: {datetime.now()}')
        # Close
        print(f'Выключил браузер: {datetime.now()}')


if __name__ == '__main__':
    main()
