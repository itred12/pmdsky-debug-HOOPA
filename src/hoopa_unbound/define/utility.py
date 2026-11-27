from __future__ import annotations
from typing import Generic, TypeVar, Any, Iterator, Tuple, overload
from dataclasses import dataclass, astuple, fields
from colorama import Fore, Style



#! ------------------------------ #
#!           FUNCTIONS            #
#! ------------------------------ #



def print_error(contents: str):
    '''
    A prettier print(), that prepends `"HOOPA_UNBOUND - ERROR:"` to the message in magenta.
    
    Similar output to typical python errors, but without the stack trace, for when such would be irrelevant/drown out the message itself (which I find normal errors to sometimes do)
    '''
    print(f"{Fore.LIGHTMAGENTA_EX}HOOPA_UNBOUND - ERROR: {Fore.LIGHTBLUE_EX}{contents}{Style.RESET_ALL}")
    
    
def print_info(contents: str):
    '''
    A prettier print(), that prepends `"HOOPA_UNBOUND - INFO:"` to the message in cyan.
    '''
    print(f"{Fore.LIGHTCYAN_EX}HOOPA_UNBOUND - INFO: {Fore.LIGHTBLUE_EX}{contents}{Style.RESET_ALL}")
    
    
# TODO: drop calls to this function if not in debug mode(?) (as to not print debug messages when not relevant)   
def print_debug(contents: str):
    print(f"{Fore.WHITE}HOOPA_UNBOUND - DEBUG: {Fore.LIGHTBLUE_EX}{contents}{Style.RESET_ALL}")
    

# Overloads used here to ensure all values passed to clamp() were cast to the same type
# does it even remotely matter? No. lol. lmao.
# But it does make it a smidgeon nicer to use, and taught me how to use overloads, so there's that
@overload
def clamp(n: int, smallest: int, largest: int) -> int: ...
@overload
def clamp(n: float, smallest: float, largest: float) -> float: ...

def clamp(n, smallest, largest):
    '''
    Clamps a value N between `smallest` and `largest` (inclusive).
    '''
    return max(smallest, min(n, largest))



def int_to_hex_str_formatted(input: int) -> str:
    """
    Returns the hex-representation of the given integer, in the format used by pmdsky_debug (all alphabetic characters capitalized)
    """
    hex_val = hex(input).upper().replace("X", "x") # Capitalize everything but the "x" in 0x<value>
    # Remove leading zero from value if present
    if hex_val[2] == "0":
        hex_val = "0x" + hex_val.removeprefix("0x0") # I'm really tired and this is the best way I could think of lol
    return hex_val



def is_str_hex(input: str) -> bool:
    return True if (input.removeprefix("0x") != input and input.removeprefix("0x").isalnum()) else False



def to_upper_camel_case(input: str) -> str:

    # Capitalize the first letter after any whitespace or underscore
    input_reconstructed = ""
    for i in range(len(input)):
        character = input[i]
        new_character = character
        if i == 0:
            new_character = new_character.upper()
        else:
            new_character = new_character.lower()

        if i > 0:
            last_character = input[i - 1]
            if last_character == ' ' or last_character == '_':
                new_character = new_character.upper()

        input_reconstructed += new_character

    input_reconstructed = input_reconstructed \
        .replace(" ", "") \
        .replace("_", "")
    return input_reconstructed

# TODO: SCREAMING_SNAKE_CASE <-> SCREAMING-KEBAB_CASE function, for work with symbol extended versions

def to_screaming_snake_case(input: str) -> str:
    input_reconstructed = ""
    for i in range(len(input)):
        character = input[i]


        # if this is an alphabetic, uppercase-character that is not the first in the string and not preceded by whitespace (which we deal with later), prepend an underscore to it
        # if this is a numeric character that is not the first in the string, and is preceeded by an alphabetic character, also prepend an underscore to it
        if (i > 0 and character.isalpha() and not character.islower() and not input[i - 1] == ' ') or (i > 0 and character.isnumeric() and input[i - 1].isalpha()): 
            input_reconstructed += "_"


        character = character.upper()
        input_reconstructed += character

    input_reconstructed = input_reconstructed.replace(" ", "_") 
    return input_reconstructed



def indent_string(amount: int = 2, input: str = "") -> str:

    indent_complete = ""
    for i in range(amount):
        indent_complete += " "

    return indent_complete + input


def indent_string_list(amount: int, input_items: list[str]) -> list[str]:
    new_items: list[str] = []
    for string in input_items:
        new_items.append(indent_string(amount, string))
    return new_items


def type_to_human_readable(input_string: str) -> str:
    '''
    Really, all this does it turn pointer types from "type*" to "type pointer" for the sake of function argument descriptions
    '''
    if input_string.endswith("*"):
        return input_string[:len(input_string) - 1] + " pointer"
    else:
        return input_string



def remove_file_extension_from_str(input_string: str) -> str:

    index = input_string.find(".")
    if index != -1:
        return input_string[:index]
    else:
        return input_string



#! ------------------------------ #
#!            CLASSES             #
#! ------------------------------ #



T = TypeVar('T')
V = TypeVar('V')
@dataclass
class Pair(Generic[T, V]):
    '''
    Akin to a single-item dictionary, where two values are tied to one-another in a consistent ordered pair.
    
    Supports unpacking assignment, meaning its contents can be assigned to variables by:
    
    ```python
        value_left, value_right = some_pair
        value_one, value_two = function_that_returns_a_pair()
    ```
    '''
    left: T
    right: V
    
    
    def __init__(self, a: T, b: V) -> None:
        self.left = a
        self.right = b
        
        
    def __str__(self) -> str:
        return "Pair<%s, %s>" % (self.left, self.right)
    
    
    def __iter__(self):
        return iter(astuple(self))
    
    
        

@dataclass
class SupportsKV:
    '''
    "Supports key-value"
    
    A dataclass such that `for property, value in class_instance` can be used to iterate over the classes' defined fields.
    
    Inheritors must also be dataclasses themselves.
    '''
    
    def __iter__(self) -> Iterator[tuple[str, Any]]:
        class_properties: list[tuple[str, Any]] = []
        for field in fields(self):
            # Due to python shenanigans, the second set of parenthesis turns the argument into a tuple
            class_properties.append((field.name, getattr(self, field.name)))
        return iter(class_properties)