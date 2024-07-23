import datetime
from flask import Flask, request, render_template
import logging, traceback
from logging.handlers import RotatingFileHandler
import send_email
import pandas as pd
from process_data import DataProcessor
import plotly.io as pio

################################################################################################################
# APP VARIABLES
################################################################################################################
app = Flask(__name__)

app.program_last_restart = 0
app.function_password = '1q2w3e4r'
app.display_password = 'r4e3w2q1'
app.email_recipients = ['atanaskolevv01@gmail.com']
app.dev_recipients = ['atanaskolevv01@gmail.com']
app.dev_mode = False
app.data_folder = 'data/'
app.data_files = ['normal_data.csv', 'fault_data.csv']
app.data_to_check = 'data_to_check.csv'



################################################################################################################
# Logs:
################################################################################################################
def init_logger():
    logger = logging.getLogger('RBD')
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(level=logging.DEBUG)
    # add a log rotating handler (rotates when the file becomes 10MB, or about 100k lines):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler('logs/server.log', maxBytes=10000000, backupCount=10)
    handler.setLevel(level=logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
app.logger = init_logger()


# ERROR LOG:
def init_error_logger():
    logger = logging.getLogger('RBD ERRORS')
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(level=logging.DEBUG)
    # add a log rotating handler (rotates when the file becomes 10MB, or about 100k lines):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler('logs/server_error.log', maxBytes=10000000, backupCount=10)
    handler.setLevel(level=logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

app.error_logger = init_error_logger()

def log(func_name, message, error=False):
    if error == True:
        app.logger.error(f'{func_name}: {message}. Check server_error.log for details.')
        app.error_logger.error(f'{func_name}: {message}')
        app.error_logger.error('================')
        app.error_logger.error('ERROR TRACEBACK:')
        app.error_logger.error('================')
        app.error_logger.error(str(traceback.format_exc()))
        app.error_logger.error('================')
        subject = f"RBD: {func_name} encountered and error"
        if app.devmode==True:
            subject += ' - DEVMODE IS ON!'
            send_email(subject, message=str(traceback.format_exc()), recipients=app.dev_emails)
        else:
            send_email(subject, message=str(traceback.format_exc()), recipients=app.dev_emails)
    else:
        app.logger.info(f'{func_name}: {message}')

def LastNlines(fname, N, phrase=None):
    text=[]
    with open(fname) as file:
        for line in (file.readlines() [-N:]):
            if phrase is not None:
                if phrase in line:
                    text.append(line)
            else:
                text.append(line)
    return text


def get_logs(length=30, search_phrase=None, logfile=None):
    if logfile is not None:
        filename = f'logs/{logfile}'
    else:
        filename='logs/server.log'
    text=''
    lines=''
    if length==0:
        lines=LastNlines(filename, 30, phrase=search_phrase)
    else:
        lines=LastNlines(filename, length, phrase=search_phrase)
    for line in lines[::-1]: #reverse to make newest on top
        text+='</br>'+line
    return text


################################################################################################################
# MANUAL FUNCTIONS
################################################################################################################


def send_test_email():
    
    message = "This is just a test"
    try:
        send_email.send_email("RBD: Test email", message = message, recipient='atanaskolevv01@gmail.com')
        log('send_test_email', "Executed successfully!", error = False)
    except:
        log("send_test_email", "Send test email failed!", error = True)


################################################################################################################
# ENDPOINTS
################################################################################################################
@app.route('/', methods = ['GET', 'POST'])
def home():
    title = 'RBD: Home'
    return render_template('index.html', title = title, last_restart = app.program_last_restart)

@app.route('/logs', methods = ['GET', 'POST'])
def log_visualization():
    title = 'RBD: Logs visualization'
    if request.method == 'POST':
        boxes = request.form.getlist('mycheckbox')
        log_type = str(boxes[0])
        N_rows = int(boxes[1])
        specific_phrase = str(boxes[2])
        text = get_logs(length = N_rows, search_phrase=specific_phrase,
                        logfile=log_type)
    else:
        text = ''
    
    return render_template('logs.html', title=title, text = text)

@app.route('/configuration', methods = ['GET', 'POST'])
def functions():
    title = 'RBD: Конфигурация'
    output = ''
    if request.method == 'POST':
        boxes = request.form.getlist('mycheckbox')
        function = str(boxes[0])
        password = str(boxes[1])
        if password == app.function_password:
            if function == 'send test email':
                send_test_email()
            elif function == 'add email recipient':
                email = str(boxes[2])
                if email not in app.email_recipients:
                    app.email_recipients.append(email)
                    output = f'Готово! {email} е добавен към листа с получатели.'
        else:
            output = f'<b style="color:red">ОТХВЪРЛЕНО! ГРЕШНА ПАРОЛА!!</b>'
    return render_template('configuration.html', title=title, output=output)

@app.route('/cepstrum', methods = ['GET', 'POST'])
def cepstrum_visualization():

    title = 'RBD: Цепструм Визуализация'
    output = ''
    if request.method == 'GET':
        dfs = []
        status = 0
        
        try:
            for file in app.data_files:
                dfs.append(pd.read_csv(app.data_folder + file))
            
            df_normal = dfs[0]
            df_fault = dfs[1]
            de_normal = DataProcessor.cepstrum_visualizer(df_normal['X100_DE_time'], 'DE')
            de_fault = DataProcessor.cepstrum_visualizer(df_fault['X188_DE_time'], 'DE_fault')
            fe_normal = DataProcessor.cepstrum_visualizer(df_normal['X100_FE_time'], 'FE')
            fe_fault = DataProcessor.cepstrum_visualizer(df_fault['X188_FE_time'], 'FE_fault')

            graph_de = pio.to_html(de_normal, full_html=False)
            graph_de_fault = pio.to_html(de_fault, full_html=False)
            graph_fe = pio.to_html(fe_normal, full_html=False)
            graph_fe_fault = pio.to_html(fe_fault, full_html=False)

            output = str(status)
            return render_template('cepstrum.html', title=title, output=output, graph_de=graph_de, graph_de_fault=graph_de_fault, graph_fe=graph_fe, graph_fe_fault=graph_fe_fault)
        except Exception as e:
            app.logger.info(f'RBD: Error: {e}')
            return render_template('cepstrum.html', title=title, output=output)
    else:
        output = 'Грешка! Пробвай пак!'
        return render_template('cepstrum.html', title=title, output=output)


@app.route('/diagnostic', methods = ['GET', 'POST'])
def diagnostic():

    title = 'RBD: Диагностика на лагерите'
    if request.method == 'GET':
        df = pd.read_csv('data/data_to_check.csv')
        anom_df = DataProcessor.diagnostic_model(df)
        fig_anom = DataProcessor.visualize_anomalies(anom_df)
        if not anom_df.empty:
            output = f'<b style="color:red">ИМА АНОМАЛИЯ! ПОГЛЕДНИ CEPSTRUM, ЗА ДА СЕ УВЕРИШ!</b>'
        anom_graph = pio.to_html(fig_anom, full_html = 'False')
        return render_template('diagnostic.html', title=title, output=output, anom_graph=anom_graph)
    else:
        output = 'Грешка! Пробвай пак!'
        return render_template('diagnostic.html', title=title, output=output)


