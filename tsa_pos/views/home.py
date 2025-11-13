from . import BaseViews
class Views(BaseViews):

    def home(self):
        return {'message': 'Welcome to the Home Page'}