import os
import shutil
from datetime import datetime

# Pasta de dados e de backup
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backup')

# Cria a pasta de backup se não existir
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_csv_files():
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.csv'):
            src = os.path.join(DATA_DIR, filename)
            dst = os.path.join(BACKUP_DIR, f'{now}_{filename}')
            shutil.copy2(src, dst)
            print(f'Backup criado: {dst}')

if __name__ == '__main__':
    backup_csv_files()
    print('Backup de arquivos CSV concluído.')
