package uk.ac.diamond.optid.views;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
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
		
		(new Label(mainComposite, SWT.NONE)).setText("Workspace Directory");
		Text txtDir = new Text(mainComposite, SWT.SINGLE | SWT.BORDER);
		txtDir.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
	}

	@Override
	public void setFocus() {		
	}

}
