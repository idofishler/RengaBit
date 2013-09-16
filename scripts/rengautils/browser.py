#!/usr/bin/env python

from selenium import webdriver
import time
import logging
import sys
import os


class Browser():

    def config_logger(self, logfile=None):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s:\n%(message)s')
        if logfile:
            handler = logging.FileHandler(logfile)
        else:
            handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def osx(self):
        return sys.platform == 'darwin'

    def share_file_via_webRTC(self, file_path):
        """
        Share this file as Renga. Using the rengabit web site http://share.rengabit.com
        The share is based on webRTC and sharefest.me
        """
        file_path = os.path.realpath(file_path)
        if self.osx():
            chromedriver = os.path.expanduser("~/.cg/lib/chromedriver")
        else:
            chromedriver = os.path.realpath("C:\\Rengabit\\lib\\chromedriver.exe")
        os.environ["webdriver.chrome.driver"] = chromedriver
        share_site = "http://share.rengabit.com"
        self._logger.debug("opening page: %s", share_site)
        driver = webdriver.Chrome(chromedriver)
        driver.get(share_site)  # Load page
        file_input = driver.find_element_by_id('files')
        file_input.send_keys(file_path)
        self._logger.debug("Sharing: %s", file_path)
        time.sleep(7)  # wait for the page reload
        share_url = driver.current_url
        if share_url == share_site:
            self._logger.warning("Share isssu: timeout exceeded")
            return False
        self._logger.debug("Sharing at url: %s", share_url)
        return share_url

    def __init__(self, logfile=None):
        self.config_logger(logfile)

if __name__ == '__main__':
    app = Browser()
    app.share_file_via_webRTC(sys.argv[1])
