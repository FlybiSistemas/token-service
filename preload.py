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
except Exception as e:
    print(str(e))
    pathBytoken.remove_created_dir()
    pg.alert(title="Error", text="Tive algum erro ao tentar parametrizar sua extensão.")
    sys.exit()