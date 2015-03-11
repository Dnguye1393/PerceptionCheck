from sys import path
path.insert(1, '/home/www-data/web2py/')
from gluon import *
print "hello world!"

db = DAL('sqlite://storage.sqlite')
db.define_table('person', Field('name'))
db.person.insert(name="Nate")

print "things seem to have worked."
