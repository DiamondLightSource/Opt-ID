package uk.ac.diamond.optid.views;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map.Entry;

import org.apache.commons.lang.ArrayUtils;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.optid.Activator;
import uk.ac.diamond.optid.properties.MagStrPropertyConstants;
import uk.ac.diamond.optid.properties.PropertyConstants;
import uk.ac.diamond.optid.util.Console;
import uk.ac.diamond.optid.util.Util;

public class MagStrForm extends ViewPart {
	
	static final String ID = "uk.ac.diamond.optid.magStrForm";
	
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(MagStrForm.class);
	
	/* Dialog settings keys */
	private static final String MAG_STR_SETTINGS = "uk.ac.diamond.optid.magStrForm.settings";
	private static final String MAG_STR_FILENAME = "uk.ac.diamond.optid.magStrForm.filename";
	private static final String MAG_STR_SIM_H = "uk.ac.diamond.optid.magStrForm.simH";
	private static final String MAG_STR_SIM_HE = "uk.ac.diamond.optid.magStrForm.simHe";
	private static final String MAG_STR_SIM_V = "uk.ac.diamond.optid.magStrForm.simV";
	private static final String MAG_STR_SIM_VE = "uk.ac.diamond.optid.magStrForm.simVe";

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
	
	// Magnet data file paths
	private Text txtMagDataH;
	private Text txtMagDataHe;
	private Text txtMagDataV;
	private Text txtMagDataVe;
	
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
		    IDialogSettings section = settings.getSection(MAG_STR_SETTINGS);

		    // If section does not exist, create it
		    if (section == null) {
		        section = settings.addNewSection(MAG_STR_SETTINGS);
		    }

