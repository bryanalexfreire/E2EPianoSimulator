# python
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import logging

from pages.base_page import BasePage
from utils.test_data import load_json_from_resources

logger = logging.getLogger(__name__)

class PianoPage(BasePage):
    URL = "https://www.musicca.com/es/piano"
    BODY = (By.TAG_NAME, "body")
    TEXT_NOTE = (By.CSS_SELECTOR, "span.white-key.marked span.note")
    BTN_MARK = (By.CSS_SELECTOR, "button.mark")
    BTN_CLEAR = (By.CSS_SELECTOR, "button.btn-reset")
    NOTES_RESOURCE = "notes_map.json"  # se carga desde `resources/`

    def __init__(self, driver):
        super().__init__(driver)
        self._notes_by_note = None  # cache {note: {"key": "z", "flag": "1c"}}

    def visit_page(self):
        self.visit(self.URL)

    def assert_piano_url(self):
        assert "piano" in self.get_current_url(), "Not on the piano page"

    def _ensure_notes_loaded(self):
        if self._notes_by_note is not None:
            return
        data = load_json_from_resources(self.NOTES_RESOURCE)  # {flag: {key, note}}
        # indexa por nombre de nota para lookup O(1)
        self._notes_by_note = {}
        for flag, entry in data.items():
            note = entry.get("note", "").strip().lower()
            key = entry.get("key")
            if note and key:
                self._notes_by_note[note] = {"key": key, "flag": flag}

    def _resolve_note(self, note_name: str) -> tuple[str, str]:
        self._ensure_notes_loaded()
        note_key = (note_name or "").strip().lower()
        if note_key not in self._notes_by_note:
            raise ValueError(f"Nota inválida o no mapeada en JSON: {note_name}")
        entry = self._notes_by_note[note_key]
        return entry["key"], entry["flag"]

    def send_keys_piano(self, key, expected_case, timeout: int = 20, expected_flag: str | None = None):
        flag = (expected_flag or expected_case or "").strip().lstrip("?")
        if not flag:
            raise ValueError("expected_flag/expected_case vacío; no se puede validar la URL")

        self.type_keys(key, timeout)

        WebDriverWait(self.driver, timeout).until(EC.url_contains(f"?{flag}"))

        current = self.get_current_url()
        assert f"?{flag}" in current, f"URL no contiene '?{flag}'. Actual: {current}"

        self.click(self.BTN_CLEAR)
        WebDriverWait(self.driver, timeout).until_not(EC.url_contains(f"?{flag}"))

    def digit_note(self, key_note: str):
        logger.info(f"Digitando la nota: {key_note}")
        self._ensure_mark_active(self.BTN_MARK)
        key, flag = self._resolve_note(key_note)  # lee la key y el flag del JSON
        # Envía la key del JSON y valida con el flag (p. ej., 1c, 1d, 2a, etc.)
        self.send_keys_piano(key, flag, expected_flag=flag)