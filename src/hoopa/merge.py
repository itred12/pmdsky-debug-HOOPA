from hoopa_unbound.constants_and_config import CONFIG
from hoopa_unbound.define.symbols_and_headers import SymbolsYamlFile, Symbol, SymbolKind, FunctionSymbol, DataSymbol, RegionalData
import copy

# I love multi-address symbols!
def listify(a):
    return a if isinstance(a, list) else [a]
    
'''
overlap_return {
    share_start : 1
    share_end : 1
    any_overlap: 1
}
Cumulative across all three regions. If true for any reason, the bitflag is enabled!
'''
def get_symbols_overlap(s1: (Symbol | SymbolsYamlFile), s2: (Symbol | SymbolsYamlFile)) -> int:
    overlap_return = 0b000
    a1 = [listify(s1.address.EU),listify(s1.address.NA),listify(s1.address.JP)]
    a2 = [listify(s2.address.EU),listify(s2.address.NA),listify(s2.address.JP)]
    l1 = [max(s1.length.EU,0),max(s1.length.NA,0),max(s1.length.JP,0)]
    l2 = [max(s2.length.EU,0),max(s2.length.NA,0),max(s2.length.JP,0)]
    for i in range(3):
        for j in range(len(a1[i])):
            for k in range(len(a2[i])):
                if a1[i][j] == a2[i][k]:
                    # share_start
                    overlap_return |= 0b001 
                if a1[i][j] + l1[i] == a2[i][k] + l2[i]:
                    # share_end
                    overlap_return |= 0b010
                if a1[i][j] <= a2[i][k] <= a1[i][j] + l1[i] or a2[i][k] <= a1[i][j] <= a2[i][k] + l2[i]:
                    # any_overlap
                    overlap_return |= 0b100

    return overlap_return


'''
Should recurse through ymls until it finds one that the symbol belongs in.

Not that there was ANY reason to search more than one layer deep, but eh why not.
'''
def try_find_valid_yml(symbol: Symbol, yml: SymbolsYamlFile) -> SymbolsYamlFile:
    if (get_symbols_overlap(symbol, yml) >> 2):
        return yml
    for sub_yml in yml.subregions:
        return_yml = try_find_valid_yml()
        if return_yml != None:
            return return_yml
    return None


'''
Attempts to add a symbol to a yml, 
Runs validation on a symbol to ensure it could be added to a yml without incident.
Verifies the following:
    - The new symbol's addresses are actually within the bounds of the yml, or the bounds of a subregion.
    - No existing symbols of the same type share an address with the new symbol (in any region)
    - No existing symbols of the same type overlap in length with the new symbol (in any region, data symbols only)
If all are true, will attempt to add the symbol to the yml.
'''
def try_add_symbol_to_yml(symbol: Symbol, yml: SymbolsYamlFile) -> [Symbol, int]: 
    conflict_symbol = None
    # If it's easier, we can just search the current yml. For things like libs, it probably will be...
    yml = try_find_valid_yml(symbol, yml)
    if (yml == None):
        print("Could not match yml to symbol!")
        return False
    # There's merit in running a check against both types, but that's doubling the lookup time...
    if(symbol.kind == SymbolKind.FUNCTION):
        for func in yml.functions:
            overlap_val = get_symbols_overlap(func, symbol)
            if overlap_val != 0:
                conflict_symbol = func
                print("Conflicting Symbol:")
                print(vars(conflict_symbol))
                break
        if conflict_symbol == None:
            yml.functions.append(symbol)
            print ("Appending to Functions!")
            return True
    else:
        for data in yml.data:
            overlap_val = get_symbols_overlap(data, symbol)
            if overlap_val != 0:
                conflict_symbol = data
                print("Conflicting Symbol:")
                print(vars(conflict_symbol))
                break
        if conflict_symbol == None:
            print("Appending To Data!")
            yml.data.append(symbol)
            return True
    
    # TODO: Handle conflict resolution between symbol and conflict_symbol!
    return False
