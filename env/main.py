from typing import Optional
import typer
import os
from .utils.settings import config
import subprocess
from .pkgs import command as pkgs
from pathlib import Path
from .utils.KTemplate import Kconfigfile

app = typer.Typer(help='RT-Thread Command line tool')

app.add_typer(pkgs.app, name='pkgs')

@app.command()
def menuconfig(menuconfig_setting: Optional[bool] = typer.Option(False, '-s', help='Env config')):
    ''' Configure RT-Thread '''

    if not config.ENV_DIR.exists():
        print(f'{config.ENV_DIR} not exists')
        print('Please execute "env pkgs init" first')
        exit(0)
    menuconfig_setting_Kconfig = Path(str(config.ENV_DIR)) / 'settings.Kconfig'
    if menuconfig_setting:
        if not menuconfig_setting_Kconfig.exists():
            try:
                with open(menuconfig_setting_Kconfig, mode='x') as f:
                    f.write(Kconfigfile)
            except FileNotFoundError as e:
                print(config.ENV_DIR)
        os.chdir(str(config.ENV_DIR))
        subprocess.run('python -m menuconfig settings.Kconfig', shell=True)
    else:
        env = os.environ.copy()
        env['PKGS_DIR'] = str(config.PKGS_DIR)
        env['RTT_DIR'] = str(config.RTT_DIR)
        env['BSP_DIR'] = str(config.BSP_DIR)
        try:
            subprocess.run('python -m menuconfig', shell=True, env=env)
        except Exception as e:
            print(e)