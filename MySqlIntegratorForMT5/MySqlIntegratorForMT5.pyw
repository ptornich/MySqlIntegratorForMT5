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
    Delay = ''
    VerboseLogging = False

    def setValuesFromWindow(self):
        self.MySqlHost = window['Host'].get()
        self.Username = window['User'].get()
        self.Database = window['Database'].get()
        self.Delay = window['Delay'].get()
        self.VerboseLogging = window['Verbose'].get()

        if window['Password'].get() != __hiddenPaswword__:
            self.Password = window['Password'].get()

        return self

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
        self._running = False
        if not self._metatrader.initialize():
            raise Exception("initialize() failed, last error: " + str(self._metatrader.last_error()))
        self._running = True
        
        accountInfo = self.getAccountInfo()
        self._login = accountInfo.login
        
    def terminate(self): 
        self._running = False
      
    def getDbConnection(self):
        return self._mysql.connect(
            host=settings.MySqlHost,
            user=settings.Username,
            password=settings.Password,
            database=settings.Database)

    def getAccountInfo(self):
        accountInfo = self._metatrader.account_info()
        if accountInfo == None and len(self._metatrader.last_error()) > 0:
            raise Exception("account_info() failed, last error: " + str(self._metatrader.last_error()))
        return accountInfo

    def getPositions(self):
        positions = self._metatrader.positions_get()
        if positions == None and len(self._metatrader.last_error()) > 0:
            raise Exception("history_deals_get() failed, last error: " + str(self._metatrader.last_error()))
        return positions

    def getHistory(self):
        from datetime import datetime
        deals = self._metatrader.history_deals_get(datetime(2000,1,1), datetime.now())
        if deals == None and len(self._metatrader.last_error()) > 0:
            raise Exception("history_deals_get() failed, last error: " + str(self._metatrader.last_error()))
        return deals

    def sendAccountInfo(self, forceUpdate = False):
        log("sendAccountInfo started", "verbose")
        positions = self.getPositions()
        
        if len(positions) == 0 and not forceUpdate:
            return

        accountInfo = self.getAccountInfo()

        db = self.getDbConnection()
        dbCursor = db.cursor()
        dbCursor.execute(f"SELECT login FROM AccountInfo WHERE login = {accountInfo.login} LIMIT 1")
        dbResults = dbCursor.fetchall()
        
        if len(dbResults) > 0:
            stmt = f"""
                UPDATE AccountInfo SET
                    trade_mode='{accountInfo.trade_mode}',
                    leverage='{accountInfo.leverage}',
                    limit_orders='{accountInfo.limit_orders}',
                    margin_so_mode='{accountInfo.margin_so_mode}',
                    trade_allowed='{accountInfo.trade_allowed}',
                    trade_expert='{accountInfo.trade_expert}',
                    margin_mode='{accountInfo.margin_mode}',
                    currency_digits='{accountInfo.currency_digits}',
                    fifo_close='{accountInfo.fifo_close}',
                    balance='{accountInfo.balance}',
                    credit='{accountInfo.credit}',
                    profit='{accountInfo.profit}',
                    equity='{accountInfo.equity}',
                    margin='{accountInfo.margin}',
                    margin_free='{accountInfo.margin_free}',
                    margin_level='{accountInfo.margin_level}',
                    margin_so_call='{accountInfo.margin_so_call}',
                    margin_so_so='{accountInfo.margin_so_so}',
                    margin_initial='{accountInfo.margin_initial}',
                    margin_maintenance='{accountInfo.margin_maintenance}',
                    assets='{accountInfo.assets}',
                    liabilities='{accountInfo.liabilities}',
                    commission_blocked='{accountInfo.commission_blocked}',
                    name='{accountInfo.name}',
                    server='{accountInfo.server}',
                    currency='{accountInfo.currency}',
                    company='{accountInfo.company}'
                WHERE login='{accountInfo.login}'"""
            dbCursor.execute(stmt)
        else:
            stmt = "INSERT INTO AccountInfo (`login`, `trade_mode`, `leverage`, `limit_orders`, `margin_so_mode`, `trade_allowed`, `trade_expert`, `margin_mode`, `currency_digits`, `fifo_close`, `balance`, `credit`, `profit`, `equity`, `margin`, `margin_free`, `margin_level`, `margin_so_call`, `margin_so_so`, `margin_initial`, `margin_maintenance`, `assets`, `liabilities`, `commission_blocked`, `name`, `server`, `currency`, `company`)"
            stmt += f" VALUES ('{accountInfo.login}', '{accountInfo.trade_mode}', '{accountInfo.leverage}', '{accountInfo.limit_orders}', '{accountInfo.margin_so_mode}', '{accountInfo.trade_allowed}', '{accountInfo.trade_expert}', '{accountInfo.margin_mode}', '{accountInfo.currency_digits}', '{accountInfo.fifo_close}', '{accountInfo.balance}', '{accountInfo.credit}', '{accountInfo.profit}', '{accountInfo.equity}', '{accountInfo.margin}', '{accountInfo.margin_free}', '{accountInfo.margin_level}', '{accountInfo.margin_so_call}', '{accountInfo.margin_so_so}', '{accountInfo.margin_initial}', '{accountInfo.margin_maintenance}', '{accountInfo.assets}', '{accountInfo.liabilities}', '{accountInfo.commission_blocked}', '{accountInfo.name}', '{accountInfo.server}', '{accountInfo.currency}', '{accountInfo.company}')"
            dbCursor.execute(stmt)
            
        db.commit()
        log("sendAccountInfo ended", "verbose")

    def sendPositions(self):
        log("sendPositions started", "verbose")
        
        db = self.getDbConnection()
        dbCursor = db.cursor()

        positions = self.getPositions()
        
        for position in positions:
            stmt = f"""
                UPDATE Position SET
                    `time`='{position.time}',
                    `time_msc`='{position.time_msc}',
                    `time_update`='{position.time_update}',
                    `time_update_msc`='{position.time_update_msc}',
                    `type`='{position.type}',
                    `magic`='{position.magic}',
                    `identifier`='{position.identifier}',
                    `reason`='{position.reason}',
                    `volume`='{position.volume}',
                    `price_open`='{position.price_open}',
                    `sl`='{position.sl}',
                    `tp`='{position.tp}',
                    `price_current`='{position.price_current}',
                    `swap`='{position.swap}',
                    `profit`='{position.profit}',
                    `symbol`='{position.symbol}',
                    `comment`='{position.comment}',
                    `external_id`='{position.external_id}'
                WHERE `login`='{self._login}' AND `ticket`='{position.ticket}'"""
            
            dbCursor.execute(stmt)
            if dbCursor.rowcount == 0:
                stmt = "INSERT INTO Position (`login`, `ticket`, `time`, `time_msc`, `time_update`, `time_update_msc`, `type`, `magic`, `identifier`, `reason`, `volume`, `price_open`, `sl`, `tp`, `price_current`, `swap`, `profit`, `symbol`, `comment`, `external_id`)"
                stmt += f" VALUES ('{self._login}', '{position.ticket}', '{position.time}', '{position.time_msc}', '{position.time_update}', '{position.time_update_msc}', '{position.type}', '{position.magic}', '{position.identifier}', '{position.reason}', '{position.volume}', '{position.price_open}', '{position.sl}', '{position.tp}', '{position.price_current}', '{position.swap}', '{position.profit}', '{position.symbol}', '{position.comment}', '{position.external_id}')"
                dbCursor.execute(stmt)
                
            db.commit()

        log("sendPositions ended", "verbose")

    def sendHistory(self):
        log("sendHistory started", "verbose")
        deals = self.getHistory()

        db = self.getDbConnection()
        dbCursor = db.cursor()
        dbCursor.execute(f"SELECT MAX(ticket) FROM History WHERE login = {self._login} LIMIT 1")
        dbResults = dbCursor.fetchall()
        
        lastTicket = 0

        if len(dbResults) > 0 and dbResults[0][0] != None:
            lastTicket = dbResults[0][0]
            
        if deals[-1].ticket > lastTicket:
            for deal in deals:
                if deal.ticket > lastTicket:
                    stmt = "INSERT INTO History (`login`, `ticket`, `order`, `time`, `time_msc`, `type`, `entry`, `magic`, `position_id`, `reason`, `volume`, `price`, `commission`, `swap`, `profit`, `fee`, `symbol`, `comment`, `external_id`)"
                    stmt += f" VALUES ('{self._login}', '{deal.ticket}', '{deal.order}', '{deal.time}', '{deal.time_msc}', '{deal.type}', '{deal.entry}', '{deal.magic}', '{deal.position_id}', '{deal.reason}', '{deal.volume}', '{deal.price}', '{deal.commission}', '{deal.swap}', '{deal.profit}', '{deal.fee}', '{deal.symbol}', '{deal.comment}', '{deal.external_id}')"
                    dbCursor.execute(stmt)
                    db.commit()

        log("sendHistory ended", "verbose")

    def run(self):
        import time
        log("Integration started", "verbose")

        try:
            enableFieldsStarted()

            try:
                delay = int(settings.Delay)
            except ValueError:
                delay = 0
            
            forceAccountInfoUpdate = True
            while self._running:
                if delay == 0:
                    window['Stop'].update(disabled=True)
                    window['Output'].update('Running')
                    self.sendAccountInfo(forceAccountInfoUpdate)
                    self.sendPositions()
                    self.sendHistory()
                    forceAccountInfoUpdate = False
                    delay = 60
                else:
                    window['Stop'].update(disabled=False)
                    delay -= 1
                    window['Output'].update(f'Waiting... {delay}')
                    time.sleep(1)

            enableFieldsStopped()
        except Exception as ex:
            log(ex, 'error')
            enableFieldsStopped(ex)

        log("Integration stopped", "verbose")

