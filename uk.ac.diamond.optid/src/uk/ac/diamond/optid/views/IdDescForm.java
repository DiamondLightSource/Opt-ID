package uk.ac.diamond.optid.views;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map.Entry;

import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CTabFolder;
import org.eclipse.swt.custom.CTabItem;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IPartListener;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.optid.Activator;
import uk.ac.diamond.optid.Console;
import uk.ac.diamond.optid.Util;
import uk.ac.diamond.optid.properties.IdDescPropertyConstants;
import uk.ac.diamond.optid.properties.PropertyConstants;

public class IdDescForm extends ViewPart {
	
	static final String ID = "uk.ac.diamond.optid.idDescForm";
	
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(IdDescForm.class);
	
	/* Dialog settings keys */
	private static final String ID_DESC_SETTINGS = "uk.ac.diamond.optid.idDescForm.settings";
	private static final String ID_DESC_TAB = "uk.ac.diamond.optid.idDescForm.tab";
	private static final String ID_DESC_FILE_PATH = "uk.ac.diamond.optid.idDescForm.filePath";
	private static final String ID_DESC_NAME = "uk.ac.diamond.optid.idDescForm.name";
	private static final String ID_DESC_TYPE = "uk.ac.diamond.optid.idDescForm.type";
	private static final String ID_DESC_PERIODS = "uk.ac.diamond.optid.idDescForm.periods";
	private static final String ID_DESC_GAP = "uk.ac.diamond.optid.idDescForm.gap";
	private static final String ID_DESC_INTERSTICE = "uk.ac.diamond.optid.idDescForm.interstice";
	private static final String ID_DESC_FULL_X = "uk.ac.diamond.optid.idDescForm.fullX";
	private static final String ID_DESC_FULL_Z = "uk.ac.diamond.optid.idDescForm.fullZ";
	private static final String ID_DESC_FULL_S = "uk.ac.diamond.optid.idDescForm.fullS";
	private static final String ID_DESC_VE_X = "uk.ac.diamond.optid.idDescForm.veX";
	private static final String ID_DESC_VE_Z = "uk.ac.diamond.optid.idDescForm.veZ";
	private static final String ID_DESC_VE_S = "uk.ac.diamond.optid.idDescForm.veS";
	private static final String ID_DESC_HE_X = "uk.ac.diamond.optid.idDescForm.heX";
	private static final String ID_DESC_HE_Z = "uk.ac.diamond.optid.idDescForm.heZ";
	private static final String ID_DESC_HE_S = "uk.ac.diamond.optid.idDescForm.heS";
	private static final String ID_DESC_X_START = "uk.ac.diamond.optid.idDescForm.xStart";
	private static final String ID_DESC_X_STOP = "uk.ac.diamond.optid.idDescForm.xStop";	
	private static final String ID_DESC_X_STEP = "uk.ac.diamond.optid.idDescForm.xStep";
	private static final String ID_DESC_Z_START = "uk.ac.diamond.optid.idDescForm.zStart";
	private static final String ID_DESC_Z_STOP = "uk.ac.diamond.optid.idDescForm.zStop";
	private static final String ID_DESC_Z_STEP = "uk.ac.diamond.optid.idDescForm.zStep";
	private static final String ID_DESC_STEPS_S = "uk.ac.diamond.optid.idDescForm.stepsS";
	private static final String ID_DESC_END_GAP = "uk.ac.diamond.optid.idDescForm.endGap";
	private static final String ID_DESC_PHASING_GAP = "uk.ac.diamond.optid.idDescForm.phasingGap";
	private static final String ID_DESC_CLAMP_CUT = "uk.ac.diamond.optid.idDescForm.clampCut";
	
	/* Combo items */
	private static final String[] ID_PARAM_TYPE_LIST = new String[] {"PPM AntiSymmetric", "APPLE Symmetric"};
	
	// Store values after perspective closed
	private IPreferenceStore propertyStore;
	
	// Directory to generate file in
	private String workingDir;
	
	/* Text to description maps */
	// Linked hash map used as we want to maintain order of insertion
	// Order of Text objects corresponds to order of arguments required by python script
	private LinkedHashMap<Text, String> textDescMap = new LinkedHashMap<>();
	private LinkedHashMap<Text, String> appleSymOnlyTextMap = new LinkedHashMap<>();
	
