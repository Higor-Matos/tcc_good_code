# tcc_good_code/tests/generate_readme.py

from datetime import datetime
import json
import subprocess


def run_pytest():
    """Executa os testes e gera o relatório resumido."""
    result = subprocess.run(
        [
            "pytest",
            "--disable-warnings",
            "--tb=short",
            "--maxfail=1",
            "-q",
            "--benchmark-json=benchmark_report.json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    lines = result.stdout.decode("utf-8").splitlines()
    for line in lines:
        if "==" in line:
            return line
    return "Nenhum teste encontrado ou erro ao executar testes."


def extract_complexity():
    """Executa o Radon para calcular a complexidade e gera o relatório."""
    exclude_dirs = [
        "../tests",
        "../venv",
        "../venv/*",
        "../venv/lib",
        "../venv/lib/python3.12",
        "../venv/lib/python3.12/site-packages",
    ]
    exclude_dirs_str = ",".join(exclude_dirs)
    result = subprocess.run(
        ["radon", "cc", "../", "-a", "-s", "--exclude", exclude_dirs_str],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    output = result.stdout.decode("utf-8")

    with open("complexity_report.txt", "w", encoding="utf-8") as file:
        file.write(output)

    lines = output.split("\n")
    for line in lines:
        if "Average complexity" in line:
            average_complexity = line.split()[-1].strip("()")
            return average_complexity
    return None


def run_security_scan():
    """Executa o Bandit para análise de segurança e retorna o resultado formatado."""
    exclude_dirs = [
        "../tests",
        "../venv",
        "../venv/*",
        "../venv/lib",
        "../venv/lib/python3.12",
        "../venv/lib/python3.12/site-packages",
        "../lib",
        "../lib/*",
    ]
    exclude_dirs_str = ",".join(exclude_dirs)

    result = subprocess.run(
        [
            "bandit",
            "-r",
            "../",
            "--exclude",
            exclude_dirs_str,
            "-f",
            "json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    output = result.stdout.decode("utf-8")
    bandit_result = json.loads(output)

    with open("security_report.json", "w", encoding="utf-8") as file:
        json.dump(bandit_result, file, indent=2)

    return bandit_result


def format_security_results(bandit_result):
    """Formata os resultados da análise de segurança para o README."""
    issues = bandit_result.get("results", [])
    if not issues:
        return "Nenhum problema de segurança encontrado.\n\n"
    else:
        formatted_results = "Os seguintes problemas de segurança foram encontrados:\n\n"
        for issue in issues:
            formatted_results += (
                f"### [{issue['issue_severity']}] {issue['issue_text']}\n"
                f"- **Arquivo**: {issue['filename']}\n"
                f"- **Linha**: {issue['line_number']}\n"
                f"- **Detalhes**: [{issue['test_id']}]({issue['more_info']})\n\n"
            )
        return formatted_results


def format_benchmark_results(benchmark_report):
    """Formata os resultados do benchmark para serem adicionados ao README."""
    benchmark_results = json.loads(benchmark_report)
    formatted_results = []

    for bench in benchmark_results["benchmarks"]:
        name = bench["name"]
        min_time = bench["stats"]["min"]
        max_time = bench["stats"]["max"]
        mean_time = bench["stats"]["mean"]
        ops = bench["stats"]["ops"]
        rounds = bench["stats"]["rounds"]

        formatted_results.append(
            f"### {name}\n"
            f"- **Tempo Mínimo**: {min_time:.6f} segundos\n"
            f"- **Tempo Máximo**: {max_time:.6f} segundos\n"
            f"- **Tempo Médio**: {mean_time:.6f} segundos\n"
            f"- **Operações por Segundo**: {ops:.2f} ops/s\n"
            f"- **Rodadas**: {rounds}\n"
        )

    return "\n".join(formatted_results)


def create_readme(
    test_output,
    complexity,
    security_results,
    performance_report="benchmark_report.json",
):
    """Cria ou atualiza o README.md com os resultados dos testes."""
    with open("README.md", "w", encoding="utf-8") as readme:
        readme.write("# Relatório de Qualidade do Código\n\n")
        readme.write(
            f"Relatório gerado em: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}\n\n"
        )

        readme.write("## Resultados dos Testes Automatizados\n")
        readme.write(
            "Este relatório apresenta o status dos testes unitários automatizados executados no código.\n\n"
        )
        readme.write(f"**Status dos Testes**: {test_output}\n\n")

        readme.write("## Complexidade Média do Código\n")
        readme.write(
            "A complexidade ciclomática média do código é uma métrica que indica a facilidade de manutenção e compreensão do código.\n\n"
        )
        readme.write(f"A complexidade média do código é: **{complexity}**\n\n")

        readme.write("## Análise de Segurança\n")
        readme.write(
            "A análise de segurança foi realizada usando o Bandit para identificar vulnerabilidades comuns em código Python.\n\n"
        )
        readme.write(security_results)

        try:
            with open(performance_report, "r", encoding="utf-8") as benchmark_file:
                benchmark_data = benchmark_file.read()
                formatted_benchmark = format_benchmark_results(benchmark_data)
                readme.write("## Relatório de Desempenho\n")
                readme.write(
                    "Os testes de desempenho medem a eficiência e a velocidade de execução das principais funções do sistema.\n\n"
                )
                readme.write(formatted_benchmark)
        except FileNotFoundError:
            readme.write("## Relatório de Desempenho\n")
            readme.write("Nenhum relatório de desempenho foi gerado.\n\n")


def main():
    test_output = run_pytest()
    complexity = extract_complexity()
    bandit_result = run_security_scan()
    security_results = format_security_results(bandit_result)
    create_readme(test_output, complexity, security_results)


if __name__ == "__main__":
    main()
