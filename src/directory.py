import os

class Directory:
    directory = ''
    icons = ''
    raiz = ''
    service = ''
    tmp = ''
    usuario = ''
    success = False
    message = ''

    def __init__(self):
        self.usuario = self.get_user()
        for i in range(0, 2):
            try:
                self.directory = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/')
                self.icons = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/icons')
                self.tmp = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/tmp')
                self.log = self.create_dir('C:/Users/'+self.usuario+'/arquivos_bytoken/log')
                self.service = os.getcwd()+'/TokenService.exe'
                self.raiz = os.getcwd()
                self.success = True
                break
            except:
                retorno = self.scan_users_ad(self.usuario)
                if(retorno['qtd'] != 1):
                    self.message = 'Foram encontrados '+str(retorno['qtd'])+' usuários para essa maquina.'
                    self.success = False
                    break
                self.usuario = retorno['user']
                continue

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
            username = self.raiz.split('Users')[1].split(os.path.sep)[1]
            if(username != None):
                return username
            return os.getlogin()
        except (IndexError, FileNotFoundError):
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
                
