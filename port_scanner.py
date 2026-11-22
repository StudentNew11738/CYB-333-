"""CYB 333: Low-rate TCP connect scanner for explicitly authorized targets."""
import argparse
import socket
import time
from datetime import datetime, timezone

ALLOWED_HOSTS = {"127.0.0.1", "localhost", "scanme.nmap.org"}


def port_number(value):
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def main():
    parser = argparse.ArgumentParser(description="Authorized, rate-limited TCP port scanner")
    parser.add_argument("host", help="127.0.0.1, localhost, or scanme.nmap.org only")
    parser.add_argument("start", type=port_number, help="first port, 1-65535")
    parser.add_argument("end", type=port_number, help="last port, 1-65535")
    parser.add_argument("--delay", type=float, default=0.2, help="seconds between attempts (minimum 0.2)")
    parser.add_argument("--timeout", type=float, default=0.6, help="connection timeout in seconds")
    args = parser.parse_args()

    if args.host.lower() not in ALLOWED_HOSTS:
        parser.error("target not authorized; use localhost or scanme.nmap.org")
    if args.start > args.end:
        parser.error("start port must not exceed end port")
    if args.end - args.start + 1 > 100:
        parser.error("maximum 100 ports per run to limit scan intensity")
    if not 0.2 <= args.delay <= 10:
        parser.error("delay must be between 0.2 and 10 seconds")
    if not 0.1 <= args.timeout <= 5:
        parser.error("timeout must be between 0.1 and 5 seconds")
    if args.host.lower() == "scanme.nmap.org" and args.end - args.start + 1 > 10:
        parser.error("scanme.nmap.org is limited to 10 ports per run")

    try:
        # Resolve the requested host before attempting any connections.
        ip = socket.gethostbyname(args.host)
    except socket.gaierror as exc:
        print(f"ERROR: Cannot resolve host {args.host}: {exc}")
        return 2

    # Defense in depth: avoid unexpectedly scanning a non-loopback IP for localhost.
    if args.host.lower() in {"localhost", "127.0.0.1"} and not ip.startswith("127."):
        print("ERROR: localhost did not resolve to a loopback address")
        return 2

    print(f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}", flush=True)
    print(f"Target: {args.host} ({ip}) | Ports: {args.start}-{args.end}", flush=True)
    print(f"Timeout: {args.timeout}s | Delay: {args.delay}s", flush=True)
    started = time.monotonic()
    open_count = 0
    for port in range(args.start, args.end + 1):
        try:
            with socket.create_connection((ip, port), timeout=args.timeout):
                print(f"Port {port}: OPEN", flush=True)
                open_count += 1
        except (ConnectionRefusedError, TimeoutError, OSError) as exc:
            print(f"Port {port}: CLOSED/FILTERED ({type(exc).__name__})", flush=True)
        if port != args.end:
            time.sleep(args.delay)
    print(f"Finished: {open_count} open of {args.end - args.start + 1} scanned; "
          f"elapsed {time.monotonic() - started:.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
