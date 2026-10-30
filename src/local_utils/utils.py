from __future__ import annotations

class HoopaUtils:
    
    @staticmethod
    def print_error(contents: str):
        print("\033[95mERROR - %s\033[00m" % contents)
    
    @staticmethod
    def print_info(contents: str):
        print("\033[94mINFO - %s\033[00m" % contents)
        
    @staticmethod
    def print_debug(contents: str):
        print("\033[37mDEBUG - %s\033[00m" % contents)
        
        
    @staticmethod
    def int_to_hex_str_formatted(input: int) -> str:
        """
        Returns the hex-representation of the given integer, in the format used by pmdsky_debug (all alphabetic characters capitalized)
        """
        hex_val = hex(input).upper().replace("X", "x") # Capitalize everything but the "x" in 0x<value>
        # Remove leading zero from value if present
        if hex_val[2] == "0":
            hex_val = "0x" + hex_val.removeprefix("0x0") # I'm really tired and this is the best way I could think of lol
        return hex_val
    
    @staticmethod
    def is_str_hex(input: str) -> bool:
        return True if (input.removeprefix("0x") != input and input.removeprefix("0x").isalnum()) else False