from __future__ import annotations
from enum import StrEnum, Enum
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, Literal, Self
from os import path
from yaml import safe_load

from hoopa_unbound.define.utility import (
    SupportsKV, Pair,
    int_to_hex_str_formatted, indent_string_list, to_screaming_snake_case, to_upper_camel_case, indent_string
)

class Region(StrEnum):
    EU = "EU"
    NA = "NA"
    JP = "JP"
    
    @staticmethod
    def from_name(name: str) -> ExtendedRegions:
        map: dict[str, ExtendedRegions] = ExtendedRegions._value2member_map_ # pyright: ignore[reportAssignmentType] #
        if name in map:
            return map[name]
        else:
            return ExtendedRegions.EU
    

class ExtendedRegions(StrEnum):
    EU = "EU"
    NA = "NA"
    JP = "JP"
    EU_ITCM = "EU-ITCM"
    NA_ITCM = "NA-ITCM"
    JP_ITCM = "JP-ITCM"
    EU_WRAM = "EU-WRAM"
    NA_WRAM = "NA-WRAM"
    JP_WRAM = "JP-WRAM"
    EU_RAM = "EU-RAM"
    NA_RAM = "NA-RAM"
    JP_RAM = "JP-RAM"
    
    @staticmethod
    def from_name(name: str) -> ExtendedRegions:
        map: dict[str, ExtendedRegions] = ExtendedRegions._value2member_map_ # pyright: ignore[reportAssignmentType] #
        if name in map:
            return map[name]
        else:
            return ExtendedRegions.EU
    

class SymbolKind(Enum):
    DATA = 0
    FUNCTION = 1
    
    
# It's a uhhhh regional dialect
@dataclass
class RegionalData(SupportsKV):
    '''
    A piece of data defined once for each region of the game. 
    
    May or may not vary for each region.
    
    May or may not be present for each region.
    '''
    EU: int
    NA: int
    JP: int
    
    
    def __init__(self, EU: int = -1, NA: int = -1, JP: int = -1) -> None:
        self.EU = EU
        self.NA = NA
        self.JP = JP
        
    
    @classmethod
    def from_dict(cls, data: dict[str, int]) -> Self:
        '''
        Initializes this object from a dictionary of data, provided the dictionary has keys matching the names of its fields.
        '''
        new_instance = cls()
        for property_name, _ in new_instance:
            if property_name in data:
                setattr(new_instance, property_name, data[property_name])
                
        return new_instance
                
        
    
    def to_strings(self, indent: int = 0) -> list[str]:
        
        string_list: list[str] = []
        for region, value in self:
            # Only specified values will be returned in the list
            if value >= 0:
                string_list.append(f"{region}: {int_to_hex_str_formatted(value)}")
        
        if indent > 0:
            return indent_string_list(indent, string_list)
        else:
            return string_list
    
        
    def any_present(self) -> bool:
        '''
        Returns whether any of this RegionalData object's fields have been filled out with data.
        
        If false, `RegionalData.to_strings()` will return an empty list.
        '''
        
        for _, value in self:
            if value >= 0:
                return True
        
        return False
        
    
    def __str__(self) -> str:
        return ", ".join(self.to_strings(0))
    
    
    def get_first(self) -> Pair[str, int]:
        '''
        Returns the first defined (value > -1) item in this RegionalData object
        '''
        for region, value in self:
            if value >= 0:
                return Pair(region, value)
        return Pair(Region.EU, -1) # Fallback
    
    
        

@dataclass
class ExtendedRegionalData(RegionalData):
    '''
    RegionalData with extended region support. Only ever used for the symbol.yml file headers.
    '''
    EU_ITCM: int = -1
    NA_ITCM: int = -1
    JP_ITCM: int = -1
    EU_WRAM: int = -1
    NA_WRAM: int = -1
    JP_WRAM: int = -1
    EU_RAM: int = -1
    NA_RAM: int = -1
    JP_RAM: int = -1
    
    
    def __init__(self, EU: int = -1, NA: int = -1, JP: int = -1) -> None:
        self.EU = EU
        self.NA = NA
        self.JP = JP
    
    
    
    def add_itcm_values(self, eu_itcm: int = -1, na_itcm: int = -1, jp_itcm: int = -1):
        self.EU_ITCM = eu_itcm
        self.NA_ITCM = na_itcm
        self.JP_ITCM = jp_itcm
        
        
    def add_ram_values(self, eu_ram: int = -1, na_ram: int = -1, jp_ram: int = -1, eu_wram: int = -1, na_wram: int = -1, jp_wram: int = -1):
        self.EU_RAM = eu_ram
        self.NA_RAM = na_ram
        self.JP_RAM = jp_ram
        self.EU_WRAM = eu_wram
        self.NA_WRAM = na_wram
        self.JP_WRAM = jp_wram


