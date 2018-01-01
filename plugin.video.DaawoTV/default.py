# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin
import urllib2,urllib,cgi, re
import HTMLParser
import xbmcaddon
import json
import traceback
import os
import sys
import cookielib
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP, Tag,NavigableString
try:
  from lxmlERRRORRRR import etree
  print("running with lxml.etree")
except ImportError:
	try:
	  # Python 2.5
	  import xml.etree.ElementTree as etree
	  print("running with ElementTree on Python 2.5+")
	except ImportError:
	  try:
		# normal cElementTree install
		import cElementTree as etree
		print("running with cElementTree")
	  except ImportError:
		try:
		  # normal ElementTree install
		  import elementtree.ElementTree as etree
		  print("running with ElementTree")
		except ImportError:
		  print("Failed to import ElementTree from any known place")

import json

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')
__icon__        = __addon__.getAddonInfo('icon')
addon_id = 'plugin.video.DaawoTV'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonPath = xbmcaddon.Addon().getAddonInfo("path")
addonversion =xbmcaddon.Addon().getAddonInfo("version")
addonArt = os.path.join(addonPath,'resources/images')
communityStreamPath = os.path.join(addonPath,'resources')
communityStreamPath =os.path.join(communityStreamPath,'community')
profile_path =  xbmc.translatePath(selfAddon.getAddonInfo('profile'))


VIEW_MODES = {
    'thumbnail': {
        'skin.confluence': 500,
        'skin.aeon.nox': 551,
        'skin.confluence-vertical': 500,
        'skin.jx720': 52,
        'skin.pm3-hd': 53,
        'skin.rapier': 50,
        'skin.simplicity': 500,
        'skin.slik': 53,
        'skin.touched': 500,
        'skin.transparency': 53,
        'skin.xeebo': 55,
    },
}

def get_view_mode_id( view_mode):
	default_view_mode=selfAddon.getSetting( "usethisviewmode" )
	if default_view_mode=="":
		view_mode_ids = VIEW_MODES.get(view_mode.lower())
		if view_mode_ids:
			return view_mode_ids.get(xbmc.getSkinDir())
	else:
		return int(default_view_mode)
	return None

def addLink(name,url,iconimage):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

def Colored(text = '', colorid = '', isBold = False):
	if colorid == 'one':
		color = 'FF11b500'
	elif colorid == 'two':
		color = 'FFe37101'
	elif colorid == 'bold':
		return '[B]' + text + '[/B]'
	else:
		color = colorid
		
	if isBold == True:
		text = '[B]' + text + '[/B]'
	return '[COLOR ' + color + ']' + text + '[/COLOR]'	
	
def addDir(name,url,mode,iconimage	,showContext=False,isItFolder=True,pageNumber="", isHTML=True,addIconForPlaylist=False, AddRemoveMyChannels=None, SelectDefaultSource=None, hideChannel=None, BySource=None, dontparse=True):
#	print name
#	name=name.decode('utf-8','replace')
	rname=name
	if not dontparse:
		if isHTML:
			h = HTMLParser.HTMLParser()
			name= h.unescape(name).decode("utf-8")
			rname=  name.encode("utf-8")
		else:
			rname=  name.encode("utf-8")
			
			
	#print rname
	#print iconimage
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(rname)

	if BySource:
		u+="&sourceFilter="+urllib.quote_plus(BySource)
	if len(pageNumber):
		u+="&pagenum="+pageNumber
	if addIconForPlaylist:
		u+="&addIconForPlaylist=yes"
	ok=True
#	print iconimage
	liz=xbmcgui.ListItem(rname, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	#liz.setInfo( type="Video", infoLabels={ "Title": name } )

	if showContext==True:
		cmd1 = "XBMC.RunPlugin(%s&cdnType=%s)" % (u, "l3")
		cmd2 = "XBMC.RunPlugin(%s&cdnType=%s)" % (u, "xdn")
		cmd3 = "XBMC.RunPlugin(%s&cdnType=%s)" % (u, "ak")
		liz.addContextMenuItems([('Play using L3 Cdn',cmd1),('Play using XDN Cdn',cmd2),('Play using AK Cdn',cmd3)])

	context_menu=[]
	if not AddRemoveMyChannels==None:
		if AddRemoveMyChannels:
			cmd1 = "XBMC.RunPlugin(%s&AddRemoveMyChannels=add)" % (u)
			context_menu.append(('Add to My Channels',cmd1))
		else:
			cmd1 = "XBMC.RunPlugin(%s&AddRemoveMyChannels=remove)" % (u)
			context_menu.append(('Remove from My Channels',cmd1))


	if SelectDefaultSource:
		#print 'select defauly'
		cmd2 = "XBMC.RunPlugin(%s&selectDefaultSource=yes)" % (u)
		context_menu.append(('Select default source',cmd2))

	if not hideChannel==None:
		if hideChannel:
			cmd3 = "XBMC.RunPlugin(%s&HideChannel=yes)" % (u)
			context_menu.append(('Hide this Channel',cmd3))
		else:
			cmd3 = "XBMC.RunPlugin(%s&HideChannel=no)" % (u)
			context_menu.append(('Unhide this Channel',cmd3))

            
	if len(context_menu)>0:
		liz.addContextMenuItems(context_menu,replaceItems=False)
		
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isItFolder)
	return ok
	
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
				
	return param

