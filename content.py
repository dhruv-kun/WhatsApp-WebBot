from datetime import datetime


class Content(object):
    def __init__(self):
        self._sent = []

    def set_type(self, data_type):

        try:
            assert data_type in ('text', 'media', 'document')
        except AssertionError:
            raise(TypeError(
                "must be text, media or document, not %s" % data_type))
        self._data_type = data_type

    def set_content(self, message=None,
                    filepath=None, file_format=None,
                    website=None, timestamp=None):
        if message is not None:
            self._message = message.replace('.', '.\n').split('\n')
        if not self._data_type == 'text':
            self._filepath = filepath
            self._format = file_format

        if isinstance(timestamp, tuple):
            self._timestamp = datetime.strptime(
                timestamp[0], timestamp[1]).time()
        else:
            self._timestamp = datetime.ctime(datetime.now())

        self._website = website

    def get_type(self):
        return self._data_type

    def get_message(self):
        return self._message

    def get_file(self):
        return self._filepath

    def get_timestamp(self):
        return self._timestamp

    def get_website(self):
        return self._website

    def add_reciver(self, reciver):
        self._sent.append(reciver)

    def save(self, file):
        # Pass a json file and save data of the
        # Content data in json format in the passed
        # file
        pass

    def __str__(self):
        stng = ""
        stng += "%s %s\n" % ("Type:", self._data_type)
        if self._data_type == 'text':
            stng += "%s %s\n" % ("Message:", self._message)
        else:
            stng += "%s %s\n" % ("Filename:", self._filepath)
            stng += "%s %s\n" % ("Format:", self._format)
            if self._message:
                stng += "%s %s\n" % ("Message:", self._message)
        stng += "%s %s\n" % ("Website:", self._website)
        stng += "%s %s\n" % ("Timestamp:", self._timestamp)
        return stng

    def __repr__(self):
        stng = ""
        stng += "%s %s\n" % ("Type:", self._data_type)
        if self._data_type == 'text':
            stng += "%s %s\n" % ("Message:", self._message)
        else:
            stng += "%s %s\n" % ("Filename:", self._filepath)
            stng += "%s %s\n" % ("Format:", self._format)
            if self._message:
                stng += "%s %s\n" % ("Message:", self._message)
        stng += "%s %s\n" % ("Website:", self._website)
        stng += "%s %s\n" % ("Timestamp:", self._timestamp)
        return stng
