from __future__ import annotations


from typing import Any, Generic, TypeVar
import os
import toml
from local_utils.utils import HoopaUtils
from io import TextIOWrapper, SEEK_END

# There's definitely a better way of doing this
def relative_path(path) -> str:
    return os.path.join(os.path.dirname(__file__), path)  

T = TypeVar('T')
class ConfigObject(Generic[T]):
    name: str
    description: list[str]
    value: T
    
    def __init__(self, name: str, description: list[str]) -> None:
        self.name = name
        self.description = description

    def _is_valid(self, value: T) -> bool:
        return True
    
    def store_value(self, value: T):
        
        if not self._is_valid(value):
            HoopaUtils.print_error("Invalid value for config option %s, see above" % self.name)
            exit(1)
            
        self.value = value
        
    def append_config(self, filestream: TextIOWrapper):
       
        filestream.seek(0, SEEK_END)
        filestream.write("\n")
        
        for description_line in self.description:
            filestream.write("# %s\n" % description_line)
        filestream.write("%s = \"\"\n\n" % self.name)
        
    
        
class OneOfConfigObj(ConfigObject[T]):
    
    valid_values: list[T]
    
    def __init__(self, name: str, description: list[str], valid_values: list[T]) -> None:
        self.valid_values = valid_values
        super().__init__(name, description)
    
    def _is_valid(self, value: T) -> bool:
        
        for item in self.valid_values:
            if value == item:
                return True
        toml.load
        
        HoopaUtils.print_info("Value is \"" + str(value) + "\", which is not one of the following valid values:")
        HoopaUtils.print_info(str(self.valid_values))
        return False
    

    



class Config:
    
    config_path = relative_path('../config.toml')
    
    _all_config_names = [
        "repository_path",
        "game_region"
    ]
    
    repository_path = ConfigObject[str](
        "REPOSITORY_PATH", [
            "The location of your clone of pmdsky-debug (or a fork of it)",
            "the program expects *its* specific layout of symbol and header files to know where-and-how to paste new information",
            "it will read from this location, but for security reasons, will never attempt to write to any file there."
        ])
    game_region = OneOfConfigObj[str](
        "GAME_REGION", [
            "The region of your ROM. Changes which field is used for saving \"address\" and \"length\" by default.",
            "Should be of NA, EU, or JP"
        ],
        ["NA", "EU", "JP"]
    )
    
    
    
    def __init__(self) -> None:
        
        if not os.path.exists(self.config_path):
            self._make_new_config()
        else:
            
            
            
            data = toml.load(self.config_path)

            for name in self._all_config_names:
                option: ConfigObject[Any] = getattr(self, name)
                if not option.name in data:
                    
                    HoopaUtils.print_error("Could not find config property %s in config.toml! Adding option and description to config...\n" % option.name)
                    with open(self.config_path, "a") as config_file:
                        option.append_config(config_file)
                    exit(1)
                
                option.store_value(data[option.name])
            
            
            
            
            
    def _make_new_config(self) -> None:
        
        HoopaUtils.print_info("Config not found, creating a new one. Remember to fill it out before use!\n")
        with open(self.config_path, "x") as destfile:
            
            # There's probably an easier way to do this
            for name in self._all_config_names:
                
                option: ConfigObject[Any] = getattr(self, name)
                option.append_config(destfile)
                
        exit(0)
        

CONFIG_INSTANCE = Config()


    
    