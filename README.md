# Network Compliance Checker

![CI](https://github.com/kat-git-hub/network-compliance-checker/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Ansible Lint](https://img.shields.io/badge/ansible--lint-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.13-blue)

A practical tool for automated network device compliance checking using Ansible and pytest.

## What it checks

| Policy | Check |
|--------|-------|
| SSH | PermitRootLogin disabled |
| SSH | Protocol 2 enforced |
| NTP | chrony installed |
| Services | vsftpd/FTP not present |

## Simulated devices

| Device | Role | Expected issues |
|--------|------|-----------------|
| router-01 | Core router | None — fully compliant |
| router-02 | Edge router | NTP missing |
| switch-01 | Access switch | FTP installed |
| switch-02 | Distribution switch | Root login enabled |
| firewall-01 | Firewall | Root login + FTP + NTP missing |

## Quick start

```bash
make up        # start containers
make run       # run ansible compliance check
make test      # run pytest tests
make test-cov  # run tests with coverage report
make lint      # ansible-lint
make report    # open HTML report
make all       # everything at once
```

## Stack

- **Ansible** — runs compliance checks across devices
- **ansible-lint** — enforces Ansible best practices
- **pytest + testinfra** — verifies compliance results via SSH
- **pytest-cov** — 100% test coverage
- **Docker** — simulates 5 network devices
- **GitHub Actions** — CI/CD pipeline
