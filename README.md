# ArqPiano - Automatización E2E con Selenium + Pytest

## Cómo ejecutar (lo más importante)

Requisitos previos
- Windows, macOS o Linux con Python 3.10+ instalado.
- Google Chrome instalado (webdriver-manager descargará el ChromeDriver compatible automáticamente).

1) Crear y activar un entorno virtual (opcional pero recomendado)

```cmd
python -m venv .venv
.venv\Scripts\activate
```

2) Instalar dependencias y plugins

```cmd
python -m pip install -U pip
pip install -r requirements.txt
```

Incluye:
- selenium
- pytest (runner de tests)
- pytest-html (reporte HTML)
- webdriver-manager (descarga/gestiona ChromeDriver)

3) Ejecutar todos los tests

```cmd
pytest -q
```

4) Ejecutar un escenario específico por marcadores (-m)

```cmd
pytest -q -m "e2e and scenario1"
pytest -q -m "e2e and scenario2"
pytest -q -m "e2e and scenario3"
```

5) Ejecutar con navegador en headless (sin UI) y adjuntar capturas siempre

```cmd
pytest -q --headless --always-screenshot
```

6) Usar el lanzador `runner.py` (selector rápido de escenarios)
- Edita la variable `SELECT` en `runner.py`:
  - "all" -> todos los tests
  - "1", "2", "3" o "10" -> mapea a `scenario1|2|3|10`
  - "scenario3" -> acepta cualquier `scenarioN`
  - "1,3,7" -> varios escenarios (se construye `e2e and (scenario1 or scenario3 or scenario7)`)
  - cualquier otra cadena se usa como expresión -m directa (p. ej. `e2e and smoke`)
- Opcionales en `runner.py`: `HEADLESS` y `ALWAYS_SCREENSHOT`.

Ejemplo:
```cmd
python runner.py
```

7) Reportes y evidencias
- Reporte HTML: `reports/pytest.html` (auto-generado por `pytest-html`).
- Logs centralizados: `reports/test.log` (el README incluye logs recientes en el HTML).
- Capturas: se adjuntan al reporte HTML como extras; el hook limpia capturas antiguas al iniciar sesión de tests.

Notas
- La fixture `--headless` y la opción `--always-screenshot` también funcionan con `runner.py` si se activan en sus variables.
- Tras la ejecución puedes abrir `reports/pytest.html` en el navegador.

---

## Herramientas, frameworks y patrones utilizados

- Selenium WebDriver (automatización del navegador).
- Pytest (framework de testing) y `pytest-html` (reporte HTML con evidencias).
- `webdriver-manager` (gestión automática de ChromeDriver compatible con tu versión de Chrome).
- Logging estándar de Python (consola + archivo `reports/test.log`).
- Page Object Model (POM)
  - `pages/base_page.py`: helpers comunes de UI (visitas, clicks, tipeo, esperas, utilidades).
  - `pages/piano_page.py`: acciones específicas de la página del piano (activar marcado, enviar notas y validar flags en URL).
- Datos externos (Data-Driven)
  - `resources/notes_map.json`: mapeo nota -> tecla física y flag de URL.
  - `resources/test_scenarios_*.json`: secuencias de notas por escenario.
- Hooks de Pytest personalizados (`conftest.py`)
  - Limpieza de capturas antiguas.
  - Captura selectiva de la tecla marcada o full-page en fallos/éxitos (si `--always-screenshot`).
  - Inserción de logs recientes en el reporte HTML (una única sección).
- Runner parametrizable (`runner.py`) que construye expresiones `-m` a partir de entradas amigables.

---

## Escenarios automatizados y su descripción

Los escenarios se describen en archivos JSON dentro de `resources/` y se ejecutan con los tests en `tests/`. Cada test reproduce una secuencia de notas con un retardo configurable (por defecto 1s si no se especifica en el JSON).

- Escenario 1 (`tests/test_e2e_scenario1.py`)
  - Archivo: `resources/test_scenarios_1.json`
  - Descripción: "Secuencia base: si, si, do, re, re, do, si, la, sol, sol, la, si, si, la, la"
  - Notas: ["si","si","do","re","re","do","si","la","sol","sol","la","si","si","la","la"]
  - Delay por defecto: 1s

