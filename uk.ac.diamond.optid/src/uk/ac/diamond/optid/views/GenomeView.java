package uk.ac.diamond.optid.views;

import java.util.ArrayList;
import java.util.Arrays;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.ui.part.ViewPart;

public class GenomeView extends ViewPart {

	private static final String[] TABLE_COL_LABELS = {"Time", "Identifier", "Cost", "INP", "HDF5"};
	
	private static final ArrayList<String> GENOME_TIMES = new ArrayList<>(Arrays.asList(new String[] {
			"10:45:35",
			"10:48:56",
			"10:52:23",
			"10:55:34",
			"10:58:52",
			"11:02:10",
			"11:05:30",
			"11:08:50",
			"11:12:12",
			"11:15:26",
			"11:18:50",
			"11:22:06",
			"11:25:24"
	}));
	
	private static final ArrayList<String> GENOME_ID = new ArrayList<>(Arrays.asList(new String[] {
			"d3d34d4d50fc",
			"84afc6344363",
			"0b5b6b56865c",
			"a900ff5073c2",
			"2af7134db74b",
			"2d09f034c71b",
			"cf7d6e73aa3b",
			"67d6cc23d90e",
			"6dea5706f3e7",
			"b7a479b917e2",
			"db4e687c7977",
			"6a94bfa9052c",
			"9bb683e6dd83"
	}));
	
	private static final ArrayList<String> GENOME_COST = new ArrayList<>(Arrays.asList(new String[] {
		"8.09236889e-06",
		"7.09123106e-06",
		"5.61277924e-06",
		"4.97448650e-06",
		"4.63226611e-06",
		"4.42992081e-06",
		"4.03510637e-06",
		"3.53861157e-06",
		"3.20790518e-06",
		"2.82621864e-06",
		"2.80814683e-06",
		"2.73036443e-06",
		"2.52544920e-06"
	}));

	@Override
	public void createPartControl(Composite parent) {
		Table table = new Table(parent, SWT.MULTI | SWT.BORDER | SWT.FULL_SELECTION);
		table.setLinesVisible(true);
		table.setHeaderVisible(true);
		for (int i = 0; i < TABLE_COL_LABELS.length; i++) {
			TableColumn column = new TableColumn(table, SWT.NONE);
			column.setText(TABLE_COL_LABELS[i]);
			column.pack();
		}
		
		for (int i = 0; i < GENOME_COST.size(); i++) {
			TableItem item = new TableItem(table, SWT.NONE);
			item.setText(0, GENOME_TIMES.get(i));
			item.setText(1, GENOME_ID.get(i));
			item.setText(2, GENOME_COST.get(i));
		}
		
		table.getItem(1).setText(3, "Open");
		table.getItem(1).setText(4, "Open");
		table.getItem(1).setForeground(3, Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));
		table.getItem(1).setForeground(4, Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));

		
		table.getItem(5).setText(3, "Open");
		table.getItem(5).setText(4, "Open");
		table.getItem(5).setForeground(3, Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));
		table.getItem(5).setForeground(4, Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));


		for (int i = 0; i < TABLE_COL_LABELS.length; i++) {
			table.getColumn(i).pack();
		}
	}

	@Override
	public void setFocus() {
	}

}
