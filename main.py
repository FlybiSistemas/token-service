from preload import *

uuidNow = get_user_uuid()
# uuidOld = get_uuid()

# uuidNow = 'QzQ2Rjc4NkQtQjAwNi1FMjExLTgzQzYtODQzNDk3MTc0NUVDQ2FzYQ=='
# uuidOld = 'QzQ2Rjc4NkQtQjAwNi1FMjExLTgzQzYtODQzNDk3MTc0NUVDQ2FzYQ=='
# parametro = {}
# parametro['funcao'] = 'CU'
# parametro['valor'] =' ByTokenSetup_868e3298'
# parametro['valor'] ='F8wSFudF85ey24DFsilhtgltOySwsnbrZBMWWHlDcGJo'

try:
    if(not parametro):
        print('Iniciando atualização padrão')
        completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, pathBytoken.directory)
        update_status_actions(completedActions)
        sys.exit()

    if('AC' in parametro['funcao']): #Atualizar certificados
        print('Iniciando chamda de atualização')
        completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, pathBytoken.directory)
        update_status_actions(completedActions)
        pg.confirm(text='Atualizado com sucesso!', title='Atenção', buttons=['OK'])
        sys.exit()

    if('IE' in parametro['funcao']): #Atualizar com chave recebida por email
        print('Iniciando atualização por email')
        response = get_certificates(parametro['valor'], pathBytoken.usuario, uuidNow)
        if(response.status_code == 200):
            try:
                if(response.json()[1] == 500):
                    pg.alert(response.json()[0], 'Erro', 'OK')
                    sys.exit()
            except:
                pass

            dadosArray = response.json()['acoes']
            completedActions = execute_actions(dadosArray, pathBytoken.directory)
            response.close()
            pg.confirm(text='Atualizado com sucesso!', title='Atenção', buttons=['OK'])
            sys.exit()
        else:
            try:
                pg.alert(response.json()[0], 'Erro', 'OK')
                response.close()
                sys.exit()
            except:
                pg.alert('Erro não identificado', 'Erro', 'OK')
                sys.exit()

    if('CU' in parametro['funcao']):
        print('Iniciando cadastro de usuário')
        try:
            retorno = send_user(pathBytoken.usuarioNome, uuidNow, parametro['valor'], pathBytoken.get_object_certificates(), versao)
            print('salvar dados no banco')
            save_encrypted_data(retorno, pathBytoken.directory+'/db.txt')
            print('Conexão '+pathBytoken.usuarioNome+' finalizada!')
        except Exception as e:
            pathBytoken.send_log(str(e))
            # pg.alert(text='Erro ao conectar usuário '+pathBytoken.usuarioNome+', favor reiniciar o programa.', title='Erro', button='OK')
        sys.exit()

    if('AE' in parametro['funcao']): #Atualizar extensão
        arquivo = os.path.join(pathBytoken.extensions, 'com.bytoken.bytoken.json')
        with open(arquivo, 'r') as f:
            dados = json.load(f)
        # os.popen('"C:\Program Files\Google\Chrome\Application\chrome.exe" --load-extension="'+pathBytoken.raiz+'/assistenteByToken" --new-window "https://bytoken.com.br"')
        # if(dados['allowed_origins'][0] == 'chrome-extension://alterar_valor/'):
            # pg.sleep(5)
            # extension = None
            # extension_id_arquivo = 'C:/Users/'+pathBytoken.usuario+'/Downloads/extension_id.txt'
            # with open(extension_id_arquivo, 'r') as f:
                # extension = f.read()
            # if(extension != None):
                # dados['allowed_origins'] = [f'chrome-extension://{extension}/']
                # with open(arquivo, 'w') as f:
                    # json.dump(dados, f, indent=4)
        extension = parametro['valor']
        dados['allowed_origins'] = [f'chrome-extension://{extension}/']
        with open(arquivo, 'w') as f:
            json.dump(dados, f, indent=4)
        pg.alert('Extensão configurada com sucesso!!')

    print('finalizando ...')
    
except Exception as e:
    print('erro: '+str(e))
    pathBytoken.send_log(str(e))