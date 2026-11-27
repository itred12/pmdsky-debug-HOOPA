

import java.awt.BorderLayout;
import java.awt.Color;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.nio.file.Path;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HexFormat;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.SortedMap;
import java.util.TreeMap;

import javax.swing.BorderFactory;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.ScrollPaneConstants;
import javax.swing.SwingConstants;

import org.apache.commons.collections4.OrderedMap;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.util.Map.Entry;
import java.util.HashMap;

import docking.DialogComponentProvider;
import docking.DockingWindowListener;
import docking.DockingWindowManager;
import docking.widgets.combobox.GComboBox;
import docking.widgets.label.GHtmlLabel;
import docking.widgets.label.GLabel;
import docking.widgets.values.AbstractValue;
import docking.widgets.values.BooleanValue;
import docking.widgets.values.ChoiceValue;
import docking.widgets.values.FileValue;
import docking.widgets.values.StringValue;
import docking.widgets.values.ValuesMapParseException;
import ghidra.app.script.GhidraScript;
import ghidra.features.base.values.GhidraValuesMap;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.util.HTMLUtilities;
import ghidra.util.exception.CancelledException;
import ghidra.util.layout.PairLayout;

public class HoopaExporterUnbound extends GhidraScript {
   
    
//!------------------------------------------//
//!             DIALOG OBJECTS
//!------------------------------------------//

    /// Look upon my dialog, ye mighty, and despair.
    /// 
    /// Shows a dialog that allows me to present values the user has already entered, so they can confirm their inputs before the program goes through and exports everything
    /// 
    /// Partially frankensteined from ValuesMapDialog
    private class ConfirmationDialog extends DialogComponentProvider {

        private static final int MAX_MESSAGE_LINE_WIDTH = 60;

        private String header;
        private Map<String, String> shownValues;
        
        private JPanel valuesPanel;
        private boolean result = false;


        protected ConfirmationDialog(String title, String header, Map<String, String> values) {
            super(title, true, true, true, false);
            
            this.header = header;

            this.shownValues = values;
            this.valuesPanel = buildValuesPanel();

            for (Entry<String, String> entry : values.entrySet()) {
                buildComponentsForValue(entry.getKey(), entry.getValue());
            }

            addWorkPanel(buildWorkPanel());
            setRememberSize(false);
            setRememberLocation(false);
            
            addOKButton();
            addCancelButton();
        }


        @Override
        protected void okCallback() {
            this.result = true;
            close();
        }

        @Override
        protected void cancelCallback() {
            this.result = false;
            super.cancelCallback();
        }


        public boolean show() {
            DockingWindowManager.showDialog(this);
            return this.result;
        }

      
        private void buildComponentsForValue(String valueName, String value) {
            valuesPanel.add(new JLabel(valueName + ":", SwingConstants.RIGHT));
            JPanel subPanel = new JPanel(new BorderLayout());

            subPanel.setBackground(new Color(20, 20, 20, 50));
            subPanel.setBorder(BorderFactory.createLoweredBevelBorder());
            subPanel.add(new JLabel(value, SwingConstants.LEFT));
            valuesPanel.add(subPanel);
        }


        private JPanel buildValuesPanel() {
            JPanel panel = new JPanel(new PairLayout(4, 10));
            panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
            panel.getAccessibleContext().setAccessibleName("Values");
            return panel;
        }


