import pyautogui as pg
import sys
from src.directory import Directory
from src.unzip import *
from src.webCertificado import *
versao = '2.2.16'
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
configure_registry("bytoken", pathBytoken.service)
if not check_schedule("TokenService_"+pathBytoken.usuario):
    print('Iniciando agendador de tarefas...')
    retorno = create_schedule("TokenService_"+pathBytoken.usuario, 3, 20, pathBytoken.service)
    if type(retorno) == list:
        pg.alert(title=retorno[0], text=retorno[1])
        sys.exit()
