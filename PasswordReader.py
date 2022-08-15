class PasswordReader():
    def __init__(self,ui):
        self.ui = ui
        self.password  = None
        self.name = None
        self.hasFile = False
        self.correctPassword = False
        self.search_password_file()

    def search_password_file(self):
        try:
            with open('password', "r") as f:
                self.read_password_file(f)
                self.hasFile = True
                if self.ui.check_if_password_is_correct( self.name,self.password):
                    self.correctPassword = True
        except IOError:
            return False

    def read_password_file(self, file):
        name = file.readline().strip('\n')
        password = file.readline().strip('\n')
        self.password = password
        self.name = name

    def write_password_file(self,name,password):
        self.password = password
        self.name = name
        f = open('password', "w")
        f.write(name+'\n'+password)
        f.close()


