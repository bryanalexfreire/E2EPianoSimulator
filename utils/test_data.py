from pathlib import Path
import json
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


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
    logger.info(f"Cargando JSON de recursos: {file_path}")

    if not file_path.exists():
        logger.error(f"Archivo de datos no encontrado: {file_path}")
        raise FileNotFoundError(f"Archivo de datos no encontrado: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            size = len(data) if hasattr(data, "__len__") else "?"
            logger.info(f"JSON cargado correctamente (tamaño={size})")
            return data
    except json.JSONDecodeError as e:
        logger.exception(f"JSON malformado en {file_path}: {e}")
        raise


def get_scenario_notes(filename: str, scenario_index: int = 0) -> List[str]:
    """Obtiene la lista `notes` de un escenario dentro de un archivo de escenarios.

    Args:
        filename: Nombre del archivo JSON dentro de `resources`.
        scenario_index: Índice del escenario a obtener (por defecto 0).

    Returns:
        Lista de notas (puede estar vacía si no hay notas o si no existe el escenario).
    """
    logger.info(f"Extrayendo notas de escenario (file='{filename}', index={scenario_index})")
    data = load_json_from_resources(filename)
    scenarios = data.get("scenarios", []) if isinstance(data, dict) else []

    if not isinstance(scenarios, list):
        logger.warning("La clave 'scenarios' no es una lista")
        return []

    if scenario_index < 0 or scenario_index >= len(scenarios):
        logger.warning(f"Índice de escenario fuera de rango: {scenario_index}")
        return []

    notes = scenarios[scenario_index].get("notes", []) if isinstance(scenarios[scenario_index], dict) else []
    logger.info(f"Notas del escenario: {notes}")
    return notes
