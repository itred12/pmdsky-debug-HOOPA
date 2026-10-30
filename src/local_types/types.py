from __future__ import annotations
from utils import HoopaUtils
from enum import Enum, StrEnum
from typing import Any
import yaml


class PMD2Region(StrEnum):
    REGION_EU = "EU"
    REGION_NA = "NA"
    REGION_JP = "JP"
    
class PMD2RegionalData:
    EU: str
    NA: str
    JP: str
    
    def __init__(self, valueNA = -1, valueEU = -1, valueJP = -1) -> None:
        self.EU = HoopaUtils.int_to_hex_str_formatted(valueEU) if valueEU > -1 else ""
        self.NA = HoopaUtils.int_to_hex_str_formatted(valueNA) if valueNA > -1 else ""
        self.JP = HoopaUtils.int_to_hex_str_formatted(valueJP) if valueJP > -1 else ""
    
    @staticmethod
    def from_dict(data: dict) -> PMD2RegionalData:
        return PMD2RegionalData(
            data["NA"] if "NA" in data else -1,
            data["EU"] if "EU" in data else -1,
            data["JP"] if "JP" in data else -1,
        )
    
        
    def is_empty(self):
        """
        Returns whether this regional docstring has any of its fields filled out.
        """
        return True if self.NA == "" and self.EU == "" and self.JP == "" else False

    ### Thought this would be needed, but seemingly vars(object) keeps order based on declaration within the object itself?? Possibly???
    ### It SEEMS consistent, and shifting the declaration in the __init__ function shifts the order in the dictionary given by vars(object)
    ### So????? OKay??
    def get_ordered_values(self):
        return {
            "EU": self.EU,
            "NA": self.NA,
            "JP": self.JP
        }


class AddressRange:
    addr_from: int
    addr_to: int
    addr_len: int
    
    def __init__(self, addr_from, addr_to) -> None:
        self.addr_from = addr_from
        self.addr_to = addr_to
        self.addr_len = addr_to - addr_from
        
    def __str__(self) -> str:
        return "ADDRESSRANGE - From: %s, To: %s, Length: %s" % (
            HoopaUtils.int_to_hex_str_formatted(self.addr_from), HoopaUtils.int_to_hex_str_formatted(self.addr_to), HoopaUtils.int_to_hex_str_formatted(self.addr_len)
            )
    
    def get_json(self) -> dict[str, int]:
        return {"from": self.addr_from, "to": self.addr_to, "length": self.addr_len}
    
    

class PMD2AddressRange:
    EU: AddressRange
    NA: AddressRange
    JP: AddressRange
    
    def __init__(self, NA: list[int] = [], EU: list[int] = [], JP: list[int] = []) -> None:
        if len(NA) == 2:
            self.NA = AddressRange(NA[0], NA[1])
        if len(EU) == 2:
            self.EU = AddressRange(EU[0], EU[1])
        if len(JP) == 2:
            self.JP = AddressRange(JP[0], JP[1])
            
            
    def get_json(self) -> dict[str, dict[str, int]]:
        data = {}
        if getattr(self, "NA"):
            data["NA"] = self.NA.get_json()
        if getattr(self, "EU"):
            data["EU"] = self.EU.get_json()
        if getattr(self, "JP"):
            data["JP"] = self.JP.get_json()
        return data
        
   
    


class PMD2OverlayData:
    name: str
    versions: list[PMD2Region]
    addresses: PMD2RegionalData
    length: PMD2RegionalData
    description: str
    
    range: PMD2AddressRange
    
    
    def __init__(self, name: str, versions: list[PMD2Region], addresses: dict[PMD2Region, int], length: dict[PMD2Region, int], description: str) -> None:
        self.name = name
        self.versions = versions
        self.addresses = PMD2RegionalData.from_dict(addresses)
        self.length = PMD2RegionalData.from_dict(length)
        self.description = description
        
        self.range = PMD2AddressRange(
            [int(self.addresses.NA, 16), int(self.addresses.NA, 16) + int(self.length.NA, 16)],
            [int(self.addresses.EU, 16), int(self.addresses.EU, 16) + int(self.length.EU, 16)],
            [int(self.addresses.JP, 16), int(self.addresses.JP, 16) + int(self.length.JP, 16)]
        )
    
    
    @staticmethod
    def from_yaml(data: str) -> PMD2OverlayData:
        parsed_data: dict[str, Any] = yaml.safe_load(data)
        
        for overlayname, overlay_data in parsed_data.items():
            return PMD2OverlayData(
                overlayname,
                overlay_data["versions"],
                overlay_data["address"],
                overlay_data["length"],
                overlay_data["description"]
            )
            
            
    