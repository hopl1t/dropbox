"""
Networks 8 - Dropbox
A file sharing client and server
"""



FORAMT_TIME = r'%Y%j%H%M%S'
download_dict = {}

class File(object):
    """
    A file object that describes varias attributes of a single file or folder
    """
    global download_dict
    def __init__(self, abs_file_path):
        self.path = abs_file_path
        self.name = os.path.XXX
        self.ext = os.path.XXX
        self.isdir = os.isdir(abs_file_path)
        self.size = os.path.XXX
        self.create_time = os.path.XXX
        if download_dict.has_key(abs_file_path):
            self.downloas = download_dict[abs_file_path]
        else:
            self.downloas = 0

def make_timestamp():
    """
    Returns a string representing local time.
    Format is: year-day in year-hour-minute-second
    example: 2018048143254:
        Year: 2018
        Day: 48
        Time: 14:32:54
    """
    ltime = datetime.today()
    timestamp = ltime.strftime(FORAMT_TIME)
    return timestamp


if __name__ == "__main__":
    print 'Start by creating a DSODServer object'
