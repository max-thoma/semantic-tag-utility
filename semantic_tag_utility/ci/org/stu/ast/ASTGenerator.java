package org.stu.ast;

import org.omg.sysml.interactive.SysMLInteractive;
import org.omg.sysml.interactive.SysMLInteractiveResult;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;

public class ASTGenerator {
    /***
     * @info       Inspired by and based on an example given by Ed Seidewitz (https://github.com/seidewitz) in the
     *             "SysML v2 Release" Google Group: (https://groups.google.com/g/sysml-v2-release/c/XOhdgqLTyBI/m/l3bIbLKMAgAJ)
     * @param args 0: Standard Lib
     *             1: Tagging Lib
     *             2: Model Path
     *             3: Model Package Name
     *             4: AST Path
     */
    public static void main(String[] args) {
        SysMLInteractive sysml = SysMLInteractive.getInstance();
        sysml.setVerbose(false);

        // Standard Libraries
        sysml.loadLibrary(args[0]);

        // Semantic Tag Libraries
        try {
            sysml.process(Files.readString(Path.of(args[1])));
        } catch (IOException e) {
            System.err.println("IOException: " + e.getMessage());
            System.exit(1);
        }

        try {
            SysMLInteractiveResult result = sysml.process(Files.readString(Path.of(args[2])));
            System.out.println(result.toString());

            if (!result.hasErrors()) {
                var exportAST = (sysml.export(args[3], Collections.emptyList()));

                try {
                    Path path = Paths.get(args[4]);
                    BufferedWriter writer = Files.newBufferedWriter(path);
                    writer.write(exportAST.toString());
                    writer.close();

                } catch (IOException e) {
                    System.err.println("An error occurred while writing to the file: " + e.getMessage());
                    System.exit(1);
                }

            } else {
                System.err.println("An error has occurred while parsing the model");
                System.exit(1);
            }

        } catch (IOException e) {
            System.err.println("IOException: " + e.getMessage());
            System.exit(1);
        }
    }
}
