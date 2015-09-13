package uk.ac.diamond.optid;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.StringUtils;

public class Util {
	
	public static int exit_value = -1;
	
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
		test(test_arguments, test_dir, test_filename);
		
		System.out.println();
		
		// run_id_setup.sh Argument Type: APPLE_Symmetric
		test(test_arguments_sym, test_dir, test_filename_sym);
	}
	
	private static void test(String[] arguments, String workingDir, String fileName) {
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
		String errorOutput = run(arguments, workingDir, fileName);
		if (exit_value == 0) {
			System.out.println("File generated successfully");
		} else {
			System.out.println("Error generating file:");
			System.out.println(errorOutput);
		}
	}
	
	//TODO: Needs to be modified to be handle all scripts i.e. add Enum to parameters
	public static String run(String[] arguments, String workingDir, String fileName) {
		String script_dir = getAbsoluteScriptDirPath();
		
		String scriptPath = createFilePath(script_dir, "run_id_setup.sh");
		String pythonPath = createFilePath(script_dir, "python/id_setup.py");
		String outFileExt = ".json";
		String outputFilePath = createFilePath(workingDir, fileName + outFileExt);

		ArrayList<String> processArray = new ArrayList<String>(Arrays.asList(arguments));
		processArray.add(0, scriptPath);
		processArray.add(1, pythonPath);
		processArray.add(outputFilePath);
		
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
	 * Combines directory and file name into single path
	 * @param dir
	 * @param fileName
	 * @return String
	 */
	public static String createFilePath(String dir, String fileName) {
		return FilenameUtils.concat(dir, fileName);
	}

}
