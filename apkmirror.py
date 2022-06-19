
import sys
import os
import re
import requests

from bs4 import BeautifulSoup
import unicodedata


apkmirrorUrl = 'https://www.apkmirror.com'
headers = {'User-Agent': 'OpenGApps APKMirrorCrawler/1.0'}

androidVersion = "Android 10+"
osType = "arm64-v8a + armeabi-v7a"

# the code version for each bitness
chrome64bit = '34'
chrome32bit = '33'

search = sys.argv[1]
mode = sys.argv[2]

foundApks = []
downloadApks = []
search = search.replace("-","+")
search_url = apkmirrorUrl + '/?post_type=app_release&searchtype=apk&s=' + search
print("Search : " + search_url)
session = requests.Session()
session.headers.update(headers)

resp    = session.get(search_url)
html    = unicodedata.normalize('NFKD', resp.text).encode('ascii', 'ignore')

dom          = BeautifulSoup(html, 'html5lib')
downloadArea = dom.findAll('div', {'class': 'listWidget'})[0]
tablerows    = downloadArea.findAll('div', {'class': 'table-row'})

bOnce = True  # Skip header row
for tr in tablerows:
    if bOnce:
        bOnce = False
        continue

    cells = tr.findAll('div', {'class': 'table-cell'})
    foundApks.append({  "name" : cells[1].get_text().strip(), 
                        "linkVersions" : cells[0].find('a')['href']})
                        # "versions": []})
                        # "vercode": None,
                        # "download_link": None})

if not foundApks:
    print ("apk not found")
    exit()

# if we want just to download the first one 
if mode == "auto":
    # print (foundApks[0]['link'])
    search_url = apkmirrorUrl + foundApks[0]['linkVersions']
    print("Search versions: " + search_url)
    resp    = session.get(search_url)
    html    = unicodedata.normalize('NFKD', resp.text).encode('ascii', 'ignore')

    dom         = BeautifulSoup(html, 'html5lib')
    downloadArea = dom.findAll('div', {'class': 'listWidget'})[0]
    tablerows    = downloadArea.findAll('div', {'class': 'table-row'})
    bOnce = True  # Skip header row
    for tr in tablerows:
        if bOnce:
            bOnce = False
            continue

        cells = tr.findAll('div', {'class': 'table-cell'})
        if androidVersion in cells[2].get_text() and osType in cells[1].get_text(): 
            url = apkmirrorUrl + cells[0].find('a')['href']

            session = requests.Session()
            session.headers.update(headers)
            print('Get version info: ' + url)

            resp    = session.get(url)
            html    = unicodedata.normalize('NFKD', resp.text).encode('ascii', 'ignore')

            dom         = BeautifulSoup(html, 'html5lib')
            contentArea = dom.findAll('div', {'class': 'tab-content'})[0]
            dl_button   = contentArea.findAll('a', {'class': 'downloadButton'})[0]
            appspecs    = contentArea.findAll('div', {'class': 'appspec-row'})

            reVersion  = re.compile('Version:\s(?P<VERNAME>.*)\s\((?P<VERCODE>\d*)[^)]*\)')
            avivername = ''
            avivercode = ''
            for appspec in appspecs:
                m = reVersion.search(appspec.find('div', {'class': 'appspec-value'}).get_text())
                if m:
                    downloadApks.append({   "version" : m.group('VERNAME'), 
                                            "vercode" : m.group('VERCODE'),
                                            "downloadLink" : dl_button['href']})

# download selected apks
for apk in downloadApks:
    bitness = ''
    print(apk["vercode"])
    if apk["vercode"].endswith(chrome64bit):
        bitness = '64'
    if apk["vercode"].endswith(chrome32bit):
        bitness = '32'
    
    if bitness == '':
        print ("bad version code " + apk["vercode"])
        continue
    apk_name = '.'.join(["chrome", apk["version"], "apkm"])
    downloadPath = os.path.join(os.getcwd() , 'download', bitness, apk_name)
    print (downloadPath)
    if os.path.exists(downloadPath):
        print (f"version {apk['version']} already install at {downloadPath}")
    
    downloadLink = apkmirrorUrl + apk["downloadLink"]
    print (f"download apk {downloadLink}")
    session = requests.Session()
    session.headers.update(headers)
    r = session.get(downloadLink)

    with open(apk_name, 'wb') as local_file:
        local_file.write(r.content)
    exit()

print (downloadApks)