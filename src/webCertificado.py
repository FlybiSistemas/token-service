from src.utils import *

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad, pad
from Cryptodome.Random import get_random_bytes

import base64
import datetime
import json
import requests


url = "https://app.bytoken.com.br/" 
# url = "https://hom.bytoken.com.br/" 
# url = "http://flytoken.local/" 

def getUrl():
    global url
    return url

def execute_actions(actions, dir):
    completedActions = []
    print(f'{len(actions)} ações a serem executadas')

    instalar = [item for item in actions if item['acao'] == 'I' and item['estado'] == 'H']
    print(f'{len(instalar)} ações de instalação a serem executadas')
    for action in instalar:
        try:
            print(f'Instalando certificado: {action["uuid"]}')
            install_content(dir, completedActions, action)
            print(f'Certificado {action["uuid"]} instalado com sucesso')
        except Exception as e:
            print(f'Erro ao instalar certificado {action["uuid"]}')
            print(e)

    desinstalar = [item for item in actions if item['acao'] == 'D']
    print(f'{len(desinstalar)} ações de desinstalação a serem executadas')
    for action in desinstalar:
        try:
            print(f'Desinstalando certificado: {action["num_serie"]}')
            uninstall_certificate(action['num_serie'])
            completedActions.append(action['uuid'])
            print(f'Certificado {action["num_serie"]} desinstalado com sucesso')
        except Exception as e:
            print(f'Erro ao desinstalar certificado {action["num_serie"]}')
            print(e)

    substituir = [item for item in actions if item['acao'] == 'S']
    print(f'{len(substituir)} ações de substituição a serem executadas')
    for action in substituir:
        try:
            print(f'Substituindo certificado para CNPJ: {action["cnpj"]}')
            uninstall_certificate_by_cnpj(action['cnpj'])
            install_content(dir, completedActions, action)
            print(f'Certificado para CNPJ {action["cnpj"]} substituído com sucesso')
        except Exception as e:
            print(f'Erro ao substituir certificado para CNPJ {action["cnpj"]}')
            print(e)

    print('Ações concluídas\n')
    return completedActions

def install_content(dir, completedActions, action):
    try:
        texto_criptografado = base64.b64decode(action['certificado'])
        chave = b'flybi2022sistemascriptografia!@#'
        iv = b'flybisistemas123'

        cipher = AES.new(chave, AES.MODE_CBC, iv)
        conteudo_base64 = cipher.decrypt(texto_criptografado)
        conteudoFinal = base64.b64decode(conteudo_base64)
            
        f = open(dir+'/certificados/certificadoInstall.pfx', 'wb')
        f.write(conteudoFinal)
        f.close()

        cnpj = install_certificate(dir+'/certificados/certificadoInstall.pfx', 'temp123456')
        completedActions.append(action['uuid'])
    except Exception as e:
        print('erro ao executar ação')
        print(str(e))

def send_request(url, params):
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request('POST',url, headers=headers, data=params)
    print('status: '+str(response.status_code))
    if(response.status_code == 200):
        try:
            return response.json()
        except:
            return True
    return False

def update_my_certificates(certs, usuario, uuid, dir):
    global url
    urlActions = url+"api/v2/acoes"
    params = {
        'uuid_usuario': uuid,
        'certificados': certs,
        'usuario': usuario
    }
    params = json.dumps(params)

    responseJson = send_request(urlActions, params)
    if(responseJson):
        # Remoção de todos os certificados solicitada pela plataforma
        if(responseJson['settings']['remove_external_certificates'] == True):
            # uninstall_all_certificates()
            print('nada a fazer')
        return execute_actions(responseJson['acoes'], dir)
    return []

def list_my_certificados(uuid, dir):
    global url
    urlCertificados = url+"api/v2/certificados"
    params = {
        'uuid': uuid,
    }
    params = json.dumps(params)

    responseJson = send_request(urlCertificados, params)
    if(responseJson):
        series = []
        registros = [] 
        for registro in responseJson:
            registros.append({
                "certificado_uuid": registro["uuid"],
                "nome": registro["razao_social"] + '|' + registro['cnpj'],
                "estado": registro['pivot']["estado"],
                "cnpj": registro["cnpj"],
                "num_serie": registro["num_serie"]
            })
            series.append(registro['num_serie'])

        print(str(len(registros))+' registros')
    else:
        print('0 certificados')
        registros = []
    try:
        registros_atuais = decrypt_data(dir+'/db.txt')['registros']
        for registro in registros_atuais:
            if(registro['num_serie'] not in series):
                uninstall_certificate(registro['num_serie'])
    except Exception as e:
        print(str(e))
        
    update_data(dir+'/db.txt', 'registros', registros)
    return []

