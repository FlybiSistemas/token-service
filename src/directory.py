import os

class Directory:
    directory = ''
    icons = ''
    raiz = ''
    service = ''
    monitor = ''
    tmp = ''
    certificados = ''
    extensions = ''
    usuario = ''
    usuarioNome = ''
    success = False
    message = ''

    def __init__(self):
        self.usuario = self.get_user()
        self.usuarioNome = os.getlogin()
        self.directory = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/')
        self.icons = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/icons')
        self.tmp = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/tmp')
        self.certificados = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/certificados')
        self.extensions = self.create_dir('C:/Users/'+self.usuario+'/AppData/Local/Google/Chrome/User Data/Default/Extensions')
        self.log = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/log')
        self.service = os.getcwd()+'/TokenService.exe'
        self.monitor = os.getcwd()+'/ByTokenMonitor.exe'
        self.raiz = os.getcwd()
        self.success = True

    def set_directory(self, dir):
        self.directory = dir

    def create_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def create_dirs(self, directorys):
        for i in range(len(directorys)):
            self.create_dir(directorys[i])

    def is_dir(self, directory):
        return os.path.isdir(directory)

    def get_user(self):
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
        
    def send_log(self, text):
        arquivo = self.log+'/log.txt'
        if os.path.isfile(arquivo):
            with open(arquivo, 'a') as f:
                f.write(text+'\n')
        else:
            with open(arquivo, 'w') as f:
                f.write(text+'\n')
        return True

    def get_object_certificates(self):
        cont = 0
        certificates = os.popen('certutil -user -store "MY"').read()
        lines = certificates.split("\n")
        certificados = []
        for line in lines:
            try:
                if('Requerente' not in line and "Número de Série" not in line and "Emissor" not in line and "NotAfter" not in line):
                    continue

                if ("Emissor" in line):
                    emissor = line.split(",")[0].split('=')[1]

                if ("NotAfter" in line):
                    data_validade = line.split(":")[1].strip().split(' ')[0]

                if ("Número de Série" in line):
                    numero_serie = line.split(":")[1].strip()

                if ('Requerente' in line):
                    camposRequerente = line.replace('Requerente: ','').split(',')
                    requerente = next((item for item in camposRequerente if "CN=" in item), None)
                    requerente = requerente.split('=')[1].split(":")
                    if len(requerente) == 1:
                        continue
                    cnpj = requerente[1].strip()
                    razao_social = requerente[0].strip()
                    certificados.append(
                        {
                            "cnpj": cnpj,
                            "razao_social": razao_social,
                            "num_serie": numero_serie,
                            "data_validade": data_validade,
                            "emissor": emissor
                        }
                    )
                    cont = cont + 1
            except:
                continue
        return certificados

    def scan_users_ad(self, usuario):
        valid_user = ''
        cont_user = 0
        for user in os.listdir('C:/Users'):
            if(usuario in user):
                print('Usuario encontradao: '+user)
                cont_user = cont_user + 1
                valid_user = user

        print('Retornando user: '+valid_user+', cont: '+str(cont_user))
        return {
            'user': valid_user,
            'qtd': cont_user
        }
                
    def remove_created_dir(self):
        if self.directory and os.path.exists(self.directory):
            for root, dirs, files in os.walk(self.directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.directory)
            
    def destroy(self):
        for root, dirs, files in os.walk(self.directory, topdown=False):
            # Remove todos os arquivos
            for file in files:
                caminho_arquivo = os.path.join(root, file)
                os.remove(caminho_arquivo)
                print(f"Arquivo removido: {caminho_arquivo}")
            
            # Remove todas as subpastas
            for dir in dirs:
                caminho_dir = os.path.join(root, dir)
                os.rmdir(caminho_dir)
                print(f"Pasta removida: {caminho_dir}")
        
        # Após remover o conteúdo, remove a pasta principal
        os.rmdir(self.directory)
        print(f"Pasta principal removida: {self.directory}")
             
            
            