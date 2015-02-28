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
        chores = db.GqlQuery("select * from Chore order by created desc limit 10")
        self.render('front.html', chores = chores)

class AddChore(BlogHandler):
    def get(self):
        self.render('add-chore.html')

    def post(self):
        name = self.request.get('chore_name')
        description = self.request.get('chore_description')

        if name and description:
            # TODO - Implement error handling for duplicate chore 
            chore = Chore(parent = blog_key(), 
                          key_name = name,  
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
        doer_name = self.request.get('doer_name')

        if doer_name:
            # TODO - Update times_completed, last_doer, last_completed for the chore
            self.redirect('/')
        else:
            error = "Please enter your name!"
            self.render("do-chore.html", doer_name = doer_name, error=error)

class ChoreDetail(BlogHandler):
    def get(self):
        self.render('chore-detail.html')

    def post(self):
        doer_name = self.request.get('doer_name')

        if doer_name:
            # TODO - Update times_completed, last_doer, 
            # last_completed(done automatically) for the chore
            self.redirect('/')
        else:
            error = "Please enter your name!"
            self.render("do-chore.html", doer_name = doer_name, error=error)


def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

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
                               ('/dochore', DoChore), 
                               ('/choredetail', ChoreDetail)
								], 
								debug=True)
