from hoopa_unbound.constants_and_config import CONFIG
from hoopa_unbound.define.symbols_and_headers import SymbolsYamlFile, Symbol, SymbolKind, FunctionSymbol, DataSymbol, RegionalData, Region
from hoopa.merge import try_add_symbol_to_yml
from os import path
import copy
version = "0.0.1"


def tests_1():
    
    arm9_symbols = SymbolsYamlFile.from_yaml(
        path.join(CONFIG.repository_path.value, "symbols/arm9.yml")  # type: ignore
    )

    # This should fail to find a valid yml
    test_symbol = FunctionSymbol("Test", RegionalData(0x2000800,0x2000800,0x2000800),RegionalData(-1,-1,-1),["..."])
    print(try_add_symbol_to_yml(test_symbol, SymbolsYamlFile.from_yaml(
        path.join(CONFIG.repository_path.value, "symbols/overlay29.yml")
    )))
    # This should fail because a symbol exists at that address already
    test_symbol = FunctionSymbol("Test", RegionalData(0x2000800,0x2000800,0x2000800),RegionalData(-1,-1,-1),["..."])
    print(try_add_symbol_to_yml(test_symbol, arm9_symbols))
    # This should succeed, because no function symbol lives at this address.
    test_symbol = FunctionSymbol("Test", RegionalData(0x2000004,0x2000004,0x2000004),RegionalData(-1,-1,-1),["..."])
    print(try_add_symbol_to_yml(test_symbol, arm9_symbols))
    # This should fail, because it overlaps with SECURE.
    test_symbol = DataSymbol("Test", RegionalData(0x2000004,0x2000004,0x2000004),RegionalData(-1,-1,-1),["..."])
    print(try_add_symbol_to_yml(test_symbol, arm9_symbols))
    
    
def tests_2():
    
    arm9_symbols = SymbolsYamlFile.from_yaml(
        path.join(CONFIG.repository_path.value, "symbols/arm9.yml")  # type: ignore
    )
    print(arm9_symbols)
    print(arm9_symbols.get_symbol_by_address(0x2005050, Region.NA, SymbolKind.ANY))
    print(arm9_symbols.get_symbol_by_name("EuclideanNorm", SymbolKind.ANY))
    
    
if __name__ == '__main__':
    print("\tHOOPA - V%s" % version)  
    
    #tests_1()
    tests_2()
    
