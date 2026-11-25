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
        map: dict[str, ExtendedRegions] = ExtendedRegions._value2member_map_ # pyright: ignore[reportAssignmentType] # My python plugin wasn't convinced this would be a map of StrEnum and not Enum
        if name in map:
            return map[name]
        else:
            return ExtendedRegions.EU
        
        
    
    

class SymbolKind(Enum):
    ANY = 0
    DATA = 1
    FUNCTION = 2
    
    
# It's a uhhhh regional dialect
@dataclass
class RegionalData(SupportsKV):
    '''
    A piece of data defined once for each region of the game. 
    
    May or may not vary for each region.
    
    May or may not be present for each region.
    '''
    EU: list[int]
    NA: list[int]
    JP: list[int]
    
    
    def __init__(self, EU: int | list[int] = [], NA: int | list[int] = [], JP: int | list[int] = []) -> None:
        # Allow initalizing from integers or lists of integers (some symbols can have more than one address)
        
        if type(EU) == int:
            self.EU = [EU]
        else:
            self.EU = EU # type: ignore
            
        if type(NA) == int:
            self.NA = [NA]
        else:
            self.NA = NA # type: ignore
            
        if type(JP) == int:
            self.JP = [JP]
        else:
            self.JP = JP # type: ignore
        
        
    
    @classmethod
    def from_dict(cls, data: dict[str, int]) -> Self:
        '''
        Initializes this object from a dictionary of data, provided the dictionary has keys matching the names of its fields.
        '''
        new_instance = cls()
        for property_name, _ in new_instance:
            corrected_name = property_name.replace("_", "-") # Match format seen in file
            if corrected_name in data:
                
                if type(data[corrected_name]) == int:
                    setattr(new_instance, property_name, [ data[corrected_name] ])
                else:
                    setattr(new_instance, property_name, data[corrected_name] )
                
        return new_instance
                
        
    
    def to_strings(self, indent: int = 0) -> list[str]:
        
        string_list: list[str] = []
        for region, value in self:
            # Only specified values will be returned in the list
            if len(value) == 1:
                string_list.append(f"{region}: {int_to_hex_str_formatted(value[0])}")
            elif len(value) > 1:
                string_list.append(f"{region}:")
                for address in value:
                    string_list.append(f"  - {int_to_hex_str_formatted(address)}")
        
        return indent_string_list(indent, string_list)
    
        
    def any_present(self) -> bool:
        '''
        Returns whether any of this RegionalData object's fields have been filled out with data.
        
        If false, `RegionalData.to_strings()` will return an empty list.
        '''
        
        for _, value in self:
            if len(value) > 0:
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
    
    # Appeasing the dataclass gods
    EU_ITCM: list[int] = field(default_factory=lambda : [])
    NA_ITCM: list[int] = field(default_factory=lambda : [])
    JP_ITCM: list[int] = field(default_factory=lambda : [])
    EU_WRAM: list[int] = field(default_factory=lambda : [])
    NA_WRAM: list[int] = field(default_factory=lambda : [])
    JP_WRAM: list[int] = field(default_factory=lambda : [])
    EU_RAM: list[int] = field(default_factory=lambda : [])
    NA_RAM: list[int] = field(default_factory=lambda : [])
    JP_RAM: list[int] = field(default_factory=lambda : [])
    
    # Also appeasing the dataclass gods. For some reason it wouldn't accept that the __init__ from the baseclass didn't require these three arguments??? so???
    def __init__(self, EU: int | list[int] = [], NA: int | list[int] = [], JP: int | list[int] = []) -> None:
        # Allow initalizing from integers or lists of integers (some symbols can have more than one address)
        if type(EU) == int:
            self.EU = [EU]
        else:
            self.EU = EU # type: ignore
    
        if type(NA) == int:
            self.NA = [NA]
        else:
            self.NA = NA # type: ignore
    
        if type(JP) == int:
            self.JP = [JP]
        else:
            self.JP = JP # type: ignore
        
        # Now that these objects are lists, __dict__ (and thus the whole functionality of SupportsKV) can't see them
        # So I have to explicitly set them at least once, just like with the config
        # ... I have a sneaking suspicion this is pass-by-reference related...
        self.EU_ITCM = []
        self.NA_ITCM = []
        self.JP_ITCM = []  
        self.EU_RAM = []
        self.NA_RAM = []
        self.JP_RAM = []
        self.EU_WRAM = []
        self.NA_WRAM = []
        self.JP_WRAM = []
        
    
    
    def add_itcm_values(self, eu_itcm: int | list[int] = [], na_itcm: int | list[int] = [], jp_itcm: int | list[int] = []):
        if type(eu_itcm) == int:
            self.EU_ITCM = [eu_itcm]
        else:
            self.EU_ITCM = eu_itcm # type: ignore
        
        if type(na_itcm) == int:
            self.NA_ITCM = [na_itcm]
        else:
            self.NA_ITCM = na_itcm # type: ignore
        
        if type(jp_itcm) == int:
            self.JP_ITCM = [jp_itcm]
        else:
            self.JP_ITCM = jp_itcm # type: ignore
        
        
        
    def add_ram_values(self, eu_ram: int | list[int] = [], na_ram: int | list[int] = [], jp_ram: int | list[int] = [], eu_wram: int | list[int] = [], na_wram: int | list[int] = [], jp_wram: int | list[int] = []):
    
        # Yeaaaah this is kinda ugly, I know.
        if type(eu_ram) == int:
            self.EU_RAM = [eu_ram]
        else:
            self.EU_RAM = eu_ram # type: ignore
        
        if type(na_ram) == int:
            self.NA_RAM = [na_ram]
        else:
            self.NA_RAM = na_ram # type: ignore
        
        if type(jp_ram) == int:
            self.JP_RAM = [jp_ram]
        else:
            self.JP_RAM = jp_ram # type: ignore
        
        if type(eu_wram) == int:
            self.EU_WRAM = [eu_wram]
        else:
            self.EU_WRAM = eu_wram # type: ignore
    
        if type(na_wram) == int:
            self.NA_WRAM = [na_wram]
        else:
            self.NA_WRAM = na_wram # type: ignore
    
        if type(jp_wram) == int:
            self.JP_WRAM = [jp_wram]
        else:
            self.JP_WRAM = jp_wram # type: ignore
    


    def to_strings(self, indent: int = 0) -> list[str]:
        strings = super().to_strings(indent)
        return [i.replace("_", "-") for i in strings]
        
            
        
        
        
    def __str__(self) -> str:
        return ", ".join(i.replace("_", "-") for i in self.to_strings(0))



