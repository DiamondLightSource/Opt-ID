package uk.ac.diamond.optid.views;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.part.ViewPart;

public class IdDescForm extends ViewPart {
	
	static final String ID = "uk.ac.diamond.optid.idDescForm";

	public IdDescForm() {
	}

	@Override
	public void createPartControl(Composite parent) {
		// Top-level composite
		Composite mainComposite = new Composite(parent, SWT.NONE);
		mainComposite.setLayout(new GridLayout(1, false));
		mainComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		
		// Create groups for each category of inputs
		setupIdParams(mainComposite);
		setupMagnetDims(mainComposite);
		setupCalParams(mainComposite);
		setupAppleSymOnlyParams(mainComposite);
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
		
		// Full magnet block
		(new Label(grpMagDims, SWT.NONE)).setText("Full");
		Text txtFullX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtFullZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtFullS = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		txtFullX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtFullZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtFullS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// VE magnet block
		(new Label(grpMagDims, SWT.NONE)).setText("VE");
		Text txtVeX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtVeZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtVeS = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		txtVeX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtVeZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtVeS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// HE magnet block
		(new Label(grpMagDims, SWT.NONE)).setText("HE");
		Text txtHeX = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtHeZ = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		Text txtHeS = new Text(grpMagDims, SWT.SINGLE | SWT.BORDER);
		txtHeX.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtHeZ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtHeS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
	}

	private void setupCalParams(Composite parent) {
		// Group - Calculation Parameters
		Group grpCalParams = new Group(parent, SWT.NONE);
		grpCalParams.setText("Calculation Parameters");
		grpCalParams.setLayout(new GridLayout(1, false));
		grpCalParams.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Composite - X & Z Container
		Composite comp1 = new Composite(grpCalParams, SWT.NONE);
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
		
		// X Start-Stop-Step
		(new Label(comp1, SWT.NONE)).setText("X");
		Text txtXStart = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		Text txtXStop = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		Text txtXStep = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		txtXStart.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtXStop.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtXStep.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Z Start-Stop-Step
		(new Label(comp1, SWT.NONE)).setText("Z");
		Text txtZStart = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		Text txtZStop = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		Text txtZStep = new Text(comp1, SWT.SINGLE | SWT.BORDER);
		txtZStart.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtZStop.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		txtZStep.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Composite - Steps in S Container
		Composite comp2 = new Composite(grpCalParams, SWT.NONE);
		comp2.setLayout(new GridLayout(2, false));
		comp2.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		// Steps in S
		(new Label(comp2, SWT.NONE)).setText("Steps in S");
		Text txtStepsS = new Text(comp2, SWT.SINGLE | SWT.BORDER);
		txtStepsS.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
	}
	
	private void setupAppleSymOnlyParams(Composite parent) {
		// Group - Apple Symmetric only parameters
		Group grpAppleSymOnly = new Group(parent, SWT.NONE);
		grpAppleSymOnly.setText("APPLE Symmetric only");
		grpAppleSymOnly.setLayout(new GridLayout(2, false));
		grpAppleSymOnly.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		
		// Text (float) Field - End gap
		(new Label(grpAppleSymOnly, SWT.NONE)).setText("End gap");
		Text txtEndGap = new Text(grpAppleSymOnly, SWT.SINGLE | SWT.BORDER);
		txtEndGap.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		
		// Text (float) Field - Phasing gap
		(new Label(grpAppleSymOnly, SWT.NONE)).setText("Phasing gap");
		Text txtPhasingGap = new Text(grpAppleSymOnly, SWT.SINGLE | SWT.BORDER);
		txtPhasingGap.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		// Text (float) Field - Clamp cut
		(new Label(grpAppleSymOnly, SWT.NONE)).setText("Clamp cut");
		Text txtClampCut = new Text(grpAppleSymOnly, SWT.SINGLE | SWT.BORDER);
		txtClampCut.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
	}
	
	@Override
	public void setFocus() {
	}

}
