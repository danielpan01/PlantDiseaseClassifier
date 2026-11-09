"""Run the same complete installed-environment audit used by daily maintenance."""

from daily_health import audit_environment, audit_rows


if __name__ == '__main__':
    rows = audit_rows(audit_environment)
    for check, status, detail in rows:
        print(f'{status}: {check}: {detail}')
    raise SystemExit(any(status == 'FAIL' for _, status, _ in rows))
