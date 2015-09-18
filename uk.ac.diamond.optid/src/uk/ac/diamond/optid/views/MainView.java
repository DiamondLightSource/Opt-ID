package uk.ac.diamond.optid.views;

import java.io.File;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map.Entry;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.DirectoryDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PerspectiveAdapter;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.events.HyperlinkEvent;
import org.eclipse.ui.forms.events.IHyperlinkListener;
import org.eclipse.ui.forms.widgets.Hyperlink;
import org.eclipse.ui.ide.IDE;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.optid.Activator;
import uk.ac.diamond.optid.properties.PropertyConstants;
import uk.ac.diamond.optid.util.Console;
import uk.ac.diamond.optid.util.Util;

public class MainView extends ViewPart {
	
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(MainView.class);

	private static final String[] CLUSTER_QUEUE_LIST = new String[] {"Low", "Medium", "High"};

	private Image imgFolder = Activator.getDefault().getWorkbench().getSharedImages().getImageDescriptor(ISharedImages.IMG_OBJ_FOLDER).createImage();
	
	// Store values after perspective closed
	private IPreferenceStore propertyStore;
	
	/* Text to description maps */
	// Linked hash map used as we want to maintain order of insertion
	// Order of Text objects corresponds to order of arguments required by  script
	private LinkedHashMap<Text, String> textDescMap = new LinkedHashMap<>();
	
	private String workingDir;
	
	/* Generated file paths */
	private String idDescFilePath;
	private String magStrFilePath;
	private String lookupGenFilePath;
	
	// Open generated file listeners
	private HyperLinkListener idDescLinkListener;
	private HyperLinkListener magStrLinkListener;
	private HyperLinkListener lookupGenLinkListener;
	
	/* UI Components */
	
	// File generation
	private Button btnIdDes;
	private Button btnMagStr;
	private Button btnLookGen;
	private Hyperlink lblIdDesStatus;
	private Hyperlink lblMagStrStatus;
	private Hyperlink lblLookGenStatus;
	
	// Cluster
	private Text txtSlots;
	private Combo cboQueue;
	private Text txtIters;
		
	private PerspectiveAdapter perspectiveListener = new PerspectiveAdapter() {
		@Override
		public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {			
			if (perspective.getId().equals("uk.ac.diamond.optid.idSortPerspective")) {
				if (changeId.equals(IWorkbenchPage.CHANGE_RESET)) {
					btnIdDes.setSelection(false);
					btnMagStr.setSelection(false);
					btnLookGen.setSelection(false);
				}
				
				// Handles case where view opened by Window -> Show View menu
				if (changeId.equals(IWorkbenchPage.CHANGE_VIEW_SHOW)) {
					IViewPart idDescForm = getWorkbenchPage().findView(IdDescForm.ID);
					// IdDescForm open
					if (idDescForm != null) {
						btnIdDes.setSelection(true);
					}
					
					IViewPart magStrForm = getWorkbenchPage().findView(MagStrForm.ID);
					// MagStrForm open
					if (magStrForm != null) {
						btnMagStr.setSelection(true);
					}
				}
			}
		}
	};
	
