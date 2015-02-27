import os
import re
from string import letters

import webapp2
#import jinja2

from google.appengine.ext import db

#template_dir = os.path.join(os.path.dirname(__file__), 'templates')
#jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
#                               autoescape = True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello webapp world!')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
