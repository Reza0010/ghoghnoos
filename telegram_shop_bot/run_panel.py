import sys
import asyncio
from PyQt6.QtWidgets import QApplication
import qasync

# Ensure the project root is in the Python path
if '.' not in sys.path:
    sys.path.append('.')

from telegram_shop_bot.admin_panel.main_window import MainWindow
from telegram_shop_bot.main import BotApp  # Correctly import from the refactored main.py

async def main():
    """
    Asynchronous main function to initialize the bot components and the admin panel.
    """
    # Instantiate the bot application logic.
    # The application object is needed to send messages from the panel.
    bot_app = BotApp(run_bot=True)

    # The application must be initialized to use its components (e.g., bot object)
    if bot_app.application:
        await bot_app.application.initialize()

    # Create and show the main window of the admin panel
    main_window = MainWindow(bot_app)
    main_window.show()

    # This part is crucial for qasync: it allows the asyncio event loop to process tasks.
    # We don't block here with loop.run_forever() in the async main.
    # The QApplication.exec() will handle the main loop.

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set up the qasync event loop to integrate asyncio with PyQt
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # The main logic is now an async function, so we run it within the event loop
    with loop:
        # Schedule the async main function to run
        loop.create_task(main())

        # Start the Qt event loop. This is a blocking call.
        app.exec()