		    // Store all component values
		    section.put(MAG_STR_FILENAME, txtFilename.getText());
		    section.put(MAG_STR_SIM_H, txtMagDataH.getText());
		    section.put(MAG_STR_SIM_HE, txtMagDataHe.getText());
		    section.put(MAG_STR_SIM_V, txtMagDataV.getText());
		    section.put(MAG_STR_SIM_VE, txtMagDataVe.getText());
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
	 * Setup vertical scroll bar for form
	 * @param parent
	 */
	private void setupScrolledComp(Composite parent) {
		scrolledComp = new ScrolledComposite(parent, SWT.V_SCROLL);
		scrolledComp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 2, 1));
		scrolledComp.setExpandHorizontal(true);
		scrolledComp.setExpandVertical(true);
		
		setupMagData(scrolledComp);

		scrolledComp.setContent(compNewFileForm);
		// Set width at which vertical scroll bar will be used
		scrolledComp.setMinSize(compNewFileForm.computeSize(SWT.DEFAULT, SWT.DEFAULT));
	}
	
	/**
	 * Setup components for creating new MAG file
	 * @param parent
	 */
	private void setupMagData(Composite parent) {
		compNewFileForm = new Composite(parent, SWT.NONE);
		GridLayout compGridLayout = new GridLayout(2, false);
		compGridLayout.verticalSpacing = 15;
		compNewFileForm.setLayout(compGridLayout);
		compNewFileForm.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		setupFilename(compNewFileForm);
		setupMagDataGrp(compNewFileForm);
	}
	
	/**
	 * Sets up Text widget to input filename for MAG output
	 * @param parent
	 */
	private void setupFilename(Composite parent) {
		// Text (String) Field - Filename
		(new Label(parent, SWT.NONE)).setText("Filename");
		
		// Remove spacing between Text widget and '.mag' label
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
		(new Label(comp, SWT.NONE)).setText(".mag");
	}
	
	/**
	 * Sets up widgets for getting SIM files
	 * @param parent
	 */
	private void setupMagDataGrp(Composite parent) {
		// Group - Magnet data parameters
		Group grpMagData = new Group(parent, SWT.NONE);
		grpMagData.setText("Magnet Data Files (.sim)");
		grpMagData.setLayout(new GridLayout(3, false));
		grpMagData.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 2, 1));
		
		// Text (String) Field - H Magnet Data path
		(new Label(grpMagData, SWT.NONE)).setText("H");
		txtMagDataH = newTextWidget(grpMagData);
		newFileDialogBtn(grpMagData, txtMagDataH);
		
		// Text (String) Field - HE Magnet Data path
		(new Label(grpMagData, SWT.NONE)).setText("HE");
		txtMagDataHe = newTextWidget(grpMagData);
		newFileDialogBtn(grpMagData, txtMagDataHe);
		
		// Text (String) Field - V Magnet Data path
		(new Label(grpMagData, SWT.NONE)).setText("V");
		txtMagDataV = newTextWidget(grpMagData);
		newFileDialogBtn(grpMagData, txtMagDataV);
		
		// Text (String) Field - VE Magnet Data path
		(new Label(grpMagData, SWT.NONE)).setText("VE");
		txtMagDataVe = newTextWidget(grpMagData);
		newFileDialogBtn(grpMagData, txtMagDataVe);
		
		// Make text box stretch to fill width of view
		txtMagDataH.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtMagDataHe.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtMagDataV.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtMagDataVe.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
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
		
		// Clear all text boxes
		btnClear.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				for (Text text : textDescMap.keySet()) {
					text.setText("");
				}
				txtFilename.setText("");
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
					
					String errorOutput = Util.run(Util.ScriptOpt.MAG_STR, arguments, workingDir, filename);
					
					if (Util.exit_value == 0) {
						Console.getInstance().newMessage(getWorkbenchPage(), 
								filename + ".mag generated successfully in " + workingDir, Console.SUCCESS_COLOUR);
						
						// Fields only saved (long-term) if file generation successful
						saveToPropertyStore();
						// Update generated file's path in property store
						// To notify MainView of new value
						String filePath = Util.createFilePath(workingDir, filename + ".mag");
						propertyStore.setValue(PropertyConstants.P_MAG_STR_PATH, filePath);
					} else {
						Console.getInstance().newMessage(getWorkbenchPage(), 
								"Error generating file " + filename + ".mag", Console.ERROR_COLOUR);
						String trimOutput = errorOutput.substring(errorOutput.indexOf("Traceback"));
						Console.getInstance().newMessage(getWorkbenchPage(), trimOutput);
					}
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
	 * Create new Text widget for SIM path
	 * @param parent
	 * @return Text
	 */
	private Text newTextWidget(Composite parent) {
		final Text txtPath = new Text(parent, SWT.SINGLE | SWT.BORDER);
		
		// Sets text colour depending on whether path is a valid .sim file
		txtPath.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				if (Util.isValidFile(txtPath.getText(), "sim")) {
					txtPath.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));
				} else {
					txtPath.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
				}
			}
		});
		
		return txtPath;
	}
	
	/**
	 * Creates new button which opens dialog to select SIM file
	 * @param parent
	 * @param txtPath
	 */
	private void newFileDialogBtn(Composite parent, final Text txtPath) {
		Button btnDlg = new Button(parent, SWT.PUSH);
		btnDlg.setImage(imgFile);
		
		// On select, open dialog to select a .sim file
		btnDlg.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				FileDialog dialog = new FileDialog(MagStrForm.this.getSite().getShell());
				
				// If string contained in textbox is a valid path to a
				// file then it is opened otherwise set to default
		        dialog.setFilterPath(txtPath.getText());
		        dialog.setText("Choose SIM file"); // Dialog title
		        dialog.setFilterExtensions(new String[] {"*.sim"});

		        String filePath = dialog.open();
		        // If a file path was successfully selected
		        if (filePath != null) {
		        	// Set the text box to the new selection
		        	txtPath.setText(filePath);
		        }
			}
		});
	}
	
	/**
	 * Enables user-entered component values to persist across invocations
	 * of view
	 */
	private void restoreComponentValues() {
		IDialogSettings settings = Activator.getDefault().getDialogSettings();
		IDialogSettings section = settings.getSection(MAG_STR_SETTINGS);
		
		if (section != null) {
			txtFilename.setText(section.get(MAG_STR_FILENAME));
			txtMagDataH.setText(section.get(MAG_STR_SIM_H));
			txtMagDataHe.setText(section.get(MAG_STR_SIM_HE));
			txtMagDataV.setText(section.get(MAG_STR_SIM_V));
			txtMagDataVe.setText(section.get(MAG_STR_SIM_VE));
		}
		
		getSite().getWorkbenchWindow().getPartService().addPartListener(partListener);
	}
	
	/**
	 * Initialise Text to String map
	 */
	private void initialiseMaps() {
		// Order of insertion corresponds to order of arguments for python script
		textDescMap.put(txtMagDataH, "H magnet data");
		textDescMap.put(txtMagDataHe, "HE magnet data");
		textDescMap.put(txtMagDataV, "V magnet data");
		textDescMap.put(txtMagDataVe, "VE magnet data");
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
		propertyStore.setValue(MagStrPropertyConstants.P_MAG_STR_FILENAME, txtFilename.getText());
		propertyStore.setValue(MagStrPropertyConstants.P_MAG_STR_H, txtMagDataH.getText());
		propertyStore.setValue(MagStrPropertyConstants.P_MAG_STR_HE, txtMagDataHe.getText());
		propertyStore.setValue(MagStrPropertyConstants.P_MAG_STR_V, txtMagDataV.getText());
		propertyStore.setValue(MagStrPropertyConstants.P_MAG_STR_VE, txtMagDataVe.getText());
	}
	
	/**
	 * Fills text fields with values from property store
	 */
	private void setFromPropertyStore() {
		txtFilename.setText(propertyStore.getString(MagStrPropertyConstants.P_MAG_STR_FILENAME));
		txtMagDataH.setText(propertyStore.getString(MagStrPropertyConstants.P_MAG_STR_H));
		txtMagDataHe.setText(propertyStore.getString(MagStrPropertyConstants.P_MAG_STR_HE));
		txtMagDataV.setText(propertyStore.getString(MagStrPropertyConstants.P_MAG_STR_V));
		txtMagDataVe.setText(propertyStore.getString(MagStrPropertyConstants.P_MAG_STR_VE));
	}
	
	/**
	 * Returns active workbench page
	 * @return
	 */
	private IWorkbenchPage getWorkbenchPage() {
		return PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage();
	}
	
	@Override
    public void dispose() {
		// Dispose acquired images
		if (imgFile != null) {
			imgFile.dispose();
		}

		super.dispose();
    }

	@Override
	public void setFocus() {
	}

}
