from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QComboBox, QVBoxLayout, QWidget
import os
import requests
from vpn_control import connect_vpn, disconnect_vpn

class VPNApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cha VPN")
        self.setGeometry(100, 100, 300, 200)

        self.status_label = QLabel("Disconnected", self)
        self.server_select = QComboBox(self)
        self.connect_btn = QPushButton("Connect", self)
        self.disconnect_btn = QPushButton("Disconnect", self)
        self.ip_label = QLabel("Current IP: Unknown", self)

        layout = QVBoxLayout()
        layout.addWidget(self.server_select)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.disconnect_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.ip_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.connect_btn.clicked.connect(self.handle_connect)
        self.disconnect_btn.clicked.connect(self.handle_disconnect)

        self.load_configs()

    def load_configs(self):
        config_dir = "configs"
        for filename in os.listdir(config_dir):
            if filename.endswith(".conf"):
                self.server_select.addItem(filename)

    def handle_connect(self):
        config_file = self.server_select.currentText()
        if connect_vpn(os.path.abspath(f"configs/{config_file}")):
            self.status_label.setText("Connected")
            self.update_ip()
        else:
            self.status_label.setText("Connection Failed")

    def handle_disconnect(self):
        config_file = self.server_select.currentText().replace(".conf", "")
        if disconnect_vpn(config_file):
            self.status_label.setText("Disconnected")
            self.ip_label.setText("Current IP: Unknown")
        else:
            self.status_label.setText("Disconnection Failed")

    def update_ip(self):
        try:
            ip = requests.get("https://ifconfig.me").text.strip()
            self.ip_label.setText(f"Current IP: {ip}")
        except:
            self.ip_label.setText("Failed to get IP")
