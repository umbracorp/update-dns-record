from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DNSRecord:
    id: str
    name: str
    content: str
    type: str
    zone_id: str
    zone_name: str


class DNSProvider(ABC):
    @abstractmethod
    def get_record(
        self, zone_name: str, record_name: str, record_type: str = "A"
    ) -> DNSRecord:
        raise NotImplementedError()

    @abstractmethod
    def update_record_content(self, record: DNSRecord, content: str) -> DNSRecord:
        raise NotImplementedError()
