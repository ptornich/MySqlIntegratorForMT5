__logFileName__ = "log.txt"
__settingsFileName__ = "settings.dat"
__hiddenPaswword__ = '**********'

def installDependencies():
    import sys
    import subprocess
    import pkg_resources

    required = {'PySimpleGUI', 'MetaTrader5', 'mysql-connector-python'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        python = sys.executable
        subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

    log("Dependencies checked", "info")

class Settings:
    MySqlHost = ''
    Username = ''
    Password = ''
    Database = ''
    VerboseLogging = False

    def save(self):
        import pickle
        with open(__settingsFileName__, 'wb+') as f:
            pickle.dump(self, f)

    @staticmethod
    def load():
        import pickle
        import os
        ret = Settings()
        if os.path.exists(__settingsFileName__):
            with open(__settingsFileName__, 'rb') as f:
                ret = pickle.load(f)
        return ret

    def displayPassword(self):
        if self.Password != '':
            return __hiddenPaswword__
        else:
            return ''

class IntegrationTask: 
    import MetaTrader5 as _metatrader
    import mysql.connector as _mysql

    def __init__(self):
        self._running = True
        self._metatrader.initialize()
      
    def terminate(self): 
        self._running = False
      
    def getDbConnection(self):
        return self._mysql.connect(
            host=settings.MySqlHost,
            user=settings.Username,
            password=settings.Password,
            database=settings.Database)

    def sendAccountInfo(self):
        accountInfo = self._metatrader.account_info()
        
        db = self.getDbConnection()
        dbCursor = db.cursor()
        dbCursor.execute(f"SELECT login FROM AccountInfo WHERE login = {accountInfo.login} LIMIT 1")
        dbResults = dbCursor.fetchall()
        
        if len(dbResults) > 0:
            # TODO
            stmt = f"UPDATE AccountInfo SET leverage='{accountInfo.leverage}' WHERE login='{accountInfo.login}'"
            dbCursor.execute(stmt)
        else:
            # TODO
            stmt = "INSERT INTO AccountInfo (login, trade_mode, leverage, limit_orders, margin_so_mode, trade_allowed, trade_expert, margin_mode, currency_digits, fifo_close, balance, credit, profit, equity, margin, margin_free, margin_level, margin_so_call, margin_so_so, margin_initial, margin_maintenance, assets, liabilities, commission_blocked, name, server, currency, company)"
            stmt += f"VALUES ('{accountInfo.login}', '{accountInfo.trade_mode}', '{accountInfo.leverage}', '{accountInfo.limit_orders}', '{accountInfo.margin_so_mode}', '{accountInfo.trade_allowed}', '{accountInfo.trade_expert}', '{accountInfo.margin_mode}', '{accountInfo.currency_digits}', '{accountInfo.fifo_close}', '{accountInfo.balance}', '{accountInfo.credit}', '{accountInfo.profit}', '{accountInfo.equity}', '{accountInfo.margin}', '{accountInfo.margin_free}', '{accountInfo.margin_level}', '{accountInfo.margin_so_call}', '{accountInfo.margin_so_so}', '{accountInfo.margin_initial}', '{accountInfo.margin_maintenance}', '{accountInfo.assets}', '{accountInfo.liabilities}', '{accountInfo.commission_blocked}', '{accountInfo.name}', '{accountInfo.server}', '{accountInfo.currency}', '{accountInfo.company}');"
            dbCursor.execute(stmt)
            
        db.commit()

    def sendPositions(self):
        print(self._metatrader.account_info())

    def sendHistory(self):
        print(self._metatrader.account_info())

    def run(self):
        import time
        log("Integration started", "info")

        settings.MySqlHost = window['Host'].get()
        settings.Username = window['User'].get()
        settings.Database = window['Database'].get()
        settings.VerboseLogging = window['Verbose'].get()

        if window['Password'].get() != __hiddenPaswword__:
            settings.Password = window['Password'].get()

        settings.save()

        window['Stop'].update(disabled=False)
        window['Start'].update(disabled=True)
        window['Host'].update(disabled=True, text_color='dark grey')
        window['User'].update(disabled=True, text_color='dark grey')
        window['Password'].update(settings.displayPassword(), disabled=True, text_color='dark grey')
        window['Database'].update(disabled=True, text_color='dark grey')
        window['Verbose'].update(disabled=True)

        delay = 0
        while self._running:
            if delay == 0:
                window['Stop'].update(disabled=True)
                window['Output'].update('Running')
                self.sendAccountInfo()
                #self.sendHistory()
                #self.sendPositions()
                delay = 60
            else:
                window['Stop'].update(disabled=False)
                delay -= 1
                window['Output'].update(f'Waiting... {delay}')
                time.sleep(1)

        window['Output'].update('')
        window['Stop'].update(disabled=True)
        window['Start'].update(disabled=False)
        window['Host'].update(disabled=False, text_color='white')
        window['User'].update(disabled=False, text_color='white')
        window['Password'].update(disabled=False, text_color='white')
        window['Database'].update(disabled=False, text_color='white')
        window['Verbose'].update(disabled=False)

        log("Integration stopped", "info")
        
def findOrCreateLogFilePath():
    import os
    if not os.path.exists(__logFileName__):
        with open(__logFileName__, 'a+') as f:
            f.write();
    return __logFileName__

def showLogFile():
    import subprocess as sp
    logFilePath = findOrCreateLogFilePath()
    sp.Popen(["notepad.exe", logFilePath])

def log(txt, severity):
    if severity.lower() == 'debug' and not settings.VerboseLogging :
        return
    from datetime import datetime
    logFilePath = findOrCreateLogFilePath()
    with open(logFilePath, 'a') as f:
        txt = f'[{datetime.now()}] {severity.upper()} {txt}\n'
        f.write(txt);

def createWindow():
    import PySimpleGUI as sg
    # Define the theme
    sg.theme('dark grey 9')

    # Define the window's contents
    layout = [
        [sg.Text('MySql Host', size=(11,1)), sg.Input(settings.MySqlHost, key='Host'), ],
        [sg.Text('Username', size=(11,1)), sg.Input(settings.Username, key='User')],
        [sg.Text('Password', size=(11,1)), sg.Input(settings.displayPassword(), key='Password')],
        [sg.Text('Database', size=(11,1)), sg.Input(settings.Database, key='Database')],
        [sg.Checkbox('Verbose Logs', settings.VerboseLogging,  key='Verbose')],
        [sg.Text(key='Output', size=(50,1), text_color='yellow')],
        [sg.Button('Start', size=(16,1)), sg.Button('Stop', size=(16,1), disabled=True), sg.Button('Logs', size=(16,1))]
    ]

    # Create the window
    return sg.Window('MySql Integrator for MT5', layout)

def main():
    import PySimpleGUI as sg
    import threading

    log("Main process started", "debug")
    
    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()

        try:
            if event == sg.WINDOW_CLOSED:
                break
    
            if event == 'Start':
                integrationTask = IntegrationTask()
                thread = threading.Thread(target=integrationTask.run, daemon=True)
                thread.start()

            if event == 'Stop':
                integrationTask.terminate()

            if event == 'Logs':
                showLogFile()
        except Exception as ex:
            log(ex, 'error')
            window['Output'].update(f'Exception: {ex}', text_color='red')

    log("Main process ended", "debug")


if __name__ == '__main__':
    log("Application started", "info")
    
    settings = Settings.load()
    window = createWindow()

    try:
        installDependencies()
        main()
    except Exception as ex:
        log(ex, 'error')
    finally:
        window.close()

    log("Application ended", "info")