def Addtypes():
	addDir('Live TV' ,'CCats' ,14,addonArt+'/Network-1-icon.png')
	addDir('Download Files' ,'cRefresh' ,17,addonArt+'/download-icon.png',isItFolder=False)
	addDir('Settings' ,'Settings' ,8,addonArt+'/setting.png',isItFolder=False) 
	return

	
def checkAndRefresh():
	try:
		import time
		lastUpdate=selfAddon.getSetting( "lastupdate" )
		do_update=False
		now_date=time.strftime("%d/%m/%Y")
		if lastUpdate==None or lastUpdate=="":
			do_update=True
		else:
			#print 'lastUpdate',lastUpdate,now_date
			if not now_date==lastUpdate:
				do_update=True
		if selfAddon.getSetting( "stopAutoUpdate" )=="true": do_update=False
		selfAddon.setSetting( id="lastupdate" ,value=now_date)
		if do_update:
			RefreshResources(True)
	except: pass

def RefreshResources(auto=False, fNameOnly=None):
#	print Fromurl
	pDialog = xbmcgui.DialogProgress()
	if auto:
		ret = pDialog.create('XBMC', 'Daily Auto loading Fetching resources...')
	else:
		ret = pDialog.create('XBMC', 'Fetching resources...')
	baseUrlForDownload='https://raw.githubusercontent.com/xamarcade/DaawoTV/master/plugin.video.DaawoTV/resources/community/'
	Fromurl=baseUrlForDownload+'Resources.xml'
	req = urllib2.Request(Fromurl)
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
	req.add_header('Referer','http://shahidaddon/')
	response = urllib2.urlopen(req)
	data=response.read()
	response.close()
	#data='<resources><file fname="Categories.xml"/><file fname="palestinecoolUrls.xml" url="http://goo.gl/yNlwCM"/></resources>'
	pDialog.update(20, 'Importing modules...')
	soup= BeautifulSOAP(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
	resources=soup('file')
	fileno=1
	totalFile = len(resources)
	import hashlib
	for rfile in resources:
		if pDialog.iscanceled(): return
		progr = (fileno*80)/totalFile
		fname = rfile['fname']
		if fNameOnly and not fname==fNameOnly: continue
		remoteUrl=None
		try:
			remoteUrl = rfile['url']
		except: pass
		isBase64=False
		try:
			isBase64= rfile['base64']=="true"
		except: pass
		if remoteUrl:
			fileToDownload = remoteUrl
		else:
			fileToDownload = baseUrlForDownload+fname
		fileHash=hashlib.md5(fileToDownload+addonversion).hexdigest()
		lastFileTime=selfAddon.getSetting( "Etagid"+fileHash)  
		if lastFileTime=="": lastFileTime=None
		resCode=200
		#print fileToDownload
		eTag=None        
		try:
			req = urllib2.Request(fileToDownload)
			req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
			req.add_header('Referer','http://shahidaddon/')

			if lastFileTime:
				req.add_header('If-None-Match',lastFileTime)
			response = urllib2.urlopen(req)
			resCode=response.getcode()
			if resCode<>304:
				try:
					eTag=response.info().getheader('Etag')
				except: pass
				data=response.read()
		except Exception as e: 
			s = str(e)
			if 'Not Modified'.lower() in s.lower(): resCode=304
			data=''
		if ('Exec format error: exec' in data or 'A file permissions error has occurred' in data) and 'xbmcplugin' not in data:
			data=''
		if len(data)>0:
			try:
				if isBase64: 
					import base64
					data=base64.b64decode(data)
			except: 
				print 'Failed..not base64.'+fname
				pDialog.update(20+progr, 'Failed..not base64.'+fname)
				data=''
		if len(data)>0:
			with open(os.path.join(communityStreamPath, fname), "wb") as filewriter:
				filewriter.write(data)
				if eTag:
					selfAddon.setSetting( id="Etagid"+fileHash ,value=eTag)    
			pDialog.update(20+progr, 'imported ...'+fname)
		elif resCode==304:
			pDialog.update(20+progr, 'No Change.. skipping.'+fname)
		else:            
			pDialog.update(20+progr, 'Failed..zero byte.'+fname)
		fileno+=1
	pDialog.close()
	dialog = xbmcgui.Dialog()
	ok = dialog.ok('XBMC', 'Download finished. Close Addon and come back')

def removeLoginFile(livePlayer,TeleDunet,showMsg=True):
	something_done=False
	try:
		if livePlayer:
			something_done=True
			selfAddon.setSetting( id="lastLivetvWorkingCode" ,value="")
			COOKIEFILE = communityStreamPath+'/livePlayerLoginCookie.lwp'
			os.remove(COOKIEFILE)
			
	except: pass
	try:
		if TeleDunet:
			if communityStreamPath not in sys.path:
				sys.path.append(communityStreamPath)
			#print processor
		
		
			#from importlib import import_module
			print 'clear cahche'
			processorObject=import_module('teledunetPlayer')
			processorObject.clearFileCache()
			print 'clear cahchesssssssssssssssssssssssssssssssddd'
			something_done=True
			COOKIEFILE = communityStreamPath+'/teletdunetPlayerLoginCookie.lwp'
			os.remove(COOKIEFILE)
	except: pass
	if something_done and showMsg:
		time = 2000  #in miliseconds
		line1="Session data removed!"
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))

