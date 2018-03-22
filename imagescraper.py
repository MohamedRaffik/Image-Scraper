import urllib.request
import os
import urllib.error
import html.parser
import datetime

imagesFound = []

class Parser(html.parser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        global imagesFound
        for attr in attrs:
            a, title = attr
            if 'background' in str(title): continue
            elif '.jpg' in str(title): imagesFound.append([title, '.jpg'])
            elif '.png' in str(title): imagesFound.append([title, '.png'])
            elif '.jpeg' in str(title): imagesFound.append([title, '.jpeg'])
            elif '.bmp' in str(title): imagesFound.append([title, '.bmp'])
            elif '.ico' in str(title): imagesFound.append([title, '.ico'])
    
def default_name():
    now = datetime.datetime.now()
    dname = 'ID'+str(now.day)+str(now.month)+str(now.year)+str(now.hour)+str(now.minute)+str(now.second)
    return dname

def link_end(link):
    end = ['.com', '.org']
    if '.com' in link:
        return (True, '.com')
    elif '.org' in link:
        return (True, '.org')
    return (False, '')

def redefine_link(sourcelink, imglink):
    imglink = imglink.replace('\\', '')
    End, EndType = link_end(imglink)
    SEnd, SEndType = link_end(sourcelink)
    if imglink[0] == '_':
        newsrclink = '/'.join(sourcelink.split('/')[:-1])+'/'
        return newsrclink+imglink
    elif 'http' not in imglink and imglink[:2] == '//':
        imglink = 'https:'+imglink
    elif 'http' not in imglink and not End:
        newsrclink = sourcelink.split(SEndType)[0]+SEndType
        if imglink[0] == '/':
            newsrclink+=imglink
        else:
            newsrclink+='/'+imglink
        return newsrclink
    elif 'http' not in imglink and EndType:
        newsrclink = 'https:'+imglink
        return newsrclink
    return imglink

def already_found(group):
    global imagesFound
    for i in imagesFound:
        if i == group:
            return True
    return False

def background_links(link):
    global imagesFound
    links = []
    link = link.replace('(', '<-SPLIT->')
    link = link.replace(')', '<-SPLIT->')
    newsplit = link.split('<-SPLIT->')
    for e in newsplit:
        if 'http' == e[:4]:
            if '.jpg' in e:
                if not already_found([e,'.jpg']):
                    imagesFound.append([e, '.jpg'])
            elif '.png' in e:
                if not already_found([e, '.png']):
                    imagesFound.append([e, '.png'])
            elif '.jpeg' in e:
                if not already_found([e, '.jpeg']):
                    imagesFound.append([e, '.jpeg'])
            elif '.bmp' in e:
                if not already_found([e, '.bmp']):
                    imagesFound.append([e, '.bmp'])
            elif '.ico' in e:
                if not already_found([e, '.ico']):
                    imagesFound.append([e, '.ico'])

def additional_links(link,char):
    global imagesFound
    links = []
    elements = link.split(char)
    for e in elements:
        if '.jpg' in e:
            if not already_found([e,'.jpg']):
                imagesFound.append([e, '.jpg'])
        elif '.png' in e:
            if not already_found([e, '.png']):
                imagesFound.append([e, '.png'])
        elif '.jpeg' in e:
            if not already_found([e, '.jpeg']):
                imagesFound.append([e, '.jpeg'])
        elif '.bmp' in e:
            if not already_found([e, '.bmp']):
                imagesFound.append([e, '.bmp'])
        elif '.ico' in e:
            if not already_found([e, '.ico']):
                imagesFound.append([e, '.ico'])
            
def remove_file(file):
    try:
        os.remove(file)
    except:
        pass

def rename_file(file, newfile):
    try:
        os.rename(file, newfile)
    except OSError:
        pass

def error_check(link, path):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent,}
    if len(path) < 1:
        return (False, 'Folder was not Selected')
    if 'http://' not in link and 'https://' not in link:
        return (False, 'Not a Valid Link (ex: http://www.youtube.com or https://www.youtube.com)')
    try:
        req = urllib.request.Request(link, None, headers)
        f = urllib.request.urlopen(req).read().decode()
    except UnicodeDecodeError or ValueError:
        return (False, 'Link Must be HTML')
    except urllib.request.HTTPError as error:
        return (False, 'HTTP Error: '+str(error.code))
    except urllib.request.URLError:
        return (False, 'Error Opening Link')
    return (True, '')

def file_check(fileinfos):
    for file in fileinfos:
        if file[0][-4:] != file[1][-4:]:
            return False
    return True
    
def download_image(link):
    global imagesFound

    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent,}
    req = urllib.request.Request(link, None, headers)

    count = 0
    site = urllib.request.urlopen(req).read().decode()
    parser = Parser()
    images = []
    parser.feed(site)
    additional_links(site, '"')
    additional_links(site, "'")
    background_links(site)
    for src in imagesFound:
        src[0] = redefine_link(link,src[0])
        images.append([src[0], src[1]])
    imagesFound = []
    return images



