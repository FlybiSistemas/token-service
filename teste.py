import os
from src.webCertificado import *

dd = decrypt_data('db.txt')
print(len(dd['registros']))
# update_data('C:\\Users\Raynder\\arquivos_bytoken\\db.txt', 'perfil;login', 'asdf')
os.system('pause')