def ShowSettings(Fromurl):
	current_LivePlayerLogin=selfAddon.getSetting( "liveTvLogin" )+selfAddon.getSetting( "liveTvPassword")
	current_teleDunetLogin=selfAddon.getSetting( "teledunetTvLogin" )+selfAddon.getSetting( "teledunetTvPassword")
	selfAddon.setSetting( id="clearLogonSettings" ,value="false")
	selfAddon.openSettings()
	#print 'after settings'
	clearLogonSettings=selfAddon.getSetting( "clearLogonSettings" )
	after_LivePlayerLogin=selfAddon.getSetting( "liveTvLogin" )+selfAddon.getSetting( "liveTvPassword")
	after_teleDunetLogin=selfAddon.getSetting( "teledunetTvLogin" )+selfAddon.getSetting( "teledunetTvPassword")
	removeLoginFile(clearLogonSettings=="true" or not current_LivePlayerLogin==after_LivePlayerLogin, clearLogonSettings=="true" or not current_teleDunetLogin==after_teleDunetLogin )
	return

def LIVETvLogin(Fromurl):
	Msg=""
	try:
	
		if communityStreamPath not in sys.path:
				sys.path.append(communityStreamPath)
		removeLoginFile(True,False,showMsg=False)
		processorObject=import_module('livetvPlayer')
		new_code=processorObject.getLoginCode()
		if new_code:
			selfAddon.setSetting( id="liveTvNonPremiumCode" ,value=new_code)
			Msg="Login successful"
		else:
			Msg="Login failed.If login not working then enter the code manually in the settings."
	except:
		traceback.print_exc(file=sys.stdout)
		Msg="Login failed.If login not working then enter the code manually in the settings."
	dialog = xbmcgui.Dialog()
	ok = dialog.ok('Livetv Login', Msg)
	return

	
def getFirstElement(elements,attrib, val):
	for el in elements:
		#print el.attrib[attrib]
		if el.attrib[attrib]==val:
			#print 'found next'
			return el
	return None

def getJson(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
	response = urllib2.urlopen(req)
	#link=response.read()
	#response.close()
	decoded = json.load(response)
	return decoded
	
	
def AddStreams():
	match=getStreams();
	#print 'match',match
	match=sorted(match,key=lambda x:x[0].lower())
	cstream='<channels>'
	infostream='<streamingInfos>'
	#print 'match',match
	for cname in match:
		if 'hdarabic' in cname[1]:
			chName=Colored(cname[0],'one',False);
			chUrl = cname[1]
			if not 'http:' in cname[2]:
				imageUrl = 'http://www.hdarabic.com/./images/'+cname[2]+'.jpg'
			else:
				imageUrl=cname[2]
			#print imageUrl
			#print chName
			addDir(chName ,chUrl ,10,imageUrl, False,isItFolder=False)		#name,url,mode,icon
		else:
			chName=Colored(cname[1],'two',False);
			chUrl = cname[0]
			imageUrl = 'http://www.teledunet.com/tv_/icones/%s.jpg'%cname[0]
			#print imageUrl
			#print chName
			addDir(chName ,chUrl ,11,imageUrl, False,isItFolder=False)		#name,url,mode,icon#<assignedcategory></assignedcategory>
			cstream+='<channel><id>%s</id><cname>%s</cname><imageurl>%s</imageurl><enabled>True</enabled></channel>'%(chUrl,cname[1],imageUrl)
			infostream+='<streaminginfo><id>%s</id><url>%s</url></streaminginfo>'%(chUrl,chUrl)
	cstream+='</channels>'
	infostream+='</streamingInfos>'
	#print cstream
	#print infostream
	return
	
def PlayStream(url, name, mode):

	if mode==10:
		req = urllib2.Request(url)
		req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		match =re.findall('file: "rtmp([^"]*)', link)

		rtmpLink=match[0]
		#rtmpLink='://192.95.32.7:1935/live/dubai_sport?user=MjA5N2Q3YjA2M2Q2ZjhiNWNjODAzYWJmM2RmNzU4YWE=&pass=fc9226bd032346a2deab1f903652229b'
		liveLink="rtmp%s app=live/ swfUrl=http://www.hdarabic.com/jwplayer.flash.swf pageUrl=http://www.hdarabic.com live=1 timeout=15"%rtmpLink
	else:
		newURL='http://www.teledunet.com/tv_/?channel=%s&no_pub'%url
		req = urllib2.Request(newURL)
		req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
		req.add_header('Referer',newURL)

		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		match =re.findall('time_player=(.*?);', link)
		match=str(long(float(match[0])))

		liveLink='rtmp://5.135.134.110:1935/teledunet playpath=%s swfUrl=http://www.teledunet.com/tv_/player.swf?id0=%s&skin=bekle/bekle.xml&channel=%s  pageUrl=http://www.teledunet.com/tv_/?channel=%s&no_pub live=1  timeout=15'%(url,match,url,url)
		
	#print 'liveLink',liveLink

	listitem = xbmcgui.ListItem( label = str(name), iconImage = "DefaultVideo.png", thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ), path=liveLink )
	xbmc.Player().play( liveLink,listitem)


