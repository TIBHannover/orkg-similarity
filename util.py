from werkzeug.routing import BaseConverter


class ListConverter(BaseConverter):
    """Convert the remaining path segments to a list"""

    def __init__(self, url_map):
        super(ListConverter, self).__init__(url_map)
        self.regex = "(?:.*)"

    def to_python(self, value):
        return value.split(u"/")

    def to_url(self, value):
        return u"/".join(value)
