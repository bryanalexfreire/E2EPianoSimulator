from time import sleep
import logging
from pathlib import Path
import base64
from html import escape as html_escape
from typing import Optional, Tuple

import pytest
from utils.driver_factory import create_driver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


_LOG_CONFIGURED = False


def _setup_logging() -> None:
    # Idempotente: evita reconfigurar el root logger varias veces durante la sesión de pytest.
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

    # Archivo (modo write para truncar en cada ejecución)
    fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
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
    parser.addoption(
        "--always-screenshot",
        action="store_true",
        help="Adjunta screenshot incluso si el test pasa (para ver evidencia en éxitos)",
    )


def pytest_configure(config):
    _setup_logging()
    logging.getLogger(__name__).info("Pytest configurado. Logging inicializado.")


def _reports_dir() -> Path:
    return Path(__file__).resolve().parent / "reports"


def _log_file_path() -> Path:
    return _reports_dir() / "test.log"


def _tail_text(file_path: Path, max_lines: int = 200, max_chars: int = 20000) -> str:
    # Lee el "final" del archivo de log para inyectarlo en el reporte HTML sin excederse.
    try:
        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        tail = lines[-max_lines:] if len(lines) > max_lines else lines
        text = "".join(tail)
        if len(text) > max_chars:
            text = text[-max_chars:]
        return text
    except FileNotFoundError:
        return "<no se encontró el archivo de log>"
    except Exception as e:
        return f"<error leyendo log: {e}>"


def _capture_marked_key_screenshot(driver) -> Tuple[Optional[bytes], str]:
    """Intenta capturar la 'tecla marcada' y, si no está presente, hace captura de toda la página.
    Devuelve (png_bytes | None, descripcion)."""
    css = "span.white-key.marked span.note"
    try:
        # Captura dirigida del elemento de mayor interés para E2E; si no aparece, cae a full-page.
        elems = driver.find_elements(By.CSS_SELECTOR, css)  # type: ignore[attr-defined]
        if elems:
            png_bytes = elems[0].screenshot_as_png
            return png_bytes, "Captura de la tecla marcada"
    except NoSuchElementException:
        pass
    except Exception as e:
        logging.getLogger(__name__).warning(f"No se pudo capturar la tecla marcada: {e}")

    # Fallback: screenshot de la página completa en base64
    try:
        b64 = driver.get_screenshot_as_base64()  # type: ignore[attr-defined]
        png_bytes = base64.b64decode(b64)
        return png_bytes, "Captura de pantalla completa (fallback)"
    except Exception as e:
        logging.getLogger(__name__).warning(f"No se pudo capturar screenshot de la página: {e}")
        return None, "Sin captura disponible"


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Antes de comenzar, limpiar screenshots previos y garantizar carpeta de reports."""
    reports_dir = _reports_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Borrar screenshots antiguos si existieran (por higiene entre corridas)
    removed = 0
    for pattern in ("*.png", "**/*.png", "*.jpg", "**/*.jpg"):
        for p in reports_dir.glob(pattern):
            try:
                p.unlink()
                removed += 1
            except Exception:
                # No bloquear si algún archivo no puede borrarse (p. ej. en uso)
                pass
    logging.getLogger(__name__).info(f"Limpieza de screenshots previos: {removed} archivos removidos en {reports_dir}")


@pytest.fixture()
def driver(request):
    _setup_logging()
    logger = logging.getLogger(__name__)

    headless = request.config.getoption("--headless")
    logger.info(f"Inicializando driver de navegador (headless={headless})")

    driver = create_driver(headless=headless)
    # Exponer el driver en el nodo del test para que los hooks puedan accederlo
    setattr(request.node, "_driver", driver)

    # Log informativo de capabilities si están disponibles.
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


# --- Personalización del reporte HTML ---

def pytest_html_report_title(report):
    report.title = "Reporte E2E Piano - pytest-html"


def pytest_html_results_summary(prefix, summary, postfix):
    """Insertar una única sección de logs en el resumen del reporte."""
    try:
        from pytest_html import extras  # type: ignore
        # Construir bloque de logs recientes
        log_tail = _tail_text(_log_file_path(), max_lines=400, max_chars=40000)
        log_html = (
            "<details style=\"margin:8px 0\" open>"
            "<summary><strong>Logs recientes (única sección)</strong></summary>"
            f"<pre style=\"white-space:pre-wrap;max-height:500px;overflow:auto;\">{html_escape(log_tail)}</pre>"
            "</details>"
        )
        prefix.append(extras.html(log_html))
    except Exception:
        # Si el plugin no está, continuamos sin bloquear
        pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Ejecuta el resto de hooks y obtiene el reporte
    outcome = yield
    report = outcome.get_result()

    html_plugin = item.config.pluginmanager.getplugin("html")
    if not html_plugin:
        return

    always_ss = item.config.getoption("--always-screenshot")

    is_interest_phase = report.when == "call"
    failed = (report.failed and report.when in {"setup", "call", "teardown"})
    passed_and_want_ss = (always_ss and is_interest_phase and getattr(report, "passed", False))

    if not (failed or passed_and_want_ss):
        return

    # Tomar la lista de extras respetando la API actual
    extras_list = list(getattr(report, "extras", [])) or list(getattr(report, "extra", []))

    # Adjuntar solo screenshot (no logs por test para evitar duplicados)
    driver = getattr(item, "_driver", None)
    if driver is not None:
        png_bytes, desc = _capture_marked_key_screenshot(driver)
        if png_bytes:
            b64_png = base64.b64encode(png_bytes).decode("ascii")
            extras_list.append(html_plugin.extras.png(b64_png, desc))


    # Asignar a ambas propiedades por compatibilidad
    report.extras = extras_list
    report.extra = extras_list
