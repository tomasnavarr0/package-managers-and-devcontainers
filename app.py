import re
import subprocess
import os

GESTORES: dict[str, str] = {
    "uv": "uv",
    "pipenv": "pipenv",
    "poetry": "poetry",
    "pip + venv": "pip"
}

def run_single_benchmark(gestor_name: str, folder_name: str) -> float | None:

    print(f"\n=======================================================")
    print(f"  EJECUTANDO BENCHMARK: {gestor_name.upper()}")
    print(f"=======================================================")
    
    os.chdir(folder_name)
    result = subprocess.run(
        ["python", "__main__.py"],
        capture_output=True,
        text=True,
        check=True,
        timeout=300 # 5 minutos de timeout
    )

    match = re.search(r"Tiempo total \(install \+ exec\): (\d+\.\d+) segundos", result.stdout)
    
    total_time = float(match.group(1))
    print(f"✅ ÉXITO ({gestor_name}): Tiempo medido = {total_time:.2f} segundos.")
    os.chdir("..")
    return total_time


def generate_report(results: dict[str, float|None]) -> str:

    sorted_results = sorted(
        results.items(),
        key=lambda item: item[1] if item[1] is not None else float('inf')
    )
    
    report = "## 📊 Comparación de Tiempos de Instalación y Ejecución (Cold Start)\n"
    report += "Este informe compara el tiempo total necesario para: 1) Instalar las dependencias (Numpy, Pandas, etc.) sin usar caché, 2) Ejecutar `pre-commit`, y 3) Ejecutar un script de análisis de datos.\n\n"
    report += "| Gestor de Paquetes | Tiempo Total (Segundos) | Notas |\n"
    report += "|:-------------------|:-----------------------:|:------|\n"
    
    for gestor, tiempo in sorted_results:
        if tiempo is not None:
            report += f"| {gestor} | **{tiempo:.2f}** | Incluye instalación, pre-commit y ejecución del script. |\n"
        else:
            report += f"| {gestor} | FALLO | Revisa el log de errores. |\n"
            
    return report

def main():
    print("Iniciando Benchmarks de Gestores de Paquetes...")
    
    benchmark_results = {}
    
    for gestor_name, folder_name in GESTORES.items():
        time_result = run_single_benchmark(gestor_name, folder_name)
        benchmark_results[gestor_name] = time_result
        
    print("\n\n#######################################################")
    print("## RESUMEN DE TIEMPOS DE EJECUCIÓN ##")
    print("#######################################################")

    report = generate_report(benchmark_results)
    print(report)

if __name__ == "__main__":
    main()