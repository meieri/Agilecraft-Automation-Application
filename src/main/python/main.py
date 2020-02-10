#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
# The AgileCraft Automation Application
# Automates a large part of the defect creation process.
#
# (C) 2019 Isaak Meier
# Released under MIT License
# email isaakmeier12@gmail.com
# icon made by Eucalyp from www.flaticon.com
# -----------------------------------------------------------

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from script_runner import ScriptRunner
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import webbrowser
import json
import time
import sys
import os

class AppContext(ApplicationContext):           # 1. Subclass ApplicationContext
    # This class makes the whole view using PyQt.
    # It also handles data updates through menu items.
    # When a button is pressed, we get the correct data for the defect
    # from our json data, and create a ScriptRunner object and QThread,
    # which are both then appended to lists persistant in this class.

    def run(self):                              # 2. Implement run()
        # Creates the main window and calls setup functions.
        # Makes top level QMainWindow, and displays it.
        # Sets up app and returns an exit code.
        self.window = QMainWindow()
        self.window.show()
        self.init_defaults()
        self.setup_layout()
        self.setup_buttons()
        self.setup_menus()
        return self.app.exec_()

    def init_defaults(self):
        # Makes some stuff.
        # Attributes:
        #     label (QLabel): A label that displays text to the user.
        #     data (dict): All of the data stored in the json file.
        self.label = QLabel(self.opening_message())
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setMaximumWidth(300)
        self.label.setWordWrap(True)

        self.editor = QTextEdit()
        self.editor_done_button = QPushButton("Done")
        self.editor_done_button.setDefault(True)
        self.editor_done_button.setAutoDefault(False)
        self.editor_done_button.clicked.connect(self.finish_edit_names)
        self.editor_cancel_button = QPushButton("Cancel")
        self.editor_cancel_button.clicked.connect(self.finish_edit_names)
        self.edit_name_mode = False

        self.data_path = self.get_resource('names.json')
        with open(self.data_path) as json_file:
            self.data = json.load(json_file)
        self.chrome_driver_path= self.get_resource('chromedriver') # 2. Set chrome driver path in the script_runner.

        self.currently_running_scripts = []
        self.threads = []

    def setup_layout(self):
        # Creates the layout.
        # Attributes:
        #     widget (QWidget): central widget of the window
        #     top_level_layout (QVBoxLayout): layout on the widget,
        #     owns the buttons and label layout as well as the editor frame
        #     button_frame (QFrame): hideable frame for all the buttons
        #     button_layout (QVBoxLayout): lays out the buttons. Not hideable.
        self.widget = QWidget()
        self.window.setCentralWidget(self.widget)

        self.top_level_layout  = QHBoxLayout()
        buttons_and_label_layout = QVBoxLayout()
        self.editor_frame = QFrame()

        self.button_frame = QFrame()
        self.button_layout = QVBoxLayout()
        self.button_frame.setLayout(self.button_layout)
        buttons_and_label_layout.addWidget(self.button_frame)
        buttons_and_label_layout.addWidget(self.label)

        editor_layout = QVBoxLayout()
        self.editor_frame.setLayout(editor_layout)
        editor_layout.addWidget(self.editor)
        editor_button_layout = QHBoxLayout()
        editor_button_layout.addWidget(self.editor_cancel_button)
        editor_button_layout.addWidget(self.editor_done_button)
        editor_layout.addLayout(editor_button_layout)

        self.top_level_layout.addLayout(buttons_and_label_layout)
        self.top_level_layout.addWidget(self.editor_frame)
        self.editor_frame.hide()
        self.widget.setLayout(self.top_level_layout)

    def setup_buttons(self):
        # Builds all the buttons.

        # Attributes:
        #     data.keys: list of all the names of the buttons from the json data
        #     button (QPushButton): gets connected to the on_button_clicked function.
        for name in self.data.keys():
            if name == "user" or name == "pass":
                continue
            button = QPushButton(name)
            button.clicked.connect(self.on_button_clicked)
            self.button_layout.addWidget(button)

    def setup_menus(self):
        # Creates and adds menu items and connects them to their respective actions.
        menu = self.window.menuBar().addMenu('Settings')
        action = menu.addAction('Set username and password')
        action.triggered.connect(self.update_user_pass)
        action = menu.addAction('Edit names')
        action.triggered.connect(self.begin_edit_names)

    def update_user_pass(self):
        # Creates a popup to change username and password.
        self.exPopup = QWidget()
        popup_layout = QFormLayout()

        self.user_box = QLineEdit()
        user_label = QLabel("Email: ")
        self.user_box.setFixedWidth(200)
        popup_layout.addRow(user_label, self.user_box)

        self.pass_box = QLineEdit()
        pass_label = QLabel("Password: ")
        self.pass_box.setFixedWidth(200)
        self.pass_box.setEchoMode(QLineEdit.Password)
        popup_layout.addRow(pass_label, self.pass_box)

        show_pass_checkbox = QCheckBox("Show password")
        show_pass_checkbox.stateChanged.connect(self.show_pass)
        popup_layout.addWidget(show_pass_checkbox)

        submit_button = QPushButton('Update Credentials')
        submit_button.setDefault(True)
        submit_button.clicked.connect(self.write_user_creds)
        popup_layout.addWidget(submit_button)

        self.exPopup.setLayout(popup_layout)
        self.exPopup.setFixedWidth(400)
        self.exPopup.show()

    def write_names(self, new_names):
        self.data[self.currently_editing_button] = new_names
        with open(self.data_path, 'w') as json_file:
            json.dump(self.data, json_file)

    def show_pass(self, state):
        # Hides and unhides the password text.
        if state == Qt.Checked:
            self.pass_box.setEchoMode(QLineEdit.Normal)
        else:
            self.pass_box.setEchoMode(QLineEdit.Password)

    def write_user_creds(self):
        # Writes new user creds data to json file and closes popup.
        self.data["user"] = self.user_box.text()
        self.data["pass"] = self.pass_box.text()

        with open(self.data_path, 'w') as json_file:
            json.dump(self.data, json_file)

        self.exPopup.close()
        self.label.setText("Your credentials have been successfully updated.")

    def read_creds(self):
        # Reads the user's credentials from the json data.
        # Returns:
        #     dict -- user password dict
        creds = {}
        try:
            creds["user"] = self.data["user"]
            creds["pass"] = self.data["pass"]
        except KeyError as e:
            self.label.setText("Please set your email and password for AgileCraft in the Settings menu.")
            return ""
        if creds["user"] == "":
            self.label.setText("Please set your email and password for AgileCraft in the Settings menu.")
            return ""
        return creds

    def begin_edit_names(self):
        # Allows users to update the names associated with a button.
        # Opens specific name data for a button in a custom editor.
        self.edit_name_mode = True
        self.editor_frame.show()
        self.window.setWindowTitle("Editing...")
        self.label.setText("Edit Mode:\nClick a button to display its names.\nOnly one name per line, please.")
        self.window.setFixedSize(self.top_level_layout.sizeHint())

    def finish_edit_names(self):
        sending_button = self.widget.sender()
        if sending_button.text() == "Done":
            new_names = self.editor.toPlainText().split("\n")
            self.write_names(new_names)
            self.label.setText(f"Successfully updated names for {self.currently_editing_button}")
        else:
            self.label.setText("Finished editing.")
        self.editor.setText("")
        self.editor_frame.hide()
        self.edit_name_mode = False
        self.window.setWindowTitle("Complete.")
        self.window.setFixedSize(self.top_level_layout.sizeHint())

    def open_editor(self, specific_names):
        names_str = "\n".join(specific_names)
        self.editor.setText(names_str)

    def opening_message(self):
        # Gets part of day from hour and makes a welcome message.
        #
        # Returns:
        #     str -- part of day
        hour = datetime.now().hour
        day_part = (
            "morning" if 5 <= hour <= 11
            else
            "afternoon" if 12 <= hour <= 17
            else
            "evening" if 18 <= hour <= 22
            else
            "time to hit the sack.."
        )
        return "Good {0}. Please select your choice.\n".format(day_part)

    def on_button_clicked(self):
        # If any button is clicked this gets called.
        # Gets the name of the button that called this method from the main widget.
        # Makes sure the creds can be read, and gets the specific_names for
        # the script from the json data using the name of the button.
        # Creates a ScriptRunner with specific_names and the button name
        # split into carrier and platform. Moves the ScriptRunner to a new QThread(), objThread.
        # Connects the start of objThread to the method calling execute_script, and
        # connects the end of the objThread  to a cleanup method.
        # Starts the thread, updates the label, and appends both the sr and the QThread to lists.
        sending_button = self.widget.sender()
        text = sending_button.text()
        splitName = text.split()
        carrier = splitName[0]
        platform = splitName[1]
        specific_names = self.data[text]

        # If edit mode is on, send these names to the editor and chill with the rest of the function
        if self.edit_name_mode:
            self.currently_editing_button = text
            self.open_editor(specific_names)
            return
        # Otherwise, read and set credentials
        creds = self.read_creds()
        if creds == "":
            return

        objThread = QThread()
        sr = ScriptRunner(carrier, specific_names, platform, creds, self.chrome_driver_path)
        sr.moveToThread(objThread)
        sr.finished.connect(self.complete_script)
        objThread.started.connect(sr.start)
        objThread.finished.connect(objThread.exit)
        objThread.start()
        self.currently_running_scripts.append(sr)
        self.threads.append(objThread)
        if len(self.currently_running_scripts) == 1:
            self.label.setText("Working on it...")
        else:
            self.label.setText(f"Working on {len(self.currently_running_scripts)} tasks...")
        self.window.setWindowTitle("In progress")

    def complete_script(self, response):
        # Called on completion of execute_script with Success or an error.
        # Removes Qthread and ScriptRunner object from their lists, and updates the label.
        # If there's an error, call that func.
        sr = self.currently_running_scripts.pop(0)
        self.threads.pop(0)
        work_items = len(self.currently_running_scripts)
        if work_items > 1:
            self.label.setText(f"Working on {work_items} tasks")
        elif work_items != 0:
            self.label.setText(f"Working on {work_items} task")

        if response == "Success" and work_items == 0:
            self.label.setText("Done.")
            self.window.setWindowTitle("Complete")
        elif response != "Success":
            self.handle_error(response, sr)

    def handle_error(self, error, scriptrunner):
        # Creates a popup to display the error to the user
        error_popup = QMessageBox(QMessageBox.NoIcon, "Oh no!", f"Oops, we encountered an error on {scriptrunner.carrier} {scriptrunner.platform}. If you don't know why, send this to Isaak: \n\n"+ error, QMessageBox.Ok, self.window)
        error_popup.show()
        error_popup.raise_()

if __name__ == '__main__':
    # Creates and starts the application.
    appctxt = AppContext()       # 1. Instantiate ApplicationContext
    exit_code = appctxt.run()    # 2. Run it
    sys.exit(exit_code)