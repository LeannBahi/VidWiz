# Leann Bahi, lbahi , 15-112 CC
#http://docs.python-requests.org/en/latest/user/quickstart/#json-
#                                                           response-content

import time
import json
import requests
import os

"""
Written with the help of iMuze coordinator : Yacin B.
 - Gave access to token.
 - Explained how to get api to access arrangemnt and how to call arrangement 
    using the desired tags.
"""




#authentication token
token = "Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZSI6InVzZXIiLCJ1c2\
VyX2lkIjoxNTgsImVtYWlsIjoibGVhbm5AZXhhbXBsZS5jb20iLCJleHAiOjg2NDAwfQ.XX0vPcsxO\
9l3RazqpLjl4FS5vrWewwbnuDtei2i-H-4"
api_base_url = 'http://api-imuze.elasticbeanstalk.com/api/4/'

def get_arrangements():
    # get called arrangement from iMuze arrangements library
    url = api_base_url + 'arrangements'
    headers = {'Authorization': token}
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print 'No arrangements. Got an error code:', e
    #if invalid arrangement return error

def create_song(title, tags, desiredLength):
    # create song using tags, given title, and desired arrangement
    url = api_base_url + 'songs'
    headers = {'Authorization': token, 'Content-Type':'application/json'}
    json = ({ 'song': { 'title' : title, 'arrangement_id' : tags, 
        'desired_length' : desiredLength } })
    #try to get api of created song
    try:
        response = requests.post(url, headers=headers, json=json)
        return response.json()
    # otherwise return error
    except requests.exceptions.RequestException as e:
        print 'Failed to create song. Got an error code:', e


def get_song(song_id):
    # get song with asked arrangement 
    url = api_base_url + 'songs/' + str(song_id)
    headers = {'Authorization': token}
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print 'No songs. Got an error code:', e


# Getting a list of all arrangements


def downloadSong(title, tags, desiredLength=7) :
  # Creating a song
    json = create_song(title, tags, desiredLength)
    song = json['response']
    print '-> Composing song'
  # loop and wait till the song is ready
    while (song['mp3_url'] == None):
    # get the song
        json = get_song(song['id'])
        song = json['response']
        print '... status: ' + song['status']
        time.sleep(5)
    link = song['mp3_url']
    print 'Song mp3 URL: ' + link
    currentDirectory = os.path.realpath(".")
    #save song file
    with open('%s/generatedSong.mp3'%currentDirectory, 'wb') as handle:
        response = requests.get(link, stream=True)
        if not response.ok:
            # Something went wrong
            pass
        for block in response.iter_content():
            handle.write(block)


