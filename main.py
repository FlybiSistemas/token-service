from preload import *

uuidNow = get_user_uuid()
uuidOld = get_uuid()

# uuidNow = 'QzQ2Rjc4NkQtQjAwNi1FMjExLTgzQzYtODQzNDk3MTc0NUVDQ2FzYQ=='
# uuidOld = 'QzQ2Rjc4NkQtQjAwNi1FMjExLTgzQzYtODQzNDk3MTc0NUVDQ2FzYQ=='
# parametro = {}
# parametro['funcao'] = 'CU'
# parametro['valor'] ='ByTokenSetup_1b083f8c'
# parametro['valor'] ='F8wSFudF85ey24DFsilhtgltOySwsnbrZBMWWHlDcGJo'

try:
    if(not parametro):
        print('Iniciando atualização padrão')
        completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, uuidOld, pathBytoken.directory)
        update_status_actions(completedActions)
        sys.exit()

    if('AC' in parametro['funcao']): #Atualizar certificados
        print('Iniciando chamda de atualização')
        completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, uuidOld, pathBytoken.directory)
        update_status_actions(completedActions)
        pg.confirm(text='Atualizado com sucesso!', title='Atenção', buttons=['OK'])
        sys.exit()

    if('IE' in parametro['funcao']): #Atualizar com chave recebida por email
        print('Iniciando atualização por email')
        response = get_certificates(parametro['valor'], pathBytoken.usuario, uuidNow, uuidOld)
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
            retorno = send_user(pathBytoken.usuarioNome, uuidNow, parametro['valor'], uuidOld, pathBytoken.get_object_certificates(), versao)
            print('salvar dados no banco')
            save_encrypted_data(retorno, pathBytoken.directory+'/db.txt')
            print('Conexão '+pathBytoken.usuarioNome+' finalizada!')
        except Exception as e:
            pathBytoken.send_log(str(e))
            # pg.alert(text='Erro ao conectar usuário '+pathBytoken.usuarioNome+', favor reiniciar o programa.', title='Erro', button='OK')
        sys.exit()

    print('finalizando ...')
    
except Exception as e:
    print('erro: '+str(e))
    pathBytoken.send_log(str(e))