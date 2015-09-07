package uk.ac.diamond.optid;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.console.ConsolePlugin;
import org.eclipse.ui.console.IConsole;
import org.eclipse.ui.console.IConsoleManager;
import org.eclipse.ui.console.IConsoleView;
import org.eclipse.ui.console.MessageConsole;
import org.eclipse.ui.console.MessageConsoleStream;

public final class Console {
	
	/* Colours to use for console output */
	public static final Color SUCCESS_COLOUR = Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN);
	public static final Color ERROR_COLOUR = Display.getDefault().getSystemColor(SWT.COLOR_RED);	
	
	private static Console instance = null;
	private static String CONSOLE_NAME = "OptID";
	private static String CONSOLE_VIEW_ID = "org.eclipse.ui.console.ConsoleView";
	
	private MessageConsole messageConsole;
	
	private Console() {
		this.messageConsole = new MessageConsole(CONSOLE_NAME, null);
		
		// Register console
		ConsolePlugin plugin = ConsolePlugin.getDefault();
		IConsoleManager consoleManager = plugin.getConsoleManager();
		consoleManager.addConsoles(new IConsole[]{messageConsole});
	}
	
	public static Console getInstance() {
		if (instance == null) {
			instance = new Console();
		}
		
		return instance;
	}
	
	public void newMessage(IWorkbenchPage page, String message) {
		newMessage(page, message, null);
	}
	
	public void newMessage(IWorkbenchPage page, String message, Color textColour) {
		MessageConsoleStream out = messageConsole.newMessageStream();
		out.setColor(textColour);
		out.println(message);

		IConsoleView view = null;
		try {
			view = (IConsoleView) page.showView(CONSOLE_VIEW_ID, null, IWorkbenchPage.VIEW_VISIBLE);
		} catch (PartInitException e) {
			e.printStackTrace();
		}
		
		view.display(messageConsole);
	}

}
