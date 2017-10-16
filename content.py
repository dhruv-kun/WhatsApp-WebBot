class Content(object):
    def __init__(self, data_type):
        # image, text, document
        assert data_type in ('text', 'media', 'document')
        self.data_type = data_type

        if self.data_type == 'text':
            self.message = None

        else:
            self.filepath = None
            self.format = None
            self.message = None

        self.website = None
        self.timestamp = None

    def save(self, file):
        # Pass a json file and save data of the
        # Content data in json format in the passed
        # file
        pass

    def __str__(self):
        stng = ""
        stng += "%s %s\n" % ("Type:", self.data_type)
        if self.data_type == 'text':
            stng += "%s %s\n" % ("Message:", self.message)
        else:
            stng += "%s %s\n" % ("Filename:", self.filename)
            stng += "%s %s\n" % ("Format:", self.format)
            if self.message:
                stng += "%s %s\n" % ("Message:", self.message)
        stng += "%s %s\n" % ("Website:", self.website)
        stng += "%s %s\n" % ("Timestamp:", self.timestamp)
        return stng
