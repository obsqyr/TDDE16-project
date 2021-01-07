#!/usr/bin/env python3
# Make HTTP requests
import requests# Scrape data from an HTML document
from bs4 import BeautifulSoup# I/O
import os# Search and manipulate strings
import re

GENIUS_API_TOKEN = "0XQzXXTW0NX0udf1li-OD3Mm4CWSdfm4TOhya3Wr-AfLiwyv42pAKpMxnzf9cGj5"

# Get artist object from Genius API
def request_artist_info(artist_name, page):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + '/search?per_page=10&page=' + str(page)
    data = {'q': artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response# Get Genius.com song url's from artist object

def request_song_url(artist_name, song_cap):
    page = 1
    songs = []
    
    while True:
        response = request_artist_info(artist_name, page)
        json = response.json()        # Collect up to song_cap song objects from artist
        song_info = []
        if not json['response']['hits']:
            raise Exception('Artist URL not found')
        #print(json['response']['hits'][0]['result'].keys())
        #print(" --- --- --- ")
        #print(json['response']['hits'][0]['result']['primary_artist']['name'])
        for hit in json['response']['hits']: # sorted after hits
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_info.append(hit)
    
        # Collect song URL's from song objects
        for song in song_info:
            if (len(songs) < song_cap):
                url = song['result']['url']
                songs.append(url)
            
        if (len(songs) == song_cap):
            break
        else:
            page += 1
        
    print('Found {} songs by {}'.format(len(songs), artist_name))
    return songs

# Scrape lyrics from a Genius.com song URL
def scrape_song_lyrics(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    #remove identifiers like chorus, verse, etc
    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    #remove empty lines
    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])         
    return lyrics

def write_lyrics_to_file(artist_name, song_count):
    f = open('lyrics/' + artist_name.lower() + '.txt', 'wb+')
    urls = request_song_url(artist_name, song_count)
    for url in urls:
        lyrics = scrape_song_lyrics(url)
        f.write(lyrics.encode("utf8"))
    f.close()
    num_lines = sum(1 for line in open('lyrics/' + artist_name.lower() + '.txt', 'rb'))
    print('Wrote {} lines to file from {} songs'.format(num_lines, song_count))

if __name__ == "__main__":
    #write_lyrics_to_file('Queens of the Stone Age', 2)
    #artist_name = 'queens of the stone age'
    #song_count = 1

    #urls = request_song_url(artist_name, song_count)
    #for url in urls:
    #    lyrics = scrape_song_lyrics(url)
        #print(lyrics)

    #create dictionary 
    
    artist_albums = {'electronic': [], 'experimental' : [],
                     'folk-country' : [], 'global' : [],
                     'jazz' : [], 'metal' : [], 'pop-rnb' : [],
                     'rap' : [], 'rock' : []}
    
    # the genre to scrape
    genre = 'folk-country'
    print("-- Scraping genre: " +  genre + " --")
    
    #for genre in artist_albums.keys():
    f = open("artist_album/"+genre+".txt", "r")
    temp = []
    for artist_album in f.read().split(";"):
        ar_al = artist_album.split('_')
        if len(ar_al) == 2:
            temp.append((ar_al[0], ar_al[1]))
    artist_albums[genre] = temp
    
    song_count = 10
    #for genre, _ in artist_albums.items():
    processed = []
    for ar_al in artist_albums[genre]:
        if ar_al[0] not in processed:
            print("processing " + ar_al[0])
            f = open("lyrics/"+genre+".txt", "a+")
            urls = ""
            try:
                urls = request_song_url(ar_al[0], song_count)
            except Exception as e:
                print("Failed: " + str(e))
                #print(urls)
            for url in urls:
                try:
                    lyrics = scrape_song_lyrics(url)
                    f.write(str(ar_al[0]) + '\n')
                    f.write(lyrics)
                    f.write('\n;\n')
                except Exception as e:
                    print("Failed: " + str(e))
            f.close()
            processed.append(ar_al[0])
        else:
            print(ar_al[0] + " has already been processed")
    print("-- Finished scraping genre: " + genre +" --")
