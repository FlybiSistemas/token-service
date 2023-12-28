from preload import *

uuidNow = get_user_uuid()
uuidOld = get_uuid()

try:
    if(not parametro):
        completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, uuidOld, pathBytoken.directory)
        update_status_actions(completedActions)
        sys.exit()

    elif(parametro['funcao'] == 'AC'): #Atualizar certificados
        completedActions = update_my_certificates(get_object_certificates(), pathBytoken.usuario, uuidNow, uuidOld, pathBytoken.directory)

    elif(parametro['funcao'] == 'IE'): #Atualizar com chave recebida por email
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
        else:
            try:
                pg.alert(response.json()[0], 'Erro', 'OK')
                response.close()
                sys.exit()
            except:
                pg.alert('Erro não identificado', 'Erro', 'OK')
                sys.exit()
        
    elif(parametro['funcao'] == 'CU'):
        try:
            retorno = send_user(pathBytoken.usuario, uuidNow, parametro['valor'], uuidOld, pathBytoken.get_object_certificates())
            save_encrypted_data(retorno, pathBytoken.directory+'/db.txt')
            pg.confirm(text='Usuário '+pathBytoken.usuario+' conectado com sucesso!', title='Atenção', buttons=['OK'])
            sys.exit()
        except:
            pg.alert(text='Erro ao conectar usuário '+pathBytoken.usuario+', favor reiniciar o programa.', title='Erro', button='OK')
            sys.exit()
    update_status_actions(completedActions)
    pg.confirm(text='Atualizado com sucesso!', title='Atenção', buttons=['OK'])
    sys.exit()
except Exception as e:
    pathBytoken.send_log(str(e))