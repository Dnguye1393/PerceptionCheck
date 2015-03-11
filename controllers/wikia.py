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
        redirect(URL('wikia', 'index', args=[title], vars=dict(edit='true')))
#    else:
#        redirect(URL('default', 'index'))

    return dict(form=form)

@auth.requires_login()
def login():
    redirect(URL('wikia', 'index', args=[request.args(0) or 'Main Page'], vars=dict(edit='true')))


def index():
        title = request.args(0) or 'Main_Page'
        form = None
        content = ''
        response.title = ''

        # Let's uppernice the title.  The last 'title()' below
        # is actually a Python function, if you are wondering.
        display_title = title.title().replace('_', ' ')

        
        #find the matching page.
        page = db(db.pagetable.title==title).select().first()
        #if page == None:
        #    redirect(URL('default', 'confirm', args=request.args))
        

        # Get the page ID.
        page_id = str(page.id)


        # Find the most recent revision with matching page ID.  
        r = db(db.revision.page_id == page_id).select(orderby=~db.revision.date_created).first()
        s = r.body if r is not None else ''
        
        # Are we editing?
        editing = request.vars.edit == 'true'
        history = request.vars.history == 'true'
        autosubmit = request.vars.autosubmit == 'true'

        # This is how you can use logging, very useful.
        logger.info("This is a request for page %r, with editing %r" %
             (title, editing))

        if editing:
            if not auth.is_logged_in():
                redirect(URL('wikia', 'login', args=request.args))

            # Get first and last names
            first_name = auth.user.first_name
            last_name = auth.user.last_name

            # We are editing.  Gets the body s of the page.
            # Creates a form to edit the content s, with s as wikia.
            form = SQLFORM.factory(Field('body', 'text',
                label='Content',
                wikia=s))
            # You can easily add extra buttons to forms.
            form.add_button('Cancel', URL('wikia', 'index', args=request.args))
            
            # Processes the form.
            if form.process().accepted:
                 db.revision.insert(page_id=page_id, auth=first_name + ' ' + last_name, body=form.vars.body)
                 redirect(URL('wikia', 'index', args=request.args))
            content = form
        elif history:
            # Create a page contain a list of all revisions.
            # Ror each revision, give in reverse chronological order:
            #   -  Author, if the user was logged in, or else IP address,
            #      if the user who created the revision was not logged in.
            #   - Time at which the revision was done. In the honor version
            #     of the assignment, implement time localization (see assignment).
            #   - C comment indicating the purpose of the revision (so when you
            #     edit, ask for such a comment, together with the edit).
            #   - A button that ssays revert to this revision.

            # Create a SQLFORM.grid and connect to it.
            def generate_revert_button(row):
                # Create a new edit with the content of the revision at *row*)
                return A('Revert to this revision', _class='btn', _href=URL('wikia', 'index', 
                    args=request.args, vars=dict(edit='true', autosubmit='true')))
            
            # Create link to "publish revision" button.
            links = [
                dict(header='', body = generate_revert_button)
                ]

            # Select all revisions with page_id matching the current page.
            query = db.revision.page_id == page_id
             
            # Create an SQLFORM.grid to view the revisions
            form = SQLFORM.grid(query,
                fields =[db.revision.auth, db.revision.date_created,
                         db.revision.rcomment],
                links = links,
                csv=False)
            content = form
        else:
            content = s
        return dict(display_title=display_title, content=content, editing=editing, history=history, revision=r)


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
