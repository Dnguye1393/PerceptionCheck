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

        return dict(display_title=display_title)

@auth.requires_login()
def profile():
    if not auth.is_logged_in():
        session.flash = "You do not have permission to view this profile"
        redirect(URL('default', 'index'))

    user_prof= db(db.cohort.user_id == auth.user_id).select().first() or None
    if user_prof == None:
        if request.vars.edit != 'true':
            redirect(URL('default', 'profile', vars=dict(edit='true')))
        else:
            bad_access = False
            is_mine = True
            given_id = 0 # Guaranteed to lead to edit
    else:
        given_id = user_prof.user_id if request.vars.id == None else int(request.vars.id)
        bad_access = True
        is_mine = (given_id == user_prof.user_id)
        bad_access = False


    form = None
    cohor = db(db.cohort.user_id == given_id).select().first() or None

    edit = (request.vars.edit == 'true') and is_mine
    if (edit == True):
        form = SQLFORM.factory( Field('firstname', default = get_first_name(), label = "First Name"),
                                Field('lastname', default = get_last_name(), label = "Last Name"),
                                Field('Email', requires = IS_EMAIL()),
                                Field('Biography', 'text'),
                               )
        #Use form w/ defaults if they already have profile
        if(cohor != None):
            form = SQLFORM.factory(
                                Field('firstname', default = get_first_name(), label = "First Name"),
                                Field('lastname', default = get_last_name(), label = "Last Name"),
                                Field('Email', requires = IS_EMAIL(), default = cohor.email),
                                Field('Biography', 'text'),
                                )

        form.add_button('Cancel', URL('default', 'profile'))
        if form.process().accepted:
            if cohor == None:
                new_ID = db.cohort.insert(first_name = form.vars.firstname,
                                            last_name = form.vars.lastname,
                                            email = form.vars.Email,
                                            bio = form.vars.Biography,
                                            user_id = auth.user_id)
                redirect(URL("default", "index"))
            else:
                 cohor.update_record(first_name = form.vars.firstname,
                                       last_name = form.vars.lastname,
                                       email = form.vars.Email,
                                       bio = form.vars.Biography)
                 redirect(URL("default", "profile"))
    else:
        if(cohor != None):
            if(cohor.user_id != auth.user_id):
                db.cohort.last_name.readable = False
            else: db.cohort.last_name.readable = True
            form = SQLFORM(db.cohort, record = cohort, readonly = True)
    return dict(form=form,edit=edit,editBtn=((not edit) and is_mine), name = get_first_name())
	
	
	
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
