from time import sleep
import logging
from pathlib import Path

import pytest
from utils.driver_factory import create_driver


_LOG_CONFIGURED = False


def _setup_logging() -> None:
    global _LOG_CONFIGURED
    if _LOG_CONFIGURED:
        return

    reports_dir = Path(__file__).resolve().parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    log_file = reports_dir / "test.log"

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Evitar duplicados si pytest reconfigura
    for h in list(root.handlers):
        root.removeHandler(h)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Consola
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Archivo
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # Reducir ruido de terceros
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    _LOG_CONFIGURED = True


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        help="Browser runs in headless mode",
    )


def pytest_configure(config):
    _setup_logging()
    logging.getLogger(__name__).info("Pytest configurado. Logging inicializado.")


@pytest.fixture()
def driver(request):
    _setup_logging()
    logger = logging.getLogger(__name__)

    headless = request.config.getoption("--headless")
    logger.info(f"Inicializando driver de navegador (headless={headless})")

    driver = create_driver(headless=headless)

    try:
        caps = getattr(driver, "capabilities", {}) or {}
        browser_name = caps.get("browserName") or "unknown"
        browser_ver = caps.get("browserVersion") or caps.get("version") or "unknown"
        logger.info(f"Driver listo: {browser_name} {browser_ver}")
    except Exception as e:
        logger.warning(f"No se pudieron leer las capabilities del driver: {e}")

    yield driver

    logger.info("Cerrando driver en 5s…")
    sleep(5)
    driver.quit()
    logger.info("Driver cerrado correctamente.")
