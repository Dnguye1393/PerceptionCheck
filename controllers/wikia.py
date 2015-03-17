import logging
from datetime import datetime

# Main Function for wikia
#Most of the code is taken straight from the homeworks
def index():
    # Title of page is reached at request.args(0)
    title = request.args(0) or 'main page'
    # Redirect to main page
    if title == 'main page':
        redirect(URL('wikia', 'index', args = [title]))

    form = None
    content = None
    newpost = request.vars.newpost == 'true'
    editing = request.vars.edit == 'true'
    history = request.vars.history == 'true'
    content = ''

    edit_button = False


    display_title = title.title()

    # Selecting the most recent revision
    page = db(db.pagetable.name == title).select().first()
    # Assigning the proper ID address
    page_id = page.id if page is not None else ''

    # Executed if no page currently exists. Taken from @163 on Piazza
    if page is None:
        content = SQLFORM.confirm('Create new page?')
        if content.accepted:
            redirect(URL('wikia', 'index', args=[title], vars=dict(newpost='true')))
    # Executed if revisions exist and can be edited
    else:
        rev = db(db.revision.page_id == page.id).select(orderby=~db.revision.date_posted).first()
        # Below was originally not working, but Rakshit helped to fix
        content = represent_wiki(rev.body)
        edit_button = True

    # Process for developing a new wiki page, very similar to developing a revision
    if newpost:
        form = SQLFORM.factory(Field('body', 'text',
                                     label='Content',
                                     ))
        form.add_button('Cancel', URL('wikia', 'index', args=[title]))
        if form.process().accepted:
            if page is None:

                page_id=db.pagetable.insert(name=title)
                db.revision.insert(body=form.vars.body, page_id=page_id)
            redirect(URL('wikia', 'index', args=[title]))
        content = form

    if editing:
        rev = db(db.revision.page_id == page.id).select(orderby=~db.revision.date_posted).first()
        form = SQLFORM.factory(Field('body', 'text',
                                     label='Content',
                                     wikia= rev.body,
                                     ),
                               Field('comments', 'text',
                                     label='Comment',
                                     wikia= rev.comments,))
        form.add_button('Cancel', URL('wikia', 'index', args=[title]))
        if form.process().accepted:
            author = ''
            if auth.user == None:
                author = request.client
            else:
                author = auth.user.first_name
            db.revision.insert(body=form.vars.body, page_id=page.id, comments=form.vars.comments, author=author)
            redirect(URL('wikia', 'index', args=[title]))
        content = form

    if history:
        def generate_revert_button(row):
            b = SQLFORM.confirm('Revert to this Revision')
            if b.accepted:
                author = ''
                if  auth.user == None:
                    author = request.client
                else:
                    author = auth.user.first_name
                f = "%d-%m-%Y %H:%M:%S"
                comment = "Reverted to " + row.date_posted.strftime(f) + " UTC"
                db.revision.insert(body=row.body, page_id=row.page_id, editior_comment=comment, author=author)
                redirect(URL('wikia', 'index', args =[title]))
            return b

        links = [
            dict(header='', body = generate_revert_button),
        ]
        table = db.revision
        gah = table.page_id
        q = gah == page.id

        form = SQLFORM.grid(q, args=request.args,
            fields=[db.revision.author, db.revision.date_posted,
            db.revision.comments],
            editable = False, deletable=False,
            links=links,
            paginate=10,
            details = False,
        )
        content = form

    # Return the title, content, declaration of the state of the page (newpost), and functionality to edit to the index view
    return dict(display_title=display_title, content=content, title=title,  newpost=newpost, edit_button=edit_button)


def test():
    """This controller is here for testing purposes only.
    Feel free to leave it in, but don't make it part of your wiki.
    """
    title = "This is the wiki's test page"
    form = None
    content = None


    # Gets the body s of the page.
    r = db.testpage(1)
    s = r.body if r is not None else ''
    # Are we editing?
    editing = request.vars.edit == 'true'
    # This is how you can use logging, very useful.
    logger.info("This is a request for page %r, with editing %r" %
                 (title, editing))
    if editing:
        # We are editing. .
        form = SQLFORM.factory(Field('body', 'text',
                                     label='Content',
                                     wikia=s
                                     ))
        # You can easily add extra buttons to forms.
        form.add_button('Cancel', URL('wikia', 'test'))
        # Processes the form.
        if form.process().accepted:
            # Writes the new content.
            if r is None:
                # First time: we need to insert it.
                db.testpage.insert(id=1, body=form.vars.body)
            else:
                # We update it.
                r.update_record(body=form.vars.body)

            redirect(URL('wikia', 'test'))
        content = form
    else:
        # We are just displaying the page
        content = s
    return dict(display_title=display_title, content=content, editing=editing)


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
