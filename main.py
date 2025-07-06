# Modules
import sys
import re
import minecraft_launcher_lib
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import subprocess
import os
import yaml

# PATHS
minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
CONFIG_PATH = "./assets/config/config.yml"


# Main Window
class mainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi("./assets/GUI/mainWindow.ui", self)
        self.startButton.clicked.connect(self.startAction)
        self.saveButton.clicked.connect(self.saveAction)
        self.minecraftVersions = self.findChild(QComboBox, "minecraftVersions")
        self.populate_versions()
        self.load_config()
        
    def load_config(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            config = {}
        self.usernameText.setText(config.get("last_username", ""))
        self.ramText.setText(config.get("ram_mb", "2048")) 
        last_version = config.get("last_version")
        if last_version and self.minecraftVersions.findText(last_version) != -1:
            self.minecraftVersions.setCurrentText(last_version)
    
    def saveAction(self):
        config = {
            "last_username": self.usernameText.text(),
            "last_version": self.minecraftVersions.currentText(),
            "ram_mb": self.ramText.text()
        }
        QMessageBox.information(self, "Saved", 'Your data is saved on "./assets/config/config.yml".')
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        
    def populate_versions(self):
        version_list = minecraft_launcher_lib.utils.get_version_list()
        for version in version_list:
            if version["type"] == "release":
                self.minecraftVersions.addItem(version["id"])
        
    def startAction(self):
        selected_version = self.minecraftVersions.currentText()
        username = self.usernameText.text()
        pattern = re.compile(r'^[A-Za-z0-9_]{1,32}$')
        if pattern.match(username): 
            ram_mb = self.ramText.text()
            jvm_arguments = [f"-Xmx{ram_mb}M", f"-Xms{ram_mb}M"]
            options = {
                "username": username,
                "uuid": "0",
                "token": "0",
                "jvmArguments": jvm_arguments
            }

            selected_version = self.minecraftVersions.currentText()
            try:
                minecraft_launcher_lib.install.install_minecraft_version(versionid=selected_version, minecraft_directory=minecraft_directory)
                minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(version=selected_version,minecraft_directory=minecraft_directory,options=options)
                subprocess.run(minecraft_command)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        else:
            QMessageBox.critical(self, "Error", "Your username isn't valid.")
            
        
        
        
# Start APP
app = QApplication(sys.argv)
_window = mainWindow()
_window.show()
app.exec_()