def enableFieldsStarted():
    window['Stop'].update(disabled=False)
    window['Start'].update(disabled=True)
    window['Host'].update(disabled=True, text_color='dark grey')
    window['User'].update(disabled=True, text_color='dark grey')
    window['Password'].update(settings.displayPassword(), disabled=True, text_color='dark grey')
    window['Database'].update(disabled=True, text_color='dark grey')
    window['Delay'].update(disabled=True, text_color='dark grey')
    window['Verbose'].update(disabled=True)

def enableFieldsStopped(exception = None):
    if exception != None:
        window['Output'].update(f'Exception: {exception}', text_color='red')
    else:
        window['Output'].update('')

    window['Stop'].update(disabled=True)
    window['Start'].update(disabled=False)
    window['Host'].update(disabled=False, text_color='white')
    window['User'].update(disabled=False, text_color='white')
    window['Password'].update(disabled=False, text_color='white')
    window['Database'].update(disabled=False, text_color='white')
    window['Delay'].update(disabled=False, text_color='white')
    window['Verbose'].update(disabled=False)

def findOrCreateLogFilePath():
    import os
    if not os.path.exists(__logFileName__):
        open(__logFileName__, 'a+').close()
    return __logFileName__

def showLogFile():
    import subprocess as sp
    logFilePath = findOrCreateLogFilePath()
    sp.Popen(["notepad.exe", logFilePath])