class Symbol():
    
    name: str
    address: RegionalData
    length: RegionalData
    description: list[str]
    
    
        
    def __init__(self, name: str = "", address: RegionalData = RegionalData(), length: RegionalData = RegionalData(), description: list[str] = []) -> None:
        
        self.name = name 
        self.address = address
        self.length = length
        self.description = description
        
        
        
    def to_strings(self, indent: int = 0) -> list[str]:
        string_list = []
        
        string_list.append(f"- name: {self.name}")
        if self.address.any_present(): # Should be, in almost all cases
            string_list.append("  address:")
            string_list.extend(self.address.to_strings(2))
            
        if self.length.any_present():
            string_list.append("  length:")
            string_list.extend(self.length.to_strings(2))
            
        if len(self.description) > 0:
            
            if len(self.description) == 1:
                string_list.append(f"  description: \"{self.description[0]}\"")
            else:
                string_list.append("  description: |-")
                string_list.extend(indent_string_list(2, self.description))
                
        return string_list
    
    
    @classmethod
    def from_data(cls, data: dict[str, Any]) -> Self:
        '''
        Initializes this object from a dictionary of data, provided the dictionary has keys mirroring its fields.
        '''
        self = cls()
        if "name" in data:
            self.name = data["name"]
            
        if "address" in data:
            self.address = RegionalData.from_dict(data["address"])
        
        if "length" in data:
            self.length = RegionalData.from_dict(data["length"])
            
        if "description" in data:
            self.description = []
            for line in data["description"].split("\n"):
                self.description.append(line)
                
        return self


# Both of these will eventually implement behavior to write the symbol to a header, hence the separated classes
        
class DataSymbol(Symbol):
    
    def __init__(self, name: str = "", address: RegionalData = RegionalData(), length: RegionalData = RegionalData(), description: list[str] = []) -> None:
        super().__init__(to_screaming_snake_case(name), address, length, description)
        # If we pass a generic symbol as a param, and need to know what type of symbol it is later.
        self.kind = SymbolKind(0)

class FunctionSymbol(Symbol):

    def __init__(self, name: str = "", address: RegionalData = RegionalData(), length: RegionalData = RegionalData(), description: list[str] = []) -> None:
        super().__init__(to_upper_camel_case(name), address, length, description)
        # If we pass a generic symbol as a param, and need to know what type of symbol it is later.
        self.kind = SymbolKind(1)
        