	// Monitor changes to properties in the perspective-wide property store
	private IPropertyChangeListener propertyChangeListener = new IPropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent event) {			
			if (event.getProperty().equals(PropertyConstants.P_ID_DESC_PATH)) {
				// Update ID Description file path to new value
				idDescFilePath = (String) event.getNewValue();
				
				// Update status
				idDescLinkListener = new HyperLinkListener(idDescFilePath);
				setLabelStatusComplete(lblIdDesStatus, idDescFilePath, idDescLinkListener);
			} else if (event.getProperty().equals(PropertyConstants.P_MAG_STR_PATH)) {				
				// Update Magnet Strength file path to new value
				magStrFilePath = (String) event.getNewValue();
								
				// Update status
				magStrLinkListener = new HyperLinkListener(magStrFilePath);
				setLabelStatusComplete(lblMagStrStatus, magStrFilePath, magStrLinkListener);
			} else if (event.getProperty().equals(PropertyConstants.P_LOOKUP_GEN_PATH)) {
				logger.debug("** lookup file path: ");
				
				// Update Lookup Generator file path to new value
				lookupGenFilePath = (String) event.getNewValue();
				
				// Update status
				lookupGenLinkListener = new HyperLinkListener(lookupGenFilePath);
				setLabelStatusComplete(lblLookGenStatus, lookupGenFilePath, lookupGenLinkListener);
			}
		}
	};
	
	// On click, opens file with given path using default editor
	private class HyperLinkListener implements IHyperlinkListener {
		private String filePath;
		
		public HyperLinkListener(String filePath) {
			this.filePath = filePath;
		}
		
		@Override
		public void linkEntered(HyperlinkEvent e) {			
		}

		@Override
		public void linkExited(HyperlinkEvent e) {			
		}

		@Override
		public void linkActivated(HyperlinkEvent e) {
			if (filePath != null) {
				File idDescfile = new File(filePath);
				if (idDescfile.exists() && idDescfile.isFile()) {	
				    IFileStore fileStore = EFS.getLocalFileSystem().getStore(idDescfile.toURI());
				    try {
				        IDE.openEditorOnFileStore(getWorkbenchPage(), fileStore);
				    } catch ( PartInitException exc ) {
				    }
				}
			}	
		}
	}
	
	// On widget selection, opens view referenced by viewId
	private class OpenViewSelectionListener extends SelectionAdapter {
		private String viewId;
		
		public OpenViewSelectionListener(String viewId) {
			this.viewId = viewId;
		}
		
		@Override
		public void widgetSelected(SelectionEvent event) {	
			Button btn = (Button) event.widget;
			if (btn.getSelection()) {
				// Show view
				try {
					getWorkbenchPage().showView(viewId, null, IWorkbenchPage.VIEW_ACTIVATE);
				} catch (PartInitException e) {
					e.printStackTrace();
				}
			} else {
				// Hide view
				IViewPart view = getWorkbenchPage().findView(viewId);
				getWorkbenchPage().hideView(view);
			}
		}
	};
		
	@Override
    public void init(IViewSite site) throws PartInitException {
		super.init(site);
		propertyStore = Activator.getDefault().getPreferenceStore();
		propertyStore.addPropertyChangeListener(propertyChangeListener);
	}

	@Override
	public void createPartControl(Composite parent) {
		// Top-level composite
		Composite mainComposite = new Composite(parent, SWT.NONE);
		// Increase spacing between components vertically
		GridLayout layout = new GridLayout(1, false);
		layout.verticalSpacing = 15;
		mainComposite.setLayout(layout);
		mainComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		setupDirField(mainComposite);
		setupOptFileGrp(mainComposite);
		setupClusterGrp(mainComposite);
		
		getSite().getWorkbenchWindow().addPerspectiveListener(perspectiveListener);
		initialiseMap();
	}
	
	/**
	 * Setup text field to choose working directory
	 * @param parent
	 */
	private void setupDirField(Composite parent) {
		// Composite to layout label, text and button in a single row
		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(new GridLayout(4, false));
		comp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Label
		(new Label(comp, SWT.NONE)).setText("Working Directory");
		
		// Textbox
		final Text txtDir = new Text(comp, SWT.SINGLE | SWT.BORDER);
		txtDir.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Button - Directory dialog
		Button btnDir = new Button(comp, SWT.PUSH);
		btnDir.setImage(imgFolder);
		
		// Button - Set working directory
		final Button btnSave = new Button(comp, SWT.PUSH);
		btnSave.setText("Save");
		btnSave.setEnabled(false);
		
		// On select, open dialog to select a directory
		btnDir.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				DirectoryDialog dialog = new DirectoryDialog(MainView.this.getSite().getShell());
				// If string contained in textbox is a valid path to a
				// directory then it is opened otherwise set to default
		        dialog.setFilterPath(txtDir.getText());
		        dialog.setText("Choose working directory"); // Dialog title

		        String dir = dialog.open();
		        // If a directory was successfully selected
		        if (dir != null) {
		        	// Set the text box to the new selection
		        	txtDir.setText(dir);
		        }
			}
		});
		
		// Sets text colour depending on whether path is a valid directory
		txtDir.addModifyListener(new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				if (Util.isValidDirectory(txtDir.getText())) {
					txtDir.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));
					btnSave.setEnabled(true);
				} else {
					txtDir.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
					btnSave.setEnabled(false);
				}
			}
		});
		
		// Note: Button will only be enabled if valid path in txtDir
		btnSave.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				String oldWorkDir = propertyStore.getString(PropertyConstants.P_WORK_DIR);
				workingDir = txtDir.getText();
				
				// Save new directory value to property store
				propertyStore.setValue(PropertyConstants.P_WORK_DIR, workingDir);
				
				// Enable form buttons
				btnIdDes.setEnabled(true);
				btnMagStr.setEnabled(true);
				btnLookGen.setEnabled(true);
				
				// If value has actually changed
				if (!workingDir.equals(oldWorkDir)) {
					// Inform user
					Console.getInstance().newMessage(getWorkbenchPage(), "Working directory set: " + workingDir);
					
					// Resets all file generation form statuses
					idDescFilePath = null;
					setLabelStatusNotComplete(lblIdDesStatus, idDescLinkListener);
					
					magStrFilePath = null;
					setLabelStatusNotComplete(lblMagStrStatus, magStrLinkListener);
					
					lookupGenFilePath = null;
					setLabelStatusNotComplete(lblLookGenStatus, lookupGenLinkListener);
				}
			}
		});
	}
	
	/**
	 * Setup group to create required optimisation files
	 * @param parent
	 */
	private void setupOptFileGrp(Composite parent) {
		Group grpOptFiles = new Group(parent, SWT.NONE);
		grpOptFiles.setText("Setup optimisation files");
		grpOptFiles.setLayout(new GridLayout(3, false));
		grpOptFiles.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		/* ID Description */
		(new Label(grpOptFiles, SWT.NONE)).setText("1.");
		
		btnIdDes = new Button(grpOptFiles, SWT.TOGGLE);
		btnIdDes.setText("ID Description");
		// Button set to fill width of containing composite
		btnIdDes.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		btnIdDes.setEnabled(false);
		// Show/hide respective form view
		btnIdDes.addSelectionListener(new OpenViewSelectionListener(IdDescForm.ID));
		
		lblIdDesStatus = new Hyperlink(grpOptFiles, SWT.NONE);
		setLabelStatusNotComplete(lblIdDesStatus, idDescLinkListener);
		
		/* Magnet Strengths */
		(new Label(grpOptFiles, SWT.NONE)).setText("2.");
		
		btnMagStr = new Button(grpOptFiles, SWT.TOGGLE);
		btnMagStr.setText("Magnet Strengths");
		// Button set to fill width of containing composite
		btnMagStr.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		btnMagStr.setEnabled(false);
		// Show/hide respective form view
		btnMagStr.addSelectionListener(new OpenViewSelectionListener(MagStrForm.ID));
		
		lblMagStrStatus = new Hyperlink(grpOptFiles, SWT.NONE);
		setLabelStatusNotComplete(lblMagStrStatus, magStrLinkListener);
		
		/* Lookup Generator */
		(new Label(grpOptFiles, SWT.NONE)).setText("3.");
		
		btnLookGen = new Button(grpOptFiles, SWT.TOGGLE);
		btnLookGen.setText("Lookup Generator");
		// Button set to fill width of containing composite
		btnLookGen.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		btnLookGen.setEnabled(false);
		// Show/hide respective form view
		btnLookGen.addSelectionListener(new OpenViewSelectionListener(LookupGenForm.ID));
		
		lblLookGenStatus = new Hyperlink(grpOptFiles, SWT.NONE);
		setLabelStatusNotComplete(lblLookGenStatus, lookupGenLinkListener);
	}
	
	/**
	 * Setup group to specify cluster settings and run optimisation
	 * @param parent
	 */
	private void setupClusterGrp(Composite parent) {
		// Group - Cluster settings
		Group grpCluster = new Group(parent, SWT.NONE);
		grpCluster.setText("Cluster Settings");
		grpCluster.setLayout(new GridLayout(2, false));
		grpCluster.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Text (int) Field - Slots
		(new Label(grpCluster, SWT.NONE)).setText("No. of slots");
		txtSlots = new Text(grpCluster, SWT.SINGLE | SWT.BORDER);
		
		// Combo (String) Field - Queue
		(new Label(grpCluster, SWT.NONE)).setText("Queue");
		cboQueue = new Combo(grpCluster, SWT.READ_ONLY);
		cboQueue.setItems(CLUSTER_QUEUE_LIST);
		cboQueue.select(0);
		
		// Text (int) Field - Iterations
		(new Label(grpCluster, SWT.NONE)).setText("No. of iterations");
		txtIters = new Text(grpCluster, SWT.SINGLE | SWT.BORDER);
		
		// Make components stretch to fill width of view
		txtSlots.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		cboQueue.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtIters.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Run
		Button btnRun = new Button(grpCluster, SWT.PUSH);
		btnRun.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 2, 1));
		btnRun.setText("Run");
		
		// On click, checks if all text widgets have values
		// Then forwards arguments to Util.run() to call script to run optimisation
		// Message printed in console indicating success or failure		
		btnRun.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				try {
					String[] arguments = getArguments();
					String errorOutput = Util.run(Util.ScriptOpt.CLUSTER, arguments, workingDir, "");
				
					if (Util.exit_value == 0) {
						Console.getInstance().newMessage(getWorkbenchPage(), 
								"Job successfully submitted to cluster", Console.SUCCESS_COLOUR);
						Console.getInstance().newMessage(getWorkbenchPage(), 
								"Genomes will be generated in: " + workingDir + "/logs", Console.SUCCESS_COLOUR);
					} else {
						Console.getInstance().newMessage(getWorkbenchPage(), 
								"Error submitting job to cluster", Console.ERROR_COLOUR);
						Console.getInstance().newMessage(getWorkbenchPage(), errorOutput);
					}
				} catch (IllegalStateException e) {
				}
			}
		});
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

	@Override
    public void dispose() {
		// Required since getSite() returns null during workbench initialisation
		if (getSite() != null) {
			getSite().getWorkbenchWindow().removePerspectiveListener(perspectiveListener);
		}
		
		// Dispose acquired images
		if (imgFolder != null) {
			imgFolder.dispose();
		}
		
		// Restore working directory value to default on close
		propertyStore.setToDefault(PropertyConstants.P_WORK_DIR);
		// Reset generated file paths on close
		propertyStore.setToDefault(PropertyConstants.P_ID_DESC_PATH);
		propertyStore.setToDefault(PropertyConstants.P_MAG_STR_PATH);
		propertyStore.setToDefault(PropertyConstants.P_LOOKUP_GEN_PATH);
		
		super.dispose();
    }
	
	/**
	 * Updates label to status of file generation complete
	 */
	private void setLabelStatusComplete(Hyperlink label, String filePath, HyperLinkListener listener) {
		label.setText("Open");
		label.setUnderlined(true);
		label.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));
		label.setCursor(new Cursor(Display.getCurrent(), SWT.CURSOR_HAND));
		label.addHyperlinkListener(listener);
	}
	
	/**
	 * Updates label to status of file generation not complete
	 */
	private void setLabelStatusNotComplete(Hyperlink label, HyperLinkListener listener) {
		label.setText("Not complete");
		label.setUnderlined(false);
		label.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
		label.setCursor(new Cursor(Display.getCurrent(), SWT.CURSOR_ARROW));
		label.removeHyperlinkListener(listener);
	}
	
	/**
	 * Initialise Text to String map
	 */
	private void initialiseMap() {
		// Order of insertion corresponds to order of arguments for script
		textDescMap.put(txtSlots, "No. of slots");
		textDescMap.put(txtIters, "No. of iterations");
	}
	
	/**
	 * Returns array of arguments required by optimisation process
	 * @return
	 * @throws IllegalStateException
	 */
	private String[] getArguments() throws IllegalStateException {
		List<String> arguments = new ArrayList<>();
		// Text fields which have errors
		List<String> errorArgs = new ArrayList<>();
		
		// Verification error in at least one of the Text widget values
		boolean error = checkArguments(arguments, errorArgs, textDescMap);
		
		try {
			// Check cboQueue
			String queueValue = process(cboQueue.getText(), "Queue");
			
			// Convert to String accepted by script
			String queueArg;
			if (queueValue.equals("Low")) {
				queueArg = "low.q";
			} else if (queueValue.equals("Medium")){
				queueArg = "medium.q";
			} else {
				queueArg = "high.q";
			}
			
			if (!error) {
				// Queue is 2nd argument in order
				// Insertion at position 2 only guaranteed to work 
				// if there were no previous errors
				arguments.add(1, queueArg);
			}
		// No queue option selected
		} catch(IllegalArgumentException e) {
			errorArgs.add(e.getMessage());
			error = true;
		}
		
		try {
			String lookupFile = process(lookupGenFilePath, "Lookup file");
			arguments.add(lookupFile);
		} catch(IllegalArgumentException e) {
			errorArgs.add(e.getMessage());
			error = true;
		}
		
		try {
			String idDescFile = process(idDescFilePath, "ID Descriptions file");
			arguments.add(idDescFile);
		} catch(IllegalArgumentException e) {
			errorArgs.add(e.getMessage());
			error = true;
		}
		
		try {
			String magStrFile = process(magStrFilePath, "Magnet Strengths file");
			arguments.add(magStrFile);
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
		if (arg == null || arg.equals("")) {
			throw new IllegalArgumentException(description);
		}
		
		return arg;
	}
	
}
