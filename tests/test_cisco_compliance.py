"""
Cisco IOS Compliance Logic Tests
Tests the parsing logic of cisco_compliance role tasks
without connecting to a real device.
"""
import pytest


SHOW_IP_SSH_COMPLIANT = "SSH Enabled - version 2.0"
SHOW_IP_SSH_NON_COMPLIANT = "SSH Enabled - version 1.99"

SHOW_LINE_VTY_COMPLIANT = """
Timeouts:      Idle EXEC    Idle Session
               00:10:00        never
"""

SHOW_LINE_VTY_NON_COMPLIANT = """
Timeouts:      Idle EXEC    Idle Session
               00:00:00        never
"""

SHOW_RUNNING_NTP_COMPLIANT = "ntp server 8.8.8.8"
SHOW_RUNNING_NTP_NON_COMPLIANT = ""
SHOW_RUNNING_PWD_COMPLIANT = "service password-encryption"
SHOW_RUNNING_PWD_NON_COMPLIANT = ""
SHOW_RUNNING_LOGIN_AAA = "aaa authentication login default local"
SHOW_RUNNING_LOGIN_LOCAL = "login local"
SHOW_RUNNING_LOGIN_NON_COMPLIANT = ""
SHOW_RUNNING_LOGGING_COMPLIANT = "logging host 10.0.0.1"
SHOW_RUNNING_LOGGING_NON_COMPLIANT = ""
SHOW_RUNNING_BANNER_COMPLIANT = "banner motd"
SHOW_RUNNING_BANNER_NON_COMPLIANT = ""
SHOW_RUNNING_ACL_COMPLIANT = "ip access-list extended NAT-ACL"
SHOW_RUNNING_ACL_NON_COMPLIANT = ""


def check_vty_timeout(output: str) -> bool:
    """Check if VTY exec timeout is set and non-zero."""
    if "Idle EXEC" not in output:
        return False
    lines = output.split("Idle EXEC")[1].strip().splitlines()
    for line in lines[1:]:
        line = line.strip()
        if line:
            timeout = line.split()[0]
            return timeout != "00:00:00"
    return False


class TestSSHVersionCompliance:
    """Tests for SSH version check logic."""

    def test_ssh_version2_compliant(self):
        assert "version 2" in SHOW_IP_SSH_COMPLIANT

    def test_ssh_version199_non_compliant(self):
        assert "version 2" not in SHOW_IP_SSH_NON_COMPLIANT

    def test_ssh_disabled_non_compliant(self):
        assert "version 2" not in ""


class TestVTYTimeoutCompliance:
    """Tests for VTY exec-timeout check logic."""

    def test_exec_timeout_set_compliant(self):
        assert check_vty_timeout(SHOW_LINE_VTY_COMPLIANT) is True

    def test_exec_timeout_zero_non_compliant(self):
        assert check_vty_timeout(SHOW_LINE_VTY_NON_COMPLIANT) is False

    def test_exec_timeout_no_idle_exec_non_compliant(self):
        assert check_vty_timeout("some random output") is False


class TestNTPCompliance:
    """Tests for NTP check logic."""

    def test_ntp_configured_compliant(self):
        assert "ntp server" in SHOW_RUNNING_NTP_COMPLIANT

    def test_ntp_missing_non_compliant(self):
        assert "ntp server" not in SHOW_RUNNING_NTP_NON_COMPLIANT


class TestPasswordEncryptionCompliance:
    """Tests for password encryption check logic."""

    def test_password_encryption_enabled_compliant(self):
        assert "service password-encryption" in SHOW_RUNNING_PWD_COMPLIANT

    def test_password_encryption_missing_non_compliant(self):
        assert "service password-encryption" not in SHOW_RUNNING_PWD_NON_COMPLIANT


class TestLoginCompliance:
    """Tests for login configuration check logic."""

    def test_login_local_compliant(self):
        output = SHOW_RUNNING_LOGIN_LOCAL
        assert "login local" in output or "aaa authentication login" in output

    def test_aaa_authentication_compliant(self):
        output = SHOW_RUNNING_LOGIN_AAA
        assert "login local" in output or "aaa authentication login" in output

    def test_no_login_non_compliant(self):
        output = SHOW_RUNNING_LOGIN_NON_COMPLIANT
        assert not ("login local" in output or "aaa authentication login" in output)


class TestLoggingCompliance:
    """Tests for logging check logic."""

    def test_logging_configured_compliant(self):
        assert "logging host" in SHOW_RUNNING_LOGGING_COMPLIANT

    def test_logging_missing_non_compliant(self):
        assert "logging host" not in SHOW_RUNNING_LOGGING_NON_COMPLIANT


class TestBannerCompliance:
    """Tests for banner check logic."""

    def test_banner_configured_compliant(self):
        assert "banner" in SHOW_RUNNING_BANNER_COMPLIANT

    def test_banner_missing_non_compliant(self):
        assert "banner" not in SHOW_RUNNING_BANNER_NON_COMPLIANT


class TestACLCompliance:
    """Tests for ACL check logic."""

    def test_acl_configured_compliant(self):
        assert "access-list" in SHOW_RUNNING_ACL_COMPLIANT

    def test_acl_missing_non_compliant(self):
        assert "access-list" not in SHOW_RUNNING_ACL_NON_COMPLIANT
