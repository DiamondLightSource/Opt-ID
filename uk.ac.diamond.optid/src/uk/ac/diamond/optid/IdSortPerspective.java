package uk.ac.diamond.optid;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;

public class IdSortPerspective implements IPerspectiveFactory {
	
	static final String ID = "uk.ac.diamond.optid.idSortPerspective";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);
		
		IFolderLayout left = layout.createFolder("idDescForm", IPageLayout.LEFT, 0.3f, editorArea);
		left.addView("uk.ac.diamond.optid.idDescForm");
		IViewLayout vLayout = layout.getViewLayout("uk.ac.diamond.optid.idDescForm");
		vLayout.setCloseable(false);	
	}

}