        private JComponent buildWorkPanel() {
            JPanel panel = new JPanel(new BorderLayout());
            if (header != null) {
                String literalHTML = HTMLUtilities.toLiteralHTML(header, MAX_MESSAGE_LINE_WIDTH);
                GHtmlLabel label = new GHtmlLabel(literalHTML);
                label.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
                panel.add(label, BorderLayout.NORTH);
            }

            JScrollPane scroll = new JScrollPane(valuesPanel);
            scroll.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER);
            panel.add(scroll, BorderLayout.CENTER);
            panel.getAccessibleContext().setAccessibleName("Confirmation Map");
            return panel;
        }


        
    }


    /// A StringValue for use in dialogs that explicitly *doesn't* remember its last choice, meaning it respects whatever its set to by other code
    private class ForgettableStringValue extends StringValue {

        public ForgettableStringValue(String name) {
            super(name);
        }

        public ForgettableStringValue(String name, String defaultValue) {
            super(name, defaultValue);
        }

        @Override
        public void copyValue(AbstractValue<String> other) {
            
        }
        
    }

    /// A ChoiceValue for use in dialogs that explicitly *doesn't* remember its last choice, meaning it respects whatever its set to by other code
    private class ForgettableChoiceValue extends AbstractValue<String> {

        // Because SOMEBODY didn't make the ChoiceValue constructor public, this now has to be an ugly-as-hell carbon copy of ChoiceValue with the one change I want to make
        // fun.
            
        private String[] choices;
        private GComboBox<String> combo;

        ForgettableChoiceValue(String name, String defaultValue, String... choices) {
            super(name, defaultValue);
            this.choices = choices;
            if (defaultValue != null && !isValidChoice(defaultValue)) {
                throw new IllegalArgumentException("Default value is not one of the valid choices!");
            }
        }

        @Override
        public JComponent getComponent() {
            if (combo == null) {
                combo = new GComboBox<String>(choices);
            }
            return combo;
        }

        @Override
        protected void updateValueFromComponent() {
            setValue((String) combo.getSelectedItem());
        }

        @Override
        protected void updateComponentFromValue() {
            combo.setSelectedItem(getValue());
        }

        @Override
        protected String fromString(String valueString) {
            if (valueString == null) {
                return null;
            }
            if (isValidChoice(valueString)) {
                return valueString;
            }
            throw new IllegalArgumentException(valueString + " is not a valid choice!");
        }

        private boolean isValidChoice(String valueString) {
            for (String choice : choices) {
                if (choice.equals(valueString)) {
                    return true;
                }
            }
            return false;
        }

        @Override
        public void copyValue(AbstractValue<String> other) {
            // All of that for this ONE override
        }
        

    }


 
//!------------------------------------------//
//!          SYMBOL-PARSING OBJECTS
//!------------------------------------------//



    /// It's a uhhh regional dialect
    private enum Region {
        EU("EU"),
        NA("NA"),
        JP("JP");
        
        public final String nameString;

        private Region(String name) {
            this.nameString = name;
        }
    }


    /// A record that holds a piece of data for each region (release) of the game
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


    /// Contains each overlay, and data that can be used to guess the overlay a memory block is tied to
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


        public static Optional<Overlay> fromString(String name) {
            for (Overlay overlay : Overlay.values()) {
                if (overlay.name == name) return Optional.of(overlay);
            }
            return Optional.empty();
        }

    }

    
    public class DefinedAddress {
        public String label;
        public List<String> description;
        public long address;
       

        public DefinedAddress(String label, long address, List<String> description) {
            this.label = label;
            this.address = address;
            this.description = description;
        }

    }


    public class DataDefinition extends DefinedAddress {
        
        public String dataType;
        public int length;

        public DataDefinition(String label, long address, int length, List<String> description, String dataType) {
            super(label, address, description);
            this.dataType = dataType;
            this.length = length;
        }
    }


    public class FunctionDefinition extends DefinedAddress {
        
        public String returnType;
        public LinkedHashMap<String, String> arguments; // Want them to be ordered

        public FunctionDefinition(String label, long address, String returnTypeName, LinkedHashMap<String, String> argumentNames, List<String> description) {
            super(label, address, description);
            this.returnType = returnTypeName;
            this.arguments = argumentNames;
        }
        
    }


    public class BlockSymbols {
        
        public ArrayList<FunctionDefinition> functions;
        public ArrayList<DataDefinition> data;
        
        public BlockSymbols() {
            this.functions = new ArrayList<>();
            this.data = new ArrayList<>();
        }

        public void addFunction(FunctionDefinition function) {
            this.functions.add(function);
        }

        public void addData(DataDefinition data) {
            this.data.add(data);
        }

    }

    
    // So Gson can take the region too
    public class ExportedData {
        public String region;
        public LinkedHashMap<String, BlockSymbols> symbols;

        public ExportedData(String region, LinkedHashMap<String, BlockSymbols> allData) {
            this.region = region;
            this.symbols = allData;
        }
    }
        

     
