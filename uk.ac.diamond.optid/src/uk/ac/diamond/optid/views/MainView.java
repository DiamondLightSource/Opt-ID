package uk.ac.diamond.optid.views;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.DirectoryDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.part.ViewPart;

public class MainView extends ViewPart {

	@Override
	public void createPartControl(Composite parent) {
		// Top-level composite
		Composite mainComposite = new Composite(parent, SWT.NONE);
		mainComposite.setLayout(new GridLayout(1, false));
		mainComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		setupDirField(mainComposite);
		setupOptFileGrp(mainComposite);
	}
	
	/**
	 * Setup text field to choose working directory
	 * @param parent
	 */
	private void setupDirField(Composite parent) {
		// Composite to layout label, text and button in a single row
		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(new GridLayout(3, false));
		comp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Label
		(new Label(comp, SWT.NONE)).setText("Working Directory");
		
		// Textbox
		final Text txtDir = new Text(comp, SWT.SINGLE | SWT.BORDER);
		txtDir.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Button
		Button btnDir = new Button(comp, SWT.PUSH);
		//TODO: Replace button label with icon
		btnDir.setText("Browse");
		// On select, open dialog to select a directory
		btnDir.addSelectionListener(new SelectionAdapter() {
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
		
		Button btnIdDes = new Button(grpOptFiles, SWT.TOGGLE);
		btnIdDes.setText("ID Description");
		// Button set to fill width of containing composite
		btnIdDes.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		Label lblIdDesStatus = new Label(grpOptFiles, SWT.NONE);
		// Initial label status
		lblIdDesStatus.setText("Not complete");
		lblIdDesStatus.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
		
		/* Magnet Strengths */
		(new Label(grpOptFiles, SWT.NONE)).setText("2.");
		
		Button btnMagStr = new Button(grpOptFiles, SWT.TOGGLE);
		btnMagStr.setText("Magnet Strengths");
		// Button set to fill width of containing composite
		btnMagStr.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		Label lblMagStrStatus = new Label(grpOptFiles, SWT.NONE);
		// Initial label status
		lblMagStrStatus.setText("Not complete");
		lblMagStrStatus.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
		
		/* Lookup Generator */
		(new Label(grpOptFiles, SWT.NONE)).setText("3.");
		
		Button btnLookGen = new Button(grpOptFiles, SWT.TOGGLE);
		btnLookGen.setText("Lookup Generator");
		// Button set to fill width of containing composite
		btnLookGen.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		Label lblLookGenStatus = new Label(grpOptFiles, SWT.NONE);
		// Initial label status
		lblLookGenStatus.setText("Not complete");
		lblLookGenStatus.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
	}

	@Override
	public void setFocus() {		
	}

}