def getSourceAndStreamInfo(channelId, returnOnFirst,pDialog, filterBySource=""):
	try:
		ret=[]
		#Ssoup=getSoup('Sources.xml');
		sourcesXml=getEtreeFromFile('Sources.xml');
		default_source=''
		config=getChannelSettings( channelId)
		match_title=''
		if config and 'defaultsource' in config:
			default_source=config['defaultsource'].split(':')[0]
			try:
				match_title= ''.join(config['defaultsource'].split(':')[1:])
				print 'match_title in settings',match_title,default_source
			except: pass
		#print 'default_source',default_source
		orderlist={}
		default_source_exists=False
		sources=sourcesXml.findall('source')
		total_sources=len(sources)
		print 'total_sources',total_sources
		for n in range(total_sources):
			val=selfAddon.getSetting( "order"+str(n+1) )
			if val and not val=="":
				#print 'val',val,default_source
				orderlist[val]=n*100
				if not default_source=='' and default_source ==val:
					orderlist[val]=-100
					
			
		num=0

		
		pDialog.update(30, 'Looping on sources')
		GLArabServerLOW=selfAddon.getSetting( "GLArabServerLOW" )
	#	GLArabServerHD=selfAddon.getSetting( "GLArabServerHD" )
		GLArabServerMED=selfAddon.getSetting( "GLArabServerMED" )
		GLArabServerLR=selfAddon.getSetting( "GLArabServerLR" )
        
	#	glHDDisabled=False if not GLArabServerHD=="Disabled" else True
		glMedDisabled=False if not GLArabServerMED=="Disabled" else True
		glLowDisabled=False if not GLArabServerLOW=="Disabled" else True
		glLRDisabled=False if not GLArabServerLR=="Disabled" else True        
		glproxyDisabled=not selfAddon.getSetting( "isGLProxyEnabled" )=="true"
		glproxyCommonDisabled=not selfAddon.getSetting( "isGLCommonProxyEnabled" )=="true"
		glproxyCommonDisabled=True #make it false if we get common proxy working
#		print "glHDDisabled",glHDDisabled
        
        
		for source in sources:
			sname = source.findtext('sname')
			num+=1
			pDialog.update(30+(num*70)/len(sources) , 'Checking ..'+source.findtext('sname'))
			if not filterBySource=="":
				if not sname==filterBySource: continue
			try:
				#print 'source....................',source
				xmlfile = source.findtext('urlfile')
				isEnabled = source.findtext('enabled').lower()
				sid = source.findtext('id')
				#print 'sid',sid,xmlfile
				isAbSolutePath=False
				if sname=="Local":
					#
					isAbSolutePath=True
					isEnabled="false"
					filename=selfAddon.getSetting( "localstreampath" ).decode('utf-8')
					if filename and len(filename)>0:
						isEnabled="true"
						xmlfile=filename
				settingname="is"+sname.replace('.','')+"SourceDisabled"
				settingDisabled=selfAddon.getSetting(settingname)
				if isEnabled=="true" and not settingDisabled=="true":
				
					streamingxml=getEtreeFromFile(xmlfile,isAbSolutePath);
					
					sInfos=streamingxml.findall('streaminginfo')
					sInfo=[]
					for inf in sInfos:
						if inf.findtext('cname').lower()==channelId.lower():
							source_title=''
#							if match_title<>'':
							try:
								if source.findtext('id')=='generic':
									source_title=inf.find('item').findtext('title')
								else:
									source_title=inf.findtext('title')
							except: pass
							#print sname,    glHDDisabled,source_title

							if sname=="GLArab" and  glproxyDisabled and glproxyCommonDisabled and 'Proxy' in source_title: continue                             
						#	if sname=="GLArab" and  glHDDisabled  and glproxyCommonDisabled and "HD" in source_title  : continue                             
							if sname=="GLArab" and  glMedDisabled and glproxyCommonDisabled and "Med" in source_title: continue    
							if sname=="GLArab" and  glLowDisabled  and glproxyCommonDisabled and "Low" in source_title: continue    
							if sname=="GLArab" and  glLRDisabled and glproxyCommonDisabled and "LR" in source_title: continue    
                            
							#print default_source,sid,match_title,inf.findtext('title'),inf
							if not default_source=='' and default_source==sname and (match_title =='' or match_title==source_title):                       
								default_source_exists=True
							sInfo.append(inf)
					name_find=sname
					if name_find in orderlist:
						order= orderlist[name_find]
					else:
						print 'not found',name_find,orderlist
						order=20000
					order+=num
					if not sInfo==None and len(sInfo)>0:
						print 'sInfo...................',len(sInfo)
						
						for single in sInfo:
							source_title=''
							if match_title<>'':
								try:
									if source.findtext('id')=='generic':
										source_title=single.find('item').findtext('title')
									else:
										source_title=single.findtext('title')
								except: pass
							if (match_title =='' or match_title==source_title):
								print 'title match for order', match_title,source_title
								order-=1
							ret.append([source,single,order])
						#if returnOnFirst:
						#	break;
			except:
				traceback.print_exc(file=sys.stdout)
				pass
	except:
		traceback.print_exc(file=sys.stdout)
		pass
	#print 'unsorted ret',ret

	#print ret
	ret= sorted(ret,key=lambda x:x[2])
	print ret
	return ret,default_source_exists and not default_source==''

