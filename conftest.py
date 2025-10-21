from time import sleep

import pytest
from utils.driver_factory import create_driver

def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        help="Browser runs in headless mode",
    )

@pytest.fixture()
def driver(request):
    headless = request.config.getoption("--headless")
    driver = create_driver(headless=headless)
    yield driver

    sleep(5)
    driver.quit()