	/* Components */
	private CTabFolder tabFolder;
	private ScrolledComposite scrolledComp;
	private Composite compNewFileForm;

	// Load file
	private Text txtFilePath;
	
	// ID parameters
	private Text txtName;
	private Combo cboType;
	private Text txtPeriods;
	private Text txtGap;
	private Text txtInterstice;
	
	// Magnet dimensions
	private Text txtFullX;
	private Text txtFullZ;
	private Text txtFullS;
	private Text txtVeX;
	private Text txtVeZ;
	private Text txtVeS;
	private Text txtHeX;
	private Text txtHeZ;
	private Text txtHeS;
	
	// Calculation parameters
	private Text txtXStart;
	private Text txtXStop;
	private Text txtXStep;
	private Text txtZStart;
	private Text txtZStop;
	private Text txtZStep;
	private Text txtStepsS;
	
	// Apply symmetric only parameters
	private Text txtEndGap;
	private Text txtPhasingGap;
	private Text txtClampCut;
			
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
		    IDialogSettings section = settings.getSection(ID_DESC_SETTINGS);

		    // If section does not exist, create it
		    if (section == null) {
		        section = settings.addNewSection(ID_DESC_SETTINGS);
		    }

		    // Store all component values
		    section.put(ID_DESC_TAB, tabFolder.getSelectionIndex());
		    section.put(ID_DESC_FILE_PATH, txtFilePath.getText());
		    section.put(ID_DESC_NAME, txtName.getText());
		    section.put(ID_DESC_TYPE, cboType.getText());
		    section.put(ID_DESC_PERIODS, txtPeriods.getText());
		    section.put(ID_DESC_GAP, txtGap.getText());
		    section.put(ID_DESC_INTERSTICE, txtInterstice.getText());
		    section.put(ID_DESC_FULL_X, txtFullX.getText());
		    section.put(ID_DESC_FULL_Z, txtFullZ.getText());
		    section.put(ID_DESC_FULL_S, txtFullS.getText());
		    section.put(ID_DESC_VE_X, txtVeX.getText());
		    section.put(ID_DESC_VE_Z, txtVeZ.getText());
		    section.put(ID_DESC_VE_S, txtVeS.getText());
		    section.put(ID_DESC_HE_X, txtHeX.getText());
		    section.put(ID_DESC_HE_Z, txtHeZ.getText());
		    section.put(ID_DESC_HE_S, txtHeS.getText());
		    section.put(ID_DESC_X_START, txtXStart.getText());
		    section.put(ID_DESC_X_STOP, txtXStop.getText());
		    section.put(ID_DESC_X_STEP, txtXStep.getText());	    
		    section.put(ID_DESC_Z_START, txtZStart.getText());
		    section.put(ID_DESC_Z_STOP, txtZStop.getText());
		    section.put(ID_DESC_Z_STEP, txtZStep.getText());
		    section.put(ID_DESC_STEPS_S, txtStepsS.getText());
		    section.put(ID_DESC_END_GAP, txtEndGap.getText());
		    section.put(ID_DESC_PHASING_GAP, txtPhasingGap.getText());
		    section.put(ID_DESC_CLAMP_CUT, txtClampCut.getText());
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
		// Top-level tabbed composite
		tabFolder = new CTabFolder(parent, SWT.NONE);
		tabFolder.setLayoutData(new GridData(GridData.FILL_BOTH));
		tabFolder.setSimple(false);
		
		// Tab 1 - Create new file
		CTabItem tabNewFile = new CTabItem(tabFolder, SWT.NONE);
		tabNewFile.setText("Create new file");
		tabNewFile.setControl(setupNewFile(tabFolder));
		
		// Tab 2 - Load file
		CTabItem tabLoadFile = new CTabItem(tabFolder, SWT.NONE);
		tabLoadFile.setText("Load file");
		tabLoadFile.setControl(setupLoadFile(tabFolder));
		
		// Default tab selection
		tabFolder.setSelection(tabNewFile);