class Symbol():
    
    name: str
    kind: SymbolKind
    address: RegionalData
    length: RegionalData
    description: list[str]
    
    
        
    def __init__(self, name: str = "", address: RegionalData = RegionalData(), length: RegionalData = RegionalData(), description: list[str] = []) -> None:
        
        self.name = name 
        self.address = address
        self.length = length
        self.description = description
        
        
    
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
    
    
    
    def __str__(self) -> str:
        return "\n".join(self.to_strings(0))
        
        
        
    def to_strings(self, indent: int = 0) -> list[str]:
        string_list = []
        
        string_list.append(f"- name: {self.name}")
        if self.address.any_present(): # Should be, in almost all cases
            string_list.append("  address:")
            string_list.extend(self.address.to_strings(indent + 4))
            
        if self.length.any_present():
            string_list.append("  length:")
            string_list.extend(self.length.to_strings(indent + 4))
            
        if len(self.description) > 0:
            
            if len(self.description) == 1:
                string_list.append(f"  description: \"{self.description[0]}\"")
            else:
                string_list.append("  description: |-")
                string_list.extend(indent_string_list(indent + 4, self.description))
        
        
        return indent_string_list(indent, string_list)
    
    
    

# Both of these will eventually implement behavior to write the symbol to a header, hence the separated classes
        
class DataSymbol(Symbol):
    
    def __init__(self, name: str = "", address: RegionalData = RegionalData(), length: RegionalData = RegionalData(), description: list[str] = []) -> None:
        super().__init__(to_screaming_snake_case(name), address, length, description)
        # If we pass a generic symbol as a param, and need to know what type of symbol it is later.
        self.kind = SymbolKind.DATA

class FunctionSymbol(Symbol):

    def __init__(self, name: str = "", address: RegionalData = RegionalData(), length: RegionalData = RegionalData(), description: list[str] = []) -> None:
        super().__init__(to_upper_camel_case(name), address, length, description)
        # If we pass a generic symbol as a param, and need to know what type of symbol it is later.
        self.kind = SymbolKind.FUNCTION
        



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
    
        if not path.isfile(yaml_file_path) or not (yaml_file_path.endswith(".yml") or yaml_file_path.endswith(".yaml")) :
            
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
        
        
    
    def get_symbol_by_name(self, name: str, kind: SymbolKind) -> Symbol | None:
        '''
        From a given name, finds and returns a symbol that has that name, if one is present.
        '''
        
        if kind == SymbolKind.FUNCTION or kind == SymbolKind.ANY:
            for sym in self.functions:
                if sym.name == name:
                    return sym
        
        if kind == SymbolKind.DATA or kind == SymbolKind.ANY:
            for sym in self.data:
                if sym.name == name:
                    return sym
                
        return None
    
    
    
    def get_symbol_by_address(self, address: int, region: Region, kind: SymbolKind) -> Symbol | None:
        '''
        From a given address, finds and returns a symbol that has that name, if one is present.
        '''

        if kind == SymbolKind.FUNCTION or kind == SymbolKind.ANY:
            for sym in self.functions:
                target_address = getattr(sym.address, region)
                # return if any address matches
                for indv_addr in target_address:
                    if indv_addr == address:
                        return sym
              

        if kind == SymbolKind.DATA or kind == SymbolKind.ANY:
            for sym in self.data:
                target_address = getattr(sym.address, region)
                for indv_addr in target_address:
                    if indv_addr == address:
                        return sym
        

        return None
           
           
    
        
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
    