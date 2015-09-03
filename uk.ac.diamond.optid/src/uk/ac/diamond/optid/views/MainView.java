package uk.ac.diamond.optid.views;

import java.nio.file.Files;
import java.nio.file.Paths;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.DirectoryDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PerspectiveAdapter;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.optid.Activator;
import uk.ac.diamond.optid.Console;

public class MainView extends ViewPart {
	
	private static final Logger logger = LoggerFactory.getLogger(MainView.class);
	
	private Image imgFolder = Activator.getDefault().getWorkbench().getSharedImages().getImageDescriptor(ISharedImages.IMG_OBJ_FOLDER).createImage();
	
	/* UI Components */
	private Button btnIdDes;
	private Button btnMagStr;
	private Button btnLookGen;
	
	private PerspectiveAdapter perspectiveListener = new PerspectiveAdapter() {
		@Override
		public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {			
			if (perspective.getId().equals("uk.ac.diamond.optid.idSortPerspective")) {
				if (changeId.equals(IWorkbenchPage.CHANGE_RESET)) {
					btnIdDes.setSelection(false);
					btnMagStr.setSelection(false);
					btnLookGen.setSelection(false);
				}
			}
		}
	};

	@Override
	public void createPartControl(Composite parent) {
		// Top-level composite
		Composite mainComposite = new Composite(parent, SWT.NONE);
		mainComposite.setLayout(new GridLayout(1, false));
		mainComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		setupDirField(mainComposite);
		setupOptFileGrp(mainComposite);
		
		getSite().getWorkbenchWindow().addPerspectiveListener(perspectiveListener);
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
				if (isValidDirectory(txtDir.getText())) {
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
				Console.getInstance().newMessage(getWorkbenchPage(), "Working directory set: " + txtDir.getText());
			}
		});
	}
	
	/**
	 * Determines whether given path is a valid directory
	 * @param path
	 * @return true if path is a valid directory
	 */
	//TODO: Move to a Util class
	private boolean isValidDirectory(String path) {
		return path.length() > 0
				& path.charAt(0) == '/'
				& Files.isDirectory(Paths.get(path));
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
		// btnIdDes selection state depends on whether IdDescForm view is open
		if (getWorkbenchPage().findView(IdDescForm.ID) != null) {
			btnIdDes.setSelection(true);
		}
		// Show/hide respective form view
		btnIdDes.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {				
				Button btn = (Button) event.widget;
				if (btn.getSelection()) {
					// Show view
					try {
						getWorkbenchPage().showView(IdDescForm.ID, null, IWorkbenchPage.VIEW_ACTIVATE);
					} catch (PartInitException e) {
						e.printStackTrace();
					}
				} else {
					// Hide view
					IViewPart view = getWorkbenchPage().findView(IdDescForm.ID);
					getWorkbenchPage().hideView(view);
				}
			}
		});
		
		Label lblIdDesStatus = new Label(grpOptFiles, SWT.NONE);
		// Initial label status
		lblIdDesStatus.setText("Not complete");
		lblIdDesStatus.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
		
		/* Magnet Strengths */
		(new Label(grpOptFiles, SWT.NONE)).setText("2.");
		
		btnMagStr = new Button(grpOptFiles, SWT.TOGGLE);
		btnMagStr.setText("Magnet Strengths");
		// Button set to fill width of containing composite
		btnMagStr.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		Label lblMagStrStatus = new Label(grpOptFiles, SWT.NONE);
		// Initial label status
		lblMagStrStatus.setText("Not complete");
		lblMagStrStatus.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
		
		/* Lookup Generator */
		(new Label(grpOptFiles, SWT.NONE)).setText("3.");
		
		btnLookGen = new Button(grpOptFiles, SWT.TOGGLE);
		btnLookGen.setText("Lookup Generator");
		// Button set to fill width of containing composite
		btnLookGen.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		Label lblLookGenStatus = new Label(grpOptFiles, SWT.NONE);
		// Initial label status
		lblLookGenStatus.setText("Not complete");
		lblLookGenStatus.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_RED));
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
		// Dispose acquired images
		if (imgFolder != null) {
			imgFolder.dispose();
		}
		
		super.dispose();
    }
	
}
