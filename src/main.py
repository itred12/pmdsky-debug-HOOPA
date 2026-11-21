from hoopa_unbound.constants_and_config import CONFIG
from hoopa_unbound.define.symbols_and_headers import SymbolsYamlFile, Symbol, SymbolKind, FunctionSymbol, DataSymbol, RegionalData
from hoopa.merge import try_add_symbol_to_yml
import copy
version = "0.0.1"


if __name__ == '__main__':
    print("\tHOOPA - V%s" % version)  
    
    arm9_symbols = SymbolsYamlFile.from_yaml("../pmdsky-debug/symbols/arm9.yml")
    
    
    # This should fail to find a valid yml
    test_symbol = FunctionSymbol("Test", RegionalData(0x2000800,0x2000800,0x2000800),RegionalData(-1,-1,-1),"...")
    print(try_add_symbol_to_yml(test_symbol, SymbolsYamlFile.from_yaml("../pmdsky-debug/symbols/overlay29.yml")))
    # This should fail because a symbol exists at that address already
    test_symbol = FunctionSymbol("Test", RegionalData(0x2000800,0x2000800,0x2000800),RegionalData(-1,-1,-1),"...")
    print(try_add_symbol_to_yml(test_symbol, arm9_symbols))
    # This should succeed, because no function symbol lives at this address.
    test_symbol = FunctionSymbol("Test", RegionalData(0x2000004,0x2000004,0x2000004),RegionalData(-1,-1,-1),"...")
    print(try_add_symbol_to_yml(test_symbol, arm9_symbols))
    # This should fail, because it overlaps with SECURE.
    test_symbol = DataSymbol("Test", RegionalData(0x2000004,0x2000004,0x2000004),RegionalData(-1,-1,-1),"...")
    print(try_add_symbol_to_yml(test_symbol, arm9_symbols))
    
