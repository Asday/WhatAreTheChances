class Result(object):
    def __init__(self, succeeded, **kwargs):
        self.success = succeeded
        self.__dict__.update(kwargs)

    def __repr__(self):
        if self.success:
            members = [member
                       for member
                       in dir(self)
                       if (member != "success")
                       and (member[0] != "_")]
            if not members:
                members = ["None"]
            return "Success!  Members available:  %s" % ", ".join(members)
        else:
            if any(map(self.__dict__.has_key, ("reason", "message"))):
                try:
                    tail = self.reason
                except AttributeError:
                    tail = self.message
            else:
                tail = ""

            return "Failure%s" % tail