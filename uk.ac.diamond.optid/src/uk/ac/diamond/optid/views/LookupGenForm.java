package uk.ac.diamond.optid.views;

import org.eclipse.jface.dialogs.IDialogSettings;
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
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.optid.Activator;
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
				
				// If string contained in textbox is a valid path to a
				// file then it is opened otherwise set to default
		        dialog.setFilterPath(txtJson.getText());
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

	@Override
	public void setFocus() {
	}

}