		initialiseMaps();
		restoreComponentValues();
	}
	
	/**
	 * Setup composite containing scrollable form and buttons
	 * @param parent
	 * @return
	 */
	private Composite setupNewFile(Composite parent) {
		Composite comp = new Composite(tabFolder, SWT.NONE);
		comp.setLayout(new GridLayout(2, false));
		comp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		setupScrolledComp(comp);
		setupSubmissionControls(comp);
		
		return comp;
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
				
				// Only clear symmetric only fields if type set
				if (cboType.getText().equals("APPLE Symmetric")) {
					for (Text text : appleSymOnlyTextMap.keySet()) {
						text.setText("");
					}	
				}
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
					String fileName = arguments[13];
					
					String errorOutput = Util.run(arguments, workingDir, fileName);
					
					// TODO: If successful, show pop-up and close view
					// File generation successful
					if (Util.exit_value == 0) {
						Console.getInstance().newMessage(getWorkbenchPage(), 
								fileName + ".json generated successfully in " + workingDir, Console.SUCCESS_COLOUR);
						// Fields only saved (long-term) if file generation successful
						saveToPropertyStore();
					} else { 
						Console.getInstance().newMessage(getWorkbenchPage(), 
								"Error generating file " + fileName + ".json", Console.ERROR_COLOUR);
						Console.getInstance().newMessage(getWorkbenchPage(), errorOutput);
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
	 * Setup vertical scroll bar for new file form
	 * @param parent
	 */
	private void setupScrolledComp(Composite parent) {
		scrolledComp = new ScrolledComposite(parent, SWT.V_SCROLL);
		scrolledComp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 2, 1));
		scrolledComp.setExpandHorizontal(true);
		scrolledComp.setExpandVertical(true);
		
		setupNewFileForm(scrolledComp);

		scrolledComp.setContent(compNewFileForm);
		// Set width at which vertical scroll bar will be used
		scrolledComp.setMinSize(compNewFileForm.computeSize(SWT.DEFAULT, SWT.DEFAULT));
	}
	
	/**
	 * Enables user-entered component values to persist across invocations
	 * of view
	 */
	private void restoreComponentValues() {
		IDialogSettings settings = Activator.getDefault().getDialogSettings();
		IDialogSettings section = settings.getSection(ID_DESC_SETTINGS);
		
		if (section != null) {
			tabFolder.setSelection(section.getInt(ID_DESC_TAB));
			txtFilePath.setText(section.get(ID_DESC_FILE_PATH));
			txtName.setText(section.get(ID_DESC_NAME));
			cboType.setText(section.get(ID_DESC_TYPE));
			txtPeriods.setText(section.get(ID_DESC_PERIODS));
			txtGap.setText(section.get(ID_DESC_GAP));
			txtInterstice.setText(section.get(ID_DESC_INTERSTICE));
			txtFullX.setText(section.get(ID_DESC_FULL_X));
			txtFullZ.setText(section.get(ID_DESC_FULL_Z));
			txtFullS.setText(section.get(ID_DESC_FULL_S));
			txtVeX.setText(section.get(ID_DESC_VE_X));
			txtVeZ.setText(section.get(ID_DESC_VE_Z));
			txtVeS.setText(section.get(ID_DESC_VE_S));
			txtHeX.setText(section.get(ID_DESC_HE_X));
			txtHeZ.setText(section.get(ID_DESC_HE_Z));
			txtHeS.setText(section.get(ID_DESC_HE_S));
			txtXStart.setText(section.get(ID_DESC_X_START));
			txtXStop.setText(section.get(ID_DESC_X_STOP));
			txtXStep.setText(section.get(ID_DESC_X_STEP));
			txtZStart.setText(section.get(ID_DESC_Z_START));
			txtZStop.setText(section.get(ID_DESC_Z_STOP));
			txtZStep.setText(section.get(ID_DESC_Z_STEP));
			txtStepsS.setText(section.get(ID_DESC_STEPS_S));
			txtEndGap.setText(section.get(ID_DESC_END_GAP));
			txtPhasingGap.setText(section.get(ID_DESC_PHASING_GAP));
			txtClampCut.setText(section.get(ID_DESC_CLAMP_CUT));
		}
		
		getSite().getWorkbenchWindow().getPartService().addPartListener(partListener);
	}
	
	/**
	 * Initialise Text to String map
	 */
	private void initialiseMaps() {
		// Order of insertion corresponds to order of arguments for python script
		textDescMap.put(txtPeriods, "Periods");
		textDescMap.put(txtFullX, "Full magnet block X-dimension");
		textDescMap.put(txtFullZ, "Full magnet block Z-dimension");
		textDescMap.put(txtFullS, "Full magnet block S-dimension");
		textDescMap.put(txtVeX, "VE magnet block X-dimension");
		textDescMap.put(txtVeZ, "VE magnet block Z-dimension");
		textDescMap.put(txtVeS, "VE magnet block S-dimension");
		textDescMap.put(txtHeX, "HE magnet block X-dimension");
		textDescMap.put(txtHeZ, "HE magnet block Z-dimension");
		textDescMap.put(txtHeS, "HE magnet block S-dimension");
		textDescMap.put(txtInterstice, "Interstice");
		textDescMap.put(txtGap, "Gap");
		// Type (combo) would be here
		// but cannot be included in the map since it is a Combo not Text
		textDescMap.put(txtName, "Name");
		textDescMap.put(txtXStart, "X Start");
		textDescMap.put(txtXStop, "X Stop");
		textDescMap.put(txtXStep, "X Step");
		textDescMap.put(txtZStart, "Z Start");
		textDescMap.put(txtZStop, "Z Stop");
		textDescMap.put(txtZStep, "Z Step");
		textDescMap.put(txtStepsS, "Steps in S");
		
		// Optional arguments
		appleSymOnlyTextMap.put(txtEndGap, "End gap");
		appleSymOnlyTextMap.put(txtPhasingGap, "Phasing gap");
		appleSymOnlyTextMap.put(txtClampCut, "Clamp cut");
	}
	
	/**
	 * Setup components for creating new JSON file
	 * @param parent
	 */
	private void setupNewFileForm(Composite parent) {
		compNewFileForm = new Composite(parent, SWT.NONE);		
		GridLayout gridLayout = new GridLayout(1, false);
		// Increase spacing between groups
		gridLayout.verticalSpacing = 15;
		compNewFileForm.setLayout(gridLayout);
	    compNewFileForm.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
	    	    
		// Create groups for each category of inputs
		setupIdParams(compNewFileForm);
		setupMagnetDims(compNewFileForm);
		setupCalParams(compNewFileForm);
		setupAppleSymOnlyParams(compNewFileForm);
	}
	
	/**
	 * Setup components for loading existing file
	 * @param parent
	 */
	private Composite setupLoadFile(Composite parent) {
		Composite comp = new Composite(parent, SWT.NONE);		
		comp.setLayout(new GridLayout(2, false));
	    comp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
	    
	    // Label
		(new Label(comp, SWT.NONE)).setText("ID Description JSON File");
		new Label(comp, SWT.NONE); // Dummy label to fill 2nd cell
		
		// Text box
		txtFilePath = new Text(comp, SWT.SINGLE | SWT.BORDER);
		txtFilePath.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Button - File path dialog
		Button btnDialog = new Button(comp, SWT.PUSH);
		btnDialog.setText("Browse");
		
		// Button - Submit file path
		Button btnSubmit = new Button(comp, SWT.PUSH);
		btnSubmit.setText("Submit");
		btnSubmit.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 2, 1));
		
		return comp;
	}

	/**
	 * Setup group of text fields to input general ID parameters
	 * @param parent
	 */
	private void setupIdParams(final Composite parent) {
		// Group - ID Parameters
		Group grpIdParams = new Group(parent, SWT.NONE);
		grpIdParams.setText("ID Parameters");
		grpIdParams.setLayout(new GridLayout(2, false));
		grpIdParams.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Text (String) Field - Name
		(new Label(grpIdParams, SWT.NONE)).setText("Name");
		txtName = new Text(grpIdParams, SWT.SINGLE | SWT.BORDER);
		
		// Combo (String) Field - Type
		(new Label(grpIdParams, SWT.NONE)).setText("Type");
		cboType = new Combo(grpIdParams, SWT.READ_ONLY);
		cboType.setItems(ID_PARAM_TYPE_LIST);
		cboType.select(0);
				
		// Text (int) Field - Periods
		(new Label(grpIdParams, SWT.NONE)).setText("Periods");
		txtPeriods = new Text(grpIdParams, SWT.SINGLE | SWT.BORDER);
		txtPeriods.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		// Text (float) Field - Gap
		(new Label(grpIdParams, SWT.NONE)).setText("Gap");
		txtGap = new Text(grpIdParams, SWT.SINGLE | SWT.BORDER);
		
		// Text (float) Field - Interstice
		(new Label(grpIdParams, SWT.NONE)).setText("Interstice");
		txtInterstice = new Text(grpIdParams, SWT.SINGLE | SWT.BORDER);
		
		// Make text box stretch to fill width of view
		txtName.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		cboType.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtGap.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtInterstice.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));	
	}
	
	/**
	 * Setup group to input magnet dimensions
	 * @param parent
	 */
	private void setupMagnetDims(Composite parent) {
		// Group - Magnet Dimensions
		Group grpMagDims = new Group(parent, SWT.NONE);
		grpMagDims.setText("Magnet Dimensions");
		// Each row has 4 cells: label followed by 3 text boxes
		grpMagDims.setLayout(new GridLayout(4, false));
		grpMagDims.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// X, Z, S labels
		new Label(grpMagDims, SWT.NONE); // Dummy label to skip 1st cell
		Label lblColTitle;
		lblColTitle = new Label(grpMagDims, SWT.NONE);
		lblColTitle.setText("X");
		lblColTitle.setLayoutData(new GridData(SWT.CENTER, SWT.FILL, true, false));
		
		lblColTitle = new Label(grpMagDims, SWT.NONE);
		lblColTitle.setText("Z");
		lblColTitle.setLayoutData(new GridData(SWT.CENTER, SWT.FILL, true, false));

		lblColTitle = new Label(grpMagDims, SWT.NONE);
		lblColTitle.setText("S");
		lblColTitle.setLayoutData(new GridData(SWT.CENTER, SWT.FILL, true, false));
		
		/* Full magnet block */
		(new Label(grpMagDims, SWT.NONE)).setText("Full");
		// Text (float) Field - Full X
		txtFullX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		
		// Text (float) Field - Full Z
		txtFullZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);

		// Text (float) Field - Full S
		txtFullS = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		
		// Make text box stretch to fill width of view
		txtFullX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtFullZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtFullS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		/* VE magnet block */
		(new Label(grpMagDims, SWT.NONE)).setText("VE");
		// Text (float) Field - VE X
		txtVeX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		
		// Text (float) Field - VE Z
		txtVeZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);

		// Text (float) Field - VE S
		txtVeS = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		
		// Make text box stretch to fill width of view
		txtVeX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtVeZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtVeS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		/* HE magnet block */
		(new Label(grpMagDims, SWT.NONE)).setText("HE");
		// Text (float) Field - HE X
		txtHeX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		
		// Text (float) Field - HE Z
		txtHeZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);

		// Text (float) Field - HE S
		txtHeS = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		
		// Make text box stretch to fill width of view
		txtHeX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtHeZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtHeS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
	}

	/**
	 * Setup group to input calculation parameters
	 * @param parent
	 */
	private void setupCalParams(Composite parent) {
		// Group - Calculation Parameters
		Group grpCalParams = new Group(parent, SWT.NONE);
		grpCalParams.setText("Calculation Parameters");
		grpCalParams.setLayout(new GridLayout(1, false));
		grpCalParams.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Composite - X & Z Container
		Composite comp1 = new Composite(grpCalParams, SWT.NONE);
		// Each row has 4 cells: label followed by 3 text boxes
		comp1.setLayout(new GridLayout(4, false));
		comp1.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Start, Stop, Step labels
		new Label(comp1, SWT.NONE); // Dummy label to skip 1st cell
		Label lblColTitle;
		lblColTitle = new Label(comp1, SWT.NONE);
		lblColTitle.setText("Start");
		lblColTitle.setLayoutData(new GridData(SWT.CENTER, SWT.FILL, true, false));
		
		lblColTitle = new Label(comp1, SWT.NONE);
		lblColTitle.setText("Stop");
		lblColTitle.setLayoutData(new GridData(SWT.CENTER, SWT.FILL, true, false));

		lblColTitle = new Label(comp1, SWT.NONE);
		lblColTitle.setText("Step");
		lblColTitle.setLayoutData(new GridData(SWT.CENTER, SWT.FILL, true, false));
		
		/* X Start-Stop-Step */
		(new Label(comp1, SWT.NONE)).setText("X");
		// Text (float) Field - X Start
		txtXStart = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		
		// Text (float) Field - X Stop
		txtXStop = new Text(comp1, SWT.SINGLE | SWT.BORDER);

		// Text (float) Field - X Step
		txtXStep = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		
		// Make text box stretch to fill width of view
		txtXStart.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtXStop.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtXStep.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		/* Z Start-Stop-Step */
		(new Label(comp1, SWT.NONE)).setText("Z");
		// Text (float) Field - Z Start
		txtZStart = new Text(comp1, SWT.SINGLE | SWT.BORDER);

		// Text (float) Field - Z Stop
		txtZStop = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		
		// Text (float) Field - Z Step
		txtZStep = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		
		// Make text box stretch to fill width of view
		txtZStart.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtZStop.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtZStep.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Composite - 'Steps in S' Container
		Composite comp2 = new Composite(grpCalParams, SWT.NONE);
		// Each row has 2 cells: label followed by a text box
		comp2.setLayout(new GridLayout(2, false));
		comp2.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		// Text (float) Field - Steps in S
		(new Label(comp2, SWT.NONE)).setText("Steps in S");
		txtStepsS = new Text(comp2, SWT.SINGLE | SWT.BORDER);
		txtStepsS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
	}
	
	/**
	 * Setup group to input Apple Symmetric only parameters
	 * <p>
	 * Visibility depends on value of Type in ID Parameters
	 * @param parent
	 */
	private void setupAppleSymOnlyParams(final Composite parent) {
		// A composite is required between parent and grpAppleSymOnly
		// since we need to show/hide contents depending on value of
		// Type in ID Parameters
		final Composite compAppleSymParams = new Composite(parent, SWT.NONE);
		GridLayout gridLayout = new GridLayout(1, false);
		// Remove margins so that group has same positioning as groups above it
		// Composite is no longer visible on the UI
		gridLayout.marginWidth = 0;
		gridLayout.verticalSpacing = 0;
		gridLayout.marginHeight = 0;
		compAppleSymParams.setLayout(gridLayout);
		// Used in cboType selection listener
	    final GridData gridDataAppleSymParams = new GridData(SWT.FILL, SWT.FILL, true, false);
	    compAppleSymParams.setLayoutData(gridDataAppleSymParams);
		
		// Group - Apple Symmetric only parameters
		Group grpAppleSymOnly = new Group(compAppleSymParams, SWT.NONE);
		grpAppleSymOnly.setText("APPLE Symmetric only");
		// Each row has 2 cells: label followed by a text box
		grpAppleSymOnly.setLayout(new GridLayout(2, false));
		grpAppleSymOnly.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		// Text (float) Field - End gap
		(new Label(grpAppleSymOnly, SWT.NONE)).setText("End gap");
		txtEndGap = new Text(grpAppleSymOnly, SWT.SINGLE | SWT.BORDER);
		
		// Text (float) Field - Phasing gap
		(new Label(grpAppleSymOnly, SWT.NONE)).setText("Phasing gap");
		txtPhasingGap = new Text(grpAppleSymOnly, SWT.SINGLE | SWT.BORDER);

		// Text (float) Field - Clamp cut
		(new Label(grpAppleSymOnly, SWT.NONE)).setText("Clamp cut");
		txtClampCut = new Text(grpAppleSymOnly, SWT.SINGLE | SWT.BORDER);
		
		// Make text box stretch to fill width of view
		txtEndGap.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtPhasingGap.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtClampCut.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Initially no value is selected in cboType so parameters are hidden
		gridDataAppleSymParams.exclude = true;
		compAppleSymParams.setVisible(false);
		
		// If "APPLE Symmetric" selected then show optional parameters
		// otherwise hide them
		cboType.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				if (cboType.getText().equals("APPLE Symmetric")) {
					gridDataAppleSymParams.exclude = false;
					compAppleSymParams.setVisible(true);
				} else {
					gridDataAppleSymParams.exclude = true;
					compAppleSymParams.setVisible(false);
				}
				
				// Resizes composite and adjusts scroll bar to adapt to new size
				compNewFileForm.pack();
				scrolledComp.setMinHeight(compNewFileForm.computeSize(SWT.DEFAULT, SWT.DEFAULT).y);
			}
		});
	}
	
	/**
	 * Returns array of arguments obtained from Text/Combo widgets in UI form
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
		// True if cboType is APPLE_AntiSymmetric
		// i.e. we need to check optional Apple sym-only widgets
		boolean optArgs = false;

		try {
			// Check cboType
			String typeValue = process(cboType.getText(), "Type");
			
			// Convert to String accepted by script
			String typeArg;
			if (typeValue.equals("PPM AntiSymmetric")) {
				typeArg = "PPM_AntiSymmetric";
			} else {
				typeArg = "APPLE_Symmetric";
				optArgs = true;
			}
			
			if (!error) {
				// Type is the 12th argument in the python script
				// Insertion at position 12 only guaranteed to work 
				// if there were no previous errors
				arguments.add(12, typeArg);
			}
		// No type option selected
		} catch(IllegalArgumentException e) {
			errorArgs.add(e.getMessage());
			error = true;
		}
		
		// Verification error in optional Apple sym-only Text widgets
		boolean optError = false;
		if (optArgs) {
			optError = checkArguments(arguments, errorArgs, appleSymOnlyTextMap);
		}
		
		// Error then arguments list not valid so print message and throw exception
		if (error | optError) {
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
				//Console.getInstance().newMessage(getWorkbenchPage(),
				//		"No value entered: " + e.getMessage(), Console.ERROR_COLOUR);
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
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_NAME, txtName.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_TYPE, cboType.getSelectionIndex());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_PERIODS, txtPeriods.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_GAP, txtGap.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_INTERSTICE, txtInterstice.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_FULL_X, txtFullX.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_FULL_Z, txtFullZ.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_FULL_S, txtFullS.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_VE_X, txtVeX.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_VE_Z, txtVeZ.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_VE_S, txtVeS.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_HE_X, txtHeX.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_HE_Z, txtHeZ.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_HE_S, txtHeS.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_X_START, txtXStart.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_X_STOP, txtXStop.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_X_STEP, txtXStep.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_Z_START, txtZStart.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_Z_STOP, txtZStop.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_Z_STEP, txtZStep.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_STEPS_S, txtStepsS.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_END_GAP, txtEndGap.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_PHASING_GAP, txtPhasingGap.getText());
		propertyStore.setValue(IdDescPropertyConstants.P_ID_DESC_CLAMP_CUT, txtClampCut.getText());	
	}
	
	/**
	 * Fills text fields with values from property store
	 */
	private void setFromPropertyStore() {
		txtName.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_NAME));
		cboType.select(propertyStore.getInt(IdDescPropertyConstants.P_ID_DESC_TYPE));
		txtPeriods.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_PERIODS));
		txtGap.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_GAP));
		txtInterstice.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_INTERSTICE));
		txtFullX.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_FULL_X));
		txtFullZ.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_FULL_Z));
		txtFullS.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_FULL_S));
		txtVeX.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_VE_X));
		txtVeZ.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_VE_Z));
		txtVeS.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_VE_S));
		txtHeX.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_HE_X));
		txtHeZ.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_HE_Z));
		txtHeS.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_HE_S));
		txtXStart.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_X_START));
		txtXStop.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_X_STOP));
		txtXStep.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_X_STEP));
		txtZStart.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_Z_START));
		txtZStop.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_Z_STOP));
		txtZStep.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_Z_STEP));
		txtStepsS.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_STEPS_S));
		txtEndGap.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_END_GAP));
		txtPhasingGap.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_PHASING_GAP));
		txtClampCut.setText(propertyStore.getString(IdDescPropertyConstants.P_ID_DESC_CLAMP_CUT));
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

}
