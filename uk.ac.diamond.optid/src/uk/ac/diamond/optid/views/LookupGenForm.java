package uk.ac.diamond.optid.views;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map.Entry;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IPartListener;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.progress.UIJob;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.optid.Activator;
import uk.ac.diamond.optid.properties.LookupGenPropertyConstants;
import uk.ac.diamond.optid.properties.PropertyConstants;
import uk.ac.diamond.optid.util.Console;
import uk.ac.diamond.optid.util.Util;

public class LookupGenForm extends ViewPart {
	
	static final String ID = "uk.ac.diamond.optid.lookupGenForm";
	
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(LookupGenForm.class);
	
	/* Dialog settings keys */
	private static final String LOOKUP_GEN_SETTINGS = "uk.ac.diamond.optid.lookupGenForm.settings";
	private static final String LOOKUP_GEN_FILENAME = "uk.ac.diamond.optid.lookupGenForm.filename";
	private static final String LOOKUP_GEN_PERIODS = "uk.ac.diamond.optid.lookupGenForm.periods";
	private static final String LOOKUP_GEN_JSON = "uk.ac.diamond.optid.lookupGenForm.json";
	private static final String LOOKUP_GEN_SYMMETRIC = "uk.ac.diamond.optid.lookupGenForm.symmetric";
	private static final String LOOKUP_GEN_RANDOM = "uk.ac.diamond.optid.lookupGenForm.random";
	
	private Image imgFile = Activator.getDefault().getWorkbench().getSharedImages().getImageDescriptor(ISharedImages.IMG_OBJ_FILE).createImage();
	
	// Store values after perspective closed
	private IPreferenceStore propertyStore;
	
	// Directory to generate file in
	private String workingDir;
	
	/* Text to description maps */
	// Linked hash map used as we want to maintain order of insertion
	// Order of Text objects corresponds to order of arguments required by python script
	private LinkedHashMap<Text, String> textDescMap = new LinkedHashMap<>();
	
	/* Components */
	private ScrolledComposite scrolledComp;
	private Composite compNewFileForm;
	
	private Text txtFilename;
	
	// Lookup parameters
	private Text txtPeriods;
	private Text txtJson;
	private Button btnSym;
	private Button btnRan;

	// Listener for view lifecycle
	private IPartListener partListener = new IPartListener() {
		@Override
		public void partOpened(IWorkbenchPart part) {			
		}
		
		@Override
		public void partDeactivated(IWorkbenchPart part) {			
		}
		
		@Override
		public void partClosed(IWorkbenchPart part) {
			// View closed, listener no longer needed
			getSite().getWorkbenchWindow().getPartService().removePartListener(this);
			
		    IDialogSettings settings = Activator.getDefault().getDialogSettings();
		    IDialogSettings section = settings.getSection(LOOKUP_GEN_SETTINGS);

		    // If section does not exist, create it
		    if (section == null) {
		        section = settings.addNewSection(LOOKUP_GEN_SETTINGS);
		    }

		    // Store all component values
		    section.put(LOOKUP_GEN_FILENAME, txtFilename.getText());
		    section.put(LOOKUP_GEN_PERIODS, txtPeriods.getText());
		    section.put(LOOKUP_GEN_JSON, txtJson.getText());
		    section.put(LOOKUP_GEN_SYMMETRIC, btnSym.getSelection());
		    section.put(LOOKUP_GEN_RANDOM, btnRan.getSelection());
		}
		
		@Override
		public void partBroughtToTop(IWorkbenchPart part) {			
		}
		
		@Override
		public void partActivated(IWorkbenchPart part) {			
		}
	};
	
