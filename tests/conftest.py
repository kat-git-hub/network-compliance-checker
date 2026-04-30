import pytest
import testinfra
import os

SSH_KEY = os.path.expanduser("~/.ssh/id_rsa")

def get_host(port):
    return testinfra.get_host(
        f"paramiko://ubuntu@localhost:{port}",
        ssh_identity_file=SSH_KEY,
    )

@pytest.fixture
def router01():
    return get_host(2221)

@pytest.fixture
def router02():
    return get_host(2222)

@pytest.fixture
def switch01():
    return get_host(2223)

@pytest.fixture
def switch02():
    return get_host(2224)

@pytest.fixture
def firewall01():
    return get_host(2225)
