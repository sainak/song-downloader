#credits: erazer

from tqdm import tqdm
import requests
import time
import json

#constants
current_milli_time = lambda: int(round(time.time() * 1000))

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': '*/*',
    'Referer': 'http://musicpleer.cloud/'
    }


#search for the song
def search_song(_srh):
    
    print('SEARCHING...')
    search_url = 'https://databrainz.com/api/search_api.cgi'
    
    search_params = {
        'jsoncallback':'jQuery1111019191608358321144_1580929162911',
        'qry':_srh,#song name goes here
        'format':'json',
        'mh':'10' ,#number of response items
        'where':'mpl'
    }

    search_resp = requests.get(search_url,headers=headers,params=search_params)
    
    if search_resp.text == '':
        print ('no results found\n\n')
        mainfunc()
    else:
        search_json = json.loads(search_resp.text[43:-1])
        print('SONGS FOUND')
        return get_song(search_json)
  

#get the song data from database 
def get_song(_search_json):
    
    song_url = 'https://databrainz.com/api/data_api_new.cgi'
    
    i = 0
    while i <= 10:
        
        song_params = {
            'jsoncallback': 'jQuery1111019191608358321144_1580929162911',
            'id':_search_json['results'][i]['url'] ,#song url goes here
            'r': 'mpl',
            'format': 'json',
            '_':current_milli_time()
        }

        print('FETCHING SONG INFO...')
        song_resp = requests.get(song_url,headers=headers,params=song_params)
        song_json = json.loads(song_resp.text[43:-1])

        if song_json['song']['returncode'] != '200':
            i += 1
            continue

        else:
            print('\n---RESULT---')
            print('title: {}'.format(song_json['song']['title']))
            print('artist: {}'.format(song_json['song']['artist']))
            print('album: {}'.format(song_json['song']['album']))
            print('release date: {}'.format(song_json['song']['date']))
            
            a = ' '
            while a != 'y' or a != 'n':
                
                a = input('Do you want to to download this song [{}] [y/n]? '.format(str(round((int(song_json['song']['size'])/1000000),2))+' MB'))
                
                if a.lower() == 'y':
                    
                    #download the song
                    print('\nDOWNLOADING...\n')
                    file_name = song_json['song']['artist']+" - "+song_json['song']['title']+".mp3"
                    
                    response = requests.get(song_json['song']['url'],stream=True)
                    
                    #progress bar stuff
                    total_size = int(response.headers.get('content-length', 0))
                    block_size = 1024 #1 Kibibyte
                    t=tqdm(total=total_size, unit='iB', unit_scale=True)

                    with open(file_name,'wb') as file:
                        for data in response.iter_content(block_size):
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
    print("\n---Songs downloader---\ntype 'exit' to terminate the program")
    
    srh = input('Name of the song: ')
    if srh.lower() == 'exit':
        pass
    else:
        search_song(srh)

#main function called
mainfunc()
