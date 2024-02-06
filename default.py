import os
import sys
import urllib
import urllib.parse
import urllib.request
import urllib.error
import urllib.response
import re
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import requests
from bs4 import BeautifulSoup
import time

thisAddon = xbmcaddon.Addon(id='plugin.video.indavideo')
thisAddonDir = xbmcvfs.translatePath(thisAddon.getAddonInfo('path'))
sys.path.append(os.path.join(thisAddonDir, 'resources', 'lib'))
sys.path.append(os.path.join(thisAddonDir, 'resources', 'search'))
session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
if sys.platform == 'win32':
    download_script = thisAddonDir + '\default.py'
    search_file = thisAddonDir + '\\resources\\search\\search.dat'
    search_tmp = thisAddonDir + '\\resources\\search\\search.tmp'
else:
    download_script = thisAddonDir + '/default.py'
    search_file = thisAddonDir + '/resources/search/search.dat'
    search_tmp = thisAddonDir + '/resources/search/search.tmp'

sbarat_abc = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

lang_flags = ['[COLOR green] SZINKRON[/COLOR]','[COLOR red] FELIRAT[/COLOR]','[COLOR yellow] NINCS FELIRAT[/COLOR]']

host_support = ['vidto.me','movshare.net','indavideo.hu','youtube.com','streamin.to']

def open_search_panel():
               
    search_text = ''
    keyb = xbmc.Keyboard('',u'Keres\u00E9s')
    keyb.doModal()
 
    if (keyb.isConfirmed()):
        search_text = keyb.getText()

    return search_text

def find_read_error(top_url):
    try:
        req = session.get(top_url, headers=headers)
        url_content = req.text
    except:
        url_content = 'HIBA'
        addon = xbmcaddon.Addon()
        addonname = addon.getAddonInfo('name')
        line1 = u'Az internetes adatb\xE1zishoz val\xF3 csatlakoz\xE1s sikertelen!'
        xbmcgui.Dialog().ok(addonname, line1)
        return url_content
    return url_content

def find_read_error_params(top_url, params):
    try:
        req = session.get(top_url, params, headers=headers)
        url_content = req.text
    except:
        url_content = 'HIBA'
        addon = xbmcaddon.Addon()
        addonname = addon.getAddonInfo('name')
        line1 = u'Az internetes adatb\xE1zishoz val\xF3 csatlakoz\xE1s sikertelen!'
        xbmcgui.Dialog().ok(addonname, line1)
        return url_content
    return url_content

def just_beta(file_host):
    addon = xbmcaddon.Addon()
    addonname = addon.getAddonInfo('name')
    line1 = u'Ebben a verzi\xF3ban, ez a vide\xF3 kiszolg\xE1l\xF3 nem t\xE1mogatott!'
    xbmcgui.Dialog().ok(addonname, line1)  
    return

def just_removed(file_host):
    addon = xbmcaddon.Addon()
    addonname = addon.getAddonInfo('name')
    line1 = u'A keresett vide\xF3t elt\xE1vol\xEDtott\xE1k!'
    xbmcgui.Dialog().ok(addonname, line1)   
    return

def empty_search():
    addon = xbmcaddon.Addon()
    addonname = addon.getAddonInfo('name')
    line1 = u'A keresett kifejez\xE9sre nincs tal\xE1lat!'
    xbmcgui.Dialog().ok(addonname, line1)   
    return

def viewmode(mview):

    return

def time_to_duration(strtime):

    strtime_a = strtime.split(':')
    duration = (int(strtime_a[0]) * 60) + int(strtime_a[1])

    return int(duration)

def build_main_directory():
    url = build_url({'mode': 'base_search', 'foldername': 'Kereses', 'pagenum': '0'})
    li = xbmcgui.ListItem(u'Keres\xE9s')
    li.setArt({'icon':thisAddon.getAddonInfo("path")})
    li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'inda_base', 'foldername': 'Ajanlott', 'pagenum': '0'})
    li = xbmcgui.ListItem(u'Aj\xE1nlott vide\u00F3k')
    li.setArt({'icon':thisAddon.getAddonInfo("icon")})
    li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    viewmode(1)
    xbmcplugin.endOfDirectory(addon_handle)

    return

def build_search_directory():
    url = build_url({'mode': 'new_search', 'foldername': 'UjKereses', 'pagenum': '1', 'search_text': ' '})
    li = xbmcgui.ListItem(u'[B]\u00DAj Keres\xE9s[/B]')
    li.setArt({'icon':thisAddon.getAddonInfo("icon")})
    li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'old_search', 'foldername': 'RegiKereses', 'pagenum': '1'})
    li = xbmcgui.ListItem(u'Keres\xE9si el\u0151zm\xE9nyek')
    li.setArt({'icon':thisAddon.getAddonInfo("icon")})
    li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    viewmode(1)
    xbmcplugin.endOfDirectory(addon_handle)

    return

