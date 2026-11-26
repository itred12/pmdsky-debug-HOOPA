

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import ghidra.app.script.GhidraScript;
import ghidra.features.base.values.GhidraValuesMap;
import ghidra.program.model.mem.MemoryBlock;

public class HoopaExporterUnbound extends GhidraScript {


    private enum Region {
        EU("EU"),
        NA("NA"),
        JP("JP");
        
        public final String nameString;

        private Region(String name) {
            this.nameString = name;
        }
    }

    private record RegionalData(int EU, int NA, int JP) {

        public int getDataOfRegion(Region region) {
            // I didnt feel like figuring out Reflection syntax all over again so this was my next best idea lol
            switch (region) {
                case EU:
                    return this.EU;
                case NA:
                    return this.NA;
                default:
                    return this.JP;
            }
        }

    }


    
    private enum Overlay {

        ARM9("arm9", new RegionalData(0x2000000, 0x2000000, 0x2000000), new RegionalData(0xB7D38, 0xB73F8, 0xB8CB8)),
        ARM7("arm7", new RegionalData(0x2380000, 0x2380000, 0x2380000), new RegionalData(0x27080, 0x27080, 0x27080)),
        OVERLAY0("overlay0", new RegionalData(0x22BD3C0, 0x22BCA80, 0x22BE220), new RegionalData(0x60880, 0x609A0, 0x609A0)),
        OVERLAY1("overlay1", new RegionalData(0x2329D40, 0x2329520, 0x232ACC0), new RegionalData(0x12C80, 0x12D20, 0x12E00)),
        OVERLAY2("overlay2", new RegionalData(0x2329D40, 0x2329520, 0x232ACC0), new RegionalData(0x2AFC0, 0x2AFA0, 0x2AFA0)),
        OVERLAY3("overlay3", new RegionalData(0x233D200, 0x233CA80, 0x233E300), new RegionalData(0xA160, 0xA160, 0xA160)),
        OVERLAY4("overlay4", new RegionalData(0x233D200, 0x233CA80, 0x233E300), new RegionalData(0x2BE0, 0x2BE0, 0x2BE0)),
        OVERLAY5("overlay5", new RegionalData(0x233D200, 0x233CA80, 0x233E300), new RegionalData(0x3240, 0x3240, 0x3260)),
        OVERLAY6("overlay6", new RegionalData(0x233D200, 0x233CA80, 0x233E300), new RegionalData(0x2460, 0x2460, 0x2460)),
        OVERLAY7("overlay7", new RegionalData(0x233D200, 0x233CA80, 0x233E300), new RegionalData(0x3300, 0x5100, 0x53E0)),
        OVERLAY8("overlay8", new RegionalData(0x233D200, 0x233CA80, 0x233E300), new RegionalData(0x2620, 0x2200, 0x2200)),
        OVERLAY9("overlay9", new RegionalData(0x233D200, 0x233CA80, 0x233E300), new RegionalData(0x2D80, 0x2D80, 0x2D20)),
        OVERLAY10("overlay10", new RegionalData(0x22BD3C0, 0x22BCA80, 0x22BE220), new RegionalData(0x1F7A0, 0x1F7A0, 0x1F6A0)),
        OVERLAY11("overlay11", new RegionalData(0x22DCB80, 0x22DC240, 0x22DD8E0), new RegionalData(0x48E40, 0x48C40, 0x48B00)),
        OVERLAY12("overlay12", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x20, 0x20, 0x20)),
        OVERLAY13("overlay13", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x2E80, 0x2E80, 0x2E80)),
        OVERLAY14("overlay14", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x3B40, 0x3AE0, 0x3AE0)),
        OVERLAY15("overlay15", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x1080, 0x1060, 0x1060)),
        OVERLAY16("overlay16", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x2D20, 0x2D20, 0x2D40)),
        OVERLAY17("overlay17", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x1CE0, 0x1CE0, 0x1CE0)),
        OVERLAY18("overlay18", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x3500, 0x3500, 0x3520)),
        OVERLAY19("overlay19", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x4220, 0x4240, 0x4220)),
        OVERLAY20("overlay20", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x3000, 0x3000, 0x3000)),
        OVERLAY21("overlay21", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x2E20, 0x2E20, 0x2E40)),
        OVERLAY22("overlay22", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x4B40, 0x4B40, 0x4B40)),
        OVERLAY23("overlay23", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x3780, 0x3780, 0x37E0)),
        OVERLAY24("overlay24", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x24E0, 0x24E0, 0x24E0)),
        OVERLAY25("overlay25", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x14C0, 0x14C0, 0x14C0)),
        OVERLAY26("overlay26", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0xE40, 0xE40, 0xE40)),
        OVERLAY27("overlay27", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0x2D60, 0x2D60, 0x2DA0)),
        OVERLAY28("overlay28", new RegionalData(0x238AC80, 0x238A140, 0x238B6A0), new RegionalData(0xC60, 0xC60, 0xC60)),
        OVERLAY29("overlay29", new RegionalData(0x22DCB80, 0x22DC240, 0x22DD8E0), new RegionalData(0x77900, 0x77620, 0x77200)),
        OVERLAY30("overlay30", new RegionalData(0x2383420, 0x2382820, 0x2383AA0), new RegionalData(0x38A0, 0x38A0, 0x3880)),
        OVERLAY31("overlay31", new RegionalData(0x2383420, 0x2382820, 0x2383AA0), new RegionalData(0x7AA0, 0x7A80, 0x7AC0)),
        OVERLAY32("overlay32", new RegionalData(0x2383420, 0x2382820, 0x2383AA0), new RegionalData(0x20, 0x20, 0x20)),
        OVERLAY33("overlay33", new RegionalData(0x2383420, 0x2382820, 0x2383AA0), new RegionalData(0x20, 0x20, 0x20)),
        OVERLAY34("overlay34", new RegionalData(0x22DCB80, 0x22DC240, 0x22DD8E0), new RegionalData(0xDC0, 0xE60, 0xDC0)),
        OVERLAY35("overlay35", new RegionalData(0x22BD3C0, 0x22BCA80, 0x22BE220), new RegionalData(0x20, 0x20, 0x20)),
        RAM("ram", new RegionalData(0x2000000, 0x2000000, 0x2000000), new RegionalData(0x400000, 0x400000, 0x400000));

        public final String name;
        public final RegionalData startAddress; // Corrosponds to start address we expect to see open in Ghidra
        public final RegionalData length; // Corrosponds to length we expect to see open in Ghidra
        
        private Overlay(String name, RegionalData startAddress, RegionalData length) {
            this.name = name;
            this.startAddress = startAddress;
            this.length = length;
        }


        public static Optional<Overlay> findOverlayFromMemBlock(Region region, MemoryBlock block) {

            for (Overlay overlay : Overlay.values()) {

                if (
                    overlay.startAddress.getDataOfRegion(region) == block.getAddressRange().getMinAddress().getOffset() 
                    && overlay.length.getDataOfRegion(region) == block.getSize()
                ) {
                    return Optional.of(overlay);
                }

            }

            return Optional.empty();
        }


        public static String[] getAllOverlayNames() {
            ArrayList<String> names = new ArrayList<>();
            for (Overlay overlay : Overlay.values()) {
                names.add(overlay.name);
            }
            names.add("");
            
            String[] namesArray = new String[names.size()];
            return names.toArray(namesArray);

        }

    }


    void printErrorMessage(String Message) {
        println("HoopaExporterUNBOUND - Error: " + Message);
    }


    private Region selectedRegion;


    @Override
    protected void run() throws Exception {

        GhidraValuesMap askPrompt = new GhidraValuesMap();
        askPrompt.defineChoice(
            "Game Region", 
            "EU", 
            "EU", "NA", "JP"
        );

        GhidraValuesMap userInputtedValues = askValues("HoopaExporter Configuration:", "test", askPrompt);
        

        this.selectedRegion = Region.valueOf(userInputtedValues.getChoice("Game Region"));
         

        GhidraValuesMap confirmPrompt = new GhidraValuesMap();
        


       

        int index = 0;
        for (MemoryBlock block : getMemoryBlocks()) {

            println(block.getName());
            println(block.getAddressRange().getMinAddress().toString());
            println(String.valueOf(block.getSize()));

            Optional<Overlay> blockOverlay = Overlay.findOverlayFromMemBlock(this.selectedRegion, block);
            
            confirmPrompt.defineChoice(
                "Memory block " + index, 
                blockOverlay.isPresent() ? blockOverlay.get().name : "",
                Overlay.getAllOverlayNames()
            );
            index++;
        }

        askValues("Confirm", "aa", confirmPrompt);



    }
    
}
