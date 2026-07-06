# Network Compliance Checker

![CI](https://github.com/kat-git-hub/network-compliance-checker/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Ansible Lint](https://img.shields.io/badge/ansible--lint-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.13-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

A policy-driven compliance checker for network infrastructure. Define your security policies once — run checks across any number of devices automatically.

## How it works
```
policies.yml          →  what to check
hosts.ini             →  where to check
known_violations.yml  →  documented exceptions
↓
Ansible checks all devices in parallel
↓
pytest verifies results
↓
HTML + JSON reports
```

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/kat-git-hub/network-compliance-checker.git
cd network-compliance-checker
poetry install
```

### 2. Add your devices to `hosts.ini`

```ini
[linux_servers]
my-server ansible_host=192.168.1.10 ansible_port=22 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa ansible_ssh_extra_args='-o StrictHostKeyChecking=no'

# Cisco IOS (requires Cisco DevNet Sandbox or real device)
# [cisco_devices]
# my-router ansible_host=10.0.0.1 ansible_port=22 ansible_user=admin ansible_connection=network_cli ansible_network_os=cisco.ios.ios
```

### 3. Define your policies in `policies.yml`

```yaml
ssh:
  permit_root_login: false
  protocol_version: 2

ntp:
  required: true
  package: chrony

forbidden_services:
  - vsftpd
  - telnet
```

### 4. Document known violations in `known_violations.yml`

```yaml
known_violations:
  legacy-server:
    - check: ntp_missing
      reason: "NTP not yet configured on this device"
```

### 5. Run

```bash
make up       # start demo containers (optional)
make run      # run compliance checks
make test     # verify with pytest
make report   # open HTML report
```

## Available commands

```bash
make up        # start demo containers
make down      # stop containers
make run       # run Ansible compliance check
make test      # run pytest tests
make test-cov  # run tests with coverage report
make lint      # ansible-lint
make report    # open HTML report
make all       # up + run + test
make clean     # stop containers, remove reports
```

## What gets checked

### Linux servers
| Check | Policy key |
|-------|-----------|
| SSH PermitRootLogin | `ssh.permit_root_login` |
| SSH Protocol version | `ssh.protocol_version` |
| NTP package installed | `ntp.required` |
| Forbidden services absent | `forbidden_services` |

### Cisco IOS (coming soon)
| Check | Command |
|-------|---------|
| SSH version | `show running-config \| include ip ssh` |
| NTP server configured | `show running-config \| include ntp` |
| Password encryption | `show running-config \| include service password-encryption` |
| VTY exec-timeout | `show running-config \| section line vty` |

## Connecting to Cisco DevNet Sandbox

1. Register at [developer.cisco.com/sandbox](https://developer.cisco.com/sandbox)
2. Reserve a free **IOS XE on CSR** sandbox
3. Add credentials to `hosts.ini`:

```ini
[cisco_devices]
sandbox-ios-xe ansible_host=YOUR_SANDBOX_HOST
               ansible_user=YOUR_USERNAME
               ansible_password=YOUR_PASSWORD
               ansible_connection=network_cli
               ansible_network_os=cisco.ios.ios
```

4. Run:
```bash
ansible-playbook -i hosts.ini cisco_site.yml
```

## Output

- **HTML report** — `reports/report.html` — visual compliance table per device
- **JSON report** — `reports/report.json` — machine-readable for CI/CD integration
- **pytest output** — pass/xfail per device and policy check

## Stack

- **Ansible** — parallel compliance checks across devices
- **ansible-lint** — enforces Ansible best practices (production profile)
- **pytest + testinfra** — policy-driven test verification
- **pytest-cov** — 100% test coverage
- **Docker** — simulates network devices locally
- **GitHub Actions** — CI/CD pipeline
