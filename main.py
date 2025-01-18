from PySide6.QtWidgets import  QVBoxLayout, QApplication, QMainWindow, QWidget, QPushButton, QLabel, QHBoxLayout, QCheckBox
from PySide6.QtCore import QSize
import sys

class sign_in_MainWindow_confirm_save_key(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sign In")
        text_label = QLabel("Remembering your VRC Key may put you at risk if your computer is compromised.\n"+
                            "Your password is not stored.\n"+
                            "Do you wish to continue?")
        #Button configuration
        button_yes = QPushButton("Yes")
        button_no = QPushButton("No")
        button_yes.setCheckable(True)
        button_no.setCheckable(True)
        button_yes.clicked.connect(self.button_yes_selected)
        button_no.clicked.connect(self.button_no_selected)

        sign_in_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        button_layout.addWidget(button_yes)
        button_layout.addWidget(button_no)

        sign_in_layout.addWidget(text_label)
        sign_in_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(sign_in_layout)

        self.setCentralWidget(container)
        self.setMinimumSize(QSize(200, 100))

        self.setCentralWidget(container)


    def button_yes_selected(self):
        print("Yes")
        return True
    def button_no_selected(self):
        print("No")
        return False

class sign_in_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sign In")
        #Button configuration
        button_signin = QPushButton("Sign in via VRC Website")
        button_signin.setCheckable(True)
        button_signin.clicked.connect(self.button_login_selected)

        #Checkbox configuration
        self.checkbox_remember_me = QCheckBox("Remember Me")
        self.checkbox_remember_me.stateChanged.connect(self.checkbox_state_changed)
        sign_in_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        button_layout.addWidget(button_signin)

        sign_in_layout.addLayout(button_layout)
        sign_in_layout.addWidget(self.checkbox_remember_me)

        container = QWidget()
        container.setLayout(sign_in_layout)

        self.setCentralWidget(container)
        self.setMinimumSize(QSize(200, 100))

        self.setCentralWidget(container)


    def button_login_selected(self):
        print("Login")
    def checkbox_state_changed(self):
        if self.checkbox_remember_me.isChecked():
            print("Remember Me: Checked")
        else:
            print("Remember Me: Unchecked")

def sign_in_user():
    """
    Creates a dialog box to allow users to log in.
    If the "Remember Me" checkbox is selected, prompt users to acknowledge that the VRChat key is NOT encrypted
    """
    app = QApplication(sys.argv)

    sign_in_window = sign_in_MainWindow()
    sign_in_window.show()

    app.exec_()
    pass

if __name__ == "__main__":
    sign_in_user()
