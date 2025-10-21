from time import sleep
import pytest
import logging
from pages.piano_page import PianoPage
from utils.test_data import load_json_from_resources

logger = logging.getLogger(__name__)

@pytest.mark.e2e
@pytest.mark.scenario1
def test_play_scenario_1(driver):
    logger.info("[Escenario 1] Inicio")
    piano = PianoPage(driver)
    piano.visit_page()
    piano.assert_piano_url()

    logger.info("[Escenario 1] Cargando datos del escenario")
    data = load_json_from_resources("test_scenarios_1.json")

    scenario = data.get("scenario", {})
    notes = scenario.get("notes", [])
    delay = scenario.get("delay", 1)
    logger.info(f"[Escenario 1] Notas a reproducir: {len(notes)} | delay={delay}s")

    for idx, note in enumerate(notes, start=1):
        logger.info(f"[Escenario 1] Nota {idx}/{len(notes)}: {note}")
        piano.digit_note(note)
        sleep(delay)

    logger.info("[Escenario 1] Fin")
