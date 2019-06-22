from werkzeug.routing import BaseConverter
import numpy as np
import flask.json as json


class ListConverter(BaseConverter):
    """Convert the remaining path segments to a list"""

    def __init__(self, url_map):
        super(ListConverter, self).__init__(url_map)
        self.regex = "(?:.*)"

    def to_python(self, value):
        # remove trailing /
        return value.rstrip("/").split(u"/")

    def to_url(self, value):
        return u"/".join(value)


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
