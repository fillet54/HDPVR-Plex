# EyeTV plugin for Plex for iOS, by sander1

import re, time

TITLE          = 'LiveTV'
ICON_DEFAULT   = 'icon-default.png'
ICON_PREFS     = 'icon-prefs.png'

STREAM_URL     = 'http://%s'

CHANGE_CH_URL = 'http://philgomez.com/streaming_old/directv_remote_control.php?command=%s'
CHANNEL_THUMB_URL = 'http://philgomez.com/tvServices/logos/%s'

LISTINGS_URL   = 'http://philgomez.com/tvServices/listings.php?startLimit=%d&endLimit=%d'

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
   url = LISTINGS_URL % (page*100 + 1, page*100 + 100)
   Log (" --> URL " +  url )
   listings = JSON.ObjectFromURL(url)

   for channel in listings:

      subtitle = str(channel['subtitle'])
      if subtitle == "None": subtitle = ""

      description = str(channel['description'])
      if description == "None": description = ""

      oc.add(VideoClipObject(
         title = str(channel['number']) + '. ' + str(channel['callSign']) + " - " + str(channel['title']),
         url = BuildUrl(STREAM_URL),
         summary = subtitle + "\n" + description,
         items = [
            MediaObject(
               parts = [
                  PartObject(key=Callback(PlayLiveVideo, channelNumber=channel['number']))
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
def PlayLiveVideo(channelNumber):
   
   channel_url = CHANGE_CH_URL % channelNumber
   resp = JSON.ObjectFromURL(channel_url)
   video_url = BuildUrl(STREAM_URL)
   return Redirect(video_url)

####################################################################################################
def BuildUrl(url):
  url = url % ':'.join([ Prefs['livetv_host_pms'], Prefs['livetv_port_pms'] ])

  Log(' --> BuildUrl return value: ' + url)
  return url

####################################################################################################
def GetThumb(url):
   try:
      Log ('  --> THUMB URL: ' + url)
      data = HTTP.Request(url, cacheTime=0).content
      return DataObject(data, 'image/jpeg')
   except:
      return Redirect(R(ICON_DEFAULT))
