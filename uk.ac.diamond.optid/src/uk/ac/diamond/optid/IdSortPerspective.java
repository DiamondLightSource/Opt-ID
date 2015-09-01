package uk.ac.diamond.optid;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;
import org.eclipse.ui.IViewLayout;

public class IdSortPerspective implements IPerspectiveFactory {
	
	static final String ID = "uk.ac.diamond.optid.idSortPerspective";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		layout.setEditorAreaVisible(true);
		
		// ID Optimisation 'Main' view
		layout.addStandaloneView("uk.ac.diamond.optid.mainView", true, IPageLayout.LEFT, 0.25f, IPageLayout.ID_EDITOR_AREA);
		IViewLayout mainViewLayout = layout.getViewLayout("uk.ac.diamond.optid.mainView");
		mainViewLayout.setCloseable(false);
		mainViewLayout.setMoveable(false);
		
		// Data manipulation tools
		IFolderLayout rightFolder = layout.createFolder("rightFolder", IPageLayout.RIGHT, 0.6f, IPageLayout.ID_EDITOR_AREA);
		rightFolder.addView("org.dawb.workbench.views.dataSetView");
		rightFolder.addView("org.dawb.workbench.plotting.views.toolPageView.2D");
		rightFolder.addView("org.dawb.common.ui.views.headerTableView");
		
		// Progress & Console views
		IFolderLayout bottomFolder = layout.createFolder("bottomFolder", IPageLayout.BOTTOM, 0.7f, IPageLayout.ID_EDITOR_AREA);
		bottomFolder.addView("org.eclipse.ui.views.ProgressView");
		bottomFolder.addView("org.eclipse.ui.console.ConsoleView");
		
		// Optimisation file generation forms
		layout.addStandaloneViewPlaceholder("uk.ac.diamond.optid.idDescForm", IPageLayout.LEFT, 0.4f, IPageLayout.ID_EDITOR_AREA, false);
	}

}
