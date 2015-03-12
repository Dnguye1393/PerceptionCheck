# coding: utf8
from datetime import datetime
import re
import unittest


def get_first_name():
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


EDITION = [ '1E' , '1.5E', '2E', '2.5E', '3E', '3.5E', '4E', '4.5E', '5E', '5.5E', 
		   '6E', 'Home Brew']
HOUSERULES = ['Yes', 'No', 'Minor Changes']
RE_LINKS = re.compile('(<<)(.*?)(>>)')
#
# List of UCSC majors

# Format for wiki links.


#
# List of cohort signed up
#
db.define_table('cohort',
                Field('user_id', db.auth_user, readable = False),
                Field('first_name', default = get_first_name() ),
                Field('last_name', default = get_last_name() ),
                Field('email', requires=IS_EMAIL(), default = get_email()),
                Field('bio', 'text')
               )
db.cohort.id.readable = False;


db.define_table('party', #to keep track of all the campaigns
				  Field('campaign_title' ),
				  Field('players'),
				  Field('requesting_to_join', 'boolean'),
				  Field('accepted', 'boolean'),
				  Field('profile_id', default = db.auth_user),
			   )
db.party.id.readable= False
db.party.campaign_title.readable= False

db.define_table('games', #main data of website Controls all the games
				Field('campaign_title'),
				Field('user_id', db.auth_user),
				Field('game'), #Replace with an Ajax search
				Field('edition'),
				Field('game_master'),
				Field('players'),
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
				Field('total_players', 'integer'),
				)


db.games.user_id.default = auth.user_id
db.games.user_id.writable = db.games.user_id.readable = False
db.games.id.readable= False
db.games.game_master.default = get_first_name()
db.games.edition.requires = IS_IN_SET(EDITION)
db.games.house_rules.requires = IS_IN_SET(HOUSERULES)
db.games.players.writable = False #okay for now
db.games.looking_for_players.default = False
db.games.house_rules.default = 'No'
db.games.edition.default = '5E'
db.games.zipcode.requires = IS_MATCH('\d{5}', error_message='Put in format #####')


db.define_table('pagetable', # Name 'page' is reserved unfortunately.
    Field('title'),
    # Complete!
    )





db.define_table('revision',
    Field('page_id'),
	Field('user_id', db.auth_user, writable = False),
	Field('campaign_title'),
    Field('rcomment'),
    Field('auth'),
    Field('date_created', 'datetime', default=request.now),
    Field('body', 'text'), # This is the main content of a revision.
    )
db.revision.user_id.default = auth.user_id
db.revision.user_id.writable = db.games.user_id.readable = False
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
    the <<page>> links to links to /wikia/index/page"""
    return MARKMIN(create_wiki_links(s))

def represent_content(v, r):
    """In case you need it: this is similar to represent_wiki, 
    but can be used in db.table.field.represent = represent_content"""
    return represent_wiki(v)

db.pagetable.title.requires = IS_NOT_IN_DB(db, 'page.title')
db.revision.body.requires = IS_NOT_EMPTY()
db

# We associate the wiki representation with the body of a revision.
db.revision.body.represent = represent_content
