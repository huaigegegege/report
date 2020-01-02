from datetime import datetime


class display(object):

    def __init__(self):
        super().__init__()
        self.title='Azure DevOps'
        self.year=datetime.now().today()
        self.header=[]
        self.body=[]
        self.msg=''
        self.emsg=''
        self.type=''