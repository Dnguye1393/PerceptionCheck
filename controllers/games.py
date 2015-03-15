# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

@auth.requires_login()
def index():
 # Get All data. 

    show_all = request.args(0) =='all'
    #q = db.games
    q = (db.games) if show_all else (db.games.looking_for_players == True)
    
    def generate_edit_button(row):
        # If the record is ours, we can edit it.
        b = ''
        b = A('Edit', _class='btn', _href=URL('games', 'edit', args=[row.id]))
        return b
    def generate_view_button(row):
		# view button to go to a seperate page
		b = ''
		b = A('View', _class= 'btn', _href=URL('games', 'view', args=[row.id]))
		return b
    def shorten_post(row):
        return row.description[:10] + '...'

    # Creates extra buttons.
    
    links = [
        dict(header='', body = generate_edit_button),
        dict(header='', body = generate_view_button),
        ]
    button = ''
    if show_all:
        button = A('See Open Games', _class='btn', _href=URL('games', 'index'))
    else:
        button = A('See All Games', _class='btn', _href=URL('games', 'index', args=['all']))

  #  if len(request.args) == 0:
        # We are in the main index.
   #     links.append(dict(header='Post', body = shorten_post))
      #  db.games.description.readable = False
    start_idx = 1 if show_all else 0
   # form = SQLFORM.grid(q, args=request.args[:start_idx],
    #form = SQLFORM.grid(q,
    form = SQLFORM.grid(q, args=request.args[:start_idx],
        fields=[db.games.game, db.games.edition,
                db.games.campaign_title,  db.games.meeting_location, db.games.meet_date, 
				 db.games.looking_for_players, db.games.open_spots,
               ], csv = False,
        editable=False, deletable=False, details= False,
        links=links,
        paginate=10,
        )
    test = db().select(db.games.campaign_title).first()
    db.party.insert(campaign_title=test)
    return dict(form=form, show_all=show_all, button=button)
    """
    # This index appears when you go to /games/index . 
    # """
    # # We want to generate an index of the posts. 
    # posts = db().select(db.games.ALL)
    # return dict(posts=posts)

@auth.requires_login()
def new():
    """Add a game."""
    show_all = request.args(0) =='all'
    form = SQLFORM(db.games)
    if form.process().accepted:
        # Successful processing.
        session.flash = T("inserted")
        redirect(URL('games', 'index'))
    return dict(form=form, show_all=show_all)

