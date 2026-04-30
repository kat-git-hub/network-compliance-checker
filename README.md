# Network Compliance Checker

![CI](https://github.com/kat-git-hub/network-compliance-checker/actions/workflows/ci.yml/badge.svg)

A practical tool for automated network device compliance checking using Ansible and pytest.

## What it checks

- **SSH** — PermitRootLogin, Protocol version
- **NTP** — chrony installed and running
- **Forbidden services** — vsftpd/FTP not present

## Quick start

```bash
make up      # start containers
make run     # run ansible compliance check
make test    # run pytest tests
make report  # open HTML report
make all     # everything at once
```

## Stack

- Ansible — runs compliance checks across devices
- pytest + testinfra — verifies results
- Docker — simulates network devices
- GitHub Actions — CI/CD pipeline
