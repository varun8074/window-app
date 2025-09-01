import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QMessageBox, QFrame
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Import your modules (each main() must return a QWidget)
import module1, module2, module3, module4, module5, module6, module7


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("✨ My Multi-Tool App")
        self.setGeometry(300, 200, 1050, 620)

        # Main Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (App Menu)
        sidebar = QVBoxLayout()
        sidebar.setSpacing(12)
        sidebar.setContentsMargins(15, 15, 15, 15)

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
        self.buttons = []

        # Create menu buttons
        for name, (icon_path, func) in self.functions.items():
            btn = QPushButton(f"  {name}")
            btn.setIcon(QIcon(icon_path))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #34495e, stop:1 #2c3e50);
                    color: #ecf0f1;
                    font-size: 14px;
                    text-align: left;
                    padding: 10px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background: #16a085;
                }
                QPushButton:checked {
                    background: #e67e22;
                    color: white;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name, f=func, b=btn: self.select_function(n, f, b))
            sidebar.addWidget(btn)
            self.buttons.append(btn)

        sidebar.addStretch()

        # Sidebar container frame
        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #8e44ad, stop:1 #2980b9);
            }
        """)
        sidebar_frame.setFixedWidth(270)

        # Content area
        self.content_area = QFrame()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_area.setStyleSheet("""
            QFrame {
                background: #f5f6fa;
                border-left: 4px solid #bdc3c7;
            }
        """)

        self.label = QLabel("✨ Select a Functionality")
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 15px; color: #2c3e50;")
        self.content_layout.addWidget(self.label)

        # Add layouts to main
        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(self.content_area)

    def select_function(self, name, func, button):
        """Highlight the selected function in sidebar"""
        self.selected_func = (name, func)
        self.label.setText(name)

        for b in self.buttons:
            b.setChecked(False)
        button.setChecked(True)

        self.run_selected()

    def run_selected(self):
        if not self.selected_func:
            QMessageBox.warning(self, "No Selection", "Please select a function from the menu.")
            return
        name, func = self.selected_func

        # Clear old widgets (except the title label)
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget and widget is not self.label:
                widget.setParent(None)

        try:
            widget = func()  # must return a QWidget
            if isinstance(widget, QWidget):
                widget.setStyleSheet("""
    QWidget {
        background: #f0f2f5;
        border: 1px solid #dcdde1;
        border-radius: 12px;
        padding: 12px;
        color: #2c3e50;
        font-size: 15px;
    }
    QLabel {
        color: #2c3e50;
        font-size: 16px;
        font-weight: bold;
    }
    QPushButton {
        background: #3498db;
        color: white;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 14px;
    }
    QPushButton:hover {
        background: #2980b9;
    }
""")

                self.content_layout.addWidget(widget)
            else:
                QMessageBox.warning(self, "Error", f"{name} did not return a QWidget.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load {name}:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MyApp()
    window.show()
    sys.exit(app.exec())
