# Contributing to Network Compliance Checker

Thanks for considering a contribution! This guide explains the project structure and how to extend it.

## Project structure

```
network-compliance-checker/

├── policies.yml              # compliance rules — edit to change what's checked

├── known_violations.yml      # documented exceptions (xfail in tests)

├── hosts.ini                 # device inventory (gitignored — see hosts.ini.example)

├── site.yml                  # Linux compliance playbook

├── cisco_site.yml            # Cisco IOS compliance playbook

├── cisco_fix.yml             # Cisco IOS remediation playbook

├── full_site.yml             # combined Linux + Cisco report

├── roles/

│   ├── compliance/           # Linux compliance checks

│   │   ├── tasks/            # check_ssh.yml, check_ntp.yml, check_services.yml

│   │   └── templates/        # report.html.j2

│   ├── cisco_compliance/     # Cisco IOS compliance checks

│   │   ├── tasks/            # check_ssh.yml, check_ntp.yml, check_security.yml,

│   │   │                       check_logging.yml, check_banner.yml, check_acl.yml

│   │   └── templates/        # cisco_report.html.j2

│   └── cisco_remediation/    # Cisco IOS auto-fix tasks

│       └── tasks/main.yml

├── templates/

│   └── full_report.html.j2   # combined report template

└── tests/

├── conftest.py           # dynamic host/policy loading for Linux tests

├── test_compliance.py    # Linux compliance tests (testinfra, real SSH)

└── test_cisco_compliance.py  # Cisco logic tests (no live connection needed)
```

## Adding a new compliance check (Linux)

1. Add the policy to `policies.yml`
2. Create or edit a task file in `roles/compliance/tasks/`
3. Register the result as `compliance_<your_check>_compliant`
4. Add the column to `roles/compliance/templates/report.html.j2` and `templates/full_report.html.j2`
5. Add a test case in `tests/test_compliance.py`

## Adding a new compliance check (Cisco IOS)

1. Create a new task file in `roles/cisco_compliance/tasks/`, e.g. `check_yourthing.yml`
2. Use `cisco.ios.ios_command` to run a `show` command
3. Register the result as `cisco_compliance_<your_check>_compliant`
4. Include the new task file in `roles/cisco_compliance/tasks/main.yml`
5. Add the column to `roles/cisco_compliance/templates/cisco_report.html.j2` and `templates/full_report.html.j2`
6. Add logic tests in `tests/test_cisco_compliance.py` (no live device needed — see existing tests for the pattern of mocking `show` command output as strings)
7. If the check is fixable, add a remediation task in `roles/cisco_remediation/tasks/main.yml`

## Adding support for a new vendor

Follow the `roles/cisco_compliance/` structure as a template:

1. Find the right Ansible collection (e.g. `junipernetworks.junos` for Juniper, `community.routeros` for MikroTik)
2. Create `roles/<vendor>_compliance/` with the same `tasks/` + `templates/` structure
3. Create a `<vendor>_site.yml` playbook at the project root
4. Add a `[<vendor>_devices]` group to `hosts.ini.example`
5. Update `templates/full_report.html.j2` to include the new vendor section
6. Document connection requirements in `README.md`

## Running tests before submitting

```bash
make lint        # ansible-lint, must pass production profile
make up           # start Docker test devices
make test         # pytest — Linux tests need containers running
make test-cov     # check coverage stays at 100%
```

For Cisco changes, test against a real device if possible (e.g. [Cisco DevNet Sandbox](https://developer.cisco.com/sandbox)) since `cisco.ios` modules cannot be meaningfully tested against the local Docker containers.

## Code style

- All Ansible tasks must use FQCN (`ansible.builtin.command`, not `command`)
- All role variables must be prefixed with the role name (`compliance_*`, `cisco_compliance_*`)
- `make lint` must report the `production` profile passing — no exceptions
- Keep `policies.yml` as the single source of truth — avoid hardcoding policy values in task files

## Known violations format

When a check fails for a documented reason, add it to `known_violations.yml` instead of skipping the test:

```yaml
known_violations:
  device-name:
    - check: check_identifier   # must match the xfail lookup key in the test
      reason: "Human-readable explanation"
```