def build_indavideo_directory():
    top_url = 'https://indavideo.hu'

    url_content = find_read_error(top_url)
    if url_content == 'HIBA':
        return

    soup = BeautifulSoup(url_content, 'html.parser')
    res = soup.find_all('div', class_='item TYPE_8')
    # video_info = re.compile('class="item TYPE_5[^=]+="([^"]+)"[^:]+://([^"]+)"[^/]+//([^"]+)".*?"duration">(.*?)</div>.*?"description">(.*?)</div>').findall(url_content)    

    if res:
        for item in res:
            video_url = item.find('a', class_='title')['href']
            video_duration = item.find('div', class_='duration').get_text(strip=True)
            video_title = item.find('a', class_='title').get_text(strip=True)
            video_image_url = 'https:' + re.search(r'url\((.*?)\)', item.find('div', class_='crop myvideos_tmb')['style']).group(1).strip()
            video_description = item.find('div', class_='description').get_text(strip=True)
            url = build_url({'mode': 'indavideo.hu', 'foldername': video_url, 'title': video_title, 'image': video_image_url, 'isdownload' : ' '})
            li = xbmcgui.ListItem(video_title)
            li.setArt({'icon':video_image_url})
            li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
            li.setInfo(type='Video', infoLabels={'duration': time_to_duration(video_duration), 'plot': video_description})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=False)

    viewmode(1)
    xbmcplugin.endOfDirectory(addon_handle)

    return

def build_search_result(pagenum, search_text):
    if search_text == ' ':
        search_text = open_search_panel()
        work_text = ''.join(search_text.split())
        if work_text != '':
            build_search_file(urllib.parse.quote(search_text, ''), 'ADD')
        else:
            empty_search()
            return

    top_url = 'https://indavideo.hu/search?p_uni=' + pagenum + '&action=search&search=' + urllib.parse.quote(search_text, '') + '&view=detailed'

    url_content = find_read_error(top_url)
    if url_content == 'HIBA':
        return

    soup = BeautifulSoup(url_content, 'html.parser')
    res = soup.find_all('div', class_='item TYPE_8')
    # video_info = re.compile('class="item TYPE_8[^=]+="([^"]+)"[^:]+://([^"]+)"[^/]+//([^"]+)".*?"duration">(.*?)</div>.*?"description">(.*?)</div>').findall(url_content)    
    next_page = re.compile('="text">(utols)').findall(url_content)

    if res:
        for item in res:
            video_url = item.find('a', class_='title')['href']
            video_duration = item.find('div', class_='duration').get_text(strip=True)
            video_title = item.find('a', class_='title').get_text(strip=True)
            video_image_url = 'https:' + re.search(r'url\((.*?)\)', item.find('div', class_='crop myvideos_tmb')['style']).group(1).strip()
            video_description = item.find('div', class_='description').get_text(strip=True)
            url = build_url({'mode': 'indavideo.hu', 'foldername': video_url, 'title': video_title, 'image': video_image_url, 'isdownload' : ' '})
            li = xbmcgui.ListItem(video_title)
            li.setArt({'icon':video_image_url})
            li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
            li.setInfo(type='Video', infoLabels={'duration': time_to_duration(video_duration), 'plot': video_description})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=False)

        if pagenum != '1':
            url = build_url({'mode': 'back_one_folder'})
            li = xbmcgui.ListItem(u'[COLOR blue]<< El\u0151z\u0151 oldal <<[/COLOR]')
            li.setArt({'icon':thisAddon.getAddonInfo("icon")})
            li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=False)

        pagenum = int(pagenum)
        pagenum += 1
        pagenum = str(pagenum)

        if next_page:
            url = build_url({'mode': 'new_search', 'foldername': 'UjKereses', 'pagenum': pagenum, 'search_text': urllib.parse.quote(search_text, '')})
            li = xbmcgui.ListItem(u'[COLOR green]>> K\xF6vetkez\u0151 oldal >>[/COLOR]')
            li.setArt({'icon':thisAddon.getAddonInfo("icon")})
            li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=True)

    viewmode(1)
    xbmcplugin.endOfDirectory(addon_handle)

    return

# def find_indavideo_videourl(foldername, foldertitle, folderimage, isdownload):
#     top_url = foldername
#     xbmc.log(top_url, level=xbmc.LOGINFO)    
#     url_content = find_read_error(top_url)
#     if url_content == 'HIBA':
#         return

#     soup = BeautifulSoup(url_content, 'html.parser')
#     iframe_src = soup.find('iframe', class_='embed-responsive-item').get('src')

#     iframe_content = find_read_error(iframe_src)
#     if iframe_content == 'HIBA':
#         return
    
#     soup = BeautifulSoup(iframe_content, 'html.parser')
#     video_player = soup.find('video', class_='video-player')
        
