package uk.ac.diamond.optid.util;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Util {
	
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(Util.class);
	
	public static int exit_value = -1;
	// Lookup generator has own exit value
	// As file generation occurs in a separate thread, the other two files
	// could be generated simultaneously
	public static int lookup_exit_value = -1;
	
	// Enum representing different script (file generation) options
	public enum ScriptOpt {
		ID_DESC,
		MAG_STR,
		LOOKUP_GEN,
		CLUSTER
	}
	
	public static void main(String[] args) {
		String[] test_arguments = new String[] {"109", "41", "16", "6.22", "41", "16",
				"3.12", "41", "16", "4.0", "0.03", "6.15", "PPM_AntiSymmetric", "J13",
				"-5.0", "5.1", "2.5", "-0.0", ".1", "0.1", "5"};
		String test_filename =  "J13";
		
		String[] test_arguments_sym = new String[] {"91", "33.", "33.", "13.95", "33.", "33.", "6.95", "33.", "33.", "6.95",
				"0.05", "20.0", "APPLE_Symmetric",
				"I21", "-5.0", "5.1", "2.5", "-5.0", "5.1", "5.0", "5",
				"5.0", "0.5", "6.0"};
		String test_filename_sym =  "I21";
		
		// Directory where output files will be generated
		String test_dir = "/home/xrp26957/Downloads";
		
		// run_id_setup.sh Argument Type: PPM_AntiSymmetric 
		testIdDesc(test_arguments, test_dir, test_filename);
		
		System.out.println();
		
		// run_id_setup.sh Argument Type: APPLE_Symmetric
		testIdDesc(test_arguments_sym, test_dir, test_filename_sym);
	}
	
	private static void testIdDesc(String[] arguments, String workingDir, String fileName) {
		String testType;
		if (arguments.length == 21) {
			testType = "PPM_AntiSymmetric";
		} else if (arguments.length == 24) {
			testType = "APPLE_SYMMETRIC";
		} else {
			System.out.println("Test has invalid number of arguments");
			return;
		}
		
		System.out.println("Running \"run_id_setup.sh\" script with valid '" + testType + "' arguments:");
		String errorOutput = run(ScriptOpt.ID_DESC, arguments, workingDir, fileName);
		if (exit_value == 0) {
			System.out.println("File generated successfully");
		} else {
			System.out.println("Error generating file:");
			System.out.println(errorOutput);
		}
	}
	
	/**
	 * Runs specified script
	 * @param option
	 * @param arguments
	 * @param workingDir
	 * @param fileName
	 * @return
	 */
	public static String run(ScriptOpt option, String[] arguments, String workingDir, String fileName) {
		String script_dir = getAbsoluteScriptDirPath();
		
		String bashScript = null;
		String pythonScript = null;
		String outFileExt = null;
		switch (option) {
			case ID_DESC:
				bashScript = "run_id_setup.sh";
				pythonScript = "python/id_setup.py";
				outFileExt = ".json";
				break;
			case MAG_STR:
				bashScript = "run_magnets.sh";
				pythonScript = "python/magnets.py";
				outFileExt = ".mag";
				break;
			case LOOKUP_GEN:
				bashScript = "run_lookup_generator.sh";
				pythonScript = "python/lookup_generator.py";
				outFileExt = ".h5";
				break;	
			case CLUSTER:
				bashScript = "cluster_mpi.sh";
				pythonScript = "python/mpi_runner.py";
				outFileExt = "";
				break;	
		}
				
		String scriptPath = createFilePath(script_dir, bashScript);
		String pythonPath = createFilePath(script_dir, pythonScript);
		String outputFilePath = createFilePath(workingDir, fileName + outFileExt);
		
		ArrayList<String> processArray = new ArrayList<String>(Arrays.asList(arguments));
		processArray.add(0, scriptPath);
		processArray.add(1, pythonPath);
		if (option == ScriptOpt.CLUSTER) {
			String sndBashScript = createFilePath(script_dir, "mpi_job.sh");
			processArray.add(1, sndBashScript);
		}
		processArray.add(outputFilePath);
		
		String output = execute(processArray);
	
		if (option == ScriptOpt.LOOKUP_GEN) {
			lookup_exit_value = exit_value;
			exit_value = -1;
		}
		
		return output;
	}
	
	/**
	 * Runs list_genomes.py script with argument dir, 
	 * directory which genomes will be displayed from
	 * @param dir
	 * @return String
	 */
	public static ArrayList<String> runListGenomes(String dir) {
		// Get absolute path of file_list.py script
		String script_dir = getAbsoluteScriptDirPath();
		String pythonScript = "python/list_genomes.py";
		String pythonPath = createFilePath(script_dir, pythonScript);

		// Create process
		ArrayList<String> processArray = new ArrayList<>();
		processArray.add("python");
		processArray.add(pythonPath);
		processArray.add(dir); // Directory to display genomes from
		
		String output = execute(processArray);
		
		// No genomes in directory, return empty list
		if (output.length() <= 7) {
			return new ArrayList<String>();
		}
		
		// Separate each line as an element in a list and sort
		String lines[] = output.split("\\n");
		ArrayList<String> genomes = new ArrayList<>(Arrays.asList(lines));
		Collections.sort(genomes);
		
		return genomes;
	}
	
	/**
	 * Runs the created process
	 * @param processArray
	 * @return
	 */
	private static String execute(ArrayList<String> processArray) {
		ProcessBuilder processBuilder = new ProcessBuilder(processArray);
		processBuilder.redirectErrorStream(true);
		
		Process process;
		try {
			process = processBuilder.start();
		} catch (IOException ioe) {
			System.out.println(ioe);
			process = null;
		}
				
		String result = "";
		if (process != null) {
			BufferedReader brOut = new BufferedReader(new InputStreamReader(
					process.getInputStream()));
			String line = null;
			try {
				while ((line = brOut.readLine()) != null) {
					result += line + "\n";
				}
				result = StringUtils.chomp(result); // Remove extra newline
				brOut.close();
			} catch (IOException ioe) {
				System.out.println(ioe);
			}
		}
		
		try {
			exit_value = process.waitFor();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		
		return result;
	}
	
	/**
	 * Gets the absolute path of the script 
	 * @return String
	 */
	private static String getAbsoluteScriptDirPath() {
		java.security.ProtectionDomain pd = Util.class.getProtectionDomain();
		if (pd == null) {
			System.out.print("No path found returning null");
			return null;
		}
		java.security.CodeSource cs = pd.getCodeSource();
		if (cs == null) {
			System.out.print("No path found returning null");
			return null;
		}
		java.net.URL url = cs.getLocation();
		if (url == null) {
			System.out.print("No path found returning null");
			return null;
		}
		java.io.File f = new File(url.getFile());
		String resultTest = f.getAbsolutePath();

		if (resultTest == null) {
			System.out.print("No path found returning null");
			return null;
		}

		if (isValidDirectory(resultTest + "/scripts")) {
			return resultTest + "/scripts/";
		} else {
			File file = new File(resultTest);
			return file.getParent() + "/scripts/";
		}

	}
	
	/**
	 * Determines whether given path is a valid directory
	 * @param path
	 * @return true if path is a valid directory
	 */
	public static boolean isValidDirectory(String path) {
		return path.length() > 0
				& path.charAt(0) == '/'
				& Files.isDirectory(Paths.get(path));
	}
	
	/**
	 * Determines whether given path is a valid file with given extension
	 * @param path
	 * @return true if path is a valid file
	 */
	public static boolean isValidFile(String path, String ext) {
		return path.length() > 0 
				& Files.isReadable(Paths.get(path))
				& FilenameUtils.isExtension(path, ext);
	}
	
	/**
	 * Combines directory and file name into single path
	 * @param dir
	 * @param fileName
	 * @return String
	 */
	public static String createFilePath(String dir, String fileName) {
		return FilenameUtils.concat(dir, fileName);
	}

}
