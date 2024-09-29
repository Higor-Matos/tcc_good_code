# tcc_good_code/tests/test_security.py

import json
import subprocess


def test_security():
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
