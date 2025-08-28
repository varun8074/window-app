import sys, threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QTextEdit, QMessageBox, QFrame
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Import your modules
import module1, module2, module3, module4, module5, module6, module7

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Multi-Tool App")
        self.setGeometry(300, 200, 950, 550)

        # Main Layout
        main_layout = QHBoxLayout(self)

        # Sidebar (App Menu)
        sidebar = QVBoxLayout()
        sidebar.setSpacing(12)

        # Function map with labels + icons
        self.functions = {
            "Key Counter": ("icons/book.svg", module1.main),
            "Window Minimizer / Closer": ("icons/monitor.svg", module2.main),
            "Auto Mouse Clicker": ("icons/mouse-pointer.svg", module3.main),
            "Mouse Recorder & Replayer": ("icons/play-circle.svg", module4.main),
            "Scroll Counter": ("icons/image.png", module5.main),
            "Window Transparency Setter": ("icons/droplet.svg", module6.main),
            "Long Right-Click Action": ("icons/zap.svg", module7.main),
        }

        self.selected_func = None

        # Create menu buttons
        for name, (icon_path, func) in self.functions.items():
            btn = QPushButton(f"  {name}")
            btn.setIcon(QIcon(icon_path))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: #2C3E50;
                    color: #ecf0f1;
                    font-size: 14px;
                    text-align: left;
                    padding: 10px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: #34495e;
                }
                QPushButton:checked {
                    background: #3498db;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name, f=func, b=btn: self.select_function(n, f, b))
            sidebar.addWidget(btn)

        sidebar.addStretch()

        # Sidebar container frame (for background color)
        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setStyleSheet("background: #2C3E50;")
        sidebar_frame.setFixedWidth(250)

        # Content area
        content_layout = QVBoxLayout()
        self.label = QLabel("Select a Functionality")
        self.label.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px; color: #2C3E50;")
        content_layout.addWidget(self.label)

        self.run_button = QPushButton("▶ Run")
        self.run_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_button.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 14px;
                border-radius: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        self.run_button.clicked.connect(self.run_selected)
        content_layout.addWidget(self.run_button)

        # Log output
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            QTextEdit {
                background: #2a2018;
                border: 1px solid #bdc3c7;
                border-radius: 10px;
                font-family: Consolas;
                font-size: 13px;
                padding: 8px;
            }
        """)
        content_layout.addWidget(self.log)

        # Add layouts to main
        main_layout.addWidget(sidebar_frame)
        main_layout.addLayout(content_layout)

    def select_function(self, name, func, button):
        """Highlight the selected function in sidebar"""
        self.selected_func = (name, func)
        self.label.setText(name)

        # Uncheck all other buttons
        for i in range(self.layout().itemAt(0).widget().layout().count()):
            w = self.layout().itemAt(0).widget().layout().itemAt(i).widget()
            if isinstance(w, QPushButton):
                w.setChecked(False)
        button.setChecked(True)

    def run_selected(self):
        if not self.selected_func:
            QMessageBox.warning(self, "No Selection", "Please select a function from the menu.")
            return
        name, func = self.selected_func
        self.log.append(f"▶ Running: {name}")
        t = threading.Thread(target=func, daemon=True)
        t.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MyApp()
    window.show()
    sys.exit(app.exec())
