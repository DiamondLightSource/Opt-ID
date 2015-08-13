package uk.ac.diamond.optid.views;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.part.ViewPart;

public class IdDescForm extends ViewPart {

	public IdDescForm() {
		// TODO Auto-generated constructor stub
	}

	@Override
	public void createPartControl(Composite parent) {
		// Top-level composite
		Composite mainComposite = new Composite(parent, SWT.NONE);
		mainComposite.setLayout(new GridLayout(1, false));
		mainComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		setupIdParams(mainComposite);
		
		setupMagnetDims(mainComposite);
		
		setupCalParams(mainComposite);
	}

	private void setupCalParams(Composite parent) {
		// Group - Calculation Parameters
		Group grpCalParams = new Group(parent, SWT.NONE);
		grpCalParams.setText("Calculation Parameters");
		grpCalParams.setLayout(new GridLayout(1, false));
		grpCalParams.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Composite - X & Y Container
		Composite comp1 = new Composite(grpCalParams, SWT.NONE);
		comp1.setLayout(new GridLayout(4, false));
		comp1.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// X Start-Stop-Step
		(new Label(comp1, SWT.NONE)).setText("X");
		Text txtXStart = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		Text txtXStop = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		Text txtXStep = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		txtXStart.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtXStop.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtXStep.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Y Start-Stop-Step
		(new Label(comp1, SWT.NONE)).setText("Y");
		Text txtYStart = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		Text txtYStop = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		Text txtYStep = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		txtYStart.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtYStop.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtYStep.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Composite - Steps in S Container
		Composite comp2 = new Composite(grpCalParams, SWT.NONE);
		comp2.setLayout(new GridLayout(2, false));
		comp2.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		// HE magnet dimensions
		(new Label(comp2, SWT.NONE)).setText("Steps in S");
		Text txtStepsS = new Text(comp2, SWT.SINGLE | SWT.BORDER);
		txtStepsS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
	}

	private void setupIdParams(Composite parent) {
		// Group - ID Parameters
		Group grpIdParams = new Group(parent, SWT.NONE);
		grpIdParams.setText("ID Parameters");
		grpIdParams.setLayout(new GridLayout(2, false));
		grpIdParams.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Text (String) Field - Name
		(new Label(grpIdParams, SWT.NONE)).setText("Name");
		Text txtName = new Text(grpIdParams, SWT.SINGLE | SWT.BORDER);
		txtName.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Combo (String) Field - Type
		(new Label(grpIdParams, SWT.NONE)).setText("Type");
		Combo cboType = new Combo(grpIdParams, SWT.READ_ONLY);
		cboType.setItems(new String[] {"PPM AntiSymmetric", "APPLE Symmetric"});
		cboType.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Text (int) Field - Periods
		(new Label(grpIdParams, SWT.NONE)).setText("Periods");
		Text txtPeriods = new Text(grpIdParams, SWT.SINGLE | SWT.BORDER);
		txtPeriods.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		// Text (float) Field - Gap
		(new Label(grpIdParams, SWT.NONE)).setText("Gap");
		Text txtGap = new Text(grpIdParams, SWT.SINGLE | SWT.BORDER);
		txtGap.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Text (float) Field - Interstice
		(new Label(grpIdParams, SWT.NONE)).setText("Interstice");
		Text txtInterstice = new Text(grpIdParams, SWT.SINGLE | SWT.BORDER);
		txtInterstice.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));			
	}
	
	private void setupMagnetDims(Composite parent) {
		// Group - Magnet Dimensions
		Group grpMagDims = new Group(parent, SWT.NONE);
		grpMagDims.setText("Magnet Dimensions");
		grpMagDims.setLayout(new GridLayout(4, false));
		grpMagDims.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		
		// Full magnet dimensions
		(new Label(grpMagDims, SWT.NONE)).setText("Full magnet blocks");
		Text txtFullMagX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtFullMagY = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtFullMagZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		txtFullMagX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtFullMagY.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtFullMagZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// VE magnet dimensions
		(new Label(grpMagDims, SWT.NONE)).setText("VE magnet blocks");
		Text txtVeMagX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtVeMagY = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtVeMagZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		txtVeMagX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtVeMagY.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtVeMagZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		// HE magnet dimensions
		(new Label(grpMagDims, SWT.NONE)).setText("HE magnet blocks");
		Text txtHeMagX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtHeMagY = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtHeMagZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		txtHeMagX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtHeMagY.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtHeMagZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
	}

	@Override
	public void setFocus() {
		// TODO Auto-generated method stub

	}

}
