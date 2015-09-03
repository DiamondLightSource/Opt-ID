package uk.ac.diamond.optid;

import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.console.ConsolePlugin;
import org.eclipse.ui.console.IConsole;
import org.eclipse.ui.console.IConsoleManager;
import org.eclipse.ui.console.IConsoleView;
import org.eclipse.ui.console.MessageConsole;
import org.eclipse.ui.console.MessageConsoleStream;

public final class Console {
	
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
		MessageConsoleStream out = messageConsole.newMessageStream();
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
