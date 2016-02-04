# -*- coding: utf-8 -*-
import re
import os
import sys
from time import strftime, strptime
import time, random

if sys.version_info >=  (2, 7):
    import json as _json
else:
    import simplejson as _json 
    
from cookielib import Cookie
from datetime import datetime, timedelta
from urlparse import urljoin

import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

import mycgi
import utils
from loggingexception import LoggingException
import rtmp

import HTMLParser
from BeautifulSoup import BeautifulSoup

from provider import Provider
from brightcove import BrightCoveProvider
from irishtvplayer import BasePlayer

urlRoot     = u"http://www.aertv.ie"
apiRoot     = u"http://api.aertv.ie"
c_brightcove = u"http://c.brightcove.com"
loginCookieName = u"Aertv_login"
domain = u".aertv.ie"

# Default values only used if we can't get the info from the net, e.g. only used if we can't get the info from the net
defaultRTMPUrl = u"rtmpe://d-deg-mcdn.magnet.ie/rtplive&" 

TIME_FORMAT = u"%Y-%m-%dT%H:%M:%S"

# Exclude channels
excludeChannels = [
                    u'/#aertv-live',
                    u'/#aertv-movies',
                    u'/#aertv-music',
                    u'/#aertv-sports',
                    u'/#unravel-travel',
                    u'/#dail-eireann',
                    u'/#dctv',
                    u'/#ashbourne',
                    u'/#ashbourne-live'
                    ]

# Hard code paths to logos for users who don't want to use EPG
channelToLogo = {
                 
                 u'rte-one' : u'http://www.aertv.ie/wp-content/uploads/2012/04/rte_one_162x129.png',
                 u'rte-two' : u'http://www.aertv.ie/wp-content/uploads/2012/04/rte_two_162x129.png',
                 u'rte-two-hd' : u'http://www.aertv.ie/wp-content/uploads/2012/05/rte_two_hd_162x129.png',
                 u'tv3' : u'http://www.aertv.ie/wp-content/uploads/2012/01/tv3_alt_162x129.png',
                 u'tg4' : u'http://www.aertv.ie/wp-content/uploads/2012/04/tg4_162x129.png',
                 u'3e' : u'http://www.aertv.ie/wp-content/uploads/2012/01/3e_alt_162x129.png',
                 #u'aertv-live' : u'http://www.aertv.ie/wp-content/uploads/2012/02/aertv_live_162x1291.png',
                 #u'aertv-movies' : u'http://www.aertv.ie/wp-content/uploads/2012/02/aertv_movies_162x1291.png',
                 #u'aertv-music' : u'http://www.aertv.ie/wp-content/uploads/2012/01/aertv_music_162x129.png',
                 #u'aertv-sports' : u'http://www.aertv.ie/wp-content/uploads/2012/04/aertv_sports_162x129.png',
                 #u'unravel-travel' : u'http://www.aertv.ie/wp-content/uploads/2012/03/unravel_travel_162x1292.png',
                 #u'dctv' : u'http://www.aertv.ie/wp-content/uploads/2012/04/dctv_162x129.png',
                 u'bbc-one' : u'http://www.aertv.ie/wp-content/uploads/2012/04/bbc_one_162x129.png',
                 u'bbc-two' : u'http://www.aertv.ie/wp-content/uploads/2012/04/bbc_two_162x129.png',
                 u'bbc-three' : u'http://www.aertv.ie/wp-content/uploads/2012/04/bbc_three_162x129.png',
                 u'bbc-four' : u'http://www.aertv.ie/wp-content/uploads/2012/04/bbc_four_162x129.png',
                 u'comedy-central' : u'http://www.aertv.ie/wp-content/uploads/2012/01/comedy_central_new_162x129.png',
                 u'comedy-central-extra' : u'http://www.aertv.ie/wp-content/uploads/2012/01/comedy_central_extra_new_162x129.png',
                 u'rte-one1' : u'http://www.aertv.ie/wp-content/uploads/2012/04/rte_one+1_162x129.png',
                 u'rte-news-now' : u'http://www.aertv.ie/wp-content/uploads/2012/04/rte_news_now_162x129.png',
                 u'bbc-news' : u'http://www.aertv.ie/wp-content/uploads/2012/04/bbc_news_162x129.png',
                 u'euronews' : u'http://www.aertv.ie/wp-content/uploads/2012/04/euronews_162x129.png',
                 u'france24' : u'http://www.aertv.ie/wp-content/uploads/2012/04/france24_162x129.png',
                 u'rt' : u'http://www.aertv.ie/wp-content/uploads/2012/04/russia_today_162x129.png',
                 u'rtejr' : u'http://www.aertv.ie/wp-content/uploads/2012/04/rte_jr_162x129.png',
                 u'cbbc' : u'http://www.aertv.ie/wp-content/uploads/2012/04/cbbc_162x129.png',
                 u'cbeebies' : u'http://www.aertv.ie/wp-content/uploads/2012/04/cbeebies_162x129.png',
                 u'nickelodeon' : u'http://www.aertv.ie/wp-content/uploads/2012/04/nickelodeon_162x129.png',
                 u'nicktoons' : u'http://www.aertv.ie/wp-content/uploads/2012/04/nicktoons_162x129.png',
                 u'nickjnr' : u'http://www.aertv.ie/wp-content/uploads/2012/04/nick_jr_162x129.png',
                 u'mtv' : u'http://www.aertv.ie/wp-content/uploads/2012/04/mtv_162x129.png',
                 u'vh1' : u'http://www.aertv.ie/wp-content/uploads/2012/04/VH1_162x129.png',
                 u'viva' : u'http://www.aertv.ie/wp-content/uploads/2012/04/viva_162x129.png'
                 #u'dail-eireann' : u'http://www.aertv.ie/wp-content/uploads/2012/04/dail_logo_162x129.png'
                 
                 
                 }


