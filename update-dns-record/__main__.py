import logging
import logging.handlers
from os import environ
from pathlib import Path
from typing import Literal, Optional

import click
import requests

from . import DNSProvider, RecordNotFound
from .cloudflare import CloudFlare

ProviderName = Literal["cloudflare"]

API_KEY = environ.get("API_KEY", default=None)
LOG_DIR = environ.get("LOG_DIR", default="./logs")
LOG_LENGTH_DAYS = int(environ.get("LOG_LENGTH_DAYS", default="7"))

log_path = Path(LOG_DIR)
log_path.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} {levelname} {msg}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.TimedRotatingFileHandler(
            filename=log_path.joinpath("update-dns-record.log"),
            encoding="utf-8",
            backupCount=LOG_LENGTH_DAYS,
            utc=True,
        ),
    ],
)


@click.command()
@click.argument("provider_name", type=str)
@click.argument("zone_name", type=str)
@click.argument("record_name", type=str)
@click.option(
    "--ip",
    type=str,
    help="IP address to set in record. If not given then IP of host machine will be assumed.",
)
@click.option(
    "--record-type",
    type=str,
    default="A",
    show_default=True,
    help="The DNS record type.",
)
@click.option(
    "--create",
    type=bool,
    is_flag=True,
    default=False,
    show_default=True,
    help="If record does not exist, create it. Default is False.",
)
def main(
    provider_name: ProviderName,
    zone_name: str,
    record_name: str,
    record_type: str = "A",
    ip: Optional[str] = None,
    create: bool = False,
):
    """
    Update a DNS record in a remote provider.

    PROVIDER_NAME: The provider to use to update the DNS record. Available choices are
    ["cloudflare"].

    ZONE_NAME: The name of the hosted zone.

    RECORD_NAME: The name of the record in the provider's system.
    """
    logging.info(f"Initialising provider '{provider_name}'...")
    provider = DNSProviderFactory.create(provider_name=provider_name)

    logging.info(
        f"Validating DNS record name '{record_name}' in zone name '{zone_name}'..."
    )
    try:
        record = provider.get_record(
            zone_name=zone_name, record_name=record_name, record_type=record_type
        )
    except RecordNotFound:
        logging.warning(f"Record '{record_name}' not found in zone '{zone_name}'")
        if create:
            record_found = False
        else:
            raise
    else:
        record_found = True

    ip = ip or get_public_ip()

    if record_found:
        logging.info(
            f"Comparing record content ({record.content}) to requested IP '{ip}'"
        )
        if record.content == ip:
            logging.info("Record content is already up-to-date.")
            return
        else:
            logging.info("Updating record content...")
            updated_record = provider.update_record_content(record=record, content=ip)
    else:
        logging.info(f"Creating record '{record_name}' in zone '{zone_name}'...")
        updated_record = provider.create_record(
            zone_name=zone_name,
            record_name=record_name,
            content=ip,
        )

    logging.info(
        f"Record '{record_name}' content updated to '{updated_record.content}'"
    )


def get_public_ip() -> str:
    logging.info("Requesting host machine public IP...")
    r = requests.get("https://api.ipify.org", params={"format": "json"})
    try:
        r.raise_for_status()
    except Exception as exc:
        logging.error(exc)
        raise
    ip = r.json()["ip"]
    logging.info(f"Host machine has public IP {ip}")
    return ip


class DNSProviderFactory:
    @staticmethod
    def create(provider_name: ProviderName) -> DNSProvider:
        if provider_name == "cloudflare":
            return CloudFlare(api_key=API_KEY)
        else:
            raise Exception(
                f"Invalid provider name '{provider_name}', options are {ProviderName}"
            )


if __name__ == "__main__":
    main()
