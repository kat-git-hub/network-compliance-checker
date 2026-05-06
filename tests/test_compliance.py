"""
Network Compliance Tests
Policy-driven checks — edit policies.yml to change what is verified.
Known violations — document in known_violations.yml instead of fixing tests.
Add devices to hosts.ini — no code changes needed.
"""
import pytest

SSHD_CONFIG = "/etc/ssh/sshd_config"


class TestSSHCompliance:
    """SSH security policy checks."""

    def test_permit_root_login_disabled(self, device_name, all_hosts, policies, violations):
        """PermitRootLogin must be disabled per policy."""
        reason = violations.get(device_name, {}).get("permit_root_login")
        if reason:
            pytest.xfail(reason)

        if not policies["ssh"]["permit_root_login"]:
            host = all_hosts[device_name]
            result = host.run(f"grep -i PermitRootLogin {SSHD_CONFIG}")
            assert "yes" not in result.stdout.lower(), (
                f"{device_name}: PermitRootLogin must be disabled"
            )

    def test_ssh_service_running(self, device_name, all_hosts, policies, violations):
        """Required services must be running."""
        for service in policies["required_services"]:
            host = all_hosts[device_name]
            assert host.service(service).is_running, (
                f"{device_name}: {service} must be running"
            )


class TestNTPCompliance:
    """NTP configuration checks."""

    def test_ntp_package_installed(self, device_name, all_hosts, policies, violations):
        """NTP package must be installed if required by policy."""
        reason = violations.get(device_name, {}).get("ntp_missing")
        if reason:
            pytest.xfail(reason)

        if policies["ntp"]["required"]:
            host = all_hosts[device_name]
            package = policies["ntp"]["package"]
            assert host.package(package).is_installed, (
                f"{device_name}: {package} must be installed per NTP policy"
            )


class TestForbiddenServices:
    """Forbidden services must not be present."""

    def test_no_forbidden_services(self, device_name, all_hosts, policies, violations):
        """Forbidden services must not be installed."""
        reason = violations.get(device_name, {}).get("ftp_installed")
        if reason:
            pytest.xfail(reason)

        host = all_hosts[device_name]
        for service in policies["forbidden_services"]:
            assert not host.package(service).is_installed, (
                f"{device_name}: {service} is forbidden by policy"
            )
