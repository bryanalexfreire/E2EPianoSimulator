from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

class BasePage:

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def visit(self, url: str):
        self.driver.get(url)

    def click(self, locator: tuple[By, str]):
        self.driver.find_element(*locator).click()

    def type_text(self, locator: tuple[By, str], text: str):
        element = self.driver.find_element(*locator)
        element.clear()
        element.send_keys(text)

    def get_element_text(self, locator: tuple[By, str]) -> str:
        return self.driver.find_element(*locator).text

    def is_element_visible(self, locator: tuple[By, str]) -> bool:
        element = self.driver.find_element(*locator)
        return element.is_displayed()

    def get_current_url(self) -> str:
        return self.driver.current_url

    def type_keys(self, key: str, timeout: int = 20):
        body = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.TAG_NAME, "body"))
        )
        body.send_keys(key)

    def click_if_visible(self, locator, timeout: int = 10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            element.click()
            return True
        except Exception as e:
            logger.warning(f"Elemento {locator} no visible: {str(e)}")
            return False

    def get_class_attribute(self, locator: tuple[By, str]) -> str:
        element = self.driver.find_element(*locator)
        return element.get_attribute("class")


    def _ensure_mark_active(self, locator: tuple[By, str]) -> None:
        # No desempaquetar el locator al consultar la clase
        classes = self.get_class_attribute(locator)
        if classes != "mark active":
            self.driver.find_element(*locator).click()

    def has_query_flag(url: str, flag: str) -> bool:
        """
        Devuelve True si la query de la URL contiene el token exacto `flag` (p.ej. '1g'),
        considerando queries sin clave (ej: '?1g') y múltiples tokens separados por '&'.
        """
        q = urlsplit(url).query  # para 'https://.../piano?1g' -> '1g'
        if not q:
            return False
        tokens = q.split("&")
        return any(t == flag for t in tokens)

