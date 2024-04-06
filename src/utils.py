import base64
import os
import psutil
import pythoncom
import subprocess
from unidecode import unidecode
import uuid
import wmi
import winreg

def check_processes(aplicacao, x = 0):
    cont = 0
    for process in psutil.process_iter():
        try:
            process_info = process.as_dict(attrs=['pid', 'name', 'exe'])
            #print(aplicacao.lower()+" em "+process_info['name'].lower())
            if aplicacao.lower() in  process_info['name'].lower():
                cont = cont + 1
                if(cont == x):
                    return x
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    if(cont == (x-1)):
        return cont
    return False

def check_permission():
    r = os.popen("net session").read()
    if(r == ''):
        return False
    return True

def get_uuid():
    try:
        return wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
    except:
        return hex(uuid.getnode()).replace('0x', '').upper()

def get_user_uuid():
    cod_uuid = ''
    try:
        # Tentando pegar o UUID da Maquina
        cod_uuid = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID
    except:
        # Tentando pegar o MAC da maquina
        cod_uuid = hex(uuid.getnode()).replace('0x', '').upper()
    usuario = os.getlogin()
    uuidHash = cod_uuid+usuario
    uuidHash = base64.b64encode(uuidHash.encode('utf-8'))
    return uuidHash.decode()

def create_schedule(tarefa, tipo, tempo, exe):
    tarefa = unidecode(tarefa).lower()
    if not os.path.isfile(exe):
        return ['error', 'Erro ao localizar serviço.']
    if(tipo == 1):
        a = os.popen('schtasks /create /sc hourly /mo '+str(tempo)+' /tn "'+tarefa+'" /tr "\''+exe+'\'"').read()
        # schtasks /create /sc hourly /mo 1 /tn "FlyToken" /tr "C:\Users\gabri\Documents\GitHub\FlyToken\dist\FlyToken.exe"
    elif(tipo == 2):
        a = os.popen('schtasks /create /sc daily /tn "'+tarefa+'" /tr "\''+exe+'\'" /st '+tempo).read()
    elif(tipo == 3):
        comando = 'schtasks /create /sc minute /mo '+str(tempo)+' /tn "'+tarefa+'" /tr "\''+exe+'\'"'
        a = os.popen(comando).read()
    elif(tipo == 4):
        comando = 'schtasks /create /sc onlogon /tn "'+tarefa+'" /tr "\''+exe+'\'"'
        a = os.popen(comando).read()
    if("XITO" in a):
        return True
    return ['error', a]

def check_schedule(tarefa):
    tarefa = unidecode(tarefa).lower()
    r = os.popen("schtasks /query").read()
    if(tarefa in r):
        return True
    return False

# função que assim como check_schedule, verifica se o executavel agente.exe esta rodando
def check_agente():
    r = os.popen("tasklist").read()
    if("agente.exe" in r):
        return True
    return False

def iniciar_agente():
    if(check_agente()):
        return True
    # o agente estará na mesma pasta que o executavel do FlyToken, então basta pegar a pasta que este arquivo esta instalado e executar o agente
    dirAtual = os.getcwd()
    executable_path = dirAtual+"\\agente.exe"
    try:
        subprocess.Popen([executable_path])
        return True
    except:
        return False

# Criação da chave HKEY_CLASSES_ROOT\bytoken no regedit
def configure_registry(initKey, exe):
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, initKey) as init_key:
            print('chave ja existe')
            pass  # A chave já existe

    except FileNotFoundError:
        # A chave não existe, então vamos criá-la
        try:
            print('criando chave')
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, initKey) as init_key:
                winreg.SetValueEx(init_key, "URL Protocol", 0, winreg.REG_SZ, "")

                with winreg.CreateKey(init_key, "shell\\open\\command") as command_key:
                    winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, exe)

        except Exception as e:
            print(f"Erro ao configurar o registro: {e}")
