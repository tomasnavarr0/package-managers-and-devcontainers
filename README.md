# 📦 Benchmark de Gestores de Paquetes en Python (`uv` vs `poetry` vs `pip` vs `pipenv`)

Este repositorio realiza una comparación práctica de rendimiento (**Cold Start Benchmark**) entre los principales gestores de paquetes y entornos virtuales del ecosistema Python:

- ⚡ **[uv](https://docs.astral.sh/uv/)** (escrito en Rust por Astral)
- 📜 **[Poetry](https://python-poetry.org/)**
- 🐍 **[pip + venv](https://pip.pypa.io/)** (estándar nativo de Python)
- 🧪 **[Pipenv](https://pipenv.pypa.io/)**

---

## 🎯 ¿Qué mide este benchmark?

Cada gestor se evalúa de manera aislada dentro de su propio subdirectorio ([`uv/`](./uv), [`poetry/`](./poetry), [`pip/`](./pip), [`pipenv/`](./pipenv)) realizando exactamente el mismo flujo de trabajo de principio a fin (**Cold Start / Sin Caché**):

1. **Creación del entorno virtual e instalación de dependencias sin caché** (`--no-cache` / `--no-cache-dir` / caché temporal limpia):
   - `numpy==2.1.2`
   - `pandas==2.2.3`
   - `matplotlib==3.9.2`
   - `requests==2.32.3`
   - `pre-commit==4.4.0`
   *(Total: ~28 paquetes contando dependencias transitivas)*
2. **Ejecución de controles de calidad de código (`pre-commit run --all-files`)**:
   - `pre-commit-hooks` (`trailing-whitespace`, `end-of-file-fixer`, `check-added-large-files`, `check-yaml`, `detect-private-key`)
   - `black` (formateo de código)
   - `flake8` (linter PEP8)
3. **Ejecución de un script de ciencia de datos y visualización**:
   - Consulta datos meteorológicos reales (pronóstico horario de temperatura en Madrid) desde la API de [Open-Meteo](https://open-meteo.com/) con `requests`.
   - Procesa la serie temporal en un `DataFrame` de `pandas` y `numpy`.
   - Genera y exporta el gráfico `weather_plot.png` con `matplotlib`.
4. **Limpieza automática**:
   - Elimina el entorno virtual (`.venv`) y cachés temporales al finalizar para garantizar que cada ejecución sea reproducible.

---

## ⏱️ Resultados del Benchmark (Tiempos Medidos)

Pruebas ejecutadas en **Windows (Python 3.12)** midiendo el tiempo total de **Instalación (Cold Start) + Ejecución de `pre-commit` + Script de Análisis y Gráfico**:

| Posición | Gestor de Paquetes | Tiempo Total (Segundos) | Velocidad Relativa (vs `uv`) | Comando de Instalación Utilizado |
|:--------:|:-------------------|:-----------------------:|:----------------------------:|:---------------------------------|
| 🥇 **1°** | **uv** | **16.64 s** | **1.00x (Base)** | `uv sync --no-cache` |
| 🥈 **2°** | **poetry** | **26.59 s** | 1.60x más lento | `poetry install --no-root` (con `POETRY_CACHE_DIR` temporal) |
| 🥉 **3°** | **pip + venv** | **43.75 s** | 2.63x más lento | `pip install -r requirements.txt --no-cache-dir` |
| **4°** | **pipenv** | **55.89 s** | 3.36x más lento | `pipenv install --dev` (con `PIP_NO_CACHE_DIR=1`) |

### 📈 Análisis de los Resultados

- **`uv` (16.64 s)**: Es el claro ganador, completando la descarga sin caché de los 28 paquetes, instalación en `.venv`, ejecución de `pre-commit` y generación del gráfico en apenas ~16.6 segundos (de los cuales la resolución tomó **2 ms**, la descarga/preparación **5.09 s** y la instalación en el entorno **1.08 s**).
- **`poetry` (26.59 s)**: Ocupa el segundo lugar gracias a su instalador paralelo moderno y al uso del archivo de bloqueo [`poetry.lock`](./poetry/poetry.lock), superando ampliamente a `pip` tradicional.
- **`pip + venv` (43.75 s)**: Aunque no tiene sobrecarga de resolución compleja al usar versiones fijadas en [`requirements.txt`](./pip/requirements.txt), su descarga e instalación secuencial sin caché penaliza el tiempo total.
- **`pipenv` (55.89 s)**: Resulta el más lento del conjunto debido a la sobrecarga en la creación del entorno, validación de [`Pipfile.lock`](./pipenv/Pipfile.lock) e invocación interna de `pip`.

---

## 🚀 ¿Cómo ejecutar el proyecto?

### 1. Requisitos previos

Necesitas tener instalado **Python 3.12** y los 4 gestores de paquetes disponibles en tu `PATH`:

```powershell
# Verificar versión de Python 3.12
py -3.12 --version

# Instalar uv (si no lo tienes)
pip install uv

# Instalar poetry y pipenv de forma aislada usando uv (recomendado)
uv tool install poetry --python 3.12
uv tool install pipenv --python 3.12
```

> **Nota sobre la versión de Python:** Las versiones fijadas en el benchmark (`numpy==2.1.2`, `pandas==2.2.3`, `matplotlib==3.9.2`) están diseñadas para **Python 3.12** (tal como se especifica en `uv/.python-version` y `pipenv/Pipfile`). Si tienes Python 3.14 como predeterminado en el sistema, ejecuta el orquestador con `py -3.12` para usar los *wheels* precompilados y evitar compilaciones desde código fuente.

---

### 2. Ejecutar el benchmark completo (Todos los gestores)

Desde la raíz del repositorio, ejecuta el script orquestador [`app.py`](./app.py):

```powershell
py -3.12 app.py
```

Esto correrá secuencialmente `uv`, `pipenv`, `poetry` y `pip + venv`, e imprimirá en consola la tabla comparativa en formato Markdown con los tiempos medidos en tu máquina.

---

### 3. Ejecutar un gestor de paquetes de forma individual

Si deseas probar o inspeccionar únicamente uno de los gestores, puedes entrar a su carpeta y ejecutar su `__main__.py`:

```powershell
# Probar solo uv
cd uv
py -3.12 __main__.py

# Probar solo poetry
cd ../poetry
py -3.12 __main__.py

# Probar solo pip + venv
cd ../pip
py -3.12 __main__.py

# Probar solo pipenv
cd ../pipenv
py -3.12 __main__.py
```

---

## 🗂️ Estructura del Repositorio

```text
package-managers-and-devcontainers/
├── app.py                      # Orquestador principal de benchmarks y generador de reporte
├── README.md                   # Documentación y resultados comparativos
├── pip/                        # Benchmark con pip + venv estándar
│   ├── __main__.py             # Script medidor para pip + venv
│   ├── requirements.txt        # Dependencias fijadas
│   ├── pyproject.toml          # Configuración de black, flake8, isort, mypy
│   ├── .pre-commit-config.yaml # Hooks de pre-commit
│   └── weather_plot.png        # Gráfico generado por el benchmark
├── pipenv/                     # Benchmark con Pipenv
│   ├── __main__.py             # Script medidor para Pipenv
│   ├── Pipfile                 # Definición de dependencias y Python 3.12
│   ├── Pipfile.lock            # Lockfile determinista de Pipenv
│   ├── pyproject.toml          # Configuración de linters/formateadores
│   ├── .pre-commit-config.yaml # Hooks de pre-commit
│   └── weather_plot.png        # Gráfico generado por el benchmark
├── poetry/                     # Benchmark con Poetry
│   ├── __main__.py             # Script medidor para Poetry
│   ├── pyproject.toml          # Definición del proyecto, dependencias y herramientas
│   ├── poetry.lock             # Lockfile determinista de Poetry
│   ├── .pre-commit-config.yaml # Hooks de pre-commit
│   └── weather_plot.png        # Gráfico generado por el benchmark
└── uv/                         # Benchmark con uv
    ├── __main__.py             # Script medidor para uv
    ├── .python-version         # Fija la versión de Python (3.12)
    ├── pyproject.toml          # Definición PEP 621 de dependencias y herramientas
    ├── uv.lock                 # Lockfile determinista de uv
    ├── .pre-commit-config.yaml # Hooks de pre-commit
    └── weather_plot.png        # Gráfico generado por el benchmark
```

---

## 🔍 Comparativa Técnica de los Gestores Evaluados

| Característica | `uv` | `poetry` | `pip + venv` | `pipenv` |
|:---------------|:----:|:--------:|:------------:|:--------:|
| **Lenguaje de implementación** | Rust | Python | Python | Python |
| **Archivo de configuración** | `pyproject.toml` (PEP 621) | `pyproject.toml` | `requirements.txt` | `Pipfile` |
| **Archivo de bloqueo (Lockfile)** | `uv.lock` | `poetry.lock` | ❌ No nativo | `Pipfile.lock` |
| **Gestión automática de `.venv`** | ✅ Sí | ✅ Sí | ❌ Manual (`python -m venv`) | ✅ Sí |
| **Gestión de versiones de Python** | ✅ Nativa (`uv python`) | ⚠️ Parcial | ❌ Externa | ❌ Externa (`pyenv`) |
| **Velocidad en Cold Start** | ⚡ **Muy Alta (16.64 s)** | 🚀 **Alta (26.59 s)** | 🐢 **Media (43.75 s)** | 🐌 **Baja (55.89 s)** |
