import pytest
import re

# Selección simple (edita SOLO esta variable y ejecuta este archivo):
#   - "all" -> ejecuta todos los tests
#   - "1" | "2" | "3" | "10" -> mapea a scenario1|2|3|10 dinámicamente
#   - "scenario1" | "scenario10" -> acepta cualquier scenarioN
#   - "1,3,7" -> ejecuta múltiples escenarios: e2e and (scenario1 or scenario3 or scenario7)
#   - cualquier otra cadena se usa como expresión -m directa (p. ej.: "e2e and smoke")
SELECT = "all"

# Opcional: si querés que el navegador corra en headless por defecto, ponelo en True
HEADLESS = True

# Opcional: si querés siempre adjuntar screenshot aunque el test pase
ALWAYS_SCREENSHOT = False


def _to_marker_expr(sel: str | None) -> str | None:
    # Traduce entradas amigables (números, "scenarioN", listas separadas por coma)
    # a una expresión de marcadores válida para pytest (-m).
    if not sel:
        return None
    s = sel.strip()
    if not s or s.lower() == "all":
        return None

    # Normalizar separadores y tokenizar
    tokens = [t.strip() for t in re.split(r"[,\s]+", s) if t.strip()]
    scenarios: list[str] = []
    others: list[str] = []

    for t in tokens:
        tl = t.lower()
        # Solo dígitos -> scenarioN
        if re.fullmatch(r"\d+", tl):
            scenarios.append(f"scenario{tl}")
            continue
        # scenarioN arbitrario
        m = re.fullmatch(r"scenario(\d+)", tl)
        if m:
            scenarios.append(tl)
            continue
        # Cualquier otra cosa, la dejamos como parte de una expresión avanzada
        others.append(t)

    expr: str | None = None

    if scenarios:
        # Unificar y ordenar para estabilidad
        uniq = sorted(set(scenarios), key=lambda x: (len(x), x))
        group = " or ".join(uniq)
        expr = f"({group})"

    if others:
        adv = " and ".join(others)
        expr = f"{adv} and {expr}" if expr else adv

    # Si hay escenarios y no se incluyó explícitamente 'e2e' en 'others', prefix automático "e2e and"
    if scenarios and (not others or not any(o.lower() == "e2e" or o.lower().startswith("e2e ") for o in others)):
        expr = f"e2e and {expr}" if expr else "e2e"

    # Si no se construyó nada (poco probable), retornar la cadena como fallback
    return expr or s


def main() -> int:
    pytest_args: list[str] = []

    expr = _to_marker_expr(SELECT)
    if expr:
        pytest_args += ["-m", expr]

    if HEADLESS:
        pytest_args.append("--headless")

    if ALWAYS_SCREENSHOT:
        pytest_args.append("--always-screenshot")

    return pytest.main(pytest_args)


if __name__ == "__main__":
    raise SystemExit(main())
