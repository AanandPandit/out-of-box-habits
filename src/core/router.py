from PyQt5.QtCore import QObject, pyqtSignal

class Router(QObject):
    navigate_signal = pyqtSignal(str) # Page name
    data_changed = pyqtSignal() # New signal for data sync

    _instance = None

    @staticmethod
    def instance():
        if Router._instance is None:
            Router._instance = Router()
        return Router._instance

    def navigate(self, page_name):
        self.navigate_signal.emit(page_name)
