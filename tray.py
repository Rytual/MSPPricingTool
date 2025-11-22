"""
System tray icon for MSP Pricing Application
Provides menu for manual updates and CSV uploads
"""
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import logging
from tkinter import Tk, filedialog
import webbrowser

from config import config, PORT
from update_db import update_database

logger = logging.getLogger(__name__)

class TrayIcon:
    """System tray icon manager"""

    def __init__(self):
        self.icon = None
        self.running = False

    def create_icon_image(self):
        """Create a simple icon image"""
        # Create a 64x64 image with a dollar sign
        width = 64
        height = 64
        color1 = (0, 120, 212)  # Microsoft blue
        color2 = (255, 255, 255)  # White

        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)

        # Draw a dollar sign
        dc.text((16, 8), "$", fill=color2, font=None)

        return image

    def on_update_api(self, icon, item):
        """Handle Update from API menu item"""
        logger.info("Manual API update triggered from tray")
        try:
            success = update_database(source='api')
            if success:
                icon.notify("Database updated successfully from API", "MSP Pricing Tool")
            else:
                icon.notify("API update failed. Check logs for details.", "MSP Pricing Tool")
        except Exception as e:
            logger.error(f"Error updating from API: {e}", exc_info=True)
            icon.notify(f"Error: {str(e)}", "MSP Pricing Tool")

    def on_upload_csv(self, icon, item):
        """Handle Upload CSV menu item"""
        logger.info("Manual CSV upload triggered from tray")
        try:
            # Create a hidden Tkinter window for file dialog
            root = Tk()
            root.withdraw()  # Hide the main window
            root.attributes('-topmost', True)  # Keep dialog on top

            # Open file dialog
            csv_path = filedialog.askopenfilename(
                title="Select NCE Pricing CSV",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )

            root.destroy()

            if csv_path:
                logger.info(f"CSV selected: {csv_path}")
                success = update_database(source='csv', csv_path=csv_path)

                if success:
                    icon.notify("Database updated successfully from CSV", "MSP Pricing Tool")
                else:
                    icon.notify("CSV import failed. Check logs for details.", "MSP Pricing Tool")
            else:
                logger.info("CSV upload cancelled")

        except Exception as e:
            logger.error(f"Error uploading CSV: {e}", exc_info=True)
            icon.notify(f"Error: {str(e)}", "MSP Pricing Tool")

    def on_open_ui(self, icon, item):
        """Open the web UI in browser"""
        try:
            url = f"http://localhost:{PORT}"
            webbrowser.open(url)
            logger.info(f"Opening web UI: {url}")
        except Exception as e:
            logger.error(f"Error opening UI: {e}", exc_info=True)

    def on_about(self, icon, item):
        """Show about information"""
        from config import APP_NAME, APP_VERSION
        icon.notify(
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Microsoft NCE Pricing Tool for MSPs\n"
            "eMazzanti Technologies",
            "About"
        )

    def on_quit(self, icon, item):
        """Handle quit menu item"""
        logger.info("Quit requested from tray")
        self.running = False
        icon.stop()

    def create_menu(self):
        """Create the tray icon menu"""
        return pystray.Menu(
            item(
                'Open Web UI',
                self.on_open_ui,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            item(
                'Update from API',
                self.on_update_api
            ),
            item(
                'Upload CSV File',
                self.on_upload_csv
            ),
            pystray.Menu.SEPARATOR,
            item(
                'About',
                self.on_about
            ),
            item(
                'Quit',
                self.on_quit
            )
        )

    def run(self):
        """Run the tray icon"""
        try:
            image = self.create_icon_image()
            menu = self.create_menu()

            self.icon = pystray.Icon(
                "msp_pricing",
                image,
                "MSP NCE Pricing Tool",
                menu
            )

            self.running = True
            logger.info("Starting system tray icon")
            self.icon.run()

        except Exception as e:
            logger.error(f"Error running tray icon: {e}", exc_info=True)

    def stop(self):
        """Stop the tray icon"""
        if self.icon:
            self.running = False
            self.icon.stop()

def run_tray_icon():
    """Run tray icon in a separate thread"""
    tray = TrayIcon()
    tray.run()

if __name__ == "__main__":
    run_tray_icon()