class SymbolsYamlFile:
    
    file_path: str
    
    header_data_path: str
    header_functions_path: str
    
    name: str
    versions: list[ExtendedRegions]
    address: ExtendedRegionalData
    length: ExtendedRegionalData
    description: list[str]
    subregions: list[SymbolsYamlFile]
    
    data: list[DataSymbol] = []
    functions: list[FunctionSymbol] = []
    
    
    def __init__(self, name: str = "", versions: list[ExtendedRegions] = [], address: ExtendedRegionalData = ExtendedRegionalData(), length: ExtendedRegionalData = ExtendedRegionalData(), description: list[str] = [], subregions: list[SymbolsYamlFile] = []) -> None:
        self.name = name
        self.versions = versions
        self.address = address
        self.length = length
        self.description = description
        self.subregions = subregions
        
    
    @classmethod
    def from_yaml(cls, yaml_file_path: str) -> Self:
        
        if not path.isfile(yaml_file_path) or not (yaml_file_path.endswith(".yml") or yaml_file_path.endswith(".yaml")):
            raise FileNotFoundError(f"HOOPA_UNBOUND - ERROR: SymbolsYamlFile attempted to be constructed with file at path [ {yaml_file_path} ], but the given path either doesn't exist, or is not a yaml (.yml) file!")
        
        self = cls()
        
        with open(yaml_file_path, "r+") as opened_file:
            raw_data: dict[str, Any] = safe_load(opened_file)
            
            for onekey, data in raw_data.items():
                self.name = onekey
                
                if type(data) != dict:
                    raise TypeError(
                        f"HOOPA_UNBOUND - ERROR: attempted to parse [ {yaml_file_path} ] as a SymbolsYamlFile object, but it was malformed!"
                        "\nSpecifically: data read from yaml didn't match sensible structure after `name`!"
                    )
                    
                
                
                if "versions" in data:
                    
                    if type(data["versions"]) != list:
                        raise TypeError(
                            f"HOOPA_UNBOUND - ERROR: attempted to parse [ {yaml_file_path} ] as a SymbolsYamlFile object, but it was malformed!"
                            f"\nSpecifically: field `versions` was present, but it wasn't a list as expected! For some reason, it is \"{data['versions']}\"."
                        )
                    
                    self.versions = []
                    for ver in data["versions"]:
                        self.versions.append(ExtendedRegions.from_name(ver))
                            
                            
                            
                if "address" in data:
                    
                    if type(data["address"]) != dict:
                        raise TypeError(
                            f"HOOPA_UNBOUND - ERROR: attempted to parse [ {yaml_file_path} ] as a SymbolsYamlFile object, but it was malformed!"
                            f"\nSpecifically: field `address` was present, but it wasn't a dict as expected! For some reason, it is \"{data['address']}\"."
                        )
                    
                    self.address = ExtendedRegionalData.from_dict(data["address"])
                    
                
                if "length" in data:
                    
                    if type(data["address"]) != dict:
                        raise TypeError(
                            f"HOOPA_UNBOUND - ERROR: attempted to parse [ {yaml_file_path} ] as a SymbolsYamlFile object, but it was malformed!"
                            f"\nSpecifically: field `length` was present, but it wasn't a dict as expected! For some reason, it is \"{data['length']}\"."
                        )
                    
                    self.length = ExtendedRegionalData.from_dict(data["length"])
                    

                if "description" in data:
                    
                    if type(data["description"]) != str:
                        raise TypeError(
                            f"HOOPA_UNBOUND - ERROR: attempted to parse [ {yaml_file_path} ] as a SymbolsYamlFile object, but it was malformed!"
                            f"\nSpecifically: field `description` was present, but it wasn't a string or multi-line string as expected! For some reason, it is \"{data['description']}\"."
                        )
                    
                    self.description = []
                    for line in data["description"].split("\n"):
                        self.description.append(line)
                        
                
                # TODO
                if "subregions" in data:
                    pass
                
                
                if "functions" in data:
                    
                    if type(data["functions"]) != list:
                        raise TypeError(
                            f"HOOPA_UNBOUND - ERROR: attempted to parse [ {yaml_file_path} ] as a SymbolsYamlFile object, but it was malformed!"
                            f"\nSpecifically: field `functions` was present, but it wasn't a list of dictionaries as expected! For some reason, it is \"{data['functions']}\"."
                        )
                    
                    self.functions = []
                    for func in data["functions"]:
                        self.functions.append(FunctionSymbol.from_data(func))
                       
                        
                if "data" in data:
        
                    if type(data["data"]) != list:
                        raise TypeError(
                            f"HOOPA_UNBOUND - ERROR: attempted to parse [ {yaml_file_path} ] as a SymbolsYamlFile object, but it was malformed!"
                            f"\nSpecifically: field `data` was present, but it wasn't a list of dictionaries as expected! For some reason, it is \"{data['data']}\"."
                        )
        
                    self.data = []
                    for dat in data["data"]:
                        self.data.append(DataSymbol.from_data(dat))
        
        
                    
                
            return self
    
    
    def __str__(self) -> str:
        strings_list = self.compose_yaml_header()
        if len(self.functions) > 0:
            strings_list.append(f"  functions: [ ... (x{len(self.functions)}) ]")
        else:
            strings_list.append(f"  functions: []")
        
        if len(self.data) > 0:
            strings_list.append(f"  data: [ ... (x{len(self.data)}) ]")
        else:
            strings_list.append(f"  data: []")
        
        return "\n".join(strings_list)
        
        
        
    def compose_yaml_header(self) -> list[str]:
        
        strings_list: list[str] = []
        
        if len(self.versions) > 0:
            strings_list.append("versions:")
            for ver in self.versions:
                strings_list.append( indent_string(2, "- " + ver) )
        
        if self.address.any_present():
            strings_list.append("address:")
            strings_list.extend(self.address.to_strings(2))
        
        if self.length.any_present():
            strings_list.append("length:")
            strings_list.extend(self.length.to_strings(2))
            
        if len(self.description) > 0:
        
            if len(self.description) == 1:
                strings_list.append(f"description: \"{self.description[0]}\"")
            else:
                strings_list.append("description: |-")
                strings_list.extend(indent_string_list(2, self.description))
        
        if len(self.subregions) > 0:
            strings_list.append("subregions:")
            for subreg in self.subregions:
                strings_list.append( indent_string(2, "- " + path.basename(subreg.file_path)) )
        
        final_list = indent_string_list(2, strings_list)
        final_list.insert(0, f"{self.name}:")
        
        return final_list
    
    
    
    def compose_yaml_functions(self) -> list[str]:
        strings_list: list[str] = []

        if len(self.functions) == 0:
            strings_list.append("functions: []")
        else:
            strings_list.append("functions:")
            self.functions.sort(key=lambda symbol: symbol.address.get_first().right ) # Sort by first address in each symbol, ascending (I *think* thats how its done?)
            for symbol in self.functions:
                strings_list.extend(symbol.to_strings(2))

        return strings_list
    
    
    
    def compose_yaml_data(self) -> list[str]:
        strings_list: list[str] = []
        
        if len(self.data) == 0:
            strings_list.append("data: []")
        else:
            strings_list.append("data:")
            self.data.sort(key=lambda symbol: symbol.address.get_first().right ) 
            for symbol in self.data:
                strings_list.extend(symbol.to_strings(2))
        
        return strings_list
    