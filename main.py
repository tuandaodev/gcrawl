import platform
import pickle
import re
import urllib
import requests
import time

from flask import Flask
from flask import request, jsonify
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

def main():
	global driver

	url = "https://drive.google.com/file/d/1rDsfryEXSS-uT8mt9t2Lp7hxf50mpqfH/view";

	options = webdriver.ChromeOptions()
    #options.add_argument("--disable-notifications")
    #options.add_argument("--disable-infobars")
    #options.add_argument("--mute-audio")
	
	#options.add_argument("browser.download.manager.showWhenStarting", False)
	#options.add_argument("browser.download.dir","D:\TestDownload")
	#options.add_argument("browser.helperApps.neverAsk.saveToDisk","application/octet-stream");
	#options.add_argument("browser.helperApps.neverAsk.openFile","application/octet-stream,video/mp4");
	
	options.add_experimental_option('prefs',  {
		"browser.download.default_directory": "D:\TestDownload",
		"browser.download.prompt_for_download": False,
		"browser.download.directory_upgrade": True,
		"browser.download.manager.showWhenStarting": False,
		"browser.helperApps.neverAsk.openFile":"application/octet-stream,video/mp4"
		}
	)

	
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument("user-data-dir=C:\Users\COMPUTER\AppData\Local\Google\Chrome Dev\User Data");

	options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"')
	options.add_argument('--Referer="https://drive.google.com/"')
    #capabilities = DesiredCapabilities.CHROME.copy()
    #capabilities['pageLoadStrategy'] = "none"

	driver = webdriver.Chrome(executable_path="D:/chromedriver.exe", options=options)

	driver.get(url)
	x = re.search(r'(?<="fmt_stream_map",")(.*)(?="])', driver.page_source.encode('utf-8'))
	#x = re.search(r'<video(.*)<\/video>', driver.page_source.encode('utf-8'))
	#x = re.search(r'<video(.*)<\/video>', driver.page_source.encode('utf-8'))
	y = x.group().decode('unicode_escape')
	words = y.split("|")
	z = words[-1]
	print(z)
	
	#testfile = urllib.URLopener()
	#testfile.retrieve(z, "lol.mp4")
	
	driver.get(z)
	
	
	#source_html = driver.page_source
	
	
    #driver.quit()
    #return source_html	
    # filling the form

def firefox():

	start = time.clock()

	global driver

	url = "https://drive.google.com/file/d/1rDsfryEXSS-uT8mt9t2Lp7hxf50mpqfH/view";

	profile = webdriver.FirefoxProfile("C:/Users/COMPUTER/AppData/Roaming/Mozilla/Firefox/Profiles/29jgfkms.default")
	
	profile.set_preference("plugin.state.flash", 0)
	profile.set_preference("plugin.state.java", 0)
	profile.set_preference("media.autoplay.enabled", False)
	
	profile.set_preference("browser.download.folderList", 2)
	profile.set_preference("browser.download.manager.showWhenStarting", False)
	profile.set_preference("browser.download.dir", "D:\\TestDownload")
	profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/octet-stream"+
                           ",application/zip"+
						   ",video/mp4"+
                           ",application/x-rar-compressed"+
                           ",application/x-gzip"+
                           ",application/msword")

	
	#options.add_argument('--headless')
	#profile.add_argument('--no-sandbox')
	#profile.add_argument("--disable-dev-shm-usage")
	#options.add_argument("user-data-dir=C:\Users\COMPUTER\AppData\Local\Google\Chrome Dev\User Data");

	#options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"')
	#profile.add_argument('--Referer="https://drive.google.com/"')
    #capabilities = DesiredCapabilities.CHROME.copy()
    #capabilities['pageLoadStrategy'] = "none"

	driver = webdriver.Firefox(profile, executable_path = 'D:\geckodriver.exe')
	
	driver.get(url)
	
	x = re.search(r'(?<="fmt_stream_map",")(.*)(?="])', driver.page_source.encode('utf-8'))
	#x = re.search(r'<video(.*)<\/video>', driver.page_source.encode('utf-8'))
	#x = re.search(r'<video(.*)<\/video>', driver.page_source.encode('utf-8'))
	y = x.group().decode('unicode_escape')
	words = y.split("|")
	urlDownload = words[-1]
	
	print(urlDownload)
	
	#testfile = urllib.URLopener()
	#testfile.retrieve(urlDownload, "lol.mp4")
	
	#driver.get(urlDownload)
	#with open('D:\TestDownload\file.mp4', 'w') as f:
	#	f.write(driver.page_source)  # write the page source to the file
	#print("Finished")
	
	cookies = driver.get_cookies()
	s = requests.Session()
	for cookie in cookies:
		s.cookies.set(cookie['name'], cookie['value'])
	with s.get(urlDownload, stream=True) as r:
		r.raise_for_status()
		with open("D:\\TestDownload\\2.mp4", 'wb') as f:
			for chunk in r.iter_content(chunk_size=2048):
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
	print("Finished")
	print(time.clock() - start)
	
if __name__ == '__main__':
	firefox()
