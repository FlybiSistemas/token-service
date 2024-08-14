from src.utils import *

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad, pad
from Cryptodome.Random import get_random_bytes

import base64
import datetime
import json
import requests


# url = "https://app.bytoken.com.br/" 
url = "https://hom.bytoken.com.br/" 
# url = "http://flytoken.local/" 

def getUrl():
    global url
    return url

def execute_actions(actions, dir):
    completedActions = []
    for action in actions:
        if (action['acao'] == 'I'):
            try:
                chave = b'flybi2022sistemascriptografia!@#'
                iv = b'flybisistemas123'
                cipher = AES.new(chave, AES.MODE_CBC, iv)
                texto_criptografado = base64.b64decode(action['certificado'])

                chave = b'flybi2022sistemascriptografia!@#'
                iv = b'flybisistemas123'

                cipher2 = AES.new(chave, AES.MODE_CBC, iv)
                conteudo_base64_2 = cipher2.decrypt(texto_criptografado)
                
                conteudoBase64 = cipher.decrypt(texto_criptografado)
                base64pad = pad(conteudoBase64, 16)
                texto_descriptografado = base64.b64decode(base64pad)


                conteudoFinal = base64.b64decode(conteudo_base64_2)
                
                f = open(dir+'/certificados/certificadoInstall.pfx', 'wb')
                f.write(conteudoFinal)
                f.close()

                cnpj = install_certificate(dir+'/certificados/certificadoInstall.pfx', 'temp123456')
                completedActions.append(action['uuid'])
            except Exception as e:
                print('erro ao executar ação')
                print(str(e))
            
        if (action['acao'] == 'D'):
            try:
                uninstall_certificate(action['num_serie'])
                completedActions.append(action['uuid'])
            except:
                print('erro ao executar ação')

    return completedActions

def get_plataform_actions(url, params):
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request('POST',url, headers=headers, data=params)
    if(response.status_code == 200):
        return response.json()
    return False

def update_my_certificates(certs, usuario, uuid, dir):
    global url
    urlActions = url+"api/v2/acoes"
    params = json.dumps({
        'uuid_usuario': uuid,
        'certificados': certs,
        'usuario': usuario
    })

    responseJson = get_plataform_actions(urlActions, params)
    if(responseJson):
        # Remoção de todos os certificados solicitada pela plataforma
        if(responseJson['settings']['remove_external_certificates'] == True):
            # uninstall_all_certificates()
            print('nada a fazer')

    
        if('certificados_bytoken' in responseJson):
            update_data(dir+'/db.txt', 'certificados_bytoken', responseJson['certificados_bytoken'])
        return execute_actions(responseJson['acoes'], dir)
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
    retorno = os.popen('certutil -user -delstore "MY" '+serie).read()
    print(retorno)
    if("Excluindo certificado" in retorno and "comando conclu" in retorno):
        razao = retorno.split("CN=")[1].split(":")[0]
        return razao
    return False 

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
                # requerente = line.split(',')[0].split(': CN=')[1].split(':')
                if len(requerente) == 1:
                    #print("Não é um certificado do usuário")
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
        except Exception as e:
            print(e)
            continue
    return certificados

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

    retorno = requests.request('POST',url, headers=headers, data=params)
    retorno = requests.post(url, params)

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
    print('URL: '+urlSend)
    print('Dados: '+urlSend)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request('POST',urlSend, headers=headers, data=params)
    if(response.status_code == 200):
        print('Conectado com sucesso')
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
        key = base64.b64decode(file_in.readline().strip())
        nonce = base64.b64decode(file_in.readline().strip())
        tag = base64.b64decode(file_in.readline().strip())
        ciphertext = base64.b64decode(file_in.readline().strip())

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    data_str = cipher.decrypt_and_verify(ciphertext, tag).decode()
    data = json.loads(data_str)

    return data

def update_data(filename, chave, valor):
    data = decrypt_data(filename)
    data[chave] = valor
    save_encrypted_data(data, filename)