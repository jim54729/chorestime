import os
import re
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class ChoreFront(BlogHandler):
    def get(self):
        chores = db.GqlQuery("select * from Chore order by times_completed desc limit 10")
        self.render('front.html', chores = chores)

class AddChore(BlogHandler):
    def get(self):
        self.render('add-chore.html')

    def post(self):
        name = self.request.get('chore_name')
        description = self.request.get('chore_description')

        if name and description:
            # TODO - Implement error handling for duplicate chore 
            chore = Chore(key_name = name,  
                          name = name, 
                          description = description, 
                          times_completed = 0, 
                          last_doer = "No one")
            chore.put()
            self.redirect('/')
        else:
            error = "Please provide a chore name and description!"
            self.render("add-chore.html", name = name, description = description, error=error)

class DoChore(BlogHandler):
    def get(self):
        self.render('do-chore.html')

    def post(self):
        chore_name = self.request.get('chore_name')
        doer = self.request.get('doer_name')

        if chore_name and doer:
            # Grab chore from database
            query = db.GqlQuery("SELECT * FROM Chore WHERE name = :1", chore_name)
            chore = query.get()
            # Update chore attributes
            chore.times_completed += 1
            chore.last_doer = doer
            # Update chore in database and redirect user to updated front page
            chore.put()  # chore.last_completed is automatically updated here by the Datastore
            self.redirect('/')
        else:
            error = "Please provide chore name and your name!"
            self.render("do-chore.html", chore_name = chore_name, doer_name = doer, error=error)


class ChoreDetail(BlogHandler):
    def get(self):
        self.render('chore-detail-enter.html')

    def post(self):
        chore_name = self.request.get('chore_name')

        if chore_name:
            # Grab reference to user-specified chore from database 
            query = db.GqlQuery("SELECT * FROM Chore WHERE name = :1", chore_name)
            chore = query.get()
            # Render chore-detail.html with chore info
            self.render('chore-detail.html', chore = chore)
        else:
            error = "Please enter a chore name!"
            self.render("chore-detail-enter.html", chore_name = chore_name, error=error)


class RemoveChore(BlogHandler):
    def get(self):
        self.render('remove-chore.html')

    def post(self):
        chore_name = self.request.get('chore_name')

        if chore_name:
            # Grab reference to user-specified chore from database 
            query = db.GqlQuery("SELECT * FROM Chore WHERE name = :1", chore_name)
            chore = query.get()
            # Delete chore from database and redirect user to updated front page
            chore.delete()
            self.redirect('/')
        else:
            error = "Please enter a chore name!"
            self.render("remove-chore.html", chore_name = chore_name, error=error)


class Chore(db.Model):
    name = db.StringProperty(required = True)
    description = db.TextProperty(required = True)
    times_completed = db.IntegerProperty()
    last_doer = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_completed = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.description.replace('\n', '<br>')
        return render_str("chore.html", chore = self)


app = webapp2.WSGIApplication([('/', ChoreFront), 
							   ('/addchore', AddChore), 
                               ('/removechore', RemoveChore),
                               ('/dochore', DoChore), 
                               ('/choredetail', ChoreDetail)
								], 
								debug=True)
