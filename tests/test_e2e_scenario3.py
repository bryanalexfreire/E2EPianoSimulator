from time import sleep
from utils.test_data import load_json_from_resources
import pytest
import logging
from pages.piano_page import PianoPage

logger = logging.getLogger(__name__)


@pytest.mark.e2e
@pytest.mark.scenario3
def test_play_scenario_3(driver):
    logger.info("[Escenario 3] Inicio")
    piano = PianoPage(driver)
    piano.visit_page()
    piano.assert_piano_url()

    logger.info("[Escenario 3] Cargando datos del escenario")
    data = load_json_from_resources("test_scenario_3.json")

    scenario = data.get("scenario", {})
    notes = scenario.get("notes", [])
    delay = scenario.get("delay", 1)
    logger.info(f"[Escenario 3] Notas a reproducir: {len(notes)} | delay={delay}s")

    for idx, note in enumerate(notes, start=1):
        logger.info(f"[Escenario 3] Nota {idx}/{len(notes)}: {note}")
        piano.digit_note(note)
        sleep(delay)

    logger.info("[Escenario 3] Fin")
