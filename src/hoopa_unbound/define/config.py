'''
Holds classes used to define and handle config options read from config.toml
'''

from typing import Any, Generic, TypeVar
from dataclasses import dataclass
from hoopa_unbound.define.utility import Pair, print_error


# Is this overengineered? 100%
# But, (in the same cadence as a satirical Masahiro Sakurai) this is my VISION

T = TypeVar('T')
class BaseConfigHolder(Generic[T]):
    '''
    Base config holder class. Used to generate a config.toml file and to read from said file when the program is ran.
    '''
    
    name: str
    '''
    The name used for this config value within the file.
    '''
    description: str | list[str]
    '''
    The description written above this config option within the file, when the config file is first created.
    '''
    is_set: bool = False
    '''
    Whether this config holder is holding a value yet (indicating a successful load) or not.
    '''
    
    # Setters and getters to make things a bit prettier and less prone to error (kept accidentally assigning `value` directly by-habit)
    _value_internal: T
    
    @property
    def value(self) -> T:
        if self.is_set:
            return self._value_internal
        else:
            return None # type: ignore
    
    @value.setter
    def value(self, value):
        success, error_msg = self._is_valid(value)
        if success:
            self._value_internal = value
            self.is_set = True
        else:
            print_error(f"Value for config \"{self.name}\" failed validation! \nReason: \n[ {error_msg} ]")
    
    
    
    def __init__(self, name: str = "", description: str | list[str] = "") -> None:
        self.name = name
        self.description = description
        
    
    
        def __repr__(self) -> str:
    
            if self.is_set:
                return f"ConfigHolder {self.name}<{self.value}>"
            else:
                return f"ConfigHolder {self.name}<UNSET>"
    
        
        
    def _is_valid(self, value) -> Pair[bool, str]:
        '''
        Can be overriden by inheriting classes to perform more scrutiny on the given value from the config file.
        
        Returns a pair of (success/failure, failure reason), where the failure reason should be a string that is used to provide feedback if the value fails validation.
        '''
        return Pair(True, "")
    
    
    def to_lines(self) -> list[str]:
        '''
        Returns the representation of the config option as written to the config.toml, when config.toml is created for the first time.
        
        Can be overriden to provide extra details for more complicated config options (see: OneofConfigGHolder)
        '''
        returned_lines: list[str] = []
        if type(self.description) == str:
            returned_lines.append(f"# {self.description}")
        else:
            returned_lines.extend([f"# {commented_line}" for commented_line in self.description]) # appends the list but with a "#" prefixed to every line
        
        # This means that config.__remake_config() can be called if some config values are invalid/missing,
        # without scrapping the user's config entirely, as the values present and valid will be kept
        if self.is_set:
            returned_lines.append(f"{self.name} = \"{str(self.value)}\"")
        else: 
            returned_lines.append(f"{self.name} = \"\"")
        
        return returned_lines
        
        
   
        
    
class OneofConfigHolder(BaseConfigHolder[T]):
    
    valid_values: list[T]
    
   
    def __init__(self, name: str, description: str | list[str], valid_values: list[T]) -> None:
        super().__init__(name, description)
        self.valid_values = valid_values
        
        
    def _is_valid(self, value) -> Pair[bool, str]:
        if not value in self.valid_values:
            # Returns self.valid_values but with each element wrapped in quotations, because I was picky
            values_list = ", ".join(['"' + str(i) + '"' for i in self.valid_values])
            
            return Pair(False, f'Invalid value for this config option! \nIs "{value}", but should be one of: [{values_list}]')
        else: 
            return Pair(True, "")
       
       
    # Overloads to append a line to the description detailing all valid values for the option
    def to_lines(self) -> list[str]:
        constructed_lines = super().to_lines()
        
        values_list = ", ".join(['"' + str(i) + '"' for i in self.valid_values])
        constructed_lines.insert(-1, f"# Must be one of: {values_list}")
        return constructed_lines
    
    
