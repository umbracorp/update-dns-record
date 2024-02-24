import logging
import logging.handlers
from typing import Literal, Optional

import click
import requests

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} {levelname} {msg}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            filename="update-dns-record.log",
            encoding="utf-8",
            maxBytes=1024,
            backupCount=3,
        ),
    ],
)


@click.command()
@click.argument("provider", type=str)
@click.argument("record_name", type=str)
@click.option(
    "--ip",
    type=str,
    help="IP address to set in record. If not given then IP of host machine will be assumed.",
)
def main(provider: Literal["cloudflare"], record_name: str, ip: Optional[str] = None):
    """
    Update a DNS record in a remote provider.

    PROVIDER: The provider to use to update the DNS record. Available choices are
    ["cloudflare"].

    RECORD_NAME: The name of the record in the provider's system.
    """
    logging.info(f"Updating DNS record '{record_name}' with provider '{provider}'")
    ip = ip or get_public_ip()
    logging.info(f"Setting '{record_name}' record to IP '{ip}'")


def get_public_ip() -> str:
    r = requests.get("https://api.ipify.org", params={"format": "json"})
    try:
        r.raise_for_status()
    except Exception as exc:
        logging.error(exc)
        raise
    return r.json()["ip"]


if __name__ == "__main__":
    main()