def selectSource(sources,fromSelectSource=False):
    if 1==1 or len(sources) > 1:
        #print 'total sources',len(sources)
        dialog = xbmcgui.Dialog()
        titles = []
        for source in sources:
            (s,i,o) =source
            #print 'i',i.id,i
            if s.findtext('id')=="generic":
                try:
                    #print 'trying generic name'
                    titles.append(s.findtext('sname')+': '+i.find('item').findtext('title'))
                    #print 'trying generic name end '
                except:
                    titles.append(s.findtext('sname'))
            else:
                try:
                    titles.append(s.findtext('sname')+': '+i.findtext('title'))
                except: titles.append(s.findtext('sname'))

        if fromSelectSource:
            titles.append(Colored('Clear Default Source setting','one',True))

        index = dialog.select('Choose your stream', titles)
        if index > -1:
            if index>len(sources)-1:
                return 'remove'#remove it
            else:
                return sources[index]
        else:
            return False

def selectDefaultSourcesForChannel(channelId ):
	try:
		pDialog = xbmcgui.DialogProgress()
		ret = pDialog.create('XBMC', 'Finding available resources...')
		pDialog.update(20, 'Finding sources..')
		providers, default_source_exists=getSourceAndStreamInfo(channelId,False,pDialog)
		if len(providers)==0:
			pDialog.close()
			time = 2000  #in miliseconds
			line1="No sources found"
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
			return None
		selectedprovider=selectSource(providers,True)
		if not selectedprovider:
			return None
		if selectedprovider=='remove':
			return ''
		fav_source=''   
		source,sInfo,order=selectedprovider #pick first one
		fav_source=source.findtext('sname')
		try:
			if source.findtext('id')=="generic":
				fav_source=source.findtext('sname')+':'+sInfo.find('item').findtext('title')
			else:
				fav_source=source.findtext('sname')+':'+sInfo.findtext('title')
		except:pass

		return fav_source
	except:
		traceback.print_exc(file=sys.stdout)
		return None
		
def PlayCommunityStream(channelId, name, mode):
	try:
		#print 'PlayCommunityStream'
		xbmcplugin.endOfDirectory(int(sys.argv[1]))
		pDialog = xbmcgui.DialogProgress()
		ret = pDialog.create('XBMC', 'Finding available resources...')
		#print 'channelId',channelId
		playFirst=selfAddon.getSetting( "playFirstChannel" )
		if playFirst==None or playFirst=="" or playFirst=="false":
			playFirst=False
		else:
			playFirst=True
		playFirst=bool(playFirst)
		pDialog.update(20, 'Finding sources..')
		providers,default_source_exists=getSourceAndStreamInfo(channelId,playFirst,pDialog, sourceFilter)
		if default_source_exists:
			playFirst=True
		if len(providers)==0:
			pDialog.close()
			time = 2000  #in miliseconds
			line1="No sources found"
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
			return
		pDialog.update(30, 'Processing sources..')
		pDialog.close()
		#source=providers[""]

		
		enforceSourceSelection=False
		#print 'playFirst',playFirst
		done_playing=False
		current_index=0
		auto_skip=False
		auto_skip=True if selfAddon.getSetting( "playOneByOne" )=="true" else False
		while not done_playing:
			#print 'trying again',enforceSourceSelection
			ret = pDialog.create('XBMC', 'Trying to play the source')
			#print 'dialogue creation'
			done_playing=True
			if (enforceSourceSelection or (len (providers)>1 and not playFirst)) and not auto_skip:
				#print 'select sources'
				selectedprovider=selectSource(providers)
				if not selectedprovider:
					return
			else:
				selectedprovider=providers[current_index]
				enforceSourceSelection=True
			#print 'picking source'
			(source,sInfo,order)=selectedprovider #pick first one
			#print source

			processor = source.findtext('processor')
			sourcename = source.findtext('sname')

			if communityStreamPath not in sys.path:
				sys.path.append(communityStreamPath)
			#print processor
		
		
			#from importlib import import_module
			processorObject=import_module(processor.replace('.py',''))
		
		
			pDialog.update(60, 'Trying to play..')
			pDialog.close()
			sinfoSoup= BeautifulSOAP(etree.tostring(sInfo), convertEntities=BeautifulStoneSoup.XML_ENTITIES)
			done_playing=processorObject.PlayStream(source,sinfoSoup,name,channelId)
			#print 'done_playing',done_playing
			if not done_playing:
				time = 2000  #in miliseconds
				line1="Failed playing from "+sourcename
				xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
				if auto_skip:
					done_playing=False
					current_index+=1
					if current_index>len(providers):
						done_playing=True
					if not done_playing:
						(s,i,o) =providers[current_index]
						titles=''
						if s.findtext('id')=="generic":
							try:
								#print 'trying generic name'
								titles=s.findtext('sname')+': '+i.find('item').findtext('title')
								#print 'trying generic name end '
							except:
								titles=s.findtext('sname')
						else:
							try:
								titles=s.findtext('sname')+': '+i.findtext('title')
							except: titles=s.findtext('sname')                       

						ret = pDialog.create('XBMC', 'Trying to play the Item# %d of %d, Cancel in 3 seconds.\n Source:%s'%(current_index+1, len(providers),titles))

						xbmc.sleep(3000)
						if pDialog.iscanceled():
							current_index=0
							done_playing=False
							enforceSourceSelection=True
							auto_skip=False
			#print 'donexxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
		return 
	except:
		traceback.print_exc(file=sys.stdout)

