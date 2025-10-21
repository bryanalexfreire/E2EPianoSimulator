from time import sleep
import pytest
from pages.piano_page import PianoPage
from utils.test_data import load_json_from_resources

@pytest.mark.e2e
def test_play_scenario_1(driver):
    piano = PianoPage(driver)
    piano.visit_page()
    piano.assert_piano_url()

    data = load_json_from_resources("test_scenarios_1.json")

    scenario = data.get("scenario", {})
    notes = scenario.get("notes", [])
    delay = scenario.get("delay", 1)

    for note in notes:
        piano.digit_note(note)
        sleep(delay)