def log(txt, severity):
    if severity.lower() == 'verbose' and not settings.VerboseLogging :
        return
    from datetime import datetime
    logFilePath = findOrCreateLogFilePath()
    with open(logFilePath, 'a') as f:
        txt = f'[{datetime.now()}] {severity.upper()}\t{txt}\n'
        f.write(txt);

def createWindow():
    import PySimpleGUI as sg
    # Define the theme
    sg.theme('dark grey 9')

    # Define the window's contents
    layout = [
        [sg.Text('MySql Host:', size=(15,1)), sg.Input(settings.MySqlHost, key='Host'), ],
        [sg.Text('Username:', size=(15,1)), sg.Input(settings.Username, key='User')],
        [sg.Text('Password:', size=(15,1)), sg.Input(settings.displayPassword(), key='Password')],
        [sg.Text('Database:', size=(15,1)), sg.Input(settings.Database, key='Database')],
        [sg.Text('Delay (in seconds):', size=(15,1)), sg.Input(settings.Delay, key='Delay')],
        [sg.Checkbox('Verbose Logs', settings.VerboseLogging,  key='Verbose')],
        [sg.Text(key='Output', size=(50,1), text_color='yellow')],
        [sg.Button('Start', size=(17,1)), sg.Button('Stop', size=(17,1), disabled=True), sg.Button('Logs', size=(17,1))]
    ]

    # Create the window
    return sg.Window('MySql Integrator for MT5', layout)

def main():
    import PySimpleGUI as sg
    import threading

    log("Main process started", "info")
    
    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()

        try:
            if event == sg.WINDOW_CLOSED:
                settings.setValuesFromWindow().save()
                break
    
            if event == 'Start':
                settings.setValuesFromWindow().save()
                integrationTask = IntegrationTask()
                thread = threading.Thread(target=integrationTask.run, daemon=True)
                thread.start()

            if event == 'Stop':
                integrationTask.terminate()

            if event == 'Logs':
                showLogFile()
        except Exception as ex:
            log(ex, 'error')
            enableFieldsStopped(ex)

    log("Main process ended", "info")


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