def import_module(name, package=None):
    """Import a module.
    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.
    """
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]
def getUrl(url, cookieJar=None,post=None,referer=None,isJsonPost=False, acceptsession=None,timeout=30):

	cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
	opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
	#opener = urllib2.install_opener(opener)
	req = urllib2.Request(url)
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
	if isJsonPost:
		req.add_header('Content-Type','application/json')
	if acceptsession:
		req.add_header('Accept-Session',acceptsession)
        
	if referer:
		req.add_header('Referer',referer)
	response = opener.open(req,post,timeout=timeout)
	link=response.read()
	response.close()
	return link;

def processProxyLogin():
    userName=selfAddon.getSetting( "ShahidVodLogin" )
    password=selfAddon.getSetting( "ShahidVodPwd" )
    post={'user':userName,'pwd':password}
    post = urllib.urlencode(post)

    html_txt=getUrl(getMainUrl()+"/proxychecklogin.php?",None,post)
    
    return cookielib.LWPCookieJar()


	
def addToMyChannels(cname):
	try:
		fileName=os.path.join(profile_path, 'MyChannels.xml')
		print fileName
		MyChannelList=getSoup(fileName,True)
	except: MyChannelList=None
	if not MyChannelList:
		MyChannelList= BeautifulSOAP('<channels></channels>')
	
	val=MyChannelList.find("channel",{"cname":cname})
	#print 'val is ',val
	if not val:
		channeltag = Tag(MyChannelList, "channel")
		channeltag['cname']=cname
		MyChannelList.channels.insert(0, channeltag)
		#print MyChannelList.prettify()

		with open(fileName, "wb") as filewriter:
			filewriter.write(str(MyChannelList))

def removeFromMyChannels(cname):
	try:
		fileName=os.path.join(profile_path, 'MyChannels.xml')
		print fileName
		MyChannelList=getSoup(fileName,True)
	except: return
	if not MyChannelList:
		return
	
	val=MyChannelList.find("channel",{"cname":cname})
	if val:
		#print 'val to be deleted',val
		val.extract()

		with open(fileName, "wb") as filewriter:
			filewriter.write(str(MyChannelList))

def ShowSources(url):
	#soup=getSoup('Categories.xml');
	cats=getEtreeFromFile('Sources.xml');
	#print cats 

	for cat in cats.findall('source'):
		isEnabled = cat.findtext('enabled').lower()
		chName=cat.findtext('sname')
		chUrl = cat.findtext('id')
		settingname="is"+chName.replace('.','')+"SourceDisabled"
		settingDisabled=selfAddon.getSetting(settingname)  
		imageUrl = cat.findtext('imageurl')
		if isEnabled=="true" and not settingDisabled=="true":
			addDir(chName ,chUrl ,26,imageUrl, False,isItFolder=True, BySource=chName)		#name,url,mode,icon
	return


	
def addCommunityCats():
	#soup=getSoup('Categories.xml');
	cats=getEtreeFromFile('Categories.xml');
	#print cats 

	if sourceFilter=="":
		addDir('My Channels' ,'My Channels' ,15,addonArt+'/mychannels.png', False,isItFolder=True)		#name,url,mode,icon
		addDir('By Sources' ,'By Sources' ,25,addonArt+'/bysource.png', False,isItFolder=True)		#name,url,mode,icon
	else:
		sources=getSourceList()
		source = sources[sourceFilter]
		sourceName=source[0]
		SourceFileName=source[2]
		SourceImageName=source[3]
		isAbsolutePath=source[4]
		addDir('** Filtered by ' + sourceName+' **','' ,99,SourceImageName, False,isItFolder=False )
	for cat in cats.findall('category'):
		chName=cat.findtext('catname')
		chUrl = cat.findtext('id')
		imageUrl = cat.findtext('imageurl')
		addDir(chName ,chUrl ,15,imageUrl, False,isItFolder=True,BySource=sourceFilter)		#name,url,mode,icon
	return

def getSourceList():
	sourcesXml=getEtreeFromFile('Sources.xml');
	sources_list={}
	for sources in sourcesXml.findall('source'): 
		id=sources.findtext('id')
		sname=sources.findtext('sname')
		ssname=sources.findtext('shortname')
		scolour=sources.findtext('colour')
		urlfile=sources.findtext('urlfile')
		imageUrl=sources.findtext('imageurl')
		isAbSolutePath=False
		if sname=="Local":
			isAbSolutePath=True
			filename=selfAddon.getSetting( "localstreampath" ).decode('utf-8')
			if filename and len(filename)>0:
				urlfile=filename
		sources_list[sname]=[ssname,scolour,urlfile,imageUrl, isAbSolutePath ]
	return sources_list

def getSourceChannelList(fileName, isAbsolutePath):
	sourcesXml=getEtreeFromFile(fileName,isAbsolutePath );
	sources_list={}
	for sources in sourcesXml.findall('streaminginfo'): 
		cname=sources.findtext('cname')
		sources_list[cname]=[cname]
	return sources_list

