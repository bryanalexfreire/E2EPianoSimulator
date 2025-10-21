from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import logging

logger = logging.getLogger(__name__)

def create_driver(headless: bool = False):

    logger.info(f"Creando ChromeDriver (headless={headless})")
    options = webdriver.ChromeOptions()
    if headless:
        # En Chrome moderno se recomienda "--headless=new" para evitar limitaciones del headless clásico
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    # Aumenta estabilidad en UI: ventana grande y sin caché de perfil
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")

    # webdriver-manager descarga/gestiona la versión compatible de ChromeDriver automáticamente
    logger.info("Instalando/obteniendo ChromeDriver con webdriver-manager…")
    driver_path = ChromeDriverManager().install()
    logger.info(f"ChromeDriver en: {driver_path}")

    driver = webdriver.Chrome(
        service=ChromeService(driver_path),
        options=options
    )

    # Implicit wait pequeño para elementos simples; las esperas críticas usan WebDriverWait explícito
    driver.implicitly_wait(3)
    logger.info("Driver inicializado con implicit_wait=3s")
    return driver