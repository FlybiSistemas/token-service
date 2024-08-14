import os

def get_user():
    try:
        user_dir = os.path.expanduser('~')
        username = os.path.basename(user_dir)
        if(username != None):
            return username
        user_dir = os.getenv('USERPROFILE')
        username = os.path.basename(user_dir)
        if(username != None):
            return username
    except (IndexError, FileNotFoundError):
        try:
            user_dir = os.getenv('USERPROFILE')
            username = os.path.basename(user_dir)
            if(username != None):
                return username
        except:
            return os.getlogin()
        
print('Existe varias formas de encontrar o nome da pasta referente a seu usuário, caso uma não de certo, sera tentado outra forma...')

print('Nome da pasta (Todas as formas):')
print('Tentativa 1: '+os.path.basename(os.path.expanduser('~')))
print('Tentativa 2: '+os.path.basename(os.getenv('USERPROFILE')))
print('Tentativa 3: '+os.getlogin())

print('Para o nome do usuário só existe uma forma, que é: '+os.login())