	// Monitor changes to properties in the perspective-wide property store
	private IPropertyChangeListener propertyChangeListener = new IPropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent event) {
			// Working directory changed in MainView
			if (event.getProperty().equals(PropertyConstants.P_WORK_DIR)) {
				// Update to latest value
				workingDir = (String) event.getNewValue();
			}
		}
	};
	
	@Override
    public void init(IViewSite site) throws PartInitException {
		super.init(site);
		propertyStore = Activator.getDefault().getPreferenceStore();
		propertyStore.addPropertyChangeListener(propertyChangeListener);
		
		workingDir = propertyStore.getString(PropertyConstants.P_WORK_DIR);
	}
	
	@Override
	public void createPartControl(Composite parent) {
		// Top-level composite
		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(new GridLayout(2, false));
		comp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		// Set up scrolled composite containing form fields
		setupScrolledComp(comp);
		// Setup Clear, Restore & Submit buttons
		setupSubmissionControls(comp);
		
		initialiseMaps();
		restoreComponentValues();
	}
	
	/**
	 * Initialise Text to String map
	 */
	private void initialiseMaps() {
		// Order of insertion corresponds to order of arguments for python script
		textDescMap.put(txtPeriods, "Periods");
		textDescMap.put(txtJson, "JSON file");
	}
	
	/**
	 * Setup vertical scroll bar for form
	 * @param parent
	 */
	private void setupScrolledComp(Composite parent) {
		scrolledComp = new ScrolledComposite(parent, SWT.V_SCROLL);
		scrolledComp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 2, 1));
		scrolledComp.setExpandHorizontal(true);
		scrolledComp.setExpandVertical(true);
		
		setupLookupGen(scrolledComp);

		scrolledComp.setContent(compNewFileForm);
		// Set width at which vertical scroll bar will be used
		scrolledComp.setMinSize(compNewFileForm.computeSize(SWT.DEFAULT, SWT.DEFAULT));
	}
	
	/**
	 * Setup components for creating new h5 lookup file
	 * @param parent
	 */
	private void setupLookupGen(Composite parent) {
		compNewFileForm = new Composite(parent, SWT.NONE);
		GridLayout compGridLayout = new GridLayout(2, false);
		compGridLayout.verticalSpacing = 15;
		compNewFileForm.setLayout(compGridLayout);
		compNewFileForm.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		setupFilename(compNewFileForm);
		setupLookupGenGrp(compNewFileForm);
	}
	
	/**
	 * Sets up Text widget to input filename for h5 output
	 * @param parent
	 */
	private void setupFilename(Composite parent) {
		// Text (String) Field - Filename
		(new Label(parent, SWT.NONE)).setText("Filename");
		
		// Remove spacing between Text widget and '.h5' label
		Composite comp = new Composite(parent, SWT.NONE);
		GridLayout gridLayout = new GridLayout(2, false);
		gridLayout.horizontalSpacing = 0;
		gridLayout.marginWidth = 0;
		gridLayout.verticalSpacing = 0;
		gridLayout.marginHeight = 0;
		comp.setLayout(gridLayout);
		comp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		txtFilename = new Text(comp, SWT.SINGLE | SWT.BORDER);
		txtFilename.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		(new Label(comp, SWT.NONE)).setText(".h5");
	}
	
	/**
	 * Sets up widgets for lookup parameters
	 * @param parent
	 */
	private void setupLookupGenGrp(Composite parent) {
		// Group - Lookup parameters
		Group grpLookupGen = new Group(parent, SWT.NONE);
		grpLookupGen.setText("Lookup Parameters");
		grpLookupGen.setLayout(new GridLayout(3, false));
		grpLookupGen.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 2, 1));
		
		// Text (int) Field - Periods
		(new Label(grpLookupGen, SWT.NONE)).setText("Periods");
		txtPeriods = new Text(grpLookupGen, SWT.SINGLE | SWT.BORDER);
		txtPeriods.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 2, 1));
		
		// Text (String) Field - JSON
		(new Label(grpLookupGen, SWT.NONE)).setText("JSON");
		txtJson = new Text(grpLookupGen, SWT.SINGLE | SWT.BORDER);
		txtJson.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Button btnDlg = new Button(grpLookupGen, SWT.PUSH);
		btnDlg.setImage(imgFile);
		
		// Button (boolean) Field - Symmetric
		(new Label(grpLookupGen, SWT.NONE)).setText("Symmetric");
		btnSym = new Button(grpLookupGen, SWT.CHECK);
		new Label(grpLookupGen, SWT.NONE);
		
		// Button (boolean) Field - Random
		(new Label(grpLookupGen, SWT.NONE)).setText("Random");
		btnRan = new Button(grpLookupGen, SWT.CHECK);
		new Label(grpLookupGen, SWT.NONE);
		
		// Sets text colour depending on whether path is a valid .json file
		txtJson.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				if (Util.isValidFile(txtJson.getText(), "json")) {
					txtJson.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));
				} else {
					txtJson.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
				}
			}
		});
		
		// On select, open dialog to select a .json file
		btnDlg.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				FileDialog dialog = new FileDialog(LookupGenForm.this.getSite().getShell());
				
				// If string contained in textbox is empty then
				// opens working directory (should contain JSON from previous form)
				// otherwise attempts to open non-empty string
				if (txtJson.getText().equals("")) {
			        dialog.setFilterPath(workingDir);
				} else {
			        dialog.setFilterPath(txtJson.getText());
				}
				dialog.setText("Choose JSON file"); // Dialog title
		        dialog.setFilterExtensions(new String[] {"*.json"});

		        String filePath = dialog.open();
		        // If a file path was successfully selected
		        if (filePath != null) {
		        	// Set the text box to the new selection
		        	txtJson.setText(filePath);
		        }
			}
		});

	}
	
	/**
	 * Setup buttons for manipulating form and submitting values
	 * @param parent
	 */
	private void setupSubmissionControls(Composite parent) {
		Button btnClear = new Button(parent, SWT.PUSH);
		btnClear.setText("Clear");
		btnClear.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		Button btnRestore = new Button(parent, SWT.PUSH);
		btnRestore.setText("Restore");
		btnRestore.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Button btnSubmit = new Button(parent, SWT.PUSH);
		btnSubmit.setText("Submit");
		btnSubmit.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 2, 1));
		
		// Reset all widgets
		btnClear.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				txtFilename.setText("");
				txtPeriods.setText("");
				txtJson.setText("");
				btnSym.setSelection(false);
				btnRan.setSelection(false);
			}
		});
		
		// On click, checks if all text widgets have values
		// Then forwards arguments to Util.run() to call script to generate file
		// Message printed in console indicating success or failure
		btnSubmit.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				try {
					String[] arguments = getArguments();
					String filename = arguments[4];
					// Remove filename from arguments array
					arguments = (String[]) ArrayUtils.removeElement(arguments, filename);
					
					// Executed in a job since lookup generation can take a few minutes
					(new LookupGenJob(arguments, workingDir, filename, getWorkbenchPage())).schedule();	
				} catch (IllegalStateException e) {
				}
			}
		});
		
		// Restores text fields with values from previous successful file generation
		btnRestore.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				setFromPropertyStore();
			}
		});
	}
	
	/**
	 * Enables user-entered component values to persist across invocations
	 * of view
	 */
	private void restoreComponentValues() {
		IDialogSettings settings = Activator.getDefault().getDialogSettings();
		IDialogSettings section = settings.getSection(LOOKUP_GEN_SETTINGS);
		
		if (section != null) {
			txtFilename.setText(section.get(LOOKUP_GEN_FILENAME));
			txtPeriods.setText(section.get(LOOKUP_GEN_PERIODS));
			txtJson.setText(section.get(LOOKUP_GEN_JSON));
			btnSym.setSelection(section.getBoolean(LOOKUP_GEN_SYMMETRIC));
			btnRan.setSelection(section.getBoolean(LOOKUP_GEN_RANDOM));
		}
		
		getSite().getWorkbenchWindow().getPartService().addPartListener(partListener);
	}
	
	/**
	 * Returns array of arguments obtained from Text widgets in UI form
	 * @return
	 * @throws IllegalStateException
	 */
	private String[] getArguments() throws IllegalStateException {
		// Contains values from input widgets in form
		List<String> arguments = new ArrayList<>();
		// Text fields which have errors
		List<String> errorArgs = new ArrayList<>();
		
		// Verification error in at least one of the Text widget values
		boolean error = checkArguments(arguments, errorArgs, textDescMap);
		
		try {
			String fileName = process(txtFilename.getText(), "Filename");
			arguments.add(fileName);
		// No filename given
		} catch(IllegalArgumentException e) {
			errorArgs.add(e.getMessage());
			error = true;
		}
		
		// Error then arguments list not valid so print message and throw exception
		if (error) {
			String msg = "";
			for (String arg : errorArgs) {
				msg += arg + "; ";
			}
			msg = msg.substring(0, msg.length() - 2); // Remove trailing '; '
			Console.getInstance().newMessage(getWorkbenchPage(), 
					"No value entered for: " + msg, Console.ERROR_COLOUR);
			throw new IllegalStateException();
		}
		
		// If random and symmetric options selected then add flags to arguments list
		if (btnSym.getSelection()) {
			arguments.add(1, "-s");
		} else {
			arguments.add(1, "");
		}
		
		if (btnRan.getSelection()) {
			arguments.add(1, "-r");
		} else {
			arguments.add(1, "");
		}

		return arguments.toArray(new String[arguments.size()]);
	}
	
	/**
	 * Determines if Text values are valid and if so adds them to the list of arguments
	 * @param arguments
	 * @param map
	 * @return boolean
	 */
	private boolean checkArguments(List<String> arguments, List<String> errorArgs, LinkedHashMap<Text, String> map) {
		boolean error = false;
		// Iterates over all <Text, Description> objects in map
		for (Entry<Text, String> entry : map.entrySet()) {
			try {
				// Attempts to add Text value to list of arguments
				arguments.add(process(entry));
			} catch(IllegalArgumentException e) {
				errorArgs.add(e.getMessage());
				error = true;
			}
		}
		return error;
	}
	
	/**
	 * Checks if Text value in entry is valid
	 * @param entry
	 * @return String
	 * @throws IllegalArgumentException
	 */
	private String process(Entry<Text, String> entry) throws IllegalArgumentException {
		String arg = entry.getKey().getText();
		String desc = entry.getValue();
		
		return process(arg, desc);
	}
	
	/**
	 * Checks if arg is valid
	 * @param arg
	 * @param description
	 * @return String
	 * @throws IllegalArgumentException
	 */
	private String process(String arg, String description) throws IllegalArgumentException {
		// No value entered
		if (arg.equals("")) {
			throw new IllegalArgumentException(description);
		}
		
		return arg;
	}
	
	/**
	 * Saves text field values to property store
	 */
	private void saveToPropertyStore() {
		propertyStore.setValue(LookupGenPropertyConstants.P_LOOKUP_GEN_FILENAME, txtFilename.getText());
		propertyStore.setValue(LookupGenPropertyConstants.P_LOOKUP_GEN_PERIODS, txtPeriods.getText());
		propertyStore.setValue(LookupGenPropertyConstants.P_LOOKUP_GEN_JSON, txtJson.getText());
		propertyStore.setValue(LookupGenPropertyConstants.P_LOOKUP_GEN_SYMMETRIC, btnSym.getSelection());
		propertyStore.setValue(LookupGenPropertyConstants.P_LOOKUP_GEN_RANDOM, btnRan.getSelection());
	}
	
	/**
	 * Fills text fields with values from property store
	 */
	private void setFromPropertyStore() {
		txtFilename.setText(propertyStore.getString(LookupGenPropertyConstants.P_LOOKUP_GEN_FILENAME));
		txtPeriods.setText(propertyStore.getString(LookupGenPropertyConstants.P_LOOKUP_GEN_PERIODS));
		txtJson.setText(propertyStore.getString(LookupGenPropertyConstants.P_LOOKUP_GEN_JSON));
		btnSym.setSelection(propertyStore.getBoolean(LookupGenPropertyConstants.P_LOOKUP_GEN_SYMMETRIC));
		btnRan.setSelection(propertyStore.getBoolean(LookupGenPropertyConstants.P_LOOKUP_GEN_RANDOM));
	}
	
	/**
	 * Returns active workbench page
	 * @return
	 */
	private IWorkbenchPage getWorkbenchPage() {
		return PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage();
	}

	@Override
	public void setFocus() {
	}
	
	// File generation executed in separate thread since it can take a while
	// depending on the number of periods chosen
	class LookupGenJob extends Job {
		
		private String[] arguments;
		private String workingDir;
		private String filename;
		private IWorkbenchPage page;

		public LookupGenJob(String[] arguments, String workingDir, String filename, IWorkbenchPage page) {
			super("Generating " + filename + ".h5");
			this.arguments = arguments;
			this.workingDir = workingDir;
			this.filename = filename;
			this.page = page;
		}
		
		@Override
		protected IStatus run(IProgressMonitor monitor) {
			String errorOutput = Util.run(Util.ScriptOpt.LOOKUP_GEN, arguments, workingDir, filename);
			(new UpdateConsole(filename, errorOutput, page)).schedule();
			return Status.OK_STATUS;
		}
	}
	
	// Display in console outcome of lookup file generation
	class UpdateConsole extends UIJob {
		
		private String filename;
		private String errorOutput;
		private IWorkbenchPage page;
		
		public UpdateConsole(String filename, String errorOutput, IWorkbenchPage page) {
			super("Displaying response");
			this.filename = filename;
			this.errorOutput = errorOutput;
			this.page = page;
		}

		@Override
		public IStatus runInUIThread(IProgressMonitor monitor) {
			if (Util.lookup_exit_value == 0) {
				Console.getInstance().newMessage(page, 
						filename + ".h5 generated successfully in " + workingDir, Console.SUCCESS_COLOUR);
				// Fields only saved (long-term) if file generation successful
				saveToPropertyStore();
				// Update generated file's path in property store
				// To notify MainView of new value
				String filePath = Util.createFilePath(workingDir, filename + ".h5");
				propertyStore.setValue(PropertyConstants.P_LOOKUP_GEN_PATH, filePath);
			} else {
				Console.getInstance().newMessage(page, 
						"Error generating file " + filename + ".h5", Console.ERROR_COLOUR);
				Console.getInstance().newMessage(page, errorOutput);
			}
			
			return Status.OK_STATUS;
		}
		
	}	

}
