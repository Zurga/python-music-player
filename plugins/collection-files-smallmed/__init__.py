
import os

import mutagen
import simplejson

from dateutil import parser as dateparser
from mutagen.easyid3 import EasyID3
from dataobjects import Track, Artist, Album

from music_collections.MusicCollection import FullMemoryCollection
from plugins import Plugin

info = {
        'class':        "CollectionFilesSmallMed",
        'author':       "Remco van der Zon",
        'description':  ""
}

class CollectionFilesSmallMed(Plugin):        
    def start(self):
        self.collectionManager.registerNewCollectionType("FilesSmallMedium", SmallMediumFileCollection)

    def stop(self):
        self.collectionManager.deregisterCollectionType("FilesSmallMedium")

"""
First implemented class type. I am not sure yet if this is 'the way to go'.
It reads an entire directory recursively. The result of the search is stored
somewhere. When the list is loaded a second time, the data is quickly loaded
from the list.
"""
class SmallMediumFileCollection(FullMemoryCollection):

    def __init__(self, name, displayname, options):
        root = options['root']
        FullMemoryCollection.__init__(self, name, displayname, False)
        

        if root!=None:
            self.collectionroot = root        
            self.loadfromfile()
        else:
            self.load_tracks_as_json(json)
            
    
    def getAllTracks(self):
        return self._tracks
    
    
    def dump_tracks_as_json(self):
        tracktree = []
        for track in self._tracks:
            tracktree.append(track.serialize())
        return simplejson.dumps(tracktree)
    
    
    def load_tracks_as_json(self, jsonstring):
        for trackdata in simplejson.loads(jsonstring):
            t = Track(None)
            t.load(trackdata)
            self._tracks.append(t)
        self.sortTracks()
        
            
    def writetofile(self):
        #Dump it to a file :)
        f = open(self._cachedir+self._name, 'w')
        f.write(self.dump_tracks_as_json())
        f.close()
            
    
    def loadfromfile(self):
        try:
            f = open(self._cachedir+self._name, 'r')
            self.load_tracks_as_json(f.read())
            f.close()
        except:
            self.scan()
        
        
    def scan(self):
        print "Start scanning SmallMediumFileCollection "+self.collectionroot
        found_tracks = []

        extentions = ["mp3"]

        for (path, dir, files) in os.walk(self.collectionroot):

            for mfile in files:
                if mfile.split(".")[-1] in extentions:
                    try:
                        filename = path+"/"+mfile
                        #audiodata = EasyID3(path+"/"+mfile)
                        audiodata = mutagen.File(filename, easy=True)
                        
                    except:
                        print "Could not open file for EasyID3"
                        break
                    
                    t = Track("file://"+path+"/"+mfile)
                    
                    if "title" in audiodata:        t.title = audiodata["title"][0]
                    if "artist" in audiodata:       t.artist = audiodata["artist"][0]
                    if "album" in audiodata:        t.album = audiodata["album"][0]
                    if "date" in audiodata:
                        try:
                            dt = dateparser.parse(audiodata["date"][0])
                            t.year = dt.year
                        except:
                            t.year = audiodata["date"][0]
                    
                    if "tracknumber" in audiodata: 
                        import re
                        t.tracknumber = int(re.findall(r'\d+', audiodata["tracknumber"][0])[0])

                    t.length = audiodata.info.length


                    found_tracks.append(t)
        
        self._tracks = found_tracks
        self.writetofile()
        self.sortTracks()
        return
    


    