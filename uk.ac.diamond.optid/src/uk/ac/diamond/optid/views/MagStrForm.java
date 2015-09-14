package uk.ac.diamond.optid.views;

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
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.optid.Activator;
import uk.ac.diamond.optid.Util;

public class MagStrForm extends ViewPart {
	
	static final String ID = "uk.ac.diamond.optid.magStrForm";
	
	private Image imgFile = Activator.getDefault().getWorkbench().getSharedImages().getImageDescriptor(ISharedImages.IMG_OBJ_FILE).createImage();
	
	/* Components */
	private ScrolledComposite scrolledComp;
	private Composite compNewFileForm;
	
	// Magnet data file paths
	private Text txtMagDataH;
	private Text txtMagDataHe;
	private Text txtMagDataV;
	private Text txtMagDataVe;

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
		compNewFileForm.setLayout(new GridLayout(1, false));
		compNewFileForm.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Group - Magnet data parameters
		Group grpMagData = new Group(compNewFileForm, SWT.NONE);
		grpMagData.setText("Magnet Data Files (.sim)");
		grpMagData.setLayout(new GridLayout(3, false));
		grpMagData.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
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
				if (Util.isValidSimFile(txtPath.getText())) {
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
