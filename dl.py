# -*- coding: utf-8 -*-
import os, colorama
from apiclient import errors
from colorama import init,Fore,Back,Style
from termcolor import colored
from apiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from concurrent.futures import ThreadPoolExecutor
import io
import os
import sys
import re
import platform
import pickle
import urllib
import urllib2
import requests
import time
import urlparse
import logging

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'

def main():
    """
    Download folder content from google dirve without zipping.
    """

    # use Colorama to make Termcolor work on Windows too
    init()
    # now, to clear the screen
    cls()

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    print colored('* Directory to save - by default it will be current directory', 'blue')
    location = raw_input("   - Path: ")
    while not location:
        location = raw_input("   - Path: ")
    type(location)
    print colored('* Sub-directory: ', 'blue')
    folder_name = raw_input("   - Path: ")
    while not folder_name:
        folder_name = raw_input("   - Path: ")
    type(folder_name)
    print colored('* GDrive Folder/File ID: ','blue')
    folder_id = raw_input("   - ID  : ")
    while not folder_id:
        folder_id = raw_input("   - ID  : ")
    type(folder_id)

    #if len(sys.argv) > 2:
        #location = unicode(sys.argv[2], 'utf-8')
    if location[-1] != '/':
        location += '/'
    try:
        folder = service.files().list(
                q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(folder_name),
                fields='files(id)').execute()
        folder_name = unicode(folder_name, 'utf-8')
        download_folder(service, folder_id, location, folder_name)

    except errors.HttpError, error:
        print 'An error occurred: {}'.format(error)

def download_folder(service, folder_id, location, folder_name):
    folder_path = r"{}{}".format(location, folder_name)
    print(folder_path)
    if not os.path.exists(r"{}".format(folder_path)):
        os.makedirs(r"{}".format(folder_path))
    location += folder_name + '/'

    result = []
    files = service.files().list(
            q="'{}' in parents".format(folder_id),
            fields='files(id, name, mimeType, size)').execute()
    result.extend(files['files'])
    result = sorted(result, key=lambda k: k[u'name'])

    total = len(result)
    if total == 0:
        print colored('Folder is empty!', 'red')
        sys.exit()
    else:
        print colored('START DOWNLOADING', 'yellow')

    current = 1

    pool = ThreadPoolExecutor(max_workers=3)
    for item in result:
        main_download(service, item, location, current, total)
        #pool.submit(main_download, service, item, location, current, total)
    pool.shutdown(wait=True)
    print('Folder {} download completed!'.format(folder_name))

def main_download(service, item, location, current, total):
    file_id = item[u'id']
    filename = no_accent_vietnamese(item[u'name'])
    mime_type = item[u'mimeType']
    print '- ', colored(filename, 'cyan'), colored(mime_type, 'cyan'), '({}/{})'.format(current, total)
    if mime_type == 'application/vnd.google-apps.folder':
        download_folder(service, file_id, location, filename)
    elif not os.path.isfile('{}{}'.format(location, filename)):
        get_video(service, file_id, location, filename, False)
        #try:
        #    download_file(service, file_id, location, filename)
        #except Exception as e: 
        #    print colored(('Cannot download by normal way, try to download by special. VideoID: {} FileName: {}'.format(file_id, filename)), 'green')
        #    get_video(service, file_id, location, filename)
    else:
        remote_size = item[u'size']
        local_size = os.path.getsize('{}{}'.format(location, filename))
        if (str(remote_size) == str(local_size) or int(remote_size/4) > int(local_size)):
            print colored('File existed!', 'magenta')
        else:
            print colored('API Local File corrupted', 'yellow')
            print('API remote_size: {} <> local_size: {}'.format(remote_size, local_size))
            #os.remove('{}{}'.format(location, filename))
            get_video(service, file_id, location, filename, True)
            #try:
            #    download_file(service, file_id, location, filename)
            #except Exception as e:
            #    print colored(('Cannot download by normal way, try to download by special. VideoID: {} FileName: {}'.format(file_id, filename)), 'green')
            #    get_video(service, file_id, location, filename)
    current += 1
    percent = float((current-1))/float(total)*100
    print colored("%.2f percent completed!" % percent,'green')

def download_file(service, file_id, location, filename):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO('{}{}'.format(location, filename), 'wb')
    downloader = MediaIoBaseDownload(fh, request,chunksize=1024*1024)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        if status:
            print '\rDownload {}%.'.format(int(status.progress() * 100)),
            print int(status.progress() * 100)," percent complete         \r",
            sys.stdout.flush()
    print ""
    print colored(('%s downloaded!' % filename), 'green')
def cls():
    os.system('cls' if os.name=='nt' else 'clear')
