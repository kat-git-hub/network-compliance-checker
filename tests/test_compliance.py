"""
Network Compliance Tests
Verifies that devices meet security policy requirements.
"""
import pytest

SSHD_CONFIG = "/etc/ssh/sshd_config"
NTP_PACKAGE = "chrony"
FTP_PACKAGE = "vsftpd"
SSH_SERVICE = "ssh"


class TestSSHCompliance:
    """SSH security policy checks."""

    def test_permit_root_login(self, device_name, device_config, all_hosts):
        """PermitRootLogin must match expected policy per device."""
        host = all_hosts[device_name]
        config = host.file(SSHD_CONFIG)
        if device_config["permit_root_login"]:
            assert config.contains("PermitRootLogin yes"), (
                f"{device_name}: expected PermitRootLogin yes (known violation)"
            )
        else:
            assert config.contains("PermitRootLogin no"), (
                f"{device_name}: expected PermitRootLogin no"
            )

    def test_ssh_protocol2(self, device_name, device_config, all_hosts):
        """Protocol 2 must be explicitly set where required."""
        host = all_hosts[device_name]
        config = host.file(SSHD_CONFIG)
        if device_config["ssh_protocol2"]:
            assert config.contains("Protocol 2"), (
                f"{device_name}: Protocol 2 should be set"
            )
        else:
            assert not config.contains("Protocol 2"), (
                f"{device_name}: Protocol 2 not expected"
            )

    def test_ssh_service_running(self, device_name, device_config, all_hosts):
        """SSH service must be running on all devices."""
        host = all_hosts[device_name]
        assert host.service(SSH_SERVICE).is_running, (
            f"{device_name}: SSH service should be running"
        )


class TestNTPCompliance:
    """NTP configuration checks."""

    def test_chrony_installed(self, device_name, device_config, all_hosts):
        """Chrony must be installed where required."""
        host = all_hosts[device_name]
        package = host.package(NTP_PACKAGE)
        if device_config["ntp_installed"]:
            assert package.is_installed, (
                f"{device_name}: chrony should be installed"
            )
        else:
            assert not package.is_installed, (
                f"{device_name}: chrony should NOT be installed (known violation)"
            )


class TestForbiddenServices:
    """Forbidden services checks."""

    def test_ftp_not_installed(self, device_name, device_config, all_hosts):
        """vsftpd must not be installed where forbidden."""
        host = all_hosts[device_name]
        package = host.package(FTP_PACKAGE)
        if device_config["ftp_installed"]:
            assert package.is_installed, (
                f"{device_name}: vsftpd present (known violation)"
            )
        else:
            assert not package.is_installed, (
                f"{device_name}: vsftpd should NOT be installed"
            )


class TestCompliantDevice:
    """Full compliance check — router-01 should pass all policies."""

    def test_router01_fully_compliant(self, all_hosts):
        host = all_hosts["router-01"]
        assert host.file(SSHD_CONFIG).contains("PermitRootLogin no")
        assert host.file(SSHD_CONFIG).contains("Protocol 2")
        assert host.package(NTP_PACKAGE).is_installed
        assert not host.package(FTP_PACKAGE).is_installed
        assert host.service(SSH_SERVICE).is_running