//!------------------------------------------//
//!             SCRIPT METHODS
//!------------------------------------------//


    /// The name of the non-exporting option for a memory block
    private final String DO_NOT_EXPORT_NAME = "[Do Not Export]";
    /// The default name of an exported file. %s is replaced with the date-time format `MM-DD-YY_H-MM-SS<AM/PM>`, but may differ depending on the system's locale (DD-MM-YY, may use 24-hr time, etc.)
    private final String BASE_EXPORT_FILE = "EXPORT_%s";
    /// File extension
    private final String OUTPUT_FILE_EXTENSION = ".hoopaexport.json";

    /**
     * Gets a string array of all of the choices allowed when the program lets the user select an overlay. 
     * @return A string array containing the yaml file-name of each overlay, in order, with the starting two elements being a blank string "" and "[Do Not Export]"
     */
    public String[] getAllOverlayOptions() {
        ArrayList<String> names = new ArrayList<>();
        names.add("");
        names.add(this.DO_NOT_EXPORT_NAME);

        for (Overlay overlay : Overlay.values()) {
            names.add(overlay.name);
        }
        
        
        String[] namesArray = new String[names.size()];
        return names.toArray(namesArray);
    }


    /**
     * Prints an error message with a prefix
     * @param Message
     */
    void printErrorMessage(String Message) {
        println("HoopaExporterUNBOUND - Error: " + Message);
    }


     /**
     * Prints an inof message with a prefix
     * @param Message
     */
    void printInfoMessage(String Message) {
        println("HoopaExporterUNBOUND - Info: " + Message);
    }



    /**
     * Takes an input number and formats it as a string in its hex representation, in the format used by the pmdsky-debug repository (all letters capitalized, leading zeroes removed)
     * @param num The given number
     * @return The number's hex representation as a string, in the same hex format used by the pmdsky-debug repository.
     */
    String toHexString(long num) {
        String baseString = HexFormat.of().toHexDigits(num).toUpperCase();
        while (baseString.startsWith("0")) {
            baseString = baseString.replaceFirst("0", "");
        }
        return "0x" + baseString;
    }

    /**
     * Equivalent to toHexString, but accepts a memory address for convenience
     * @param address The given address
     * @return the offset of the address, as a string, in the same hex format used by the pmdsky-debug repository.
     */
    String toHexString(Address address) {
        return toHexString(address.getOffset());
    }
    

    /// The game region of the binary
    private Region gameRegion;
    /// The path for the output file
    private String outputFilePath;
    /// When asking which memory blocks to export, controls whether the program will use the size and offset of each memory block to attempt to automatically guess which overlay it belongs to.
    private boolean autoDetect;
    /// When asking which memory blocks to export, controls whether the program will leave any overlays it can't guess (or all of them, if autoDetect is false) as [Do Not Export] or as just plain nothing before first being set.
    private boolean doNotExportByDefault;
    private LinkedHashMap<Overlay, List<MemoryBlock>> targetBlocks = new LinkedHashMap<>();

 