def view():
    #request to add self to a gamwe
	#allow GM to add people who are requesting to get into game
	#use username to define each person
	#finish adding Request for GM 
	#finish delete or ignore for DM
	#Finish Clean up for unecessary requests
	#add Link to wikia
    """View a post."""
    # p = db(db.games.id == request.args(0)).select().first()
    p = db.games(request.args(0)) or redirect(URL('games', 'index')) #keep track of info from pervious page
    b = db.party(request.args(0)) #keep track of info on this page
    openspots = p.open_spots #number of spots open
    destroy = request.vars.delete #delete function
    hello = db.party.campaign_title == p.campaign_title #makeing sure ot match the right campaign
    isjoin = request.vars.join == 'y'#Check to see if they are requesting to join the game
    isaccepted = request.vars.accepted == 'y' #check to see if accepted var is y
    row_id = request.vars.person #row id 
	
	
    edit_button = '' #edit button for the GM
    if p.user_id == auth.user_id:
        edit_button = A('Edit', _class='btn', _href=URL('games', 'edit', args=[p.id]))
		
		
		
    def generate_accept_button(row):
        accept = '' #if the GM accepts a person
        if auth.user_id == p.user_id:
            accept = A('Accept Request', _class='btn', _href=URL('games', 'view', args = [request.args(0)], vars = dict(person = row.id, join= 'N', accepted ='y' )  ))
        return accept
    def generate_profile_button(row):
        profil = '' #if a Gm wants to check a person's profile. I don't want random people to check other people's profiles
        if auth.user_id == p.user_id:
            profil = A('Check Profile', _class= 'btn',  _href=URL('default', 'profile', args=(b.email) )) #vars = dict(peremail =row.email)
        return profil
    def generate_del_button(row):
        # If the item is ours we can delete it
        b = ''
        if auth.user_id == p.user_id:
            b = A('Ignore Request', _class='btn', _href=URL('games', 'view', args = [request.args(0)], vars = dict(person = row.id, delete= 'y')))
        return b

    links = [ 
             #dict( header = '', body = generate_join_button),
			dict( header = '', body = generate_accept_button),
			dict(header = '', body = generate_profile_button),
			dict(header = '', body = generate_del_button),
			 ]
    form = ''
    button = ''
    form2 = ''
    form_add = ''
    openNumSpotsInc = lambda b: b+1
    openNumSpotsDec = lambda b: b-1

    if destroy:
        db(db.party.id == request.vars.person).delete()
        var = db(db.party.id == request.vars.person).select(db.party.accepted)
        if var:
            p.update_record( open_spots = openNumSpotsInc(openspots)) #increment the counts
        redirect((URL('games', view, args = [request.args(0)])))

    if p.user_id != auth.user_id: #this is for the user, who is not the GM, to request to join
        if isjoin:
          #  if db.party.players == auth.user.email:
			#	if 
				#    session.flash = T('Already Requested.')
                  #  redirect(URL('games', 'view', args = [request.args(0)]))
            #If they requested to join
            form_add = SQLFORM.grid(db.party, fields = [db.party.requesting_to_join], user_signature= False)
            db.party.insert(campaign_title = p.campaign_title, players= auth.user.email, requesting_to_join = True)
        else:
			#have not requested to join yet
            button = A('Request to Join', _class='btn', _href=URL('games', 'view', args = [request.args(0)], vars = dict(join= 'y')  ))
    if isaccepted:		
        if p.user_id == auth.user_id: #check to see if accept the person into the group
            changing = db(db.party.id==row_id).select().first()
            p.update_record(open_spots = openNumSpotsDec(openspots)) #decrease number of Open spots
            changing.update_record(requesting_to_join = False, accepted = True)
			#minus one to open spots
            redirect(URL('games', view, args = [request.args(0)]))
    form = SQLFORM(db.games, record = p, readonly=True) #basic information on the game
    form3 = SQLFORM.grid(hello, fields = [db.party.players, db.party.requesting_to_join, db.party.accepted], user_signature=False, 
						 sortable= False, searchable= False, links = links, csv= False, editable=False, deletable=False, details= False,) #Players in the party


    return dict(form = form, form2=form2, form_add = form_add, form3= form3, edit_button = edit_button, button=button, title = p.campaign_title)


@auth.requires_login()
def edit():
    """Edit a post."""
    show_all = request.args(0) =='all'
    # p = db(db.games.id == request.args(0)).select().first()
    p = db.games(request.args(0)) or redirect(URL('games', 'index'))

    if p.user_id != auth.user_id:
        session.flash = T('Not authorized.')
        redirect(URL('games', 'index'))
    form = SQLFORM(db.games, record=p)
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('games', 'view', args=[p.id]))
    # p.name would contain the name of the poster.
    return dict(form=form, show_all=show_all)

@auth.requires_login()
def delete():
    """Deletes a post."""
    p = db.games(request.args(0)) or redirect(URL('games', 'index'))
    if p.user_id != auth.user_id:
        session.flash = T('Not authorized.')
        redirect(URL('games', 'index'))
    db(db.games.id == p.id).delete()
    redirect(URL('games', 'index'))

@auth.requires_login()
def delete2():
    """Deletes a post."""
    p = db.games(request.args(0)) or redirect(URL('games', 'index'))
    if p.user_id != auth.user_id:
        session.flash = T('Not authorized.')
        redirect(URL('games', 'index'))
    db(db.party.id == row.id).delete()
    redirect(URL('games', 'index'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
