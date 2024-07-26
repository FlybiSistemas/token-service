import pyautogui as pg
import sys
from src.directory import Directory
from src.unzip import *
from src.webCertificado import *
versao = '2.3.17'
parametro = False
if(len(sys.argv) > 1):
    print('Função: '+str(sys.argv[1]))
    parametro = {
        'funcao': sys.argv[1],
    }
    if(len(sys.argv) > 2):
        parametro['valor'] = sys.argv[2]
        print('Valor: '+str(sys.argv[2]))
pathBytoken = Directory()
if(not pathBytoken.success):
    pg.alert('Usuário Error', pathBytoken.message)
    sys.exit()
try:
    configure_registry("bytoken", pathBytoken.service)
    host_name = "com.bytoken.bytoken"
    json_file_path = "//AppData//Local//Google//Chrome//User Data//Default//Extensions//com.bytoken.bytoken.json"
    configure_native_messaging_host(host_name, json_file_path, pathBytoken)
    if not check_schedule("TokenService_"+pathBytoken.usuario):
        print('Iniciando agendador de tarefas...')
        retorno = create_schedule("TokenService_"+pathBytoken.usuario, 3, 20, pathBytoken.service)
        if type(retorno) == list:
            pg.alert(title=retorno[0], text=retorno[1])
            sys.exit()
    arquivo = os.path.join(pathBytoken.extensions, 'com.bytoken.bytoken.json')
    with open(arquivo, 'r') as f:
        dados = json.load(f)
    os.popen('"C:\Program Files\Google\Chrome\Application\chrome.exe" --load-extension="'+pathBytoken.raiz+'/assistenteByToken" --new-window "https://bytoken.com.br"')
    if(dados['allowed_origins'][0] == 'chrome-extension://alterar_valor/'):
        pg.sleep(5)
        extension = None
        extension_id_arquivo = 'C:/Users/'+pathBytoken.usuario+'/Downloads/extension_id.txt'
        with open(extension_id_arquivo, 'r') as f:
            extension = f.read()
        if(extension != None):
            dados['allowed_origins'] = [f'chrome-extension://{extension}/']
            with open(arquivo, 'w') as f:
                json.dump(dados, f, indent=4)
except Exception as e:
    print(str(e))
    pathBytoken.remove_created_dir()
    pg.alert(title="Error", text="Tive algum erro ao tentar parametrizar sua extensão.")
    sys.exit()