# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations


import logging
logging.basicConfig(filename='errors.log', level=logging.DEBUG)


def confirm():
    form = FORM.confirm("Yes")
    title = request.args(0)
    if form.accepted:
        page_id = db.pagetable.insert(title=title)
        db.revision.insert(page_id=page_id, auth=auth.user.first_name + ' ' + auth.user.last_name)
        redirect(URL('default', 'index', args=[title], vars=dict(edit='true')))
#    else:
#        redirect(URL('default', 'index'))

    return dict(form=form)

@auth.requires_login()
def login():
    redirect(URL('default', 'index', args=[request.args(0) or 'Main Page'], vars=dict(edit='true')))

@auth.requires_login()
def index():
        title = request.args(0) or 'Main_Page'
        display_title = title.title().replace('_', ' ')
        editing = auth.user.email
        return dict(display_title=display_title, editing=editing)

	
	
#Profile Edit and new are All part of the Profile Function. 
@auth.requires_login()
def profile():
	#Profile will ahve their name and Email adress
	#will have a Preferred type of game Games
	#will have Bio ,or a background to allwo DM to get insight onto their player
    
    emailCheck = request.vars.peremail
    emailz= ''
    if emailCheck is None:
        emailz = request.args(0)
    else:
        emailz = emailCheck
        
        
    p = db.profiling(db.profiling.email == emailz)#or redirect(URL('default', 'index'))
    form = SQLFORM(db.profiling, record=p, readonly=True)
    editButton = ''
    #if p.email == auth.user.email:
    editButton = A('Edit Profile', _class='btn', _href=URL('default', 'edit', args=[emailz]))


    return dict(form=form, editing = emailz, editButton = editButton)
	
	
@auth.requires_login()
def new():
    """Add a profile."""
    form = SQLFORM(db.profiling)
    if form.process().accepted:
        # Successful processing.
        session.flash = T("inserted")
        redirect(URL('default', 'index'))
    return dict(form=form)
	
@auth.requires_login()
def edit():
    """Edit a profile."""
    emailz = request.args(0)
    v= db.profiling(request.args(0))
    p = db.profiling(db.profiling.email == emailz)#or redirect(URL('default', 'index'))
    if request.args(0) != auth.user.email:
        session.flash = T('Not authorized.')
        redirect(URL('default', 'index'))
    form = SQLFORM(db.profiling, record=p)
    if form.process().accepted:

        session.flash = T('Updated')
        redirect(URL('default', 'profile', args=(auth.user.email)))
    # p.name would contain the name of the poster.
    return dict(form=form, editing=emailz)

#Forum and Edit both are part of the 'same' functions of Creating a Forum for the website

def forum():
    #The forums allow users to discuss topics over a public area
    #this does not overlap with messages because it provides an open, recorded discussion for everyone to see
    #can also act as a looking for group/dm for the users as well
    """Forum base index"""
    editing = request.vars.editing
    def generate_view_button(row):
        b = A('View', _class='btn', _href=URL('default', 'view', args=[row.id]))
        return b
    
    if editing:
        button = ''
        form = SQLFORM.factory(db.forums) #forums Form llowing user to edit
        if form.process().accepted:
            db.forums.insert(body=form.vars.body, title=form.vars.title, topic=form.vars.topic)
            redirect(URL('default', 'forum'))
        elif form.errors:
            response.flash='error'

    else:
        links=[dict(header='', body = generate_view_button)]

        form = SQLFORM.grid(db.forums, user_signature = False,
                fields=[db.forums.title, db.forums.topic, db.forums.date_posted, db.forums.poster],
                editable=False, deletable=False, details = False, create = False, searchable = False, csv = False, 
                paginate=10, orderby =~ db.forums.date_posted,  links=links)

    return dict(form=form)



def view():
    """View the Forums"""
    #Tied specifcally to Forums
    row_id = request.args(0)#Grab Everything
    form2 = ''
    rightOne = db.forums.id == request.args(0)
    title = db.forums(row_id).title
    form = SQLFORM.grid(rightOne, fields=[db.forums.title, db.forums.specific_campaign, db.forums.topic, db.forums.poster, db.forums.date_posted, ],
                        sortable= False, searchable= False, csv= False, editable=False, deletable=False, create = False, details= False, user_signature= False )
    check = db.forums(row_id).body #get Description
    posting = request.vars.posting 
    button = A('Post', _class='btn', _href=URL('default', 'view', args = [row_id], vars=dict(posting= True)))  
    thread = db(db.forums.title == title).select().first()
    thread_id = thread.id if thread is not None else None
    if posting:
        button = ''
        form = SQLFORM.factory(db.forumThread)
        if form.process().accepted:
            db.forumThread.insert(body=form.vars.body, forumThread_id = thread_id)
            redirect(URL('default', 'view', args = [row_id]))

    else:
        form2 = SQLFORM.grid(db.forumThread.forumThread_id == thread_id, user_signature = False,
                fields=[db.forumThread.date_posted,db.forumThread.body, db.forumThread.poster],
                editable=False, deletable=False, details = False, create = False, searchable = False, csv = False, 
                paginate=10, orderby = db.forumThread.date_posted)

    # p.name would contain the name of the poster.
    return dict(form=form, form2=form2, check=check, button=button)





def user():
    """ge_id = str(page.id)page_id = str(page.id)
            # We are just displaying the page
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