//!------------------------------------------//
//!             SCRIPT PROPER
//!------------------------------------------//



    @Override
    protected void run() throws Exception {

        getHoopaExporterOptions();
        getSelectedMemoryBlocksAndOverlays();
        confirmSelectedOptionsAndOverlays();

        // This is where the fun begins
        gatherSymbolsFromBlocks();
    }

    //!-----------------//
    //!  CONFIGURATION
    //!-----------------//

    /**
     * Gets the initial options, like the game region, output file location, and other settings.
     * @throws CancelledException
     * @throws ValuesMapParseException 
     */
    void getHoopaExporterOptions() throws CancelledException, ValuesMapParseException {

        GhidraValuesMap askPrompt = new GhidraValuesMap();
        ChoiceValue inputGameRegion = askPrompt.defineChoice(
            "Game Region", 
            "EU", 
            "EU", "NA", "JP"
        );
        
        
        FileValue outputDir = askPrompt.defineDirectory("Export directory", new File(""));

        Date currentTime = new Date();
        String dateString = DateFormat.getDateInstance(DateFormat.DATE_FIELD)
            .format(currentTime)
            .replace("/", "-");

        String timeString = DateFormat.getTimeInstance(DateFormat.DEFAULT)
            .format(currentTime)
            .replace(":", "-")
            .replace(" ", ""); // I don't know what's up with this weird space in the time format on my system?? So I'll just account for it?? I guess??
         

        ForgettableStringValue outputFile = new ForgettableStringValue("Exported file name (as " + OUTPUT_FILE_EXTENSION + ")", String.format(BASE_EXPORT_FILE, dateString + "_" + timeString));
        askPrompt.addValue(outputFile);

        BooleanValue inputAutoDetect = askPrompt.defineBoolean("Auto-detect overlays from memory block addresses/lengths?", false);
        BooleanValue inputDoNotExportByDefault = askPrompt.defineBoolean("Use [Do Not Export] by default?", false);
        
        GhidraValuesMap userInputtedValues = askValues("HoopaExporter Configuration:", "Initial Configuration:", askPrompt);
        
        this.gameRegion = Region.valueOf(inputGameRegion.getValue());
        this.autoDetect = inputAutoDetect.getValue();
        this.doNotExportByDefault = inputDoNotExportByDefault.getValue();
        this.outputFilePath = Path.of(outputDir.getValue().getAbsolutePath(), outputFile.getValue() + OUTPUT_FILE_EXTENSION).toString();
    }



    /**
     * Iterates over the opened program blocks and presents a dialog allowing the user to choose which ones they want to export, by tying them to the name of an overlay file in pmdsky-debug.
     * @throws CancelledException
     */
    void getSelectedMemoryBlocksAndOverlays() throws CancelledException {

        Map<MemoryBlock, ForgettableChoiceValue> overlaysToExport = new HashMap<>();

        GhidraValuesMap confirmPrompt = new GhidraValuesMap();
        

        int index = 0;
        for (MemoryBlock block : getMemoryBlocks()) {

            
            AddressRange blockRange = block.getAddressRange();
            Optional<Overlay> blockOverlay = Overlay.findOverlayFromMemBlock(this.gameRegion, block);

            String choiceName = String.format(
                "Memory block %d - \"%s\" (Address %s - %s, length %s)", 
                index, block.getName(), toHexString(blockRange.getMinAddress()), toHexString(blockRange.getMaxAddress()), toHexString(block.getSize())
            );

            String blockDefault;
            if (!this.autoDetect || blockOverlay.isEmpty()) {
                blockDefault = (this.doNotExportByDefault ? DO_NOT_EXPORT_NAME : "");
            } else {
                blockDefault = blockOverlay.get().name;
            }


            ForgettableChoiceValue overlayChoicer = new ForgettableChoiceValue(choiceName, blockDefault, getAllOverlayOptions());
            confirmPrompt.addValue(overlayChoicer);
            

            overlaysToExport.put(
                block, 
                overlayChoicer
            );
            index++;
        }
        
        askValues("Confirm Blocks", "Please select which of the following memory blocks to export, and which overlay they corrospond to. Set a block to \"" + DO_NOT_EXPORT_NAME + "\" to exclude it from the export.", confirmPrompt);

        for (Entry<MemoryBlock, ForgettableChoiceValue> selectedEntry : overlaysToExport.entrySet()) {
            
            MemoryBlock givenBlock = selectedEntry.getKey();
            ForgettableChoiceValue givenChoice = selectedEntry.getValue();

            if (givenChoice.getValue().equals(DO_NOT_EXPORT_NAME) || givenChoice.getValue().isEmpty()) continue;

            Overlay overlay = Overlay.fromString(givenChoice.getValue()).get(); 

            if (!targetBlocks.containsKey(overlay)) {
                targetBlocks.put(overlay, new ArrayList<MemoryBlock>());
            };
            targetBlocks.get(overlay).add(givenBlock);

        }


    }


    /**
     * After the settings and overlays are gathered, confirm the given settings with a custom window (this took me WAAAAY too long to do :sob:)
     * @throws CancelledException
     */
    void confirmSelectedOptionsAndOverlays() throws CancelledException {

        String exportedBlocks = "";
        for (Entry<Overlay, List<MemoryBlock>> entry : this.targetBlocks.entrySet()) {
            Overlay overlay = entry.getKey();
            List<MemoryBlock> blocks = entry.getValue();

            for (MemoryBlock block : blocks) {
                exportedBlocks += "%s (as %s)\n, ".formatted(block.getName(), overlay.name);
            }

        }
        // In case nothing was exported??
        if (exportedBlocks.length() > 3) {
            exportedBlocks = exportedBlocks.substring(0, exportedBlocks.length() - 3); // Remove trailing comma and space
        }
        

        LinkedHashMap<String, String> confirmedOptions = new LinkedHashMap<>();

        confirmedOptions.put("Game region", this.gameRegion.nameString);
        confirmedOptions.put("Output file location", this.outputFilePath);
        confirmedOptions.put("Exported memory blocks", exportedBlocks);

        ConfirmationDialog dialog = new ConfirmationDialog("Confirm settings", "Does this seem correct?", confirmedOptions);
        if (!dialog.show()) {
            throw new CancelledException();
        }
    }


    //!-----------------//
    //!  EXPORTING
    //!-----------------//
    

    void gatherSymbolsFromBlocks() throws IOException {

        LinkedHashMap<String, BlockSymbols> allData = new LinkedHashMap<>();
        int symbolCount = 0;
        int blockCount = 0;

        for (Entry<Overlay, List<MemoryBlock>> entry : this.targetBlocks.entrySet()) {
            
            Overlay overlay = entry.getKey();
            List<MemoryBlock> givenBlocks = entry.getValue();

            printInfoMessage("Gathering symbols for overlay \"%s\"...".formatted(overlay.name));

            BlockSymbols blockSymbolsHolder = new BlockSymbols();

            for (MemoryBlock block : givenBlocks) {
                blockCount++;
                
                printInfoMessage("Finding symbols in MemoryBlock \"%s\"...".formatted(block.getName()));

                Iterator<Address> addressIterator = block.getAddressRange().iterator();

                while (addressIterator.hasNext()) {
                    Address address = addressIterator.next();

                    Data data = getDataAt(address);
                    Symbol symbol = getSymbolAt(address);

                    // Data symbol
                    if (symbol != null && data != null) {

                        
                        // SourceType.ANALYSIS can sometimes include symbols named automatically (i.e., veneers are named the same as their wrapped function by default)
                        // so we filter only for USER_DEFINED and IMPORTED symbols, since I *think* that's the only ones we care about
                        SourceType source = symbol.getSource();
                        if (source != SourceType.USER_DEFINED && source != SourceType.IMPORTED ) continue; 

                        ArrayList<String> plateCommentContents = new ArrayList<>();

                        String plateComment = getPlateComment(address);
                        if (plateComment != null) {
                            for (String line : plateComment.split("\n")) {
                                plateCommentContents.add(line);
                            }
                        }

                        

                        blockSymbolsHolder.addData(
                            new DataDefinition(
                                symbol.getName(), 
                                address.getOffset(), 
                                address.getSize(), 
                                plateCommentContents, 
                                data.getDataType().getName()
                            )
                        );
                        symbolCount++;

                        continue;
                    }


                    Function function = getFunctionAt(address);

                    // Function symbol
                    if (function != null) {

                        SourceType source = function.getSignatureSource();
                        if (source != SourceType.USER_DEFINED && source != SourceType.IMPORTED ) continue;


                        LinkedHashMap<String, String> argumentMap = new LinkedHashMap<>();
                        if (function.getParameters() != null) {
                            for (Parameter param : function.getParameters()) {
                                argumentMap.put(param.getName(), param.getDataType().getName());
                            }
                        }


                        ArrayList<String> plateCommentContents = new ArrayList<>();
                        String plateComment = getPlateComment(address);
                        if (plateComment != null) {
                            for (String line : plateComment.split("\n")) {
                                plateCommentContents.add(line);
                            }
                        }


                        blockSymbolsHolder.addFunction(
                            new FunctionDefinition(
                                function.getName(), 
                                address.getOffset(), 
                                function.getReturn().getDataType().getName(), // As per my comment in the last version of the exporter: "I know it seems kinda cursed, but nothing in this call chain is marked as nullable, so im just gonna take its word for it!""
                                argumentMap, 
                                plateCommentContents
                            )
                        );
                        symbolCount++;

                    }

                }


            }

            allData.put(overlay.name, blockSymbolsHolder);
        }

        Gson gson = new GsonBuilder()
            .setPrettyPrinting()
            .create();


        Writer writer = new FileWriter(this.outputFilePath);
        gson.toJson(new ExportedData(this.gameRegion.nameString, allData), writer);
        writer.close();

        printInfoMessage("Done! Exported %s symbols over %s blocks.".formatted(symbolCount, blockCount));

    }
    
}
