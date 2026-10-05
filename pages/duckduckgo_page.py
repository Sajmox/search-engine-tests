import logging

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class DuckDuckGoPage:
    URL = "https://duckduckgo.com/"

    SEARCH_INPUT = (By.CSS_SELECTOR, "[placeholder='Search privately']")
    DUCKBAR = (By.CSS_SELECTOR, "[data-testid='duckbar']")
    IMAGES_TAB = (By.LINK_TEXT, "Images")
    REGION_DROPDOWN_ACTIVATE_BUTTON = (By.XPATH, "(//*[@data-testid='region-filter-label'])[2]")
    PANEL_DROPDOWN = (By.CSS_SELECTOR, "[data-trigger='MenuTrigger']")
    REGION_ANY_OPTION = (By.XPATH, ".//*[normalize-space()='All regions']")
    SIZE_DROPDOWN_ACTIVATE_BUTTON = (By.XPATH, "//button[normalize-space()='All sizes']")
    SIZE_WALLPAPER_OPTION = (By.XPATH, ".//*[normalize-space()='Wallpaper']")
    LICENSE_DROPDOWN_ACTIVATE_BUTTON = (By.XPATH, "//button[normalize-space()='All Licenses']")
    LICENSE_PUBLIC_DOMAIN_OPTION = (By.XPATH, ".//*[normalize-space()='Public Domain']")
    IMAGE_RESULTS = (By.CSS_SELECTOR, "ol > li")

    def __init__(self, driver: WebDriver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _visible(self, locator: tuple) -> WebElement:
        def found(driver: WebDriver):
            try:
                for el in driver.find_elements(*locator):
                    try:
                        if el.is_displayed():
                            return el
                    except StaleElementReferenceException:
                        continue
            except StaleElementReferenceException:
                return False
            return False

        return self.wait.until(found, message=f"No visible element: {locator}")

    def _click(self, locator: tuple) -> None:
        self._visible(locator).click()

    def _select(self, label: str, dropdown: tuple, option: tuple) -> None:
        logger.info("  %s — opening menu", label)
        self._click(dropdown)

        def option_ready(driver: WebDriver):
            try:
                for panel in driver.find_elements(*self.PANEL_DROPDOWN):
                    if not panel.is_displayed():
                        continue
                    for el in panel.find_elements(*option):
                        if el.is_displayed():
                            return el
            except StaleElementReferenceException:
                return False
            return False

        self.wait.until(
            option_ready,
            message=f"Option not found in menu: {label}",
        ).click()
        logger.info("  %s — OK", label)

    def open_and_search(self, book_name: str) -> None:
        logger.info("Search: book %s", book_name)
        self.driver.get(self.URL)
        field = self.wait.until(EC.visibility_of_element_located(self.SEARCH_INPUT))
        field.send_keys(f"book {book_name}", Keys.ENTER)

    def open_images(self) -> None:
        logger.info("Open Images tab")
        duckbar = self.wait.until(EC.visibility_of_element_located(self.DUCKBAR))
        duckbar.find_element(*self.IMAGES_TAB).click()

    def apply_filters(self) -> None:
        logger.info("Filters:")
        self._select("Region → All regions", self.REGION_DROPDOWN_ACTIVATE_BUTTON, self.REGION_ANY_OPTION)
        self._select("Size → Wallpaper", self.SIZE_DROPDOWN_ACTIVATE_BUTTON, self.SIZE_WALLPAPER_OPTION)
        self._select("License → Public Domain", self.LICENSE_DROPDOWN_ACTIVATE_BUTTON, self.LICENSE_PUBLIC_DOMAIN_OPTION)

    def get_results(self) -> list[WebElement]:
        self.wait.until(EC.presence_of_element_located(self.IMAGE_RESULTS))
        results = self.driver.find_elements(*self.IMAGE_RESULTS)
        logger.info("Tiles in grid: %s", len(results))
        return results

    def source_of(self, result: WebElement) -> str:
        nodes = []
        if result.get_attribute("title"):
            nodes.append(result)
        nodes.extend(result.find_elements(By.XPATH, ".//*[@title]"))
        source = (nodes[1].get_attribute("title") or "").strip()
        logger.info("3rd tile title: %s", source)
        return source

    def size_of(self, result: WebElement) -> tuple[int, int]:
        label = result.find_element(By.CSS_SELECTOR, "div").text.lower().replace("×", "x")
        logger.info("First div text: %r", label.strip())
        parts = [p for p in label.replace("x", " ").split() if p.isdigit()]
        width, height = int(parts[0]), int(parts[1])
        logger.info("Size: %s x %s", width, height)
        return width, height