def no_accent_vietnamese(s):
    #s = s.decode('utf-8', errors='ignore')
    s = re.sub(u'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(u'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(u'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(u'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(u'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(u'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(u'[ìíịỉĩ]', 'i', s)
    s = re.sub(u'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(u'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(u'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(u'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(u'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(u'[Đ]', 'D', s)
    s = re.sub(u'[đ]', 'd', s)
    s = re.sub(u':', '-', s)
    return s.encode('utf-8')
def get_video(service, file_id, location, filename, is_file):
    try:
        print colored(('Starting Download VideoID: {} FileName: {}'.format(file_id, filename)), 'green')
        #cookie_string = "SID=NgeYOTwjofd58AGxXI_7MMEFjofP7_FB163aH9OFQ4uB7AFlpCALhBpsVonNNM3yw3hS1w.;HSID=AwF4AAd1uQ5w3Vea2;SSID=ACpvM-QH8WJebhM8b;APISID=Ky2l7JyC6itSvSyP/AutQup09Kw7MoySLt;SAPISID=nHWlb0yEMtadASbf/A2AAE8NCLnboPu7hh;NID=180=HDVzHVHRxcTwCCw4F11hv3UahG-v8pKAb9Mi1evmRkg1FzBndzDcdYGKnqU4NPyELxe5NpB4smtxLWRVMXYNiru8rpmDUMwllUhjpeWQWtrz68L1HI4V-zvHN0InAcusMlbij9F_k9Zij3CtHncw0KDb_vCeLLRbPisYZ3zpH6_Co8zXj05kkcKU701rZaHmltbiqNydVQ;DRIVE_STREAM=Csb25Trh83A;1P_JAR=2019-4-3-15;SIDCC=AN0-TYu9m8jJN_PGjDcSLzNfj4ksYqkFAQv8wGeVX0f8-HWPHLUSPfOpw2QIGGrXgqiN5ES2;"
        cookie_string = "SID=NgeYOTwjofd58AGxXI_7MMEFjofP7_FB163aH9OFQ4uB7AFlpCALhBpsVonNNM3yw3hS1w.;HSID=AwF4AAd1uQ5w3Vea2;SSID=ACpvM-QH8WJebhM8b;APISID=Ky2l7JyC6itSvSyP/AutQup09Kw7MoySLt;SAPISID=nHWlb0yEMtadASbf/A2AAE8NCLnboPu7hh;NID=181=Vz0682gtnOMhlTwVBwpF4Co2nJJsGJGYS9vugjdY7x4B9B4f42aDrIWvM5P3W4GDgVmikgzVRjS8_IDauD19VdBW2Q-uHig6pSOmXOW0g_EetCfOxuDFflHrJZnA9UXU5WrZEz5chUlhw_-arjECqEcqHFXPRsxN9o8zJTalyIHWiXZYDeZcTFHvMMuQLH-u36l6WLMq3hw;DRIVE_STREAM=LGCt4SHW9uc;1P_JAR=2019-4-18-16;SIDCC=AN0-TYuLG_PMbYwL2SYy6zAuj0Ukehw_pOCeRaXkHSFrpsECxrxKekAkEg_dEOURvFSstRS6pQ;"
        url = "https://mail.google.com/e/get_video_info?docid=" + file_id
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', cookie_string))
        data = opener.open(url).read()
        info =  urlparse.parse_qs(data)

        try:
            
            if (info["status"][0] == "fail"):
                print colored('Error get_video_info: Khong the phat video. Co loi xay ra. Chi Tiet:', 'red')
                print info["reason"][0]
                return

            info = info["fmt_stream_map"][0]
            paras = info.split('|')
        except Exception as e:
            print colored(('Error Read get_video_info VideoID: {} FileName: {}'.format(file_id, filename)), 'red')
            logging.exception("message")
            return

        downloadLink = ""
        finalDownloadURL = ""
        for word in paras:
            if (word.find("itag=22") != -1):
                downloadLink = word.split(',')
        if len(downloadLink) > 0:
            finalDownloadURL = downloadLink[0]
            print("")
            print('Download URL: {}'.format(finalDownloadURL))
        else:
            print("Cannot file download URL:")
            return
        print("")
        print("Download Path:")
        print('{}{}'.format(location, filename))
        s = requests.Session()
        cookies_arr = cookie_string.split(';')
        for cookie_string in cookies_arr:
            cookie_arr = cookie_string.split('=')
            if len(cookie_arr) > 1:
                s.cookies.set(cookie_arr[0], cookie_arr[1])
        
        start = time.clock()
        r = s.get(finalDownloadURL, stream=True)
        print("Download GET Status: " + str(r.status_code))
        r.raise_for_status()
        total_length = r.headers.get('content-length')
        print('Total Length: {} MB'.format(int(total_length)/(1024*1024)))
        
        if (is_file is True):
            if os.path.isfile('{}{}'.format(location, filename)):
                local_size = os.path.getsize('{}{}'.format(location, filename))
                if (str(total_length) == str(local_size)):
                    print colored('TD File existed!', 'magenta')
                    return
                else:
                    os.remove('{}{}'.format(location, filename))
                    print colored('TD Local File corrupted', 'red')
                    print('total_length: {}MB <> local_size: {}MB'.format(int(total_length/(1024*1024)), int(local_size/(1024*1024))))

        dl = 0
        if total_length is None:
            with open('{}{}'.format(location, filename), 'wb') as f:
                for chunk in r.iter_content(chunk_size=2048):
                    if chunk:
                        f.write(chunk)
        else:
            with open('{}{}'.format(location, filename), 'wb') as f:
                for chunk in r.iter_content(chunk_size=2048):
                    if chunk:
                        dl += len(chunk)
                        f.write(chunk)
                        done = 100 * dl / int(total_length)
                        sys.stdout.write("\r[%s%s] %s%%   %s KBps" % ('=' * done, ' ' * (100-done), done, dl//(1024*(time.clock() - start))))
        print("")
        print('File {} downloaded!'.format(filename))

    except Exception as e:
        print colored(('Error VideoID: {} FileName: {}'.format(file_id, filename)), 'red')
        print e
        logging.exception("message")
    return

if __name__ == '__main__':
    main()