- Escenario 2 (`tests/test_e2e_scenario2.py`)
  - Archivo: `resources/test_scenario_2.json`
  - Descripción: "Repetición de la secuencia base dos veces."
  - Notas: secuencia del Escenario 1 repetida dos veces (total 30 notas)
  - Delay por defecto: 1s

- Escenario 3 (`tests/test_e2e_scenario3.py`)
  - Archivo: `resources/test_scenario_3.json`
  - Descripción: "Secuencia larga con repetición final del Escenario 1."
  - Notas: secuencia extendida que culmina repitiendo la del Escenario 1
  - Delay por defecto: 1s

Notas y teclas (fuente: `resources/notes_map.json`)
- do -> tecla "z" (flag `1c`)
- re -> tecla "x" (flag `1d`)
- mi -> tecla "c" (flag `1e`)
- fa -> tecla "q" (flag `1f`)
- sol -> tecla "w" (flag `1g`)
- la -> tecla "e" (flag `2a`)
- si -> tecla "r" (flag `2b`)

Durante la ejecución, al presionar la tecla correcta la página añade `?{flag}` a la URL. Luego el test pulsa el botón "clear" para limpiar la URL antes de la siguiente nota.

---

## Buenas prácticas implementadas

- Page Object Model (POM)
  - Aísla la lógica de UI en clases de página; los tests quedan expresivos y concisos.
- Esperas explícitas robustas
  - `WebDriverWait` + condiciones para sincronizar eventos (visibilidad, cambios en la URL, etc.).
  - `implicitly_wait` pequeño para elementos triviales; lo crítico usa esperas explícitas.
- Datos externos y cacheo
  - Carga perezosa del mapa de notas desde JSON y cache en memoria para evitar I/O repetido.
- Limpieza y evidencias
  - Hook que elimina capturas antiguas antes de iniciar, y adjunta capturas (tecla marcada si existe) en fallos o cuando se solicita siempre.
  - Inserción de logs recientes en el reporte HTML una sola vez para evitar duplicidades.
- Configurabilidad
  - Headless con `--headless` y/o variable en `runner.py`.
  - Selector de escenarios amigable en `runner.py` (construye `-m` automáticamente).
- Logging claro y trazable
  - Nombres de métodos y mensajes pensados para diagnóstico rápido; logs centralizados en `reports/test.log`.
- Tipado y comentarios
  - Uso de hints de tipos para locators y funciones clave.
  - Comentarios añadidos en las partes más complejas (esperas, activación de marcado, validación de flags, hooks de reporte).

---

## Estructura del proyecto (resumen)

```
├─ pages/
│  ├─ base_page.py       # utilidades comunes (visitar, click, type, esperas, etc.)
│  └─ piano_page.py      # acciones específicas del piano (enviar notas, validar flags)
├─ tests/
│  ├─ test_e2e_scenario1.py
│  ├─ test_e2e_scenario2.py
│  └─ test_e2e_scenario3.py
├─ utils/
│  ├─ driver_factory.py  # creación de ChromeDriver con webdriver-manager
│  └─ test_data.py       # carga de JSON y helpers de datos
├─ resources/
│  ├─ notes_map.json
│  ├─ test_scenarios_1.json
│  ├─ test_scenario_2.json
│  └─ test_scenario_3.json
├─ reports/              # salida de `pytest.html`, `test.log` y capturas
├─ conftest.py           # fixtures y hooks (screenshot, logs en HTML, etc.)
├─ runner.py             # lanzador con selector de escenarios
├─ pytest.ini            # configuración de pytest y marcadores
└─ requirements.txt
```

---

## Solución de problemas (troubleshooting)

- Error con Chrome/ChromeDriver
  - `webdriver-manager` descarga automáticamente una versión compatible. Verifica que Chrome esté instalado y actualizado.
- Proxy/Internet restringido
  - Si tu red bloquea descargas, puede fallar la obtención automática de ChromeDriver. Reintenta en una red abierta o configura variables de proxy de `pip`/`webdriver-manager`.
- Sin reporte HTML
  - Asegúrate de instalar `pytest-html` (incluido en `requirements.txt`). El `pytest.ini` ya añade `--html=reports/pytest.html --self-contained-html`.
- Tiempo y estabilidad
  - Si la página tarda más, aumenta los `timeout` en las esperas explícitas (por ejemplo en `send_keys_piano`).

---

## Licencia

@Bryan Freire 2025. Uso libre para fines educativos y de práctica.

