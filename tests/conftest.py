import os
import pytest
import testinfra

SSH_KEY = os.path.expanduser("~/.ssh/id_rsa")

# Описание всех устройств и их ожидаемое состояние
DEVICES = {
    "router-01": {
        "port": 2221,
        "permit_root_login": False,
        "ssh_protocol2": True,
        "ntp_installed": True,
        "ftp_installed": False,
    },
    "router-02": {
        "port": 2222,
        "permit_root_login": False,
        "ssh_protocol2": False,
        "ntp_installed": False,
        "ftp_installed": False,
    },
    "switch-01": {
        "port": 2223,
        "permit_root_login": False,
        "ssh_protocol2": False,
        "ntp_installed": True,
        "ftp_installed": True,
    },
    "switch-02": {
        "port": 2224,
        "permit_root_login": True,
        "ssh_protocol2": False,
        "ntp_installed": True,
        "ftp_installed": False,
    },
    "firewall-01": {
        "port": 2225,
        "permit_root_login": True,
        "ssh_protocol2": False,
        "ntp_installed": False,
        "ftp_installed": True,
    },
}

def get_host(port: int):
    return testinfra.get_host(
        f"paramiko://ubuntu@localhost:{port}",
        ssh_identity_file=SSH_KEY,
    )

@pytest.fixture(scope="session")
def all_hosts() -> dict:
    """Return all hosts as testinfra connections."""
    return {
        name: get_host(config["port"])
        for name, config in DEVICES.items()
    }

def pytest_generate_tests(metafunc):
    """Auto-parametrize tests that use device_name + host fixtures."""
    if "device_name" in metafunc.fixturenames:
        metafunc.parametrize(
            "device_name,device_config",
            [(name, cfg) for name, cfg in DEVICES.items()],
            ids=list(DEVICES.keys()),
        )
