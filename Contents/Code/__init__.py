TITLE        = Prefs['title']
FRONT_PAGE   = Prefs['podcastUrl']
ART          = Prefs['background']
ICON         = Prefs['icon']
ICON_ARCHIVE = Prefs['archiveIcon']

######################################################################
# Plex plugin for the podbean podcast site.
# Originally written for Carnmoney Church www.carnmoney.org
# by Gary Bell.
#
######################################################################
def Start(): # Initialize the plug-in

	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

# Setup the default attributes for the ObjectContainer
ObjectContainer.title1     = TITLE
ObjectContainer.view_group = 'List'
ObjectContainer.art        = R(ART)

# Setup the default attributes for the other objects
DirectoryObject.thumb = R(ICON)
DirectoryObject.art = R(ART)
VideoClipObject.thumb = R(ICON)
VideoClipObject.art = R(ART)

PREFIX = '/music/CarnmoneyPodcasts'
#####################################################################
@handler(PREFIX, TITLE)
def MainMenu():
	
	dom = HTML.ElementFromURL(FRONT_PAGE)
	
	ocTitle2 = dom.xpath('.//div[@class="header-block"]/h1/span/text()')[0]
	if ocTitle2:
		ObjectContainer.title2 = ocTitle2
		
	
	oc = ObjectContainer()
	# Static content
	oc.add(DirectoryObject(key=Callback(ArchiveMenu, title="Archives"), title="Archives",summary="Past Podcast episodes", thumb = R(ICON_ARCHIVE)))
	oc.add(DirectoryObject(key=Callback(SeriesMenu, title="Series"), title="By Series",summary="Podcasts by the Sermon series"))
	#oc.add(InputDirectoryObject(key=Callback(Search, prompt="Search for..."), title="Search Podcasts", summary="The description of what you are searching for...", thumb = R(ICON)))
	# latest podcasts. We put them at the top level for convenience.

	latest_oc = getTrackObjectsOnPage(title=ObjectContainer.title2,url = FRONT_PAGE)
	for object in latest_oc.objects:
		oc.add(object)
	return oc 
	
	
@route(PREFIX + '/search')
def Search(query, url = None):
	oc = ObjectContainer()
	return oc 
	
	
@route(PREFIX+'/archive')
def ArchiveMenu(title):
	oc = ObjectContainer(title2=title)
	dom = HTML.ElementFromURL(FRONT_PAGE)
	archive_list = dom.xpath('//*[@id="sidebar"]/ul/li[@class="widget"][1]/ul/li') #Best we can do
	for list_item in archive_list :
		month_and_year = list_item.xpath('./a/text()')[0]
		url = list_item.xpath('./a/@href')[0]
		# The archive URLs don't always have the protocol prepended. Add it if needs be.
		if url.startswith('//') :
			url = 'http:' + url
		oc.add(DirectoryObject(key=Callback(ArchivePeriodMenu, title=month_and_year,url = url), title=month_and_year,summary="Podcast episodes from " + month_and_year))
	
	return oc
	
@route(PREFIX+'/series')	
def SeriesMenu(title):
	oc = ObjectContainer(title2 = title)
	return oc
	
	
@route(PREFIX+'/period')
def ArchivePeriodMenu(title,url):
	oc = ObjectContainer(title2 = title)
	period_oc = getTrackObjectsOnPage(title,url)
	for object in period_oc.objects:
		oc.add(object)
	return oc

def getTrackObjectsOnPage(title,url = FRONT_PAGE):
	oc = ObjectContainer(title2=title)
	dom = HTML.ElementFromURL(url)
	index = 0
	for podcast in dom.xpath('//div[@class="post"]'):
		index +=1
		title = podcast.xpath('./div[@class="middlebox"]/div[@class="posttitle"]/h2/a/text()')[0]
		summary = podcast.xpath('./div[@class="middlebox"]/div[@class="entry"]/p/text()')[0]
		url = podcast.xpath('./div[@class="middlebox"]/div[@class="posttitle"]/h2/a/@href')[0]
		date = podcast.xpath('./div[@class="datebox"]/div[@class="dateother"]/text()')[0]
		oc.add(TrackObject(index=index,url = url,title = date + " " +title,artist="Carnmoney Church",thumb = R(ICON),source_title="podbean",summary=summary))
	return oc

