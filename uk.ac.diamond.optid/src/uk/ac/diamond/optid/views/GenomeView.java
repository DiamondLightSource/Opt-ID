package uk.ac.diamond.optid.views;

import java.util.ArrayList;
import java.util.Arrays;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.IJobChangeEvent;
import org.eclipse.core.runtime.jobs.ISchedulingRule;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.core.runtime.jobs.JobChangeAdapter;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.progress.UIJob;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.optid.Activator;
import uk.ac.diamond.optid.properties.PropertyConstants;
import uk.ac.diamond.optid.util.Util;

public class GenomeView extends ViewPart {
	
	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(GenomeView.class);

	private static final String[] TABLE_COL_LABELS = {"Time", "Cost", "Processed"};
	private static final int REFRESH_INTERVAL = 180000; // 3 minutes
	
	private IPreferenceStore propertyStore;
	private Action refreshAction = new RefreshAction();
	private Job fetchGenomeJob = new FetchGenomesJob();
	private UIJob displayGenomesJob = new DisplayGenomesJob();
	
	private String genomeDir;
	private ArrayList<String> genomeInfo;

	private Table table;
	
	// Monitor changes to properties in the perspective-wide property store
	private IPropertyChangeListener propertyChangeListener = new IPropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent event) {
			// New genome directory, i.e. new cluster job started
			if (event.getProperty().equals(PropertyConstants.P_GENOME_DIR)) {
				genomeDir = (String) event.getNewValue(); // Update value
				fetchGenomeJob.schedule(); // Schedule job to update table
			}
		}
	};
	
	private ISchedulingRule rule = new ISchedulingRule() {
		@Override
		public boolean isConflicting(ISchedulingRule rule) {
			return rule == this;
		}

		@Override
		public boolean contains(ISchedulingRule rule) {
			return rule == this;
		}
	};
	
	@Override
    public void init(IViewSite site) throws PartInitException {
		super.init(site);
		
		// Ensures jobs do not run concurrently
		fetchGenomeJob.setRule(rule);
		displayGenomesJob.setRule(rule);
		
		// Immediately schedule UIJob to display genomes in table after
		// they have been fetched
		fetchGenomeJob.addJobChangeListener(new JobChangeAdapter() {
			@Override
			public void done(IJobChangeEvent event) {
				super.done(event);
				displayGenomesJob.schedule();
			}
		});
		
		propertyStore = Activator.getDefault().getPreferenceStore();
		propertyStore.addPropertyChangeListener(propertyChangeListener);
		// Get existing genome directory
		genomeDir = propertyStore.getString(PropertyConstants.P_GENOME_DIR);
	}

	@Override
	public void createPartControl(Composite parent) {
		createActionBar();
		setupTable(parent);
		startFetchGenomeService();
	}
	
	/**
	 * Setup table that fills entire view
	 * @param parent
	 */
	private void setupTable(Composite parent) {
		// Entire row selectable and only one row can be selected at a time
		table = new Table(parent, SWT.BORDER | SWT.FULL_SELECTION);
		table.setLinesVisible(true);
		table.setHeaderVisible(true);
		
		// Create columns
		for (int i = 0; i < TABLE_COL_LABELS.length; i++) {
			TableColumn column = new TableColumn(table, SWT.NONE);
			column.setText(TABLE_COL_LABELS[i]);
			column.pack();
		}		
	}
	
	/**
	 * Creates action bar with refresh action
	 */
	private void createActionBar() {
		IActionBars bars = getViewSite().getActionBars();
		bars.getToolBarManager().add(refreshAction);
	}
	
	/**
	 * Determines whether cluster job is currently executing
	 * @return running
	 */
	private boolean isRunning() {
		return !genomeDir.equals("");
	}
	
	/**
	 * Start fetch genome data job
	 */
	private void startFetchGenomeService() {
		if (isRunning()) {
			fetchGenomeJob.schedule();
		}
	}

	@Override
	public void setFocus() {
	}
	
	/**
	 * Fetch list of genomes in <b>genomeDir</b>
	 *
	 */
	class FetchGenomesJob extends Job {

		public FetchGenomesJob() {
			super("Fetching genomes");
		}

		@Override
		protected IStatus run(IProgressMonitor monitor) {
			genomeInfo = Util.runListGenomes(genomeDir);
			schedule(REFRESH_INTERVAL); // Schedule next fetch
			
			return Status.OK_STATUS;
		}
		
	}
	
	/**
	 * Display genome data in table
	 *
	 */
	class DisplayGenomesJob extends UIJob {

		public DisplayGenomesJob() {
			super("Displaying genomes");
		}

		@Override
		public IStatus runInUIThread(IProgressMonitor monitor) {
			table.removeAll();
			fillTable();
			packTable();
			updateContentDescription();
			
			return Status.OK_STATUS;
		}
		
		/**
		 * Each genome string parsed and displayed in corresponding column
		 */
		private void fillTable() {
			for (int i = 0; i < genomeInfo.size(); i++) {
				String genome = genomeInfo.get(i);
				String data[] = genome.split("\\s+");
				
				String time = data[0] + " " + data[1];
				String cost = getCost(data[2]);
				
				TableItem item = new TableItem(table, SWT.NONE);
				item.setText(0, time);
				item.setText(1, cost);
				item.setText(2, "No");
			}
		}
		
		/**
		 * Updates content description to show number of genomes displayed in the table
		 */
		private void updateContentDescription() {
			int numGenomes = genomeInfo.size();
			if (numGenomes == 1) {
				setContentDescription("Showing 1 genome");
			} else {
				setContentDescription("Showing " + numGenomes + " genomes");
			}
		}
		
		/**
		 * Packs table by reducing width of each column to the minimum size
		 * to display all text content without obstruction
		 */
		private void packTable() {
			for (int i = 0; i < TABLE_COL_LABELS.length; i++) {
				table.getColumn(i).pack();
			}
		}
		
		/**
		 * Parses genome filename to get the cost part
		 * @param genomeFileName
		 * @return cost
		 */
		private String getCost(String genomeFileName) {
			return genomeFileName.substring(0, genomeFileName.indexOf('_'));
		}
		
	}
	
	/**
	 * Schedules fetch job
	 *
	 */
	class RefreshAction extends Action {
		
		RefreshAction() {
			setText("Refresh table");
			setImageDescriptor(Activator.getDefault().getWorkbench().getSharedImages()
					.getImageDescriptor(ISharedImages.IMG_ELCL_SYNCED));
		}

		public void run() {
			startFetchGenomeService();
		}
		
	}

}
