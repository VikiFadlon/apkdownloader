
import sys
import os
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import unicodedata


apkmirrorUrl = 'https://www.apkmirror.com'

# the code version for each bitness
chrome64bit = '34'
chrome32bit = '33'


downloadApks = []

session = requests.Session()
session.headers.update({'User-Agent': 'OpenGApps APKMirrorCrawler/1.0'})

def get_url(url):
    print(f"GET {url}")
    resp = session.get(url)
    html = unicodedata.normalize('NFKD', resp.text).encode('ascii', 'ignore')
    return  BeautifulSoup(html, 'html5lib')
    

def search_apks(search):
    foundApks = []
    search = search.replace("-","+")
    search_url = apkmirrorUrl + '/?post_type=app_release&searchtype=apk&s=' + search
    print(f"search `{search.replace('-',' ')}` in apkmirror" + search_url)
    
    dom = get_url(search_url)

    downloadArea = dom.findAll('div', {'class': 'listWidget'})[0]
    tablerows = downloadArea.findAll('div', {'class': 'table-row'})
    
    bOnce = True  # Skip header row
    for tr in tablerows:
        if bOnce:
            bOnce = False
            continue

        cells = tr.findAll('div', {'class': 'table-cell'})
        foundApks.append({  "name" : cells[1].get_text().strip(), 
                            "link" : apkmirrorUrl + cells[0].find('a')['href']})

    return foundApks

def get_versions(apk):
    versions = []
    name = apk['name'].split('\n')[0]
    print(f"download apk {name}")
    dom          = get_url(apk['link'])
    downloadArea = dom.findAll('div', {'class': 'listWidget'})[0]
    tablerows    = downloadArea.findAll('div', {'class': 'table-row'})
    bOnce = True  # Skip header row
    for tr in tablerows:
        if bOnce:
            bOnce = False
            continue

        cells = tr.findAll('div', {'class': 'table-cell'})
        versions.append({   "Aversion" : cells[2].get_text(),
                            "OS" : cells[1].get_text(),
                            "link" : apkmirrorUrl + cells[0].find('a')['href']})
    return versions
        
        #     versions.append(cells)

def get_apks(version):

    apks = []
    print(f'Get version info:')
    dom    = get_url(version['link'])
    
    contentArea = dom.findAll('div', {'class': 'tab-content'})[0]
    dl_button   = contentArea.findAll('a', {'class': 'downloadButton'})[0]
    appspecs    = contentArea.findAll('div', {'class': 'appspec-row'})

    # check if trichrome is needed
    apk_warnings = dom.findAll('div', {'class': 'apk-warning-panel'})
    
    trichromeLink = ''
    for apk_warning in apk_warnings:
        if "This APK requires a library" in apk_warning.get_text():
            trichromeLink = apk_warning.find('a')['href']

    reVersion  = re.compile('Version:\s(?P<VERNAME>.*)\s\((?P<VERCODE>\d*)[^)]*\)')
    for appspec in appspecs:
        m = reVersion.search(appspec.find('div', {'class': 'appspec-value'}).get_text())
        if m:
            apks.append({   "version" : m.group('VERNAME'), 
                            "vercode" : m.group('VERCODE'),
                            "downloadLink" : dl_button['href'],
                            "trichromeLink" : trichromeLink})
    return apks

# # download selected apks
# for apk in downloadApks:
    
#     apk_name = '.'.join(["chrome", apk["version"], "apkm"])
    
#     bitness = ''
#     if apk["vercode"].endswith(chrome64bit):
#         bitness = '64'
#     if apk["vercode"].endswith(chrome32bit):
#         bitness = '32'
    
#     if bitness == '':
#         print ("bad version code " + apk["vercode"])
#         continue

#     downloadPath = os.path.join(os.getcwd() , 'download', bitness, apk["version"])
    
#     Path(downloadPath).mkdir(parents=True, exist_ok=True)

#     apkPath = os.path.join(downloadPath, apk_name)

#     if os.path.exists(apkPath):
#         print (f"{apk_name} already install at {apkPath}")
#         continue
    
#     downloadLink = apkmirrorUrl + apk["downloadLink"]
#     print (f"download page {downloadLink}")

#     resp = session.get(downloadLink)


