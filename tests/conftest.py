"""
conftest.py — dynamic host and policy loading.
Reads hosts from hosts.ini and policies from policies.yml.
Add your own devices to hosts.ini — no code changes needed.
Linux hosts only — Cisco devices are tested via Ansible.
"""
import os
import warnings
import pytest
import testinfra
import yaml

SSH_KEY = os.path.expanduser("~/.ssh/id_rsa")
ROOT = os.path.join(os.path.dirname(__file__), "..")
HOSTS_INI = os.path.join(ROOT, "hosts.ini")
POLICIES_FILE = os.path.join(ROOT, "policies.yml")
VIOLATIONS_FILE = os.path.join(ROOT, "known_violations.yml")

LINUX_GROUPS = {"routers", "switches", "firewalls", "network_devices"}


def load_policies() -> dict:
    with open(POLICIES_FILE) as f:
        return yaml.safe_load(f)


def load_known_violations() -> dict:
    with open(VIOLATIONS_FILE) as f:
        data = yaml.safe_load(f)
    violations = {}
    for host, checks in data.get("known_violations", {}).items():
        violations[host] = {item["check"]: item["reason"] for item in checks}
    return violations


def load_hosts() -> dict:
    """Parse hosts.ini — Linux hosts only, skip Cisco devices."""
    hosts = {}
    current_group = None
    skip_group = False

    with open(HOSTS_INI) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("["):
                group = line.strip("[]")
                current_group = group
                skip_group = "cisco" in group.lower() or ":children" in group
                continue

            if skip_group:
                continue

            parts = line.split()
            hostname = parts[0]
            params = {}
            for part in parts[1:]:
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k.strip()] = v.strip()

            if "ansible_port" not in params:
                continue

            # skip network_cli devices
            if params.get("ansible_connection") == "network_cli":
                continue

            hosts[hostname] = {
                "host": params.get("ansible_host", "localhost"),
                "port": int(params.get("ansible_port", 22)),
                "user": params.get("ansible_user", "ubuntu"),
            }

    return hosts


def get_host(host: str, port: int, user: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return testinfra.get_host(
            f"paramiko://{user}@{host}:{port}",
            ssh_identity_file=SSH_KEY,
        )


@pytest.fixture(scope="session")
def policies() -> dict:
    return load_policies()


@pytest.fixture(scope="session")
def violations() -> dict:
    return load_known_violations()


@pytest.fixture(scope="session")
def all_hosts() -> dict:
    hosts = load_hosts()
    return {
        name: get_host(cfg["host"], cfg["port"], cfg["user"])
        for name, cfg in hosts.items()
    }


def pytest_generate_tests(metafunc):
    if "device_name" in metafunc.fixturenames:
        hosts = load_hosts()
        metafunc.parametrize(
            "device_name",
            list(hosts.keys()),
            ids=list(hosts.keys()),
        )


def pytest_configure(config):
    warnings.filterwarnings(
        "ignore",
        message="Unknown ssh-ed25519 host key",
        category=UserWarning,
    )