def getCommunityChannels(catType):
	#soup=getSoup('Channels.xml');#changetoEtree
	Channelsxml=getEtreeFromFile('Channels.xml')
	#channels=soup('channel')
	retVal=[]
		
	#for channel in channels:
	searchCall='channel'
	#if not catType=="all":
	searchCall='.//category'
	#print searchCall
	MyChannelList=None
	hidechanneloption=True
	sourcesXml=getEtreeFromFile('Sources.xml');
	sources_list={}
	for sources in sourcesXml.findall('source'): 
		sname=sources.findtext('sname')
		ssname=sources.findtext('shortname')
		scolour=sources.findtext('colour')
		sources_list[sname]=[ssname,scolour]
	if catType=="My Channels":
		try:
			fileName=os.path.join(profile_path, 'MyChannels.xml')
			#print fileName
			MyChannelList=getSoup(fileName,True)
			#print MyChannelList
		except: MyChannelList=None
		
	for channel in Channelsxml.findall('channel'):
		#print channel
		chName=channel.findtext('cname')
		if 1==1:
			config=getChannelSettings( chName)
			#print 'config is ',config
			if not catType=="all":
				exists=False
				if not catType=="My Channels":
					supportCats= channel.findall(searchCall)
					if len(supportCats)==0:
						continue
					
					for c in supportCats:
						if c.text.lower()==catType.lower():
							exists=True
							break
				else:
					#check if channel exists in file
					if MyChannelList:
						val=MyChannelList.find("channel",{"cname":chName})
						if val:
							exists=True
				if config and 'hidden' in config:
					exists=not config['hidden']=="yes"
				if not exists:
					continue

			

		
		if config and 'hidden' in config:
			hidechanneloption=not config['hidden']=="yes"
		#chUrl = channel.id.text
		imageUrl =channel.findtext('imageurl')
		chUrl=chName
		if config and 'defaultsource' in config:
			default_source=config['defaultsource'].split(':')[0]
			#chName+='['+default_source+']'
			if default_source in sources_list:
				short_name='['+sources_list[default_source][0]+']'
				colour=sources_list[default_source][1]
				short_name=Colored(text = short_name, colorid = colour, isBold = False)
				print short_name

				chName+=' '+short_name
				
 		retVal.append([chUrl,chName,imageUrl,hidechanneloption])
	return retVal
	

def addCommunityChannels(catType):
	channels=getCommunityChannels(catType)
	channels=sorted(channels,key=lambda x:x[1].lower())
	FilterBySource=False
	ExistsInSource=False
	print 'Source Filter',sourceFilter
	if not sourceFilter=="":
		FilterBySource=True
		sources=getSourceList()
		source = sources[sourceFilter]
		sourceName=source[0]
		SourceFileName=source[2]
		SourceImageName=source[3]
		isAbsolutePath=source[4]
		addDir('** Filtered by ' + sourceName+' **','' ,99,SourceImageName, False,isItFolder=False )
		streamingxml=getEtreeFromFile(SourceFileName,isAbsolutePath);
		sInfos=streamingxml.findall('streaminginfo')
		sInfo=getSourceChannelList(SourceFileName, isAbsolutePath )
		#print sInfo

	for channel in channels:
		ExistsInSource=False
		chName=channel[1]
		chUrl = channel[0]
		imageUrl = channel[2]
		hideChannel=channel[3]
		addRemoveMyChannel=not catType=="My Channels"
		#print chName,chName in sInfo,
		if FilterBySource and not chUrl in sInfo: continue
		addDir(chName ,chUrl ,16,imageUrl, False,isItFolder=False,AddRemoveMyChannels=addRemoveMyChannel, SelectDefaultSource=True,hideChannel=hideChannel, BySource=sourceFilter )		#name,url,mode,icon
	return

def setChannelSettings(cname,settingName,SettingVal):
	current_setting=getChannelSettings(cname)
	if current_setting==None:
		current_setting={settingName:SettingVal}
	else:
		current_setting[settingName]=SettingVal
	#print 'current_setting',current_setting
	saveChannelSettings(cname,current_setting)


def getChannelSettings(cname):
	current_string=selfAddon.getSetting( cname+"-settings")
	#print cname+"-settings",current_string
	if current_string=="":
		return None
	#print 'current_string',current_string
	return json.loads(current_string)


def saveChannelSettings(cname, json_data):
	store=""
	if json_data:
		store=json_data
	selfAddon.setSetting( id=cname+"-settings" ,value=json.dumps(store))



	
	
def getEtreeFromFile(fileName, isabsolutePath=False):
	try:
		#print 'communityStreamPath',communityStreamPath
		#print 'fileName',fileName
		strpath=os.path.join(communityStreamPath, fileName)
		#print 'strpath',strpath
		if isabsolutePath:
			strpath=fileName
		data = open(strpath, "r").read()
		return getETreeFromString(data)
	except:
		print 'somethingwrong'
		traceback.print_exc(file=sys.stdout)
	
#obselete
def getSoup(fileName, isabsolutePath=False):
	strpath=os.path.join(communityStreamPath, fileName)
	if isabsolutePath:
		strpath=fileName
	data = open(strpath, "r").read()
	return BeautifulSOAP(data)#, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
	#return BeautifulStoneSoup(data,convertEntities=BeautifulStoneSoup.XML_ENTITIES);

def getETreeFromUrl(video_url):
	req = urllib2.Request(video_url)
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
	response = urllib2.urlopen(req)
	data=response.read()
	response.close()

	return getETreeFromString(data)
	#return BeautifulSOAP(data)
def getETreeFromString(str):
	return etree.fromstring(str)


	
#print "i am here"
params=get_params()
url=None
name=None
mode=None
linkType=None
pageNumber=None
AddRemoveMyChannels=None
sourceFilter=""

