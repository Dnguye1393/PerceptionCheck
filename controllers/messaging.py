#messaging system. Index really isn't used so won't be connecting to that all. 
#mostly going to go around with
# create and inbox and read
#messaging
#allow people to contact each other
def index():
    return dict()
    
@auth.requires_login()    
def inbox():
    body=db(db.mssging.reciever_email == auth.user.id).select(db.mssging.ALL) #puts all the messages For the user into one spot
    var = db.mssging(request.args(0))
    form = ''
    return dict(body=body, form = form)
    

@auth.requires_login()        
def create():
    form=SQLFORM(db.mssging) #messaging system using SQLFORM
    if form.accepts(request.vars, session):
        session.flash='Record inserted'
        redirect(URL(r=request,f='inbox'))
    elif form.errors:
        response.flash='error'
    return dict(form=form)


def truncate():
    return db.mssging.truncate()
        
@auth.requires_login()    
def read():
    return dict(form=SQLFORM(db.mssging, request.args(0), readonly= True)) #put specific message on screen 
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id[
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
