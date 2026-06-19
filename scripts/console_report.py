"""
Console compliance report — reads reports/report.json
and prints a colored summary table to the terminal.

Usage:
    poetry run python scripts/console_report.py
"""
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.text import Text

REPORT_PATH = Path(__file__).parent.parent / "reports" / "report.json"


def status_text(value) -> Text:
    if value is True:
        return Text("✓", style="bold green")
    if value is False:
        return Text("✗", style="bold red")
    return Text("?", style="dim")


def main() -> int:
    if not REPORT_PATH.exists():
        print(f"Report not found at {REPORT_PATH}. Run 'make full-run' first.")
        return 1

    data = json.loads(REPORT_PATH.read_text())
    console = Console()

    console.print()
    console.print(f"[bold]Network Compliance Report[/bold]  [dim]({data['generated']})[/dim]")
    console.print()

    # --- Linux devices ---
    linux_devices = data.get("linux_devices", {})
    if linux_devices:
        table = Table(title="Linux Devices", title_style="bold cyan")
        table.add_column("Device")
        table.add_column("Root Login\nDisabled", justify="center")
        table.add_column("SSH Proto 2", justify="center")
        table.add_column("NTP", justify="center")

        forbidden_keys = set()
        for d in linux_devices.values():
            forbidden_keys.update(d.get("forbidden_services", {}).keys())
        forbidden_keys = sorted(forbidden_keys)
        for svc in forbidden_keys:
            table.add_column(svc, justify="center")
        table.add_column("Status", justify="center")

        for name, d in linux_devices.items():
            forbidden = d.get("forbidden_services", {})
            forbidden_ok = all(forbidden.values()) if forbidden else True
            compliant = (
                d.get("permit_root_login_disabled")
                and d.get("ssh_protocol2_enforced")
                and d.get("ntp_installed")
                and forbidden_ok
            )
            row = [
                name,
                status_text(d.get("permit_root_login_disabled")),
                status_text(d.get("ssh_protocol2_enforced")),
                status_text(d.get("ntp_installed")),
            ]
            for svc in forbidden_keys:
                row.append(status_text(forbidden.get(svc)))
            row.append(
                Text("PASS", style="bold green") if compliant else Text("FAIL", style="bold red")
            )
            table.add_row(*row)

        console.print(table)
        console.print()

    # --- Cisco devices ---
    cisco_devices = data.get("cisco_devices", {})
    if cisco_devices:
        table = Table(title="Cisco IOS Devices", title_style="bold blue")
        table.add_column("Device")
        table.add_column("SSH v2", justify="center")
        table.add_column("VTY Timeout", justify="center")
        table.add_column("NTP", justify="center")
        table.add_column("Pwd Encrypt", justify="center")
        table.add_column("Login", justify="center")
        table.add_column("Logging", justify="center")
        table.add_column("Banner", justify="center")
        table.add_column("ACL", justify="center")
        table.add_column("Status", justify="center")

        for name, d in cisco_devices.items():
            if d.get("unreachable"):
                table.add_row(
                    name,
                    *([Text("—", style="dim")] * 8),
                    Text("UNREACHABLE", style="dim italic"),
                )
                continue

            compliant = all([
                d.get("ssh_version2"),
                d.get("vty_exec_timeout"),
                d.get("ntp_configured"),
                d.get("password_encryption"),
                d.get("login_local_or_aaa"),
                d.get("logging_configured"),
                d.get("banner_configured"),
                d.get("acl_configured"),
            ])
            table.add_row(
                name,
                status_text(d.get("ssh_version2")),
                status_text(d.get("vty_exec_timeout")),
                status_text(d.get("ntp_configured")),
                status_text(d.get("password_encryption")),
                status_text(d.get("login_local_or_aaa")),
                status_text(d.get("logging_configured")),
                status_text(d.get("banner_configured")),
                status_text(d.get("acl_configured")),
                Text("PASS", style="bold green") if compliant else Text("FAIL", style="bold red"),
            )

        console.print(table)
        console.print()

    return 0


if __name__ == "__main__":
    sys.exit(main())