try:
	sourceFilter=urllib.unquote_plus(params["sourceFilter"])
except:
	pass
print 'sourceFilter',sourceFilter
	
try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass

try:
	pageNumber=params["pagenum"]
except:
	pageNumber="";

args = cgi.parse_qs(sys.argv[2][1:])
cdnType=''
try:
	cdnType=args.get('cdnType', '')[0]
except:
	pass

addIconForPlaylist=""
try:
	addIconForPlaylist=args.get('addIconForPlaylist', '')[0]
except:
	pass


AddRemoveMyChannels=None
try:
	AddRemoveMyChannels=args.get('AddRemoveMyChannels', None)[0]
except:
	pass

selectDefaultSource=None

try:
	selectDefaultSource=args.get('selectDefaultSource', None)[0]
except:
	pass

HidChannel=None
try:
	HidChannel=args.get('HideChannel', None)[0]
except:
	pass

	

print 	mode,pageNumber

try:
	if not AddRemoveMyChannels==None:
		if AddRemoveMyChannels=="add":
			addToMyChannels(url)
			line1 = 'Channel has been added to My Channels list'
			time = 2000  #in miliseconds
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
			mode=-1
		else:
			removeFromMyChannels(url)
			line1 = 'Channel has been removed from My Channels list'
			time = 2000  #in miliseconds
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
			mode=15
			url="My Channels"
			print mode

	if not HidChannel==None:
		if HidChannel=="yes":
			setChannelSettings(url,'hidden',HidChannel)
			line1 = 'Channel has been hidden in categories'
			time = 2000  #in miliseconds
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
			mode=-1
		else:
			setChannelSettings(url,'hidden','')
			line1 = 'Channel has been unhidden in categories'
			time = 2000  #in miliseconds
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
			mode=-1
			url=""
			
	if not selectDefaultSource==None:
		default_source=selectDefaultSourcesForChannel(url)
		print 'v',default_source
		if not default_source==None:
			print 'saving settings',default_source    
			setChannelSettings(url,'defaultsource',default_source)
			line1 = 'setting saved'
			time = 2000  #in miliseconds
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
		mode=-1

	if mode==299: #add communutycats
		print 'delete cache'
		removeLoginFile(True,True)
		line1 = 'Login sessions cleared!'
		time = 2000  #in miliseconds
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
		xbmc.executebuiltin('Container.Update(plugin://plugin.video.DaawoTV)')
		mode=-1
		
	if mode==None or url==None or len(url)<1:
		print "InAddTypes"
		checkAndRefresh()        
		Addtypes()

	elif mode==2:
		print "Ent url is "+name,url
		AddChannels(url)

	elif mode==3 or mode==6:
		print "Ent url is "+url
		AddSeries(url,pageNumber,name)

	elif mode==4 or mode==7:
		print "Play url is "+url
		AddEnteries(url,pageNumber)

	elif mode==5 or mode==32:
		PlayShowLink(url)
	elif mode==8:
		print "Play url is "+url,mode
		ShowSettings(url)
	elif mode==24:
		print "Play url is "+url,mode
		LIVETvLogin(url)
	elif mode==9:
		print "Play url is "+url,mode
		AddStreams();
	elif mode==10 or mode==11:
		print "Play url is "+url,mode
		PlayStream(url,name,mode);
	elif mode==14 or mode==26: #add communutycats
		print "Play url is "+url,mode
		checkAndRefresh() 
		addCommunityCats();
	elif mode==15: #add communutycats
		print "Play url is "+url,mode
		addCommunityChannels(url);
	elif mode==16: #add communutycats
		print "PlayCommunityStream Play url is "+url,mode
		PlayCommunityStream(url,name,mode);	
	elif mode==17: #add communutycats
		print "RefreshResources Play url is "+url,mode
		RefreshResources();
	elif mode==18: #
		print "youtube url is "+url,mode
		AddYoutubeSources(url)
	elif mode==19: #
		print "youtube url is "+url,mode
		AddYoutubeLanding(url)
	elif mode==20: #add communutycats
		print "youtube url is "+url,mode
		AddYoutubeVideosByChannelID(url,addIconForPlaylist);	
	elif mode==21: #add communutycats
		print "play youtube url is "+url,mode
		PlayYoutube(url);	
	elif mode==22: #add communutycats
		print "play youtube url is "+url,mode
		AddYoutubePlaylists(url);	
	elif mode==23: #add communutycats
		print "play youtube url is "+url,mode
		AddYoutubeVideosByPlaylist(url);	
	elif mode==25: #add communutycats
		print "play youtube url is "+url,mode
		ShowSources(url);	
	elif mode==31: #add communutycats
		print "play youtube url is "+url,mode
		AddShahidMovies(url);	
	elif mode==27: #add communutycats
		print "play youtube url is "+url,mode
		AddShahidVodMovietypes();	        
        

except:
	print 'somethingwrong'
	traceback.print_exc(file=sys.stdout)

try:
	if (not mode==None) and mode>1:
		view_mode_id = get_view_mode_id('thumbnail')
		if view_mode_id is not None:
			print 'view_mode_id',view_mode_id
			xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
except: pass
if not ( mode==5 or mode==10 or mode==8 or mode==11 or mode==16 or mode==17 or mode==32):
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