#     if video_player:
#         xbmc.log('player found', level=xbmc.LOGINFO)
#         video_src = video_player.get('src')
#         xbmc.log(video_src, level=xbmc.LOGINFO)
#         # top_url = 'http://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData/' + embed_url_hash[0]

#         # url_content = find_read_error(top_url)
#         # if url_content == 'HIBA':
#         #     return

#         # direct_url = re.compile('video_file":"([^"]+)"').findall(url_content)

#         # if direct_url:
#         if isdownload == 'DOWNLOAD':
#             foldertitle = foldertitle[:41] + '.mp4'
#             download_video(foldertitle, direct_url[0].replace('\\', ''))
#         else:
#             videoitem = xbmcgui.ListItem(label=foldertitle)
#             videoitem.setArt({'thumb':folderimage})
#             videoitem.setInfo(type='video', infoLabels={'Title': foldertitle})
#             xbmc.Player().play(video_src, videoitem)
#     else:
#         just_removed(foldertitle)
           
#     return
def find_indavideo_videourl(foldername, foldertitle, folderimage, isdownload):
    top_url = foldername
            
    url_content = find_read_error(top_url)
    if url_content == 'HIBA':
        return

    embed_url_hash = re.compile('indavideo\.hu/player/video/([0-9a-f]+)').findall(url_content)
    xbmc.log(embed_url_hash[0], level=xbmc.LOGINFO)
   
    if embed_url_hash:
        top_url = 'https://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData/' + embed_url_hash[0] + r'/12////?' + foldername + r'%26callback%3DjQuery35102423255304617309_1707207329192%26_%3D1707207329193&callback=jQuery35107093453080001533_1707209240665&_=1707209240666'

        url_content = find_read_error(top_url)
        if url_content == 'HIBA':
            return

        direct_url = re.compile('video_file":"([^"]+)"').findall(url_content)
        file_hash = re.compile(r'"filesh":\s*{\s*"360":\s*"([^"]+)"\s*}').findall(url_content)
        xbmc.log(direct_url[0], level=xbmc.LOGINFO)
        if direct_url:
            if isdownload == 'DOWNLOAD':
                foldertitle = foldertitle[:41] + '.mp4'
                download_video(foldertitle, direct_url[0].replace('\\', ''))
            else:
                videoitem = xbmcgui.ListItem(label=foldertitle)
                videoitem.setArt({'thumb':folderimage})
                videoitem.setInfo(type='Video', infoLabels={'Title': foldertitle})
                xbmc.Player().play(direct_url[0].replace('\\', '') + "&token=" + file_hash[0], videoitem)
        else:
            just_removed(foldertitle)
    else:
        just_removed(foldertitle)
           
    return

def build_search_file(search_text, function):
    if function == 'ADD':
        file_data = search_text + '\n'
        the_file = open(search_file,'a')
        the_file.write(file_data)
        the_file.close()
        the_tmp = open(search_tmp,'a')
        the_tmp.write(file_data)
        the_tmp.close()
    
    elif function == 'REMOVE':
        file_data = search_text
        the_tmp = open(search_tmp,'r')
        the_file = open(search_file,'w')
        for line in the_tmp:
            if line != file_data:
                the_file.write(line)
        the_file.close()
        the_tmp.close()

        the_file = open(search_file,'r')
        the_tmp = open(search_tmp,'w')
        for line in the_file:
            the_tmp.write(line)
        the_tmp.close()
        the_file.close()
        xbmc.executebuiltin("Container.Refresh")
        
    return

def build_old_search_directory():
    try:
        the_file = open(search_file,'r')
        for line in the_file:
            url = build_url({'mode': 'new_search', 'foldername': 'UjKereses', 'pagenum': '1', 'search_text': urllib.parse.unquote(line)})
            li = xbmcgui.ListItem(urllib.parse.unquote(line))
            li.setArt({'icon':thisAddon.getAddonInfo("icon")})
            li.setProperty('fanart_image', thisAddon.getAddonInfo('fanart'))
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=True)        
                
        the_file.close()
        viewmode(1)
        xbmcplugin.endOfDirectory(addon_handle)          
    except:
        viewmode(1)
        xbmcplugin.endOfDirectory(addon_handle)

    return

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

mode = args.get('mode', None)

if mode is None:

    build_main_directory()

elif mode[0] == 'base_search':

    build_search_directory()

elif mode[0] == 'inda_base':

    build_indavideo_directory()

elif mode[0] == 'new_search':

    build_search_result(args['pagenum'][0], args['search_text'][0])

elif mode[0] == 'indavideo.hu':
    
    find_indavideo_videourl(args['foldername'][0], args['title'][0], args['image'][0], args['isdownload'][0])

elif mode[0] == 'old_search':
    
    build_old_search_directory()

elif mode[0] == 'back_one_folder':

    xbmc.executebuiltin('Action(ParentDir)')