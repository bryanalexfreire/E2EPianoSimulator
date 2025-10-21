from time import sleep
from utils.test_data import load_json_from_resources
import pytest
from pages.piano_page import PianoPage


@pytest.mark.e2e
def test_play_scenario_3(driver):
    piano = PianoPage(driver)
    piano.visit_page()
    piano.assert_piano_url()


    data = load_json_from_resources("test_scenario_3.json")

    scenario = data.get("scenario", {})
    notes = scenario.get("notes", [])
    delay = scenario.get("delay", 1)

    for note in notes:
        piano.digit_note(note)
        sleep(delay)
