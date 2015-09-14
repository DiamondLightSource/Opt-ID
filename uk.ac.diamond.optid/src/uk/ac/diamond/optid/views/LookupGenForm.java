package uk.ac.diamond.optid.views;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.optid.Activator;

public class LookupGenForm extends ViewPart {
	
	static final String ID = "uk.ac.diamond.optid.lookupGenForm";
	
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

	@Override
	public void setFocus() {
	}

}
