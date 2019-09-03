from  urllib import parse
import os
import requests

def getCoverArt(url: str) -> str:
    if not ValidURL(url): raise ValueError
    links = [ img for img in getImages(url) if 'artworks' in img and '500x500' in img ]
    return links[0] 

def ValidURL(url: str) -> bool:
    u = parse.urlparse(url)
    # Check if scheme(http or https) and netloc(domain) are not empty
    return u[0] != '' and u[1] != ''

def getImages(url: str) -> list:
    html = requests.get(url, headers={'User-Agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}).text
    image_extensions = ['.jpg', '.ico', 'png', '.jpeg']
    links = [ 
        { 'link': element.replace('\\', ''), 'extension': [ img for img in image_extensions if img in element ][0] } 
        for element in html.split('"')
        if '/' in element and any( element.endswith(img) for img in image_extensions )
    ]

    links = set([ l['link'].split(l['extension'])[0] + l['extension'] for l in links ])
    links = [ l for l in [ l if 'http' == l[:4] else os.path.join(url, l) for l in links ] if ValidURL(l) ] 
    return links

if __name__ == '__main__':
    notValid, choice = True, -1
    url = ''

    while notValid:
        url = input('Enter URL: ')
        notValid = not ValidURL(url)
        if notValid: print('Invalid URL, Ex: https://www.google.com')

    while choice != 1 and choice != 0:
        try:
            choice = int( input('\n[0] Download All Images\n[1] Download SoundCloud Cover Art / Image\n\nEnter a number: ') )
        except ValueError as e:
            continue

    links = getImages(url) if choice == 0 else [ getCoverArt(url) ]

    for link in links:
        filename = link.split('/')[-1]
        count = 0
        while os.path.isfile(filename):
            count += 1 
            filename = '({}){}'.format(count, filename)

        html_data = requests.get(link)

        if html_data.headers['Content-Type'].split('/')[0] != 'image': continue

        with open(filename, 'wb') as f:
            f.write(html_data.content)
        
        print('"{}" downloaded from {}'.format(filename, link))
