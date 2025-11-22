import os
import subprocess
import time
import shutil

CODE_TO_RUN: str = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any

def fetch_weather_data(lat: float = 40.4168, lon: float = -3.7038) -> dict[str, Any]:
    import requests
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=Europe/Madrid"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['hourly']
    raise ValueError(f"Error fetching weather: {response.status_code}")

weather_data = fetch_weather_data()

df = pd.DataFrame({
    'time': pd.to_datetime(weather_data['time']),
    'temperature': weather_data['temperature_2m']
})
print("DataFrame de temperaturas horarias (primeras 5 filas):")
print(df.head())

plt.figure(figsize=(10, 5))
plt.plot(df['time'], df['temperature'], marker='o', linestyle='-', color='b')
plt.title('Pronóstico de Temperatura Horaria (Madrid)')
plt.xlabel('Tiempo')
plt.ylabel('Temperatura (°C)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('weather_plot.png')
print("Plot guardado como 'weather_plot.png'.")
"""

TEMP_SCRIPT_NAME = "temp_runner_script.py"


def main() -> None:
    venv_dir = ".venv"
    temp_cache_dir = ".temp_poetry_cache"

    os.environ["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"
    os.environ["POETRY_CACHE_DIR"] = temp_cache_dir

    with open(TEMP_SCRIPT_NAME, "w", encoding="utf-8") as f:
        f.write(CODE_TO_RUN)

    start_time = time.time()

    subprocess.check_call(["poetry", "install", "--no-root"])
    subprocess.run(["poetry", "run", "pre-commit", "run", "--all-files"], check=False)
    subprocess.check_call(["poetry", "run", "python", TEMP_SCRIPT_NAME])

    end_time = time.time()
    total_time = end_time - start_time

    print(f"Tiempo total (install + exec): {total_time:.2f} segundos")

    if os.path.exists(venv_dir):
        shutil.rmtree(venv_dir)

    if os.path.exists(temp_cache_dir):
        shutil.rmtree(temp_cache_dir)

    if os.path.exists(TEMP_SCRIPT_NAME):
        os.remove(TEMP_SCRIPT_NAME)

    return total_time


if __name__ == "__main__":
    main()
