from pathlib import Path
import json
from typing import Any, Dict, List


def _resources_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "resources"


def load_json_from_resources(filename: str) -> Dict[str, Any]:
    """Carga y devuelve el contenido JSON del archivo ubicado en `resources/`.

    Args:
        filename: Nombre del archivo dentro de `resources` (por ejemplo, "test_scenarios_1.json").

    Raises:
        FileNotFoundError: si el archivo no existe.
        json.JSONDecodeError: si el JSON está malformado.

    Returns:
        Dict con el contenido del JSON.
    """
    resources = _resources_dir()
    file_path = resources / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Archivo de datos no encontrado: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_scenario_notes(filename: str, scenario_index: int = 0) -> List[str]:
    """Obtiene la lista `notes` de un escenario dentro de un archivo de escenarios.

    Args:
        filename: Nombre del archivo JSON dentro de `resources`.
        scenario_index: Índice del escenario a obtener (por defecto 0).

    Returns:
        Lista de notas (puede estar vacía si no hay notas o si no existe el escenario).
    """
    data = load_json_from_resources(filename)
    scenarios = data.get("scenarios", []) if isinstance(data, dict) else []

    if not isinstance(scenarios, list):
        return []

    if scenario_index < 0 or scenario_index >= len(scenarios):
        return []

    return scenarios[scenario_index].get("notes", []) if isinstance(scenarios[scenario_index], dict) else []

