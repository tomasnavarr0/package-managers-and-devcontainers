import os
import sys
import subprocess
import time
import venv
import shutil

CODE_TO_RUN: str = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any

def fetch_weather_data(lat: float = 40.4168, lon: float = -3.7038) -> dict[str, Any]:
    import requests  # Mover import aquí para después de install
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

def main() -> None:
    venv_dir = ".venv"
    venv.create(venv_dir, with_pip=True)

    if sys.platform == "win32":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    start_time = time.time()

    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt", "--no-cache-dir"])
    subprocess.check_call([venv_python, "-m", "pre_commit", "run", "--all-files"])

    subprocess.check_call([venv_python, "-c", CODE_TO_RUN])

    end_time = time.time()
    total_time = end_time - start_time

    print(f"Tiempo total (install + exec): {total_time:.2f} segundos")
    shutil.rmtree(venv_dir)
    return total_time


if __name__ == "__main__":
    main()