class AerTVProvider(BrightCoveProvider):

    def __init__(self):
        super(AerTVProvider, self).__init__()
        self.loggedIn = False
        self.plus = False

    def ShowMe(self):
        AERTV_NOTICE = os.path.join( sys.modules[u"__main__"].PROFILE_DATA_FOLDER, u"aertv_notice" )
        if (len(sys.modules[u"__main__"].addon.getSetting( u'AerTV_email' )) == 0 or len(sys.modules[u"__main__"].addon.getSetting( u'AerTV_password' )) == 0) and xbmcvfs.exists(AERTV_NOTICE):
            return False
        
        return True
            

    def initialise(self, httpManager, baseurl, pluginHandle, addon, language, PROFILE_DATA_FOLDER, RESOURCE_PATH):
        super(AerTVProvider, self).initialise(httpManager, baseurl, pluginHandle, addon, language, PROFILE_DATA_FOLDER, RESOURCE_PATH)
        
        self.aertvNoticeFilePath = os.path.join( sys.modules[u"__main__"].PROFILE_DATA_FOLDER, u"aertv_notice" )
        
        if hasattr(sys.modules[u"__main__"], u"opener"):
            httpManager.SetOpener(sys.modules[u"__main__"].opener)
            
        if hasattr(sys.modules[u"__main__"], u"cookiejar"):
            self.cookiejar = sys.modules[u"__main__"].cookiejar

        return self.Login()
    
    def Login(self):
        self.log(u"", xbmc.LOGDEBUG)
        """
        {
            'epg': 'WEB_STD',
            'user': {
                'decay': 40,
                'email': 'email',
                'fname': 'fname',
                'id': '87354',
                'ipicid': 'aertv530916c892b25',
                'is_paid_subscriber': 0/1,
                'lname': 'lname',
                'login': True,
                'mailchimp': None,
                'packages': [
                    {
                        'code': 'WEB_STD',
                        'desc': 'Free Channel Pack',
                        'package_id': '1'
                    },
                    {
                        "code":"AERTV_PLUS",
                        "desc":"Aertv Plus",
                        "package_id":"6"
                    }                    
                ],
                'session': 'YWVydHY1MzA5MTZjODkyYjI0_1393452432',
                'status': '1',
                'val_code': None
            }
        }
        """
        
        loginJSON = None
        
        email = self.addon.getSetting( u'AerTV_email' ).decode(u'utf8')
        password = self.addon.getSetting( u'AerTV_password' ).decode(u'utf8')
        
        if len(email) == 0 or len(password) == 0:
            if not xbmcvfs.exists(self.aertvNoticeFilePath):
                file = open(self.aertvNoticeFilePath, u'w')
                try:
                    file.write(" ")
                finally:
                    file.close()
                    
                dialog = xbmcgui.Dialog()
                dialog.ok(self.language(30105), self.language(30106))
                
                self.addon.openSettings(sys.argv[ 0 ])
                
                email = self.addon.getSetting( u'AerTV_email' ).decode(u'utf8')
                password = self.addon.getSetting( u'AerTV_password' ).decode(u'utf8')
                
            if len(email) == 0 or len(password) == 0:
                self.log(u"No AerTV login details", xbmc.LOGDEBUG)
                return False

        try:
            loginJSON = self.LoginViaCookie()
        except (Exception) as exception:
            if not isinstance(exception, LoggingException):
                exception = LoggingException.fromException(exception)

            # 'AerTV login failed', 
            exception.addLogMessage(self.language(30101))
            exception.process(severity = self.logLevel(xbmc.LOGWARNING))
        
                
        if loginJSON is None:
            try:
                values = [{u'api':u'login'},{u'user':email},{u'pass':password}]
                loginJSON = self.AttemptLogin(values, logUrl = False)

                self.log(u"After weblogin loginJSON is None: " + unicode(loginJSON is None), xbmc.LOGDEBUG)
                
                if loginJSON is None:
                    # 'AerTV login failed', 
                    exception = LoggingException(self.language(30101))
                    # "Status Message: %s
                    exception.process(severity = self.logLevel(xbmc.LOGERROR))
                    return False
                
                self.log(u"Login successful", xbmc.LOGDEBUG)
                
                sessionId = loginJSON[u'user'][u'session']
                
                days02 = 2*24*60*60
                expiry = int(time.time()) + days02
                    
                self.log(u"Aertv_login expiry: " + unicode(expiry), xbmc.LOGDEBUG)
                
                sessionCookie = self.MakeCookie(u'Aertv_login', sessionId, domain, expiry )
                self.cookiejar.set_cookie(sessionCookie)
                self.cookiejar.save()

                loginJSON = self.LoginViaCookie()
                
            except (Exception) as exception:
                if not isinstance(exception, LoggingException):
                    exception = LoggingException.fromException(exception)
            
                # Error logging into AerTV
                exception.addLogMessage(self.language(30101))
                exception.process(severity = self.logLevel(xbmc.LOGERROR))
                return False
            
        
        self.LogLoginInfo(loginJSON)
        
        if len(utils.getDictionaryValue(loginJSON[u'user'], u'packages')) < 2:
            # Error logging into AerTV
            exception = LoggingException(self.language(30101)) 
            exception.process(severity = self.logLevel(xbmc.LOGERROR))
            return False
        
        return True
        
    def LogLoginInfo(self, loginJSON):
        self.log(u'is_paid_subscriber: %s' % utils.getDictionaryValue(loginJSON[u'user'], u'is_paid_subscriber'))
        self.log(u'login: %s' % utils.getDictionaryValue(loginJSON[u'user'], u'login'))
        self.log(u'status: %s' % utils.getDictionaryValue(loginJSON[u'user'], u'status'))
        
        packages = utils.getDictionaryValue(loginJSON[u'user'], u'packages')
        
        if packages:
            self.log(u'status: %s' % utils.drepr(packages))
    
    def AttemptLogin(self, values, logUrl = False):
        self.log(u"", xbmc.LOGDEBUG)
        try:
            loginJSONText = None
            loginJSON = None
            
            url = self.GetAPIUrl(values)

            loginJSONText = self.httpManager.GetWebPageDirect(url, logUrl = logUrl)
            loginJSON = _json.loads(loginJSONText)
            
            for key in loginJSON:
                self.log(u"loginJSON['%s'] exists" % key, xbmc.LOGDEBUG)
                
            if u'user' in loginJSON:
                self.log(u"loginJSON['user']", xbmc.LOGDEBUG)

                for key in loginJSON[u'user']:
                    if key == u'fname' or key == u'lname' or key == 'email':
                        self.log(u"loginJSON['user']['%s'] exists" % key, xbmc.LOGDEBUG)
                    else:
                        self.log(u"loginJSON['user']['%s'] = %s" % (key, utils.drepr(loginJSON[u'user'][key])), xbmc.LOGDEBUG)
                        
                         
            # Check for failed login
            if loginJSON[u'user'][u'login'] != True:
                # Show error message
                if u'status' in loginJSON[u'user']: 
                    statusMessage = loginJSON[u'user'][u'status']
                else:
                    statusMessage = u"None"
                
                    
                # 'AerTV login failed', 
                logException = LoggingException(self.language(30101))
                # "Status Message: %s
                logException.process(self.language(30102) % statusMessage, u"", xbmc.LOGDEBUG)

                return None
            
            self.log(u"AerTV successful login", xbmc.LOGDEBUG)
            return loginJSON
        except (Exception) as exception:
            if not isinstance(exception, LoggingException):
                exception = LoggingException.fromException(exception)

            if loginJSONText is not None:
                msg = u"loginJSONText:\n\n%s\n\n" % loginJSONText
                exception.addLogMessage(msg)
            
            if loginJSON is not None:
                msg = u"epgJSON:\n\n%s\n\n" % utils.drepr(loginJSON)
                exception.addLogMessage(msg)

            raise exception


    def LoginViaCookie(self):
        self.log(u"", xbmc.LOGDEBUG)
        loginJSON = None
        
        # List all the cookies with the matching name. Result is either an empty list, or a list with a single item
        loginCookieList = [cookie for cookie in self.cookiejar if cookie.name == loginCookieName]
        
        if len(loginCookieList) == 0:
            self.log(u"No AerTV_login cookie", xbmc.LOGDEBUG)
            return None
        
        loginCookie = loginCookieList[0]
        
        now = time.time()
        if loginCookie.is_expired(now):
            self.log(u"AerTV_login cookie expired", xbmc.LOGDEBUG)
            return None
        
        values = [{u'api':u'cookie'}, {u'login':u'web'}]
        loginJSON = self.AttemptLogin(values)
        
        return loginJSON
    

    def GetProviderId(self):
        return u"AerTV"

    def ExecuteCommand(self, mycgi):
        return super(AerTVProvider, self).ExecuteCommand(mycgi)

    def ShowRootMenu(self):
        self.log(u"", xbmc.LOGDEBUG)
        
        try:
            channels = None
            epgJSON = None 
            
            channels = self.GetAvailableChannels()
            
            if self.addon.getSetting( u'AerTV_show_epg' ) <> u'false':
                values = [{u'api':u'epg'}, {u'type':u'basic'}]
                url = self.GetAPIUrl(values)
                
                epgJSONText = self.httpManager.GetWebPage(url, 300)
                
                self.log(u"epgJSONText: \n\n%s\n\n" % epgJSONText, xbmc.LOGDEBUG)
                
                epgJSON = _json.loads(epgJSONText)
                
                return self.ShowEPG(channels, epgJSON)
            else:
                return self.ShowChannelList(channels)
        
        except (Exception) as exception:
            if not isinstance(exception, LoggingException):
                exception = LoggingException.fromException(exception)

            if epgJSON is not None:
                msg=u"epgJSON:\n\n%s\n\n" % utils.drepr(epgJSON)
                exception.addLogMessage(msg)

            if channels is not None:
                msg=u"channels:\n\n%s\n\n" % utils.drepr(channels)
                exception.addLogMessage(msg)

            # Cannot show root menu
            exception.addLogMessage(self.language(30010))
            exception.process(severity = self.logLevel(xbmc.LOGERROR))
            return False

    def GetAvailableChannels(self):
        html = self.httpManager.GetWebPage(urlRoot, 300)    
        
        self.log(u"Root url: \n\n%s\n\n" % html, xbmc.LOGDEBUG)

        soup = BeautifulSoup(html)
        
        channels = []
        for channel in soup.findAll('a', 'live-channel'):
             if len(channel('span')) > 0 or channel[u'href'] in excludeChannels:
                     continue
             channels.append(channel)
        
        return channels
    
    def GetAPIUrl(self, parameters):
        # {'api':'ddl', 'type':'basic'} => www.apiRoot.com/api/ddl/type/basic
        url = apiRoot
        
        for keyValue in parameters:
            key = [key for key in keyValue][0]
            url = url + u'/' + key + u'/' + keyValue[key]
            
        return url

    def ParseCommand(self, mycgi):
        self.log(u"", xbmc.LOGDEBUG)
        (channel, logo, loggedInStr) = mycgi.Params( u'channel', u'logo', u'loggedIn') 
       
        if loggedInStr == u'1':
            self.loggedIn = True
            
        if channel <> u'':
            if logo == u'' and channel in channelToLogo:
                logo = channelToLogo[channel]
                    
            return self.PlayVideoWithDialog(self.PlayChannel, (channel, logo))

        return False
    

    def ShowChannelList(self, channels):
        self.log(u"", xbmc.LOGDEBUG)
        
        listItems = []

        for anchor in channels:
            try:
                playerIndex = anchor[u'href'].find(u'#')
                if playerIndex == -1:
                    continue

                slug = anchor[u'href'][playerIndex + 1:]

                newLabel = anchor.text
                description = newLabel
                logo = channelToLogo[slug]
                
                newListItem = xbmcgui.ListItem( label=newLabel )
                newListItem.setThumbnailImage(logo)
                channelUrl = self.GetURLStart() + u'&channel=' + slug + u'&logo=' + mycgi.URLEscape(logo)
                
                infoLabels = {u'Title': newLabel, u'Plot': description, u'PlotOutline': description}
    
                newListItem.setInfo(u'video', infoLabels)
                newListItem.setProperty(u"Video", u"true")

                listItems.append( (channelUrl, newListItem, False) )
            except (Exception) as exception:
                # Problem getting details for a particular channel, show a warning and keep going 
                if not isinstance(exception, LoggingException):
                    exception = LoggingException.fromException(exception)
    
                # Error processing channel 
                message = self.language(30067)
            
                try:
                    message = message + u" " + anchor.text
                    #message = message.encode('utf8')
                except NameError:
                    pass
                      
                exception.addLogMessage(message)
                exception.process(severity = self.logLevel(xbmc.LOGWARNING))
            

        xbmcplugin.addDirectoryItems( handle=self.pluginHandle, items=listItems )
        xbmcplugin.endOfDirectory( handle=self.pluginHandle, succeeded=True )
        
        return True

    def ShowEPG(self, channels, epgJSON):
        self.log(u"", xbmc.LOGDEBUG)
    
        channelDetails = self.ParseEPGData(epgJSON)
        
        listItems = []

        for anchor in channels:
            try:
                playerIndex = anchor[u'href'].find(u'#')
                if playerIndex == -1:
                    continue

                slug = anchor[u'href'][playerIndex + 1:]

                (label, description, logo) = self.GetListItemDataForSlug(channelDetails, slug)
                newLabel = anchor.text + " " + label
                
                newListItem = xbmcgui.ListItem( label=newLabel )
                newListItem.setThumbnailImage(logo)
                channelUrl = self.GetURLStart() + u'&channel=' + slug + u'&logo=' + mycgi.URLEscape(logo) 
                
                infoLabels = {u'Title': newLabel, u'Plot': description, u'PlotOutline': description}
    
                newListItem.setInfo(u'video', infoLabels)
                newListItem.setProperty(u"Video", u"true")

                listItems.append( (channelUrl, newListItem, False) )
            except (Exception) as exception:
                # Problem getting details for a particular channel, show a warning and keep going 
                if not isinstance(exception, LoggingException):
                    exception = LoggingException.fromException(exception)
    
                # Error processing channel 
                message = self.language(30067)
            
                try:
                    message = message + u" " + anchor.text
                    #message = message.encode('utf8')
                except NameError:
                    pass
                      
                exception.addLogMessage(message)
                exception.process(severity = self.logLevel(xbmc.LOGWARNING))
            

        xbmcplugin.addDirectoryItems( handle=self.pluginHandle, items=listItems )
        xbmcplugin.endOfDirectory( handle=self.pluginHandle, succeeded=True )
        
        return True

    def GetTimeCutOffs(self):
        offset = int(self.addon.getSetting( u'AerTV_epg_offset' ))
        startCutOff =  datetime.now() + timedelta(hours=offset)
        startCutOff = startCutOff.replace(second=0,microsecond=0)

        # round time
        if startCutOff.minute > 29:
            startRound = startCutOff.replace(minute=30)
        else:
            startRound = startCutOff.replace(minute=0)
            
        endCutOff = startRound + timedelta(hours=2)

        return (startCutOff, endCutOff)

    def GetEPGDetails(self, channelEntry, startCutOff, endCutOff):
        detail = [channelEntry[u'channel'][u'logo']]
        videoCount = 0

        self.log(u"startCutOff: %s, endCutOff: %s" % (repr(startCutOff), repr(endCutOff)), xbmc.LOGDEBUG)
        for video in channelEntry[u'videos']:
            try:
                self.log(u"repr(datetime): " + repr(datetime))
                self.log(u"video: " + utils.drepr(video))
                self.log(u"video['starttime']: " + video[u'starttime'])

                try:
                    startTime = datetime.strptime(video[u'starttime'], TIME_FORMAT)
                    endTime = datetime.strptime(video[u'endtime'], TIME_FORMAT)
                except TypeError:
                    startTime = datetime.fromtimestamp(time.mktime(time.strptime(video[u'starttime'], TIME_FORMAT)))
                    endTime = datetime.fromtimestamp(time.mktime(time.strptime(video[u'endtime'], TIME_FORMAT)))
                    
                if startTime >= startCutOff and startTime < endCutOff:
                    self.log(u"startTime >= startCutOff and startTime < endCutOff", xbmc.LOGDEBUG)
                    videoCount = videoCount + 1
    
                    if endTime > endCutOff:
                        self.log(u"endTime > endCutOff", xbmc.LOGDEBUG)
                        # Add "Now ... Ends at ..." if count is 0, or "Next..."
                        detail.append(video) 
                        break
                    else:
                        self.log(u"endTime <= endCutOff", xbmc.LOGDEBUG)
                        # Add Now .../Next ... depending on count
                        detail.append(video) 
    
                elif startTime < startCutOff and endTime > startCutOff:
                    self.log(u"startTime < startCutOff and endTime > startCutOff", xbmc.LOGDEBUG)
                    videoCount = videoCount + 1
    
                    # Add Now .../Next ... depending on count
                    detail.append(video)
                else:
                    self.log(u"Ignoring video: " + video[u'name'])
                    
                if (videoCount > 1):
                    break
            except (Exception) as exception:
                if not isinstance(exception, LoggingException):
                    exception = LoggingException.fromException(exception)
    
                self.log(u"video: %s" % repr(video))
                
                # Error processing EPG entry
                exception.addLogMessage(self.language(30027))
                exception.printLogMessages(severity = xbmc.LOGWARNING)

        return detail
    
    #TODO Consider breaking the epgJSON processing into a separate class
    def ParseEPGData(self, epgJSON):
        (startCutOff, endCutOff) = self.GetTimeCutOffs()
        channelDetails = {}
    
        # Using slug as the identifier for each channel, create a dictionary that allows details of each channel to be looked up by slug.
        for channelEntry in epgJSON[u'data']:
            slug = channelEntry[u'channel'][u'slug']
            
            detail = self.GetEPGDetails(channelEntry, startCutOff, endCutOff)
                 
            """
            # Now
            if len(channelEntry['videos']) > 0:
                detail.append(channelEntry['videos'][0])

                # Next
                if len(channelEntry['videos']) > 1:
                    detail.append(channelEntry['videos'][1])

            """
            channelDetails[slug] = detail

        return channelDetails

    def GetListItemData(self, detail):
        description = ''
        if len(detail) == 1:
            label = u'Unknown or Off Air'
            self.log(repr(detail))
        else:
            description = detail[1][u'description']
            label = detail[1][u'name']
            if len(detail) > 2:
                # E.g. "Nuacht [18:00 Six One]"
                startTime = strptime(detail[2][u'starttime'], TIME_FORMAT)
                label = u"   " + label + u"   [  " + strftime(u"%H:%M", startTime) + u"  " + detail[2][u'name']  + u"  ]"
            else:
                # E.g. "Nuacht [  Ends at 18:00  ]"
                endTime = strptime(detail[1][u'endtime'], TIME_FORMAT)
                label = u"   " + label + u"   [  Ends at " + strftime(u"%H:%M", endTime) + u"  ]"
        
        return label, description, detail[0]

        
    def GetListItemDataForSlug(self, channelDetails, slug):
        detail = channelDetails[slug]

        return self.GetListItemData(detail)
    

    def PlayChannel(self, channel, logo):
        """
        RTE 1 jQuery110109518442715161376_1395526161546(
        {
         "player":"Get player here from post ",
         "data":{
             "post_id":"17",
             "freebie":true,
             "auth":true,
             "magonly":false,
             "channel":"RT\u00c9 One",
             "internal":"off",
             "streamname":"",
             "free":true,
             "videoId":"rte-one",
             "publisherId":"1242843906001",
             "playerId":"1454761980001",
             "playerKey":"AQ~~,AAABIV9E_9E~,lGDQr89oSbKT02RqV22r-E007AitVINH",
             "appStreamUrl":"",
             "show":"The Saturday Night Show"
            },
        "flag":"new"
        })
        """
        try:
            jsonData = None
            values = [{u'api':u'player'}, {u'type':u'name'}, {u'val':channel}]
            url = self.GetAPIUrl(values)
        
            # "Getting channel information"
            self.dialog.update(10, self.language(30107))

            jsonData = self.httpManager.GetWebPage(url, 20000)
            playerJSON=_json.loads(jsonData)
            self.log(u"json data:" + unicode(playerJSON))
            
            playerId = playerJSON[u'data'][u'playerId']
            publisherId = playerJSON[u'data'][u'publisherId']
            playerKey = playerJSON[u'data'][u'playerKey']
    
            viewExperienceUrl = urlRoot + u'/#' + channel
            
            streamType = unicode(self.addon.getSetting( u'AerTV_stream_type' ))
            self.log(u"Stream type setting: " + streamType)
            
            try:
                if self.dialog.iscanceled():
                    return False
                # "Getting stream url"
                self.dialog.update(25, self.language(30087))
                streamUrl = self.GetStreamUrl(playerKey, viewExperienceUrl, playerId, contentRefId = channel, streamType = streamType)
                self.log(u"streamUrl: %s" % streamUrl)
            except (Exception) as exception:
                if not isinstance(exception, LoggingException):
                    exception = LoggingException.fromException(exception)
    
                self.log(u" channel: %s" % channel)

                # Error getting rtmp url.
                exception.addLogMessage(self.language(30066))
                # Cannot play video stream
                raise exception
                
            if self.dialog.iscanceled():
                return False
            # "Getting \"Now Playing\" data
            self.dialog.update(35, self.language(30088))

            # Set up info for "Now Playing" screen
            infoLabels = self.GetInfoLabels(playerJSON)

            #RTMP
            if streamUrl.upper().startswith(self.language(30081)):
                playPathIndex = streamUrl.index(u'&') + 1
                playPath = streamUrl[playPathIndex:]
                qsData = self.GetQSData(channel, playerId, publisherId, playerKey)
                swfUrl = self.GetSwfUrl(qsData)
                pageUrl = urlRoot
                
                if u'videoId' in playerJSON[u'data']:
                    videoId = playerJSON[u'data'][u'videoId']
                else:
                    videoId = playerJSON[u'data'][u'offset'][u'videos'][0]
                    
                app = u"rtplive?videoId=%s&lineUpId=&pubId=%s&playerId=%s" % (videoId, publisherId, playerId)
                rtmpVar = rtmp.RTMP(rtmp = streamUrl, app = app, swfUrl = swfUrl, playPath = playPath, pageUrl = pageUrl, live = True)
                self.AddSocksToRTMP(rtmpVar)
                
                self.Play(infoLabels, logo, rtmpVar)            
            else:
                self.Play(infoLabels, logo, url = streamUrl)
            return True
       
        except (Exception) as exception:
            if not isinstance(exception, LoggingException):
                exception = LoggingException.fromException(exception)

            if jsonData is not None:
                msg = u"jsonData:\n\n%s\n\n" % jsonData
                exception.addLogMessage(msg)
            
            # Error preparing or playing stream
            exception.addLogMessage(self.language(30066))
            exception.process(severity = self.logLevel(xbmc.LOGERROR))
            return False

    def GetInfoLabels(self, playerJSON):
        infoLabels = None
        
        try:
            channel = playerJSON['data']['channel']
            label = channel + u"   " + playerJSON['data']['show']
            description = label
            infoLabels = {u'Title': label, u'Plot': description}
        except (Exception) as exception:
            if not isinstance(exception, LoggingException):
                exception = LoggingException.fromException(exception)

            # Error getting title and logo info for %s
            exception.addLogMessage(self.language(30068) % channel)
            exception.process(severity = xbmc.LOGWARNING)

        return infoLabels

        
    def GetEpgJSON(self, url):
        epgJSONText = self.httpManager.GetWebPage(url, 0)
        epgJSON = _json.loads(epgJSONText)
        
        return epgJSON 
            
    """
    {
        'TTLToken': '',
        'URL': u'https://www.aertv.ie/#rte-one',
        'contentOverrides': [
            {
                'contentId': nan,
                'contentIds': None,
                'contentRefId': u'rte-one',
                'contentRefIds': None,
                'contentType': 0,
                'featuredId': nan,
                'featuredRefId': None,
                'target': u'videoPlayer'
            }
        ],
        'deliveryType': nan,
        'experienceId': 1535624864001.0,
        'playerKey': u'AQ~~,AAABIV9E_9E~,lGDQr89oSbJf6x1rDuEAWKPqTYfK-JH2'
    },
    u'a7ef6ffbfba938b174f5044af3343163a0877c48'
    """
    def GetAmfClassHash(self, className):
        return u'a7ef6ffbfba938b174f5044af3343163a0877c48'
    

    def GetQSData(self, videoPlayer, playerId, publisherId, playerKey):
        #TODO Use a default url, in case of exception and log response
        qsdata = {}
        qsdata[u'width'] = u'100%'
        qsdata[u'height'] = u'100%'
        qsdata[u'flashID'] = u'aertv'
        qsdata[u'playerID'] = playerId
        qsdata[u'purl'] = urlRoot
        qsdata[u'@videoPlayer'] = videoPlayer
        qsdata[u'playerKey'] = playerKey
        qsdata[u'publisherID'] = publisherId
        qsdata[u'bgcolor'] = u'#FFFFFF'
        qsdata[u'isVid'] = u'true'
        qsdata[u'isUI'] = u'true'
        qsdata[u'autostart'] = u'true'
        qsdata[u'wmode'] = u'transparent'
        qsdata[u'localizedErrorXML'] = u'https://aertv.ie/wp-content/themes/aertv/aertv-custom-error-messages.xml'
        qsdata[u'templateLoadHandler'] = u'liveTemplateLoaded'
        qsdata[u'includeAPI'] = u'true'
        qsdata[u'debuggerID'] = u''
        qsdata[u'isUI'] = u'true'
        
        return qsdata    
    
