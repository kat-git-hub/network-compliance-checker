"""
Network Compliance Tests
Verifies that devices meet security policy requirements.
"""
import pytest


class TestSSHCompliance:
    """SSH security policy checks."""

    def test_router01_no_root_login(self, router01):
        """router-01 should have PermitRootLogin no."""
        sshd_config = router01.file("/etc/ssh/sshd_config")
        assert sshd_config.contains("PermitRootLogin no")

    def test_switch02_root_login_violation(self, switch02):
        """switch-02 should have PermitRootLogin yes — known violation."""
        sshd_config = switch02.file("/etc/ssh/sshd_config")
        assert sshd_config.contains("PermitRootLogin yes")

    def test_firewall01_root_login_violation(self, firewall01):
        """firewall-01 should have PermitRootLogin yes — known violation."""
        sshd_config = firewall01.file("/etc/ssh/sshd_config")
        assert sshd_config.contains("PermitRootLogin yes")

    def test_router01_ssh_protocol2(self, router01):
        """router-01 should have Protocol 2 explicitly set."""
        sshd_config = router01.file("/etc/ssh/sshd_config")
        assert sshd_config.contains("Protocol 2")


class TestNTPCompliance:
    """NTP configuration checks."""

    def test_router01_chrony_installed(self, router01):
        """router-01 should have chrony installed."""
        chrony = router01.package("chrony")
        assert chrony.is_installed

    def test_router02_chrony_missing(self, router02):
        """router-02 should NOT have chrony — known violation."""
        chrony = router02.package("chrony")
        assert not chrony.is_installed

    def test_switch01_chrony_installed(self, switch01):
        """switch-01 should have chrony installed."""
        chrony = switch01.package("chrony")
        assert chrony.is_installed

    def test_firewall01_chrony_missing(self, firewall01):
        """firewall-01 should NOT have chrony — known violation."""
        chrony = firewall01.package("chrony")
        assert not chrony.is_installed


class TestForbiddenServices:
    """Forbidden services checks."""

    def test_router01_no_ftp(self, router01):
        """router-01 should NOT have vsftpd installed."""
        vsftpd = router01.package("vsftpd")
        assert not vsftpd.is_installed

    def test_switch01_ftp_violation(self, switch01):
        """switch-01 should have vsftpd — known violation."""
        vsftpd = switch01.package("vsftpd")
        assert vsftpd.is_installed

    def test_firewall01_ftp_violation(self, firewall01):
        """firewall-01 should have vsftpd — known violation."""
        vsftpd = firewall01.package("vsftpd")
        assert vsftpd.is_installed

    def test_router01_ssh_running(self, router01):
        """SSH service should be running on router-01."""
        ssh = router01.service("ssh")
        assert ssh.is_running


class TestCompliantDevice:
    """Full compliance check for router-01 — should pass all policies."""

    def test_router01_fully_compliant(self, router01):
        assert router01.file("/etc/ssh/sshd_config").contains("PermitRootLogin no")
        assert router01.package("chrony").is_installed
        assert not router01.package("vsftpd").is_installed
