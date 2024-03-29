import logging

import requests

from . import (
    DNSProvider,
    DNSRecord,
    RecordNotFound,
    TooManyRecordsFound,
    TooManyZonesFound,
    ZoneNotFound,
)


class CloudFlare(DNSProvider):
    def __init__(self, api_key: str):
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.api_key = api_key

    def get_record(
        self, zone_name: str, record_name: str, record_type: str = "A"
    ) -> DNSRecord:
        zone_id = self._get_zone_id(zone_name=zone_name)
        return self._get_record(
            zone_id=zone_id, record_name=record_name, record_type=record_type
        )

    def create_record(
        self, zone_name: str, record_name: str, content: str, record_type: str = "A"
    ) -> DNSRecord:
        zone_id = self._get_zone_id(zone_name=zone_name)
        return self._create_record(
            zone_id=zone_id,
            record_name=record_name,
            content=content,
            record_type=record_type,
        )

    def update_record_content(self, record: DNSRecord, content: str) -> DNSRecord:
        r = requests.patch(
            self.base_url + f"/zones/{record.zone_id}/dns_records/{record.id}",
            json={"content": content},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            r.raise_for_status()
        except Exception as exc:
            logging.error(exc)
            raise

        record_data = r.json()["result"]
        return DNSRecord(
            id=record_data["id"],
            name=record_data["name"],
            content=record_data["content"],
            type=record_data["type"],
            zone_id=record_data["zone_id"],
            zone_name=record_data["zone_name"],
        )

    def _get_zone_id(self, zone_name: str) -> str:
        r = requests.get(
            self.base_url + "/zones",
            params={"name": zone_name},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            r.raise_for_status()
        except Exception as exc:
            logging.error(exc)
            raise

        data = r.json()

        number_of_zones = len(data["result"])
        if number_of_zones == 0:
            exc = ZoneNotFound(f"Zone '{zone_name}' not found.")
            logging.error(exc)
            raise exc

        if number_of_zones > 1:
            exc = TooManyZonesFound(
                f"Too many zones ({number_of_zones}) found for zone name '{zone_name}'"
            )
            logging.error(exc)
            raise exc

        return data["result"][0]["id"]

    def _get_record(
        self, zone_id: str, record_name: str, record_type: str = "A"
    ) -> str:
        r = requests.get(
            self.base_url + f"/zones/{zone_id}/dns_records",
            params={"name": record_name, "type": record_type},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            r.raise_for_status()
        except Exception as exc:
            logging.error(exc)
            raise

        data = r.json()

        number_of_records = len(data["result"])
        if number_of_records == 0:
            exc = RecordNotFound(
                f"Record '{record_name}' of type '{record_type}' not found."
            )
            logging.error(exc)
            raise exc

        if number_of_records > 1:
            exc = TooManyRecordsFound(
                (
                    f"Too many records ({number_of_records}) found for record name "
                    f"'{record_name}' of type '{record_type}'"
                )
            )
            logging.error(exc)
            raise exc

        record_data = data["result"][0]
        return DNSRecord(
            id=record_data["id"],
            name=record_data["name"],
            content=record_data["content"],
            type=record_data["type"],
            zone_id=record_data["zone_id"],
            zone_name=record_data["zone_name"],
        )

    def _create_record(
        self,
        zone_id: str,
        record_name: str,
        content: str,
        record_type: str = "A",
    ) -> DNSRecord:
        r = requests.post(
            self.base_url + f"/zones/{zone_id}/dns_records",
            json={"content": content, "name": record_name, "type": record_type},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            r.raise_for_status()
        except Exception as exc:
            logging.error(exc)
            raise

        data = r.json()

        record_data = data["result"]
        return DNSRecord(
            id=record_data["id"],
            name=record_data["name"],
            content=record_data["content"],
            type=record_data["type"],
            zone_id=record_data["zone_id"],
            zone_name=record_data["zone_name"],
        )
