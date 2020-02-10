#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# (C) 2019 Isaak Meier
# Released under MIT License
# email isaakmeier12@gmail.com
# icon made by Eucalyp from www.flaticon.com
# -----------------------------------------------------------

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from PyQt5.QtCore import *
import time
import sys
import os

class ScriptRunner(QObject):
    # This runs the selenium automation on a different thread and sends a pyqtSignal when finished.

    # Arguments:
    #     QObject {QThread} -- the thread that that the ScriptRunner runs on.
    finished = pyqtSignal(str)

    def __init__(self, carrier, specific_names, platform, creds, chrome_driver_path):
        # Sets the data up to be used with the script.

        # Arguments:
        #     carrier {str} -- ATT, Sprint, TMO, or Verizon
        #     specific_names {list} -- list of the names to put into the defect
        #     platform {str} -- iOS or Android
        #     creds {dict} -- email and password
        #     chrome_driver_path {str} -- the path of the chromedriver needed for selenium to run chrome
        #     finished{str} -- called on completion
        QObject.__init__(self)
        self.carrier = carrier
        self.specific_names = specific_names
        self.platform = platform
        self.creds = creds
        self.chrome_driver_path= chrome_driver_path

    def start(self):
        # Calls the main execute_script method
        # Calls 'finished' function with the result of the script.
        self.driver = webdriver.Chrome(self.chrome_driver_path)
        try:
            self.execute_script()
            self.finished.emit("Success")
        except Exception as e:
            self.finished.emit(str(e))

    def initial_paths(self):
        # These are the xpaths for all of the dropdowns we need to click. They are put into a list of tuples (dropdown, element) and returned.
        pd_path = '//*[@id="AddDefectForm"]/div[2]/div/div/div[1]/div[1]/div[1]/div[3]/div[1]'
        rb_path = '//*[@id="txtPriority_X"]/li[1]'

        sd_path = '//*[@id="AddDefectForm"]/div[2]/div/div/div[1]/div[1]/div[1]/div[3]/div[3]'
        pb_path = '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[1]/div[3]/div[3]/div/ul/li[2]/a'

        std_path = '//*[@id="AddDefectForm"]/div[2]/div/div/div[1]/div[1]/div[1]/div[3]/div[5]'
        ob_path = '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[1]/div[3]/div[5]/div/ul/li[1]/a'

        state_path = '//*[@id="AddDefectForm"]/div[2]/div/div/div[1]/div[1]/div[1]/div[3]/div[7]'
        ab_path = '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[1]/div[3]/div[7]/div/ul/li[1]/a'

        cd_path = '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[2]/div[1]/div/div[2]'
        bb_path = '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[2]/div[1]/div/div[2]/div/ul/li[1]/a'

        fd_path = '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[2]/div[1]/div/div[4]/div'
        hb_path = '//*[@id="Low"]'

        prd_path = '//*[@id="txtProduct_chosen"]/a'
        artb_path = self.get_art_path()

        id_path = '//*[@id="txtRelease_chosen"]/a'
        p4_path = '//*[@id="txtRelease_chosen"]/div/ul/li[9]'

        team_path = '//*[@id="txtTeamID_chosen"]/a'
        ag_path = '//*[@id="txtTeamID_chosen"]/div/ul/li[2]'

        dropdown_paths = [
            (pd_path, rb_path),
            (sd_path, pb_path),
            (std_path, ob_path),
            (state_path, ab_path),
            (cd_path, bb_path),
            (fd_path, hb_path),
            (prd_path, artb_path),
            (id_path, p4_path),
            (team_path, ag_path)]
        return dropdown_paths

    def final_paths(self):

        rd_path = '//*[@id="txtReleaseVehicle_chosen"]/ul'
        ga_path = '//*[@id="txtReleaseVehicle_chosen"]/div/ul/li[3]'

        platform_dropdown_path = '//*[@id="txt_C58_CDrop1_chosen"]/a'
        plat_but_path = ""
        if self.platform == 'iOS':
            plat_but_path = '//*[@id="txt_C58_CDrop1_chosen"]/div/ul/li[3]'
        if self.platform == 'Android':
            plat_but_path = '//*[@id="txt_C58_CDrop1_chosen"]/div/ul/li[2]'

        phase_path= '//*[@id="txt_C58_CDrop2_chosen"]/a'
        jv_path= '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[2]/table/tbody/tr[7]/td[2]/div/div/div/div/ul/li[3]'

        solution_path = '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[2]/table/tbody/tr[8]/td[2]/div/div/div/a'
        standard_path = '/html/body/div[17]/form/div[2]/div/div/div[1]/div[1]/div[2]/table/tbody/tr[8]/td[2]/div/div/div/div/ul/li[2]'

        dropdown_paths = [
            (rd_path, ga_path),
            (platform_dropdown_path, plat_but_path),
            (phase_path, jv_path),
            (solution_path, standard_path)]
        return dropdown_paths

    def login(self):
        email_input  = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.NAME,'sso_id')))
        pass_input = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.NAME,'sso_password')))
        email_input.send_keys(self.creds["user"])
        pass_input.send_keys(self.creds["pass"])
        login_btn  = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.NAME,'btnLogin')))
        login_btn.click()
        header = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID,"header-menu-strSubNavButtons")))
        create_btn = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME,"btn-secondary")))
        self.driver.execute_script("arguments[0].click();", create_btn)

    def entitle(self):
        defect_title = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID,'txtDefect')))
        defect_title.send_keys(f'[RP] [{self.carrier}] [{self.platform}]')

    def select_dropdowns(self, paths):
        for path in paths:
            dropdown = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, path[0])))
            dropdown.click()
            button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, path[1])))
            button = self.driver.find_element_by_xpath(path[1])
            button.click()
            if path[0] == '//*[@id="txtProduct_chosen"]/a' or path[0] == '//*[@id="txtRelease_chosen"]/a':
                # These two paths will display a loading overlay that will intercept clicks unless we wait for it.
                time.sleep(2)

    def get_art_path(self):
        # Get correct xpath based on carrier.
        if self.carrier == 'ATT':
            return '//*[@id="txtProduct_chosen"]/div/ul/li[3]'
        if self.carrier == 'Sprint':
            return '//*[@id="txtProduct_chosen"]/div/ul/li[6]'
        if self.carrier == 'TMO':
            return '//*[@id="txtProduct_chosen"]/div/ul/li[8]'
        if self.carrier == 'Verizon':
            return '//*[@id="txtProduct_chosen"]/div/ul/li[9]'

    def fill_description(self):
        # switch to iframe
        self.driver.switch_to.frame(0)
        desc_textarea = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body')))
        desc_textarea.send_keys("Version:\nDevice Info:\nDefect Video URL:\nhttps://crosscarrier.atlassian.net/wiki/spaces/JV/pages/278659307/Videos+for+Certification+Testing+and+Defect")
        self.driver.switch_to.default_content()

    def scroll_to_bottom(self):
        # scroll to bottom of doc, hard
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = self.driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        time.sleep(1)

    def put_names(self):
        notify_textarea = self.driver.find_element_by_xpath('//*[@id="txtNotifyTagIt"]/ul[1]/li/input')
        for name in self.specific_names:
            notify_textarea.send_keys(name + Keys.TAB)

    def execute_script(self):
        # The meat of the script.

        # Raises:
        #     e: Will most likely be an ElementClickInterceptedException or a NoSuchElementException.
        #        We just display this message to the user, because if something goes wrong it means the site's code has changed and some xpath needs to be updated.
        try:
            self.driver.get(url='https://xci.agilecraft.com/login?ReturnUrl=%2fDefectsGrid%3fBugID%3d&BugID=#')
            self.login()
            self.entitle()
            self.select_dropdowns(self.initial_paths())
            self.fill_description()
            self.scroll_to_bottom()
            self.select_dropdowns(self.final_paths())
            self.put_names()
        except Exception as e:
            raise e


