"""
conftest.py — dynamic host and policy loading.
Reads hosts from hosts.ini, policies from policies.yml,
and known violations from known_violations.yml.
Add your own devices to hosts.ini — no code changes needed.
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
    hosts = {}
    with open(HOSTS_INI) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("[") or line.startswith("#"):
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


def is_known_violation(device_name: str, check: str, violations: dict) -> str | None:
    """Return reason string if violation is known, else None."""
    return violations.get(device_name, {}).get(check)


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
