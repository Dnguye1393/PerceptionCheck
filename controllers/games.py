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

    if len(request.args) == 0:
        # We are in the main index.
        links.append(dict(header='Post', body = shorten_post))
        db.games.description.readable = False
    start_idx = 1 if show_all else 0
   # form = SQLFORM.grid(q, args=request.args[:start_idx],
    #form = SQLFORM.grid(q,
    form = SQLFORM.grid(q, args=request.args[:start_idx],
        fields=[db.games.game, db.games.edition, db.games.date_posted,
                db.games.campaign_title,  db.games.meeting_location, db.games.meet_date, 
				db.games.welcome_new, db.games.looking_for_players, db.games.open_spots,
                db.games.description], csv = False,
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
    """View a post."""
    # p = db(db.games.id == request.args(0)).select().first()
    p = db.games(request.args(0)) or redirect(URL('games', 'index'))
    b = db.party(request.args(0))
    hello = db.party.campaign_title == p.campaign_title
    isjoin = request.vars.join == 'y'#Check to see if they are requesting to join the game
    form3 = SQLFORM.grid(hello, fields = [db.party.players, db.party.requesting_to_join], user_signature=False, 
						 sortable= False, searchable= False, csv= False,)
# if isjoin:
     #   db.players.update( requesting_to_join = auth.username)
    #    
    links = [ 
             #dict( header = '', body = generate_join_button),
			# dict( header = '', body = generate_accept_button),
			 ]
    form = ''
    button = ''
    form2 = ''
    form_add = ''
    if p.user_id != auth.user_id: #this is for the user, who is not the GM, to request to join
        if isjoin:
            #If they requested to join
            #form_add = SQLFORM.grid(db.party, fields = [db.party.requesting_to_join], user_signature= False)
            db.party.insert(campaign_title = p.campaign_title, requesting_to_join = auth.user_id)
        else:
			#have not requested to join yet
            button = A('Request to Join', _class='btn', _href=URL('games', 'view', args = [request.args(0)], vars = dict(join= 'y')  ))
    form = SQLFORM(db.games, record = p, readonly=True)
    
    return dict(form = form, form2=form2, form_add = form_add, form3= form3, button=button)


@auth.requires_login()
def edit():
    """View a post."""
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
