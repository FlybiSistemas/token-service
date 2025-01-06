from preload import *

try:
    db_data = decrypt_data(pathBytoken.directory+'/db.txt')
    if('login' in db_data['perfil']):
        uuidNow = db_data['perfil']['login']
        print('UUID recuperado do banco, variavel login')
    else:
        uuidNow = db_data['perfil']['uuid']
        print('UUID recuperado do banco, variavel uuid')
except:
    print('Nenhum UUID salvo no banco local.')
# uuidOld = get_uuid()

if os.path.exists('uuid.txt'):
    with open('uuid.txt', 'r') as file:
        uuidNow = file.read().strip()
# parametro = {}
# parametro['funcao'] = 'AC'
# parametro['valor'] =' ByTokenSetup_868e3298'
# parametro['valor'] ='3ZOwnBAtsMAIG19BA56CAk2xWWp2pxb2QyFhP1aHkXlA'

try:
    if(not parametro):
        print('Iniciando atualização padrão')
        object_cerficates = get_object_certificates()
        completedActions = update_my_certificates(object_cerficates, pathBytoken.usuario, uuidNow, pathBytoken.directory)
        update_status_actions(completedActions)
        sys.exit()

    if('AC' in parametro['funcao']): #Atualizar certificados
        print('Iniciando chamada de atualização')
        completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, pathBytoken.directory)
        update_status_actions(completedActions)
        pg.confirm(text='Atualizado com sucesso!', title='Atenção', buttons=['OK'])
        sys.exit()
        
    if('EC' in parametro['funcao']): #escolher certificados
        registros = decrypt_data(pathBytoken.directory+'/db.txt')['registros']
        registros_filtrados = []
        enabled = []
        for registro in registros:
            if registro["estado"] == 'D':
                registros_filtrados.append(registro)
            else:
                enabled.append(registro["certificado_uuid"])
        print(f'{len(registros_filtrados)} registros devem estar habilitados na plataforma')
        enable_my_certificados(uuidNow, enabled)
        completedActions = update_my_certificates(registros_filtrados, pathBytoken.usuario, uuidNow, pathBytoken.directory)
        update_status_actions(completedActions)
        pg.confirm(text='Atualizado com sucesso!', title='Atenção', buttons=['OK'])
        for registro in registros_filtrados:
            uninstall_certificate(registro['num_serie'])
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

    if('SC' in parametro['funcao']): #Enviar certificado usado
        send_used_certificate(parametro['valor'], parametro['aux'], pathBytoken.usuario, uuidNow)
        sys.exit()

    if('LC' in parametro['funcao']): #Listar certificados permitidos
        print('Pegando lista de certificados')
        list_my_certificados(uuidNow, pathBytoken.directory)

    # Funções extras
    if('DA' in parametro['funcao']): #Desinstalar app
        print("lendo arquivo db...")
        try:
            registros = decrypt_data(pathBytoken.directory+'/db.txt')['registros']
            print(len(registros)+' certificados para desistalar')
            for registro in registros:
                uninstall_certificate(registro['num_serie'])
        except Exception as e:
            print(e)
        print('removendo pasta')
        pathBytoken.destroy()
        
        
        sys.exit()

    # Funções Login
    if('LG' in parametro['funcao']):
        print('Iniciando processo de autenticação')
        r = autenticar_usuario(parametro['valor'])
        if(r):
            pg.alert('Usuário autenticado com sucesso!')
            update_data(pathBytoken.directory+'/db.txt', 'perfil;login', parametro['valor'])
            update_data(pathBytoken.directory+'/db.txt', 'perfil;usuario', r['usuario']['nome'])
            try:
                registros = decrypt_data(pathBytoken.directory+'/db.txt')['registros']
                print(len(registros)+' certificados para desistalar')
                for registro in registros:
                    uninstall_certificate(registro['num_serie'])
            except:
                print('Erro ao procurar certificados para desinstalar.')
            completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, pathBytoken.directory)
            update_status_actions(completedActions)
        else:
            pg.alert('Usuário ou senha incorretos.')
            
    if('RG' in parametro['funcao']):
        print('Iniciando processo de registro')
        r = registrar_usuario(parametro['valor'], parametro['aux'], parametro['ext'])
        if(r):
            pg.alert('Usuário registrado com sucesso!')
            update_data(pathBytoken.directory+'/db.txt', 'perfil;login', parametro['valor'])
            update_data(pathBytoken.directory+'/db.txt', 'perfil;usuario', r['usuario']['nome'])
            try:
                registros = decrypt_data(pathBytoken.directory+'/db.txt')['registros']
                print(len(registros)+' certificados para desistalar')
                for registro in registros:
                    uninstall_certificate(registro['num_serie'])
            except:
                print('Erro ao procurar certificados para desinstalar.')
            completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, pathBytoken.directory)
            update_status_actions(completedActions)
        else:
            pg.alert('Usuário ou senha incorretos.')

    print('finalizando ...')
    
except Exception as e:
    print('erro: '+str(e))
    pathBytoken.send_log(str(e))