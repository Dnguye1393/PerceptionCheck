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
    if p.email == auth.user.email:
        editButton = A('Edit Profile', _class='btn', _href=URL('default', 'edit', args=[emailz]))
  #  if profile_id is None: # check to see accessed not from view
 #       profile_id = auth.user_id
        
  #  profile_base =(db.profiling.email == request.args(0))#gets the specific profile
#    if profile_base is None: # if new profile
 #       redirect(URL('default', 'new'))
   # form = SQLFORM(profile_base, fields=[db.profiling.first_name, db.profiling.last_name, db.profiling.email, db.profiling.bio],
        #                deletable = False, csv=False,)
   # form = SQLFORM(db.profiling, readonly= True)
 #   if editing:
  #      redirect(URL('default', 'edit', args=[profile_id]))

    #if normal view
     #view it

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
    p = db.profiling(db.profiling.email == emailz)#or redirect(URL('default', 'index'))
    form = SQLFORM(db.profiling, record=p)
    #form = SQLFORM.factory(Field('First_Name', default = p.first_name),
     #                      Field('Last_Name', default = p.last_name),
      #                     Field('Email', default = p.email),
       #                    Field('bio', default= p.bio,),
        #                   table_name = 'Profile')
    
    
    if form.process().accepted:
        p.update_record(**dict(form.vars))
        #db(p).update(first_name = form.vars.First_Name)
        #db(p).update(last_name = form.vars.Last_Name)
        #db(p).update(email = form.vars.Email)
        #db(p).update(bio = form.vars.bio)
        session.flash = T('Updated')
        redirect(URL('default', 'profile', args=(auth.user.email)))
    # p.name would contain the name of the poster.
    return dict(form=form, editing=emailz)
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
