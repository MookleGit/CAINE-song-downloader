from pytube import YouTube
from pydub import AudioSegment
import ffmpeg
import os
import pandas as pd

print("MAKE SURE THE GOOGLE SHEETS IS AVAILABLE TO VIEW FOR ANYONE WITH LINK!!!")
print("ALSO MAKE SURE THE ROW ABOVE THE LINKS IS NAMED 'LINK'")

quit = ""
while (quit != "q"):
    try:
        link = str(input("Enter the URL of the google sheets page. Enter q to quit program. \n"))
        if (link == "q"):
            quit = "q"  
            break
        # filter input string to convert it into an export format for pandas
        if ((link.find("/edit") > -1) & (quit != "q")):
            link = link[0:link.find("/edit")]
        if ((link.find("/export") < 0) & (quit != "q")):
            link = link + "/export?gid=0&format=csv"
        g_sheet = pd.read_csv(link, index_col=0)
    except:
        print("URL is incorrect, or couldn't read from it")
    else:
        break

while quit != "q":
    try:
        start_row = int(input("Which row is the first song in the list?\n")) - 3
        songList = g_sheet.drop(g_sheet.index[range(start_row)])
        # move the headers
        header = songList.iloc[0]
        print(header)
        songList = songList[1:]

        songList.columns = header

        print(songList) # print list to make it clearer

        numSongs = int(input("How many songs do you have total?\n"))
        duration = input("How long do you want the songs to be downloaded as? Input 0 for full song, press enter to default to 30 seconds after timestamp.")
        if (duration == ""):
            print("Defaulting to 30 seconds.....")
            duration = int(30)
        else:
            duration = int(duration)
    except:
        print("Please enter a valid number!")
    else:
        break

if (quit != "q"):
    # create directories for the songs & trims if they do not exist.
    path = os.getcwd()

    songpath = os.path.join(path, "songs")
    trimpath = os.path.join(path, "trims")

    if (not(os.path.exists(songpath))): # check if songs folder exists
        print("making song directory")
        os.mkdir(os.path.join(path, "songs"))

    if (not(os.path.exists(trimpath))): # check if trims folder exists
        print("making trim directory")
        os.mkdir(os.path.join(path, "trims"))
        
    bugged_links = []
    for song in range(numSongs):
        link = songList["Link"][song]
        title = str(songList["Title"][song])
        # print("Does this exist? " + os.path.join(path, "songs/" + str(song+1) + ".mp3")) # meant for debugging

        if (not(os.path.exists(os.path.join(songpath, str(song+1) + ".mp3")))):
            print("Downloading: "  + title + " Link: " + str(link))
            yt = YouTube(link)

            # check for timestamp in the link. There are two forms of links
            timestamp = 0
            if (link.find("&t=") > -1):
                timestamp = str(link)[link.find("&t=")+3:link.rfind("s")]
                timestamp = int(timestamp) * 1000
                print("timestamp at: " + str(timestamp))
            elif (link.find("?t=") > -1):
                timestamp = str(link)[link.find("?t=")+3:]
                timestamp = int(timestamp) * 1000
                print("timestamp at: " + str(timestamp))
            
            # we do a try except in the case that the yt link no longer works
            try:
                # obtain the audio from yt link
                audio = yt.streams.filter(only_audio=True).first()
                audio.download(output_path=songpath, filename=str(song+1) + ".mp3")

                # prepare for ffmpeg audio processing
                cur_song = AudioSegment.from_file(songpath + "/" + str(song+1) + ".mp3")

                # Trim the song to duration given. If song ends before
                # timestamp + duration, trim to end of song.
                if (duration != 0):
                    print("trimming song")
                    if (not((timestamp + int(duration)*1000) > len(cur_song))):
                        cur_song = cur_song[timestamp:timestamp+(int(duration)*1000)]
                    else:
                        print("trimming to end of song")
                        cur_song = cur_song[timestamp:int(len(cur_song))]
                # export from audio process back into mp3
                cur_song.export(trimpath + "/" + str(song+1) + "_trim.mp3", format="mp3")

            except:
                print(title + " can't be downloaded! Is the link still valid?")
                bugged_links.append(title)
        else:
            print("song " + str(song+1) + " already downloaded?")
    # print links that were not downloadable
    if (len(bugged_links) > 0):
        print("These songs were unable to be downloaded. Check if the link is valid.")
        for l in bugged_links:
            print(l)

    print("download complete!")
    # This is so the pyinstaller .exe doesn't immediately close.
    input("Enter anything to close program.....")
else:
    print("Closing program...")
