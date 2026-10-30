from config import CONFIG_INSTANCE
from os import path, mkdir, scandir
from utils import HoopaUtils
import yaml
from yaml.parser import Parser
from local_types.types import PMD2OverlayData
import json



class Interpreter:
    
    pmdsky_debug_directory: str
    headers_folder: str
    symbols_folder: str
    out_folder: str
    cache_folder: str
    
    symbol_tree: dict[str, PMD2OverlayData]
    
    def __init__(self) -> None:
        
        this_directory = path.dirname(path.dirname(__file__))
        HoopaUtils.print_info("Getting interpreter set up, making sure folders can be found...")
        
        self.out_folder = path.join(this_directory, "out")
        if not path.isdir(self.out_folder):
            
            HoopaUtils.print_debug("Remaking output directory at [%s]..." % path.abspath(self.out_folder))
            # I can just remake this one
            mkdir(self.out_folder)
            
        else:
            HoopaUtils.print_debug("Found output directory at [%s]..." % path.abspath(self.out_folder))
            
        self.cache_folder = path.join(this_directory, "cache")
        if not path.isdir(self.cache_folder):
            
            HoopaUtils.print_debug("Remaking cache directory at [%s]..." % path.abspath(self.cache_folder))
            # This too
            mkdir(self.cache_folder)
            
        else:
            HoopaUtils.print_debug("Found cache directory at [%s]..." % path.abspath(self.cache_folder))
        
        self.pmdsky_debug_directory = path.relpath(CONFIG_INSTANCE.repository_path.value, this_directory)
        if not path.isdir(self.pmdsky_debug_directory):
            HoopaUtils.print_error("Path to pmdsky_debug (or a clone of it) was invalid! Check your config.toml!")
            exit(1)
        HoopaUtils.print_debug("Found pmdsky_debug folder at [%s]..." % path.abspath(self.pmdsky_debug_directory))    
        
        self.headers_folder = path.join(self.pmdsky_debug_directory, "headers")
        if not path.isdir(self.headers_folder):
            HoopaUtils.print_error("Somehow could not find headers folder within your pmdsky_debug folder! Huh????")
            exit(1)
        HoopaUtils.print_debug("Found headers folder at [%s]..." % self.headers_folder)
            
        self.symbols_folder = path.join(self.pmdsky_debug_directory, "symbols")
        if not path.isdir(self.symbols_folder):
            HoopaUtils.print_error("Somehow could not find symbols folder within your pmdsky_debug folder! Bwuh?????")
            exit(1)
        HoopaUtils.print_debug("Found symbols folder at [%s]..." % self.symbols_folder)
        self._build_symbol_tree()    
    
    
    def _build_symbol_tree(self): 
        
        self.symbol_tree = {}
        
        for symbol_file in scandir(self.symbols_folder):
            
            if symbol_file.is_file() and symbol_file.name.endswith(".yml"):
                self.symbol_tree[symbol_file.name] = self.get_symbol_data(symbol_file.path)
                
            elif symbol_file.is_dir():
                for subfile in scandir(symbol_file.path):
                     if symbol_file.is_file() and symbol_file.name.endswith(".yml"):
                        self.symbol_tree[symbol_file.name] = self.get_symbol_data(symbol_file.path)
            
        ranges_NA = {}
        ranges_EU = {}
        ranges_JP = {}            
        for name, symbol in self.symbol_tree.items():
            ranges = symbol.range.get_json()
            if not ranges: continue
            if "NA" in ranges:
                ranges_NA[name] = ranges["NA"]
            if "EU" in ranges:
                ranges_EU[name] = ranges["EU"]
            if "JP" in ranges:
                ranges_JP[name] = ranges["JP"]
           
        out_na = path.join(self.out_folder, "ranges_NA.json")
        out_eu = path.join(self.out_folder, "ranges_EU.json")
        out_jp = path.join(self.out_folder, "ranges_JP.json")
        
        
        with open(out_na, "w") as na:
            json.dump(ranges_NA, na, indent=4)
        with open(out_eu, "w") as eu:
            json.dump(ranges_EU, eu, indent=4)
        with open(out_jp, "w") as jp:
            json.dump(ranges_JP, jp, indent=4)
            
            
    def get_symbol_data(self, file_path: str) -> PMD2OverlayData:
        with open(file_path, "r") as contents:
                            
            symbol_info = ""
            for line in contents:
                if line.strip().startswith("functions"): break
                symbol_info += line 
            print(file_path)
            return PMD2OverlayData.from_yaml(symbol_info)
           
            
            
    
            
Interpreter()