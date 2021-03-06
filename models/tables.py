# coding: utf8
from datetime import datetime
import re
import unittest
crud = Crud(db)

#Functions for Tables
def get_first_name(): #
	name = "noName"
	if auth.user:
		name = auth.user.first_name
	return name

def get_last_name():
    lname = ''
    if auth.user:
        lname = auth.user.last_name
    return lname

def get_email():
    emailz = ''
    if auth.user:
        emailz = auth.user.email
    return emailz

#List of sets for tables
EDITION = [ '1E' , '1.5E', '2E', '2.5E', '3E', '3.5E', '4E', '4.5E', '5E', '5.5E', '6E', 'Home Brew']
HOUSERULES = ['Yes', 'No', 'Minor Changes']
GAMETYPE = ['Shadowrun', 'Dungeon and Dragons', 'Savage Worlds', 'Pathfinder', 'World of Darkness', 'Traveller', 'Call of Cuthulu', 'GURPS',  'Other']
TOPIC = ['Games', 'Looking for Group', 'Looking for Players', 'Questions Rules', 'Story Time', 'Other']

#for Wikia
RE_LINKS = re.compile('(<<)(.*?)(>>)')

# Profiles for Gm's to view. No one else has access to other people's Views unless you are a Gm and people request to join yoru game
db.define_table('profiling', 
                Field('user_id', db.auth_user, writable= False, readable = False),
                Field('first_name', default = get_first_name() ),
                Field('last_name', default = get_last_name() ),
				Field('email', default = get_email()), #used as the main identifier as well as to show for messaging
                Field('Preferences', requires= IS_IN_SET(GAMETYPE, multiple = True)), #list of games and picking which one you want to play
                Field('bio', 'text', default = 'Talk about yourself')
               )
db.profiling.id.readable = False;
db.profiling.user_id.readable = False;


#Party is table to keep track of all the people who request to join your game and who is already in your game
db.define_table('party', #to keep track of all the campaigns
				  Field('campaign_title' ),
				  Field('players'),
                  Field('user_id', db.auth_user),
				  Field('requesting_to_join', 'boolean'),
				  Field('accepted', 'boolean'),
                  Field('email', default = get_email()),
				  Field('profile_id', default = db.auth_user),
			   )
db.party.id.readable= False
db.party.user_id.readable= False
db.party.user_id.writable = False
db.party.campaign_title.readable= False

#Games is the List of games on the website Anyone can create one
db.define_table('games', #main data of website Controls all the games
				Field('campaign_title'),
				Field('user_id', db.auth_user),
				Field('game'), #Replace with an Ajax search
				Field('edition'),
				Field('game_master'),
				#Field('players'),
				Field('meeting_location'), #make more extesnive
				Field('zipcode'),
				Field('house_rules'),
				Field('date_posted', default = request.now),
				Field('date_start', 'datetime'),
				Field('meet_date', 'datetime'),
				Field('description', 'text'),
				Field('welcome_new', 'boolean'),
				Field('open_spots', 'integer'),
				Field('looking_for_players', 'boolean'),
				Field('maximum_amount_of_players', 'integer'),
				)


db.games.user_id.default = auth.user_id
db.games.user_id.writable = db.games.user_id.readable = False
db.games.id.readable= False
db.games.game_master.default = get_first_name()
db.games.edition.requires = IS_IN_SET(EDITION, zero = None)
db.games.house_rules.requires = IS_IN_SET(HOUSERULES, zero = None)
db.games.game.requires = IS_IN_SET(GAMETYPE, zero=None)
db.games.looking_for_players.default = False
db.games.house_rules.default = 'No'
db.games.edition.default = '5E'
db.games.zipcode.requires = IS_MATCH('\d{5}', error_message='Put in format #####')
db.games.campaign_title.required = True
db.games.open_spots.required = True
db.games.maximum_amount_of_players.required = True





# Wikia Portion taken from Homework assignemnts and Adapted for use. 


db.define_table('pagetable', # Name 'page' is reserved unfortunately.
    Field('name', 'text'),
    )

db.define_table('revision',
	Field('campaign_title'),
    Field('page_id', db.pagetable),
    Field('author'),
    Field('date_posted', 'datetime', default = request.now),
    Field('body', 'text'), # This is the main content of a revision.
    #Field('comments', 'text'),
    )

db.revision.page_id.readable = False

def create_wiki_links(s):
    """This function replaces occurrences of '<<polar bear>>' in the 
    wikitext s with links to default/page/polar%20bear, so the name of the 
    page will be urlencoded and passed as argument 1."""
    def makelink(match):
        # The tile is what the user puts in
        title = match.group(2).strip()
        # The page, instead, is a normalized lowercase version.
        page = title.lower()
        return '[[%s %s]]' % (title, URL('wikia', 'index', args=[page]))
    return re.sub(RE_LINKS, makelink, s)

def represent_wiki(s):
    """Representation function for wiki pages.  This takes a string s
    containing markup language, and renders it in HTML, also transforming
    the <<page>> links to links to /default/index/page"""
    return MARKMIN(create_wiki_links(s))

def represent_content(v, r):
    """In case you need it: this is similar to represent_wiki, 
    but can be used in db.table.field.represent = represent_content"""
    return represent_wiki(v)

# We associate the wiki representation with the body of a revision.
db.revision.body.represent = represent_content





#messaging system 
#added so that Players and Gm's could talk Privately
#based off of: https://github.com/blackshirt/simple-private-messaging-system
db.define_table('mssging',
    Field('sender_id', db.auth_user, default=auth.user_id, readable=False, writable=False),
    Field('reciever_email', db.auth_user, readable=False),
    Field('first_name', default = get_first_name()),
    Field('timesent', 'datetime', default=request.now, readable=False, writable=False),
    Field('subject','string', length=255),
    Field('body', 'text'),
    Field('opened', 'boolean', writable=False, readable=False, default=False),
    Field('timeopened', 'datetime', readable=False, writable=False)
    )

db.mssging.reciever_email.requires=IS_IN_DB(db, db.auth_user.id,'%(email)s') #list of email in the db
db.mssging.timesent.default = datetime.utcnow()
db.mssging.id.readable = False


#List of Threads in a Forum For discussion or finding a Dm/Group 
#Will allow users to discuss Openly
db.define_table('forums',
                Field('poster_email', default = get_email()),
                Field('title'),
                Field('topic'),
                Field('body', 'text'),
                Field('date_posted', 'datetime'),
                Field('poster'),
                Field('specific_campaign') #add ajax here???
    )
db.forums.specific_campaign.requires=IS_IN_DB(db, db.games.campaign_title,'%(campaign_title)s', multiple = True)
db.forums.topic.requires = IS_IN_SET(TOPIC)
db.forums.topic.required = True
db.forums.poster.default = get_first_name()
db.forums.poster.writable = False
db.forums.specific_campaign.required= False
db.forums.date_posted.writable = False
db.forums.date_posted.default = request.now
db.forums.id.readable = False

#Forum Threads Extension
#this is the actual Thread. The posts on here will be tied t oteh Forums, to kee everying in line
db.define_table('forumThread',
                Field('forumThread_id', readable = False, writable = False),
                Field('date_posted', 'datetime', default = request.now),
                Field('poster'),
                Field('body', 'text'),
    )
db.forumThread.poster.default = get_email()
db.forumThread.poster.writable = False
db.forumThread.id.readable = False