#     html    = unicodedata.normalize('NFKD', resp.text).encode('ascii', 'ignore')
#     dom     = BeautifulSoup(html, 'html5lib')
#     notes   = dom.findAll('p', {'class': 'notes'})

#     apkDownloadLink = ''
#     for note in notes:
#         if "Your download will start immediately. If not, please click here" in note.get_text():
#             apkDownloadLink = note.find('a')['href']
#             print(f"download href = {note.find('a')['href']}")
#             break

#     if not apkDownloadLink:
#         print (f"fail to found download link to download")
#         continue

#     apkDownloadLink = apkmirrorUrl + apkDownloadLink
#     print (f"apkDownloadLink {apkDownloadLink}")
    
#     resp = session.get(apkDownloadLink)
    
#     with open(apkPath, 'wb') as local_file:
#         local_file.write(resp.content)

#     # download trichrome if needed
#     if apk["trichromeLink"]:
#         apk_name = '.'.join(["trichrome", apk["version"], "apk"])
#         apkPath = os.path.join(downloadPath, apk_name)

#         if os.path.exists(apkPath):
#             print (f"{apk_name} already install at {apkPath}")
#             continue
        
#         url = apkmirrorUrl + apk["trichromeLink"]

#         print(f'Get trichrome info: {url}')

#         resp    = session.get(url)
#         html    = unicodedata.normalize('NFKD', resp.text).encode('ascii', 'ignore')

#         dom         = BeautifulSoup(html, 'html5lib')
#         contentArea = dom.findAll('div', {'class': 'tab-content'})[0]
#         dl_button   = contentArea.findAll('a', {'class': 'downloadButton'})[0]

#         if not dl_button['href']:
#             print(f"fail to found trichrome link")
#             continue

#         downloadLink = apkmirrorUrl + dl_button['href']
#         print (f"download page {downloadLink}")

#         resp = session.get(downloadLink)


#         html    = unicodedata.normalize('NFKD', resp.text).encode('ascii', 'ignore')
#         dom     = BeautifulSoup(html, 'html5lib')
#         notes   = dom.findAll('p', {'class': 'notes'})

#         apkDownloadLink = ''
#         for note in notes:
#             if "Your download will start immediately. If not, please click here" in note.get_text():
#                 apkDownloadLink = note.find('a')['href']
#                 print(f"download href = {apkDownloadLink}")
#                 break

#         if not apkDownloadLink:
#             print (f"fail to found download link to download")
#             continue

#         apkDownloadLink = apkmirrorUrl + apkDownloadLink
#         print (f"apkDownloadLink {apkDownloadLink}")
    
#         resp = session.get(apkDownloadLink)
    
#         with open(apkPath, 'wb') as local_file:
#             local_file.write(resp.content)

def print_apks(foundApks):
    print("{:<8} {:<15} {:<50}".format('index', 'name', 'link'))
    for i, apk in enumerate(foundApks):
        print("{:<8} {:<15} {:<50}".format(i, apk['name'].split('\n')[0], apk["link"]))
    

def print_versions(versions):
    print("{:<8} {:<15} {:<25} {:<35}".format('index', 'Android version', 'OS', 'link'))
    for i, ver in enumerate(versions):
        print("{:<8} {:<15} {:<25} {:<35}".format(i, ver['Aversion'], ver['OS'], ver["link"]))

if __name__ == "__main__":
    search  = sys.argv[1]
    mode    = sys.argv[2]

    androidVersion  = "Android 10+"
    osType          = "arm64-v8a + armeabi-v7a"

    foundApks = search_apks(search)
    if not foundApks:
        print ("fail to found apks")
        exit()

    print_apks(foundApks)

    if mode == "auto":
        apk = foundApks[0]
        versions = get_versions(apk)
        if not versions:
            print (f"fail to get versions from {apk['name']} link {apk['link']}")
            exit()
        print_versions(versions)

        selected_versions = []
        for i,ver in enumerate(versions):
            if androidVersion in ver['Aversion'] and osType in ver['OS']: 
                print (f"index {i} selected")
                selected_versions.append(ver)


        if not selected_versions:
            print (f"not found versions for version: {androidVersion} os: {osType}")
            exit()
        
        for ver in selected_versions:
            apks = get_apks(ver)

            if not apks:
                print (f"fail to found apks got version {ver['Aversion']} os {ver['OS']} link {ver['link']}")
                continue
            
        



