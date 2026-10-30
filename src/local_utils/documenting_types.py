from data_types import PMD2RegionalData
from io import TextIOWrapper, SEEK_END
import os

class YamlDoc:
    name: str
    address: PMD2RegionalData
    length: PMD2RegionalData
    description: str | list[str]
    
    def to_yaml(self, stream: TextIOWrapper, indent = 0):
        
        stream.write("\n")
        
        # Always goes name, then address, then length, THEN description
        indent_str = ""
        for i in range(indent):
            indent_str += " "
    
        stream.write("%s- name: %s\n" % (indent_str, self.name))
        indent_str += "  " # Two extra spaces to line up
        
        if getattr(self, "address"):
            stream.write("%saddress:\n" % indent_str)
            self.address.write_to_yaml(stream, indent + 4) # 2 after name, 2 indent from address block
        
        if getattr(self, "length"):
            stream.write("%slength:\n" % indent_str)
            self.length.write_to_yaml(stream, indent + 4) # 2 after name, 2 indent from address block
            
        if getattr(self, "description"):
            stream.write("%sdescription:" % indent_str)
        
            if type(self.description) == str:
                stream.write(' "%s"' % self.description)
            else:
                stream.write(" |-\n")
                indent_str += "  "
                for line in self.description:
                    stream.write("%s%s\n" % (indent_str, line))
        
        
    
root_project_dir = os.path.dirname(
    os.path.dirname( os.path.dirname(__file__) )
)
        
dat = YamlDoc()
dat.name = "TestSymbol"
dat.address = PMD2RegionalData(0x6300000, 0x4000000)
dat.length = PMD2RegionalData(0x4, 0x6)
dat.description = ["This description spans across multiple lines.", "", "Wow!"]

with open(os.path.join(root_project_dir, "out/test.yml"), "w") as out:
    dat.to_yaml(out)
        
        
        
    