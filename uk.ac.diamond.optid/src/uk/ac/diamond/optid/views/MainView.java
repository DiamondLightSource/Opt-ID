package uk.ac.diamond.optid.views;

import java.io.File;

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
import uk.ac.diamond.optid.Console;
import uk.ac.diamond.optid.Util;
import uk.ac.diamond.optid.properties.PropertyConstants;

public class MainView extends ViewPart {
	
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(MainView.class);
	
	private Image imgFolder = Activator.getDefault().getWorkbench().getSharedImages().getImageDescriptor(ISharedImages.IMG_OBJ_FOLDER).createImage();
	
	// Store values after perspective closed
	private IPreferenceStore propertyStore;
	
	// Generated file paths
	private String idDescFilePath;
	
	// Open generated file listeners
	private HyperLinkListener idDescLinkListener;
	
	/* UI Components */
	private Button btnIdDes;
	private Button btnMagStr;
	private Button btnLookGen;
	private Hyperlink lblIdDesStatus;
		
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
				setLabelStatusComplete(lblIdDesStatus, idDescFilePath);
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
				String newWorkDir = txtDir.getText();
				
				// Save new directory value to property store
				propertyStore.setValue(PropertyConstants.P_WORK_DIR, newWorkDir);
				
				// Enable form buttons
				btnIdDes.setEnabled(true);
				btnMagStr.setEnabled(true);
				btnLookGen.setEnabled(true);
				
				// If value has actually changed
				if (!newWorkDir.equals(oldWorkDir)) {
					// Inform user
					Console.getInstance().newMessage(getWorkbenchPage(), "Working directory set: " + newWorkDir);
					
					// Resets all file generation form statuses
					idDescFilePath = null;
					setLabelStatusNotComplete(lblIdDesStatus, idDescLinkListener);
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
		
		lblIdDesStatus = new Hyperlink(grpOptFiles, SWT.NONE);
		setLabelStatusNotComplete(lblIdDesStatus, idDescLinkListener);
		
		/* Magnet Strengths */
		(new Label(grpOptFiles, SWT.NONE)).setText("2.");
		
		btnMagStr = new Button(grpOptFiles, SWT.TOGGLE);
		btnMagStr.setText("Magnet Strengths");
		// Button set to fill width of containing composite
		btnMagStr.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		btnMagStr.setEnabled(false);
		
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
		btnLookGen.setEnabled(false);
		
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
		
		super.dispose();
    }
	
	/**
	 * Updates label to status of file generation complete
	 */
	private void setLabelStatusComplete(Hyperlink label, String filePath) {
		label.setText("Open");
		label.setUnderlined(true);
		label.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));
		label.setCursor(new Cursor(Display.getCurrent(), SWT.CURSOR_HAND));

		idDescLinkListener = new HyperLinkListener(idDescFilePath);
		label.addHyperlinkListener(idDescLinkListener);
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
	
}
