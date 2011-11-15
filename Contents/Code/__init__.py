# EyeTV plugin for Plex for iOS, by sander1

import re, time

TITLE          = 'LiveTV'
ICON_DEFAULT   = 'icon-default.png'
ICON_PREFS     = 'icon-prefs.png'

STREAM_URL     = 'http://%s'

REMOTE_CONTROL_URL = 'http://%s/streaming_old/directv_remote_control.php?command=%%s'
CHANNEL_THUMB_URL = 'http://%s/tvServices/logos/channel_%%s.png'
CHANNEL_ART_URL   = 'http://%s/tvServices/logos/channel_%%s_art.png'

CHANNEL_DISPLAY = '%s. %s - %s (%s-%s)'
LISTINGS_URL   = 'http://%s/tvServices/listings.php?startLimit=%%d&endLimit=%%d'

STREAMING_SERVER      = 1
REMOTE_CONTROL_SERVER = 2
GUIDE_SERVER          = 3

KEY_UP = 'key%20up'
KEY_DOWN = 'key%20down'
KEY_SELECT = 'key%20select'
KEY_EXIT = 'key%20exit'
KEY_LIST = 'key%20list'
####################################################################################################
def Start():
  Plugin.AddPrefixHandler('/video/livetv', MainMenu, TITLE, ICON_DEFAULT)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='videos')

  ObjectContainer.title1 = TITLE
  ObjectContainer.content = ContainerContent.GenericVideos

  DirectoryObject.thumb = R(ICON_DEFAULT)
  VideoClipObject.thumb  = R(ICON_DEFAULT)

  # Low cachetime because of changing m3u8 urls
  HTTP.CacheTime = 0
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'

####################################################################################################
def MainMenu():
  oc = ObjectContainer(no_cache=True)
  oc.add(DirectoryObject(key=Callback(LiveListings), title='Live Listings'))
  oc.add(DirectoryObject(key=Callback(DvrList), title='DVR Listings'))
  oc.add(PrefsObject(title='Preferences', thumb=R(ICON_PREFS)))

  return oc

####################################################################################################
def LiveListings():
   oc = ObjectContainer(no_cache=True)
   for i in range(10):
      oc.add(DirectoryObject(key=Callback(Live, page=i), title='Channels ' + str(i*100+1) + ' to ' + str(i*100+100)))

   return oc

def Live(page):
   oc = ObjectContainer(no_cache=True, view_group='List')
   url = BuildUrl(LISTINGS_URL, GUIDE_SERVER) % (page*100 + 1, page*100 + 100)
   Log (" --> URL " +  url )
   listings = JSON.ObjectFromURL(url)

   for channel in listings:

      channelNumber = str(channel['number'])
      programTitle = str(channel['title'])
      callSign = str(channel['callSign'])
      startTime = str(channel['start'])
      endTime = str(channel['end'])

      subtitle = str(channel['subtitle'])
      if subtitle == "None": subtitle = ""

      description = str(channel['description'])
      if description == "None": description = ""

      art_url = BuildUrl(CHANNEL_ART_URL, GUIDE_SERVER) % channelNumber
      thumb_url = BuildUrl(CHANNEL_THUMB_URL, GUIDE_SERVER) % channelNumber
      oc.add(VideoClipObject(
         title = CHANNEL_DISPLAY % (channelNumber, callSign, programTitle, startTime, endTime),
         url = BuildUrl(STREAM_URL, STREAMING_SERVER),
         summary = subtitle + "\n" + description,
         art = Callback(GetArt, url=art_url),
         thumb = Callback(GetThumb, url=thumb_url),
         items = [
            MediaObject(
               parts = [
                  PartObject(key=Callback(PlayLiveVideo, channelNumber=channelNumber))
                  ],
               protocols = [Protocol.HTTPVideo],
               platforms = [ClientPlatform.MacOSX],
               video_codec = VideoCodec.H264,
               audio_codec = AudioCodec.AAC,
               video_resolution = 720,
               aspect_ratio = '1.77',
               video_frame_rate = 30
               )
            ]
         ))
   return oc

####################################################################################################
def DvrList():
  # Change the channel
  DvrControl(KEY_LIST)

  # setup the menu
  oc = ObjectContainer(no_cache=True)
  oc.add(VideoClipObject(
     title = "Go to Video/Menu",
     url = BuildUrl(STREAM_URL, STREAMING_SERVER),
     items = [
        MediaObject(
           parts = [
              PartObject(key=Callback(PlayDvr))
              ],
           protocols = [Protocol.HTTPVideo],
           platforms = [ClientPlatform.MacOSX],
           video_codec = VideoCodec.H264,
           audio_codec = AudioCodec.AAC,
           video_resolution = 720,
           aspect_ratio = '1.77',
           video_frame_rate = 30
           )
        ]
     ))
  oc.add(DirectoryObject(key=Callback(DvrControl, key=KEY_UP), title='Up'))
  oc.add(DirectoryObject(key=Callback(DvrControl, key=KEY_DOWN), title='Down'))
  oc.add(DirectoryObject(key=Callback(DvrControl, key=KEY_SELECT), title='Select'))
  oc.add(DirectoryObject(key=Callback(DvrControl, key=KEY_EXIT), title='Exit'))

  return oc

def DvrControl(key):
   # Change the channel to the selected channel
   channel_url = BuildUrl(REMOTE_CONTROL_URL, REMOTE_CONTROL_SERVER) % key
   resp = JSON.ObjectFromURL(channel_url)

def PlayDvr():

   # return the video stream. This is always the same url for all the channels.
   video_url = BuildUrl(STREAM_URL, STREAMING_SERVER)
   return Redirect(video_url)

####################################################################################################
def PlayLiveVideo(channelNumber):
   
   # Change the channel to the selected channel
   channel_url = BuildUrl(REMOTE_CONTROL_URL, REMOTE_CONTROL_SERVER) % channelNumber
   resp = JSON.ObjectFromURL(channel_url)

   # return the video stream. This is always the same url for all the channels.
   video_url = BuildUrl(STREAM_URL, STREAMING_SERVER)
   return Redirect(video_url)

####################################################################################################
def BuildUrl(url, dest):
  
  if dest == STREAMING_SERVER:
     host = Prefs['livetv_streaming_host']
     port = Prefs['livetv_streaming_port']
  elif dest == REMOTE_CONTROL_SERVER:
     host = Prefs['livetv_remote_control_host']
     port = Prefs['livetv_remote_control_port']
  elif dest == GUIDE_SERVER:
     host = Prefs['livetv_guide_host']
     port = Prefs['livetv_guide_port']

  url = url % ':'.join([ host, port ])

  Log(' --> BuildUrl return value: ' + url)
  return url

####################################################################################################
def GetThumb(url):
   try:
      data = HTTP.Request(url, cacheTime=0).content
      return DataObject(data, 'image/png')
   except:
      return Redirect(R(ICON_DEFAULT))

####################################################################################################
def GetArt(url):
   try:
      data = HTTP.Request(url, cacheTime=0).content
      return DataObject(data, 'image/png')
   except:
      return Redirect(R(ICON_DEFAULT))