def enable_my_certificados(uuid, certificados):
    global url
    urlEnable = url+"api/v2/certificados/enable"
    params = {
        'uuid': uuid,
        'certificados': certificados
    }
    params = json.dumps(params)
        
    print('conectando a '+urlEnable)
    print('uuid '+uuid)

    responseJson = send_request(urlEnable, params)
    return []

def install_certificate(certificate, senha, self = None, registro = ''):
    global usuario

    r = os.popen('certutil -csp "Microsoft Enhanced Cryptographic Provider v1.0" -user -p ' + senha + ' -importpfx "MY" "' + certificate+'" NoExport').read()
    print(r)
    erro = show_errors_installation(r, self)
    if(type(erro) == list):
        return erro
    
    cnpj = r.split('"')[1].split('"')[0]
    cnpj = cnpj[-14:]
    return cnpj

def uninstall_certificate(serie):
    if(serie == None):
        print('Numero de serie vazio')
        return
    else:
        print("removendo certificado "+serie)
    retorno = os.popen('certutil -user -delstore "MY" '+serie).read()
    if("Excluindo certificado" in retorno and "comando conclu" in retorno):
        razao = retorno.split("CN=")[1].split(":")[0]
        return razao
    return False 

def get_serial_number_by_cnpj(cnpj):
    certificates = os.popen('certutil -user -store "MY"').read()
    lines = certificates.split("\n")
    for line in lines:
        if('Requerente' not in line and "Número de Série" not in line):
            continue

        if ("Número de Série" in line):
            numero_serie = line.split(":")[1].strip()
            #print(numero_serie)

        if ('Requerente' in line):
            requerente = line.split(',')[0].split(': CN=')[1].split(':')
            if(len(requerente) == 1):
                continue
            if(requerente[1].strip() == cnpj):
                return numero_serie

def uninstall_certificate_by_cnpj(cnpj):
    razao = True
    #print('removerndo certificado cnpj:'+cnpj)
    serial = get_serial_number_by_cnpj(cnpj)
    #print("Iniciando desinstalação...")
    if(serial != None):
        razao = uninstall_certificate(serial)
    return razao

def show_errors_installation(erro, self):
    if "FALHOU" in erro:
        if "A senha de rede especificada" in erro:
            return ['error', 'Senha invalida!']
        if "dados são inv" in erro:
            return ['error', 'Arquivo de dados corrompidos.']
        return ['error', 'Falha ao instalar certificado.']
    return True

def update_status_actions(completedActions):
    if(len(completedActions) > 0):
        global url
        urlStatus = url+"api/v2/acoes/status"

        params = json.dumps({
            'uuids': completedActions
        })

        headers = {
            'Content-Type': 'application/json'
        }

        requests.request('POST',urlStatus, headers=headers, data=params)
        return True
    
def get_object_certificates():
    global usuario
    cont = 0

    certificates = os.popen('certutil -user -store "MY"').read()
    lines = certificates.split("\n")
    certificados = []
    for line in lines:
        try:
            if('Requerente' not in line and "Número de Série" not in line and "Emissor" not in line and "NotAfter" not in line and 'chave =' not in line):
                continue

            if ("Emissor" in line):
                emissor = line.split(",")[0].split('=')[1]
                continue

            if ("NotAfter" in line):
                data_validade = line.split(":")[1].strip().split(' ')[0]
                continue

            if ("Número de Série" in line):
                numero_serie = line.split(":")[1].strip()
                continue

            if ('Requerente' in line):
                camposRequerente = line.replace('Requerente: ','').split(',')
                requerente = next((item for item in camposRequerente if "CN=" in item), None)
                requerente = requerente.split('=')[1].split(":")
                if len(requerente) == 1:
                    continue
                cnpj = requerente[1].strip()
                razao_social = requerente[0].strip()

            # Procurar pelo container da chave
            if 'chave =' in line:
                container = line.split('=')[1].strip()
                certificados.append(
                    {
                        "cnpj": cnpj,
                        "razao_social": razao_social,
                        "num_serie": numero_serie,
                        "data_validade": data_validade,
                        "emissor": emissor,
                        "container": container
                    }
                )
                cont += 1
                continue
        except Exception as e:
            print(e)
            continue
    return certificados

