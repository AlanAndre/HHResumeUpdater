from random import uniform
from time import sleep

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException)
from webdriver_manager.chrome import ChromeDriverManager

import config

logger.add('updater.log', format='{time} {level} {message}',
           level='DEBUG', retention='5 days')


def browser_options():
    proxy = "socks5://localhost:9050"
    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server={proxy}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # don't need images
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    # options.add_argument("--headless")
    return options


@logger.catch  # Catches errors
def main(timer):
    while timer > 0:
        logger.info('Приступаю к работе')
        driver = webdriver.Chrome(options=browser_options(), executable_path=ChromeDriverManager().install())
        driver.get("http://check.torproject.org")
        # Start
        driver.get('https://hh.ru/')
        logger.info('Открыл браузер')
        # Enter
        driver.find_element_by_link_text('Войти').click()
        logger.info('Нажал кнопку "Войти"')
        sleep(uniform(1.0, 3.5))  # some random for good measure
        try:
            # Tries if there is a password field
            driver.find_elements_by_class_name('bloko-input')[2]
        except IndexError:
            driver.find_element_by_css_selector('span.bloko-link-switch').click()
        # Login
        login = driver.find_elements_by_class_name('bloko-input')
        login[1].send_keys(config.user_name)
        logger.info('Ввел номер телефона или почту')
        sleep(uniform(1.0, 3.5))
        # Password
        login[2].send_keys(config.password)
        logger.info('Ввел пароль')
        sleep(uniform(1.0, 3.5))
        # Enter
        try:
            driver.find_element_by_css_selector('.account-login-actions > button:nth-child(1)').click()
        except NoSuchElementException:
            driver.find_elements_by_class_name('bloko-form-row')[1].click()
        logger.info('Залогинился на сайт')
        sleep(3)
        # Enter resume
        driver.find_element_by_css_selector(".HH-Supernova-NaviLevel2-Link").click()
        # driver.find_element_by_link_text("Мои резюме").click()
        logger.info('Зашел во вкладку "Мои резюме"')
        sleep(2)
        # Поднимает в поиске резюме. Цикл для того, чтобы поднимать несколько резюме.
        for i in driver.find_elements_by_css_selector(".applicant-resumes-update-button"):
            try:
                i.click()
                logger.info('Поднял резюме в поиске')
                sleep(2)
            except ElementClickInterceptedException:
                logger.info('Еще рано! кнопка недоступна!')
        # Close
        driver.close()
        logger.info('Выключил браузер')
        # Counter
        timer -= 1
        logger.info(f'Перематываю счетчик, осталось отработать {timer} раз')
        # Waiting 4 hours and some random for good measure
        logger.info('Ложусь спать на 4 часа\n')
        sleep(60 * 60 * 4)
        logger.info('Проснулся')


if __name__ == '__main__':
    main(5)
