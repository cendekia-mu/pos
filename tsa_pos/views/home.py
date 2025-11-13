from . import BaseViews
import logging
_logging = logging.getLogger(__name__)
class Views(BaseViews):
    def beranda(self):
        _logging.debug("Rendering home view")
        return {'message': 'Welcome to the Home Page'}