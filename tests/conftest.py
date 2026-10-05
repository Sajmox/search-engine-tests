import logging

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pages.duckduckgo_page import DuckDuckGoPage

logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("WDM").setLevel(logging.WARNING)


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield browser
    browser.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.failed and report.when in ("setup", "call") and "driver" in item.funcargs:
        try:
            allure.attach(
                item.funcargs["driver"].get_screenshot_as_png(),
                name=f"failure_{report.when}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
    if report.failed and call.excinfo:
        print(f"\n>>> {call.excinfo.typename}: {call.excinfo.value}\n", flush=True)


@pytest.fixture
def searched_page(driver, book_name):
    page = DuckDuckGoPage(driver)
    page.open_and_search(book_name)
    return page
