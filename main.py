import platform
import pickle
import re
import urllib
import urllib2
import requests
import time
import urlparse
import sys

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

	url = "https://drive.google.com/file/d/1rDsfryEXSS-uT8mt9t2Lp7hxf50mpqfH/view"

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
def get_video():

	start = time.clock()

	#cookie_string = "SID=NgeYOTwjofd58AGxXI_7MMEFjofP7_FB163aH9OFQ4uB7AFlpCALhBpsVonNNM3yw3hS1w.;HSID=AwF4AAd1uQ5w3Vea2;SSID=ACpvM-QH8WJebhM8b;APISID=Ky2l7JyC6itSvSyP/AutQup09Kw7MoySLt;SAPISID=nHWlb0yEMtadASbf/A2AAE8NCLnboPu7hh;NID=180=HDVzHVHRxcTwCCw4F11hv3UahG-v8pKAb9Mi1evmRkg1FzBndzDcdYGKnqU4NPyELxe5NpB4smtxLWRVMXYNiru8rpmDUMwllUhjpeWQWtrz68L1HI4V-zvHN0InAcusMlbij9F_k9Zij3CtHncw0KDb_vCeLLRbPisYZ3zpH6_Co8zXj05kkcKU701rZaHmltbiqNydVQ;DRIVE_STREAM=Csb25Trh83A;1P_JAR=2019-4-3-15;SIDCC=AN0-TYu9m8jJN_PGjDcSLzNfj4ksYqkFAQv8wGeVX0f8-HWPHLUSPfOpw2QIGGrXgqiN5ES2;"

	cookie_string = firefox()

	videoid = "1mI4CVGQ0shx7R-k9JLFar5sLLFSRaVJv"
	url = "https://drive.google.com/e/get_video_info?docid=" + videoid

	opener = urllib2.build_opener()
	opener.addheaders.append(('Cookie', cookie_string))
	data = opener.open(url).read()
	info =  urlparse.parse_qs(data)
	info = info["fmt_stream_map"][0]

	paras = info.split('|')

	downloadLink = ""
	for word in paras:
		if (word.find("itag=22") != -1):
			downloadLink = word.split(',')

	finalDownloadURL = downloadLink[0]
	print(finalDownloadURL)	

	return

	s = requests.Session()
	
	cookies_arr = cookie_string.split(';')
	for cookie_string in cookies_arr:
		cookie_arr = cookie_string.split('=')
		if len(cookie_arr) > 1:
			s.cookies.set(cookie_arr[0], cookie_arr[1])

	with s.get(finalDownloadURL, stream=True) as r:
		r.raise_for_status()
		total_length = r.headers.get('content-length')
		dl = 0
		if total_length is None:
			with open("D:\\TestDownload\\2.mp4", 'wb') as f:
				for chunk in r.iter_content(chunk_size=2048):
					if chunk:
						f.write(chunk)
		else:
			with open("D:\\TestDownload\\2.mp4", 'wb') as f:
				for chunk in r.iter_content(chunk_size=2048):
					if chunk:
						dl += len(chunk)
						f.write(chunk)
						done = 100 * dl / int(total_length)
						sys.stdout.write("\r[%s%s] %s%%" % ('=' * done, ' ' * (100-done), done))
	print("")
	print("Finished")
	print(time.clock() - start + "s")

def firefox():

	start = time.clock()

	global driver

	videoid = "1rDsfryEXSS-uT8mt9t2Lp7hxf50mpqfH";
	url = "https://drive.google.com/file/d/" + videoid + "/view";

	#May Nha
	profile = webdriver.FirefoxProfile("C:/Users/COMPUTER/AppData/Roaming/Mozilla/Firefox/Profiles/29jgfkms.default")
	#May TMA
	#profile = webdriver.FirefoxProfile("C:/Users/DMTUAN/AppData/Roaming/Mozilla/Firefox/Profiles/7narmi87.default-1548039786631")

	profile.set_preference("plugin.state.flash", 0)
	profile.set_preference("plugin.state.java", 0)
	profile.set_preference("media.autoplay.enabled", False)
	
	#profile.set_preference("browser.download.folderList", 2)
	#profile.set_preference("browser.download.manager.showWhenStarting", False)
	#profile.set_preference("browser.download.dir", "D:\\TestDownload")
	#profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
    #                       "application/octet-stream"+
    #                       ",application/zip"+
	#						   ",video/mp4"+
    #                       ",application/x-rar-compressed"+
    #                       ",application/x-gzip"+
    #                       ",application/msword")

	
	#options.add_argument('--headless')
	#profile.add_argument('--no-sandbox')
	#profile.add_argument("--disable-dev-shm-usage")
	#options.add_argument("user-data-dir=C:\Users\COMPUTER\AppData\Local\Google\Chrome Dev\User Data");

	#options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"')
	#profile.add_argument('--Referer="https://drive.google.com/"')
    #capabilities = DesiredCapabilities.CHROME.copy()
    #capabilities['pageLoadStrategy'] = "none"

	driver = webdriver.Firefox(profile, executable_path = 'geckodriver.exe')
	
	#url = "https://drive.google.com/e/get_video_info?docid=" + videoid;

	driver.get(url)

	cookies = driver.get_cookies()
	cookie_string = ""
	for cookie in cookies:
		cookie_string = cookie_string + cookie['name']  + "=" + cookie['value'] + ";"

	print(cookie_string)

	return cookie_string
	
	x = re.search(r'(?<="fmt_stream_map",")(.*)(?="])', driver.page_source.encode('utf-8'))
	#x = re.search(r'<video(.*)<\/video>', driver.page_source.encode('utf-8'))
	#x = re.search(r'<video(.*)<\/video>', driver.page_source.encode('utf-8'))
	y = x.group().decode('unicode_escape')
	words = y.split("|")
	urlDownload = words[-1]
	
	print(urlDownload)
	
	cookies = driver.get_cookies()
	s = requests.Session()
	cookie_string = ""
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
	#get_video()
