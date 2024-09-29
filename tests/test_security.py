# tcc_good_code/tests/test_security.py

import json
import subprocess


def run_security_scan():
    """Executa o Bandit para análise de segurança e retorna o resultado formatado."""
    exclude_dirs_str = "../venv, ../tests, ../lib"
    result = subprocess.run(
        ["bandit", "-r", "../", "--exclude", exclude_dirs_str, "-f", "json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    output = result.stdout.decode("utf-8")
    return json.loads(output)


def test_security():
    bandit_result = run_security_scan()

    with open("security_report.json", "w", encoding="utf-8") as file:
        json.dump(bandit_result, file, indent=2)

    issues = bandit_result.get("results", [])

    high_severity_issues = [
        issue for issue in issues if issue["issue_severity"] == "HIGH"
    ]
    medium_severity_issues = [
        issue for issue in issues if issue["issue_severity"] == "MEDIUM"
    ]

    assert (
        len(high_severity_issues) == 0
    ), f"Foram encontrados {len(high_severity_issues)} problemas de segurança de severidade ALTA"
    assert (
        len(medium_severity_issues) == 0
    ), f"Foram encontrados {len(medium_severity_issues)} problemas de segurança de severidade MÉDIA"
