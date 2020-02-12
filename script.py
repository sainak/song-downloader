#created by aakash714
#download songs from databrainz database
#v3.1

import json
import time

import requests
from tqdm import tqdm


get_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': '*/*',
    'Referer': 'http://musicpleer.cloud/'
}

i = 0
search_response_items = 50 #number of response items

#search for the song in teh database
def search_song(_srh):
    
    print('SEARCHING...')
    search_url = 'https://databrainz.com/api/search_api.cgi'
    
    search_params = {
        'jsoncallback':'jQuery1111019191608358321144_1580929162911',
        'qry':_srh,#song name goes here
        'format':'json',
        'mh':search_response_items,
        'where':'mpl'
    }

    try:
        search_resp = requests.get(search_url,headers=get_headers,params=search_params)
    
    except requests.exceptions.Timeout:
        print('\tconnection timed out RETRYING...\n ')
        search_song(_srh)

    except requests.exceptions.ConnectionError:
        print('\tconnection ERROR\n ')
        exit(1)

    if search_resp.text == '':
        print ('no results found\n')
        
        mainfunc()
    
    else:
        search_json = json.loads(search_resp.text[43:-1])
        print('SONGS FOUND')
        
        return search_json
  
    
#get the song data from database 
def get_song(_search_json):
    
    global i
    song_url = 'https://databrainz.com/api/data_api_new.cgi'
    
    while i <= search_response_items:
        
        song_params = {
            'jsoncallback': 'jQuery1111019191608358321144_1580929162911',
            'id':_search_json['results'][i]['url'] , #song url goes here
            'r': 'mpl',
            'format': 'json',
            '_':int(round(time.time() * 1000))
        }

        print('FETCHING SONG INFO[{}]...'.format(i))
        try:
            song_resp = requests.get(song_url,headers=get_headers,params=song_params)
        
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
            print('size: {} MB'.format(round((int(song_json['song']['size'])/1000000),2)))
            return song_json
            

#download the song
def download_song(_song_json):
            
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
    
    mainfunc()


#main function
def mainfunc():
    
    global i
    i = 0
    
    print("\n===|Songs downloader - by EraZeR|===\ntype 'exit' to terminate the program")
    
    srh = input('Name of the song: ')
    if srh.lower() == 'exit':
        exit(0)
    else:
        search_json = search_song(srh)
        
        song_json = get_song(search_json)
            
    a = ' '
    while a != 'q' or a != 'e':
        
        print('\nEnter')
        print("    'q' to DOWNLOAD the song")
        print("    'w' to search NEXT RESULT")
        print("    'e' to CANCEL")
        
        a = input('  >>>').lower()
        print('')
        
        if a == 'q':
            download_song(song_json)
            break
        
        elif a == 'w':
            i += 1
            song_json = get_song(search_json)
            continue
            
        elif a == 'e':
            break
        
        else:
            continue
        
    mainfunc()
        

#main function called
mainfunc()
