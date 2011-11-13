# EyeTV plugin for Plex for iOS, by sander1

import re, time

TITLE          = 'LiveTV'
ICON_DEFAULT   = 'icon-default.png'
ICON_PREFS     = 'icon-prefs.png'

STREAM_URL     = 'http://%s'

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
  oc.add(DirectoryObject(key=Callback(Live), title='Live TV'))
  oc.add(PrefsObject(title='Preferences', thumb=R(ICON_PREFS)))

  return oc

####################################################################################################
def Live():
   oc = ObjectContainer(no_cache=True, view_group='List')
   oc.add(VideoClipObject(
      title = 'Channel 710',
      url = BuildUrl(STREAM_URL),
      items = [
         MediaObject(
            parts = [
               PartObject(key=Callback(PlayLiveVideo, serviceID='710'))
               ],
            protocols = [Protocol.HTTPVideo],
            platforms = [ClientPlatform.MacOSX],
            video_codec = VideoCodec.H264,
            audio_codec = AudioCodec.AAC
            )
         ]
      ))
   return oc

####################################################################################################
def PlayLiveVideo(serviceID):
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
    data = HTTP.Request(url, cacheTime=CACHE_1DAY).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON_DEFAULT))