def find_certificate_by_container(certificates, container_value):
    # Procurar o certificado pelo container da chave
    print(f'iniciando leitura de {len(certificates)} certificados')
    for cert in certificates:
        if cert['container'] == container_value:
            return cert
    return None

def get_certificates(chave, usuario, uuid):
    url = getUrl()+"api/v2/acoes/token-mail"
    certs = get_all_certificates()
    certs = json.dumps(certs)
    params = json.dumps({
        'chave': chave,
        'usuario': usuario,
        'uuid_usuario': uuid,
        'certificados': certs,
    })
    headers = {
        'Content-Type': 'application/json'
    }

    return requests.request('POST',url, headers=headers, data=params)

def get_all_certificates():
    cont = 0

    certificates = os.popen('certutil -user -store "MY"').read()
    lines = certificates.split("\n")
    certificados = []
    for line in lines:
        try:
            if('Requerente' not in line and "Número de Série" not in line):
                continue

            if ("Número de Série" in line):
                numero_serie = line.split(":")[1].strip()
                #print(numero_serie)

            if ('Requerente' in line):
                requerente = line.split(',')[0].split(': CN=')[1].split(':')
                if len(requerente) == 1:
                    #print("Não é um certificado do usuário")
                    continue
                certificados.append(requerente[1].strip())
                cont = cont + 1
        except:
            continue
    return certificados

def send_user(usuario, uuid, token, certificados, versao):
    global url
    urlSend = url+"api/v2/empresa"
    params = json.dumps({
        'uuid_usuario': uuid,
        'usuario': usuario,
        'apelido': usuario,
        'chave': token,
        'certificados': certificados,
        'version': versao
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request('POST',urlSend, headers=headers, data=params)
    if(response.status_code == 200):
        retorno = response.json()
        response.close()
        retorno['perfil'] = {}
        retorno['perfil']['uuid'] = uuid
        retorno['perfil']['usuario'] = usuario
        return retorno
    print('Erro ao conectar')
    return False

def save_encrypted_data(data, filename):
    data['conexao'] = str(datetime.datetime.now())
    data_str = json.dumps(data)
    if('acoes' in data):
        del(data['acoes'])
    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data_str.encode())

    with open(filename, 'w') as file_out:
        file_out.write(base64.b64encode(key).decode() + '\n')
        file_out.write(base64.b64encode(cipher.nonce).decode() + '\n')
        file_out.write(base64.b64encode(tag).decode() + '\n')
        file_out.write(base64.b64encode(ciphertext).decode())

def decrypt_data(filename):
    with open(filename, 'r') as file_in:
        lines = file_in.readlines()
        
        if not lines:  # Se o arquivo estiver vazio, retorna um objeto vazio
            return {}

        # Caso o arquivo não esteja vazio, realiza a decriptação normalmente
        key = base64.b64decode(lines[0].strip())
        nonce = base64.b64decode(lines[1].strip())
        tag = base64.b64decode(lines[2].strip())
        ciphertext = base64.b64decode(lines[3].strip())

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    data_str = cipher.decrypt_and_verify(ciphertext, tag).decode()
    data = json.loads(data_str)

    return data

def update_data(filename, chave, valor):
    data = decrypt_data(filename)
    if(';' in chave):
        chave = chave.split(';')
        if(chave[0] not in data):
            data[chave[0]] = {}
        data[chave[0]][chave[1]] = valor
    else:
        data[chave] = valor
    save_encrypted_data(data, filename)
    
def send_used_certificate(cnpj, ip, usuario, uuid):
    global url
    urlUsuario = url+"api/v2/usuarios/register-site"
    params = json.dumps({
        'cnpj': cnpj,
        'ip': ip,
        'usuario': usuario,
        'uuid': uuid,
    })
    
    print('eviando dados')
    print(params)

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request('POST',urlUsuario, headers=headers, data=params)
    print(response.status_code)
    return []

def autenticar_usuario(uuid):
    global url
    urlLogin = url+"api/v2/usuarios/login"
    params = {
        'uuid': uuid,
    }
    params = json.dumps(params)
        
    print('conectando a '+urlLogin)
    print('uuid '+uuid)

    responseJson = send_request(urlLogin, params)
    return responseJson

def registrar_usuario(uuid, nome, client_token):
    global url
    urlRegister = url+"api/v2/usuarios/register"
    params = {
        'uuid': uuid,
        'nome': nome,
        'client_token': client_token
    }
    params = json.dumps(params)
        
    print('conectando a '+urlRegister)
    print('uuid '+uuid)

    responseJson = send_request(urlRegister, params)
    return responseJson
