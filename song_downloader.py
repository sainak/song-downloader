#credits: erazer

import json
import time

import requests
from tqdm import tqdm


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': '*/*',
    'Referer': 'http://musicpleer.cloud/'
}

response_items = 10 #number of response items


#search for the song
def search_song(_srh):
    
    print('SEARCHING...')
    search_url = 'https://databrainz.com/api/search_api.cgi'
    
    search_params = {
        'jsoncallback':'jQuery1111019191608358321144_1580929162911',
        'qry':_srh,#song name goes here
        'format':'json',
        'mh':response_items,
        'where':'mpl'
    }

    try:
        search_resp = requests.get(search_url,headers=headers,params=search_params)
    
    except requests.exceptions.Timeout:
        search_song(srh)

    except requests.exceptions.ConnectionError:
        print('\tconnection ERROR\n ')
        exit(1)
    
    if search_resp.text == '':
        print ('no results found\n')
        
        mainfunc()
    
    else:
        search_json = json.loads(search_resp.text[43:-1])
        print('SONGS FOUND')
        
        get_song(search_json)


#get the song data from database 
def get_song(_search_json):
    
    song_url = 'https://databrainz.com/api/data_api_new.cgi'
    
    i = 0
    while i <= response_items:
        
        song_params = {
            'jsoncallback': 'jQuery1111019191608358321144_1580929162911',
            'id':_search_json['results'][i]['url'] , #song url goes here
            'r': 'mpl',
            'format': 'json',
            '_':int(round(time.time() * 1000))
        }

        print('FETCHING SONG INFO...')
        try:
            song_resp = requests.get(song_url,headers=headers,params=song_params)
        
        except requests.exceptions.ConnectionError:
            print('\tconnection ERROR\n ')
            exit(1)
        
        song_json = json.loads(song_resp.text[43:-1])

        if song_json['song']['returncode'] != '200':
            print('\tnot found')
            i += 1
            continue
        
        else:
            print('\n---RESULT---')
            print('title: {}'.format(song_json['song']['title']))
            print('artist: {}'.format(song_json['song']['artist']))
            print('album: {}'.format(song_json['song']['album']))
            print('release date: {}'.format(song_json['song']['date']))
            
            download_song(song_json)


#download the song
def download_song(_song_json):

    a = ' '
    while a != 'y' or a != 'n':
        
        a = input(
            'Do you want to to download this song [{}] [y/n]? '.format(
                str(round((int(_song_json['song']['size'])/1000000),2))+' MB'
                )
            )
        
        if a.lower() == 'y':
            
            print('\nDOWNLOADING...\n')
            try:
                file_resp = requests.get(_song_json['song']['url'],stream=True)

            except requests.exceptions.ConnectionError:
                print('\tconnection ERROR\n ')
                exit(1)
            
            file_name = _song_json['song']['artist']+" - "+_song_json['song']['title']+".mp3"
            
            total_size = int(file_resp.headers.get('content-length', 0))
            t = tqdm(total=total_size, unit='iB', unit_scale=True)

            with open(file_name,'wb') as file:
                for data in file_resp.iter_content(1024):
                    t.update(len(data)) #update the progress bar
                    file.write(data)
            
            t.close()
            print('DOWNLOAD SUCESSFUL\n')
            break
        
        elif a.lower() == 'n':
            break
        
        else:
            continue
        
    mainfunc()


#main function
def mainfunc():
    
    print("\n===|Songs downloader|===\ntype 'exit' to terminate the program")
    
    srh = input('Name of the song: ')
    if srh.lower() == 'exit':
        exit(0)
    else:
        search_song(srh)


#main function called
mainfunc()
