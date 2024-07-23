import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pickle

class DataProcessor:

    @staticmethod
    def cepstrum_calculation(signal):
        spectrum = np.fft.fft(signal)
        log_spectrum = np.log(np.abs(spectrum) + np.finfo(float).eps)
        cepstrum = np.fft.ifft(log_spectrum).real

        freqs = np.fft.fftfreq(len(log_spectrum), 1/12000)
        quefrencies = np.fft.fftfreq(len(cepstrum), 1/12000)

        return cepstrum, log_spectrum, freqs, quefrencies
    
    @staticmethod
    def cepstrum_visualizer(signal, name):
        signal_cepstrum, signal_log_spectrum, signal_freq, signal_quefreq = DataProcessor.cepstrum_calculation(signal)
        lifter = np.ones_like(signal_cepstrum)
        lifter[:30] = 0
        fig = make_subplots(rows=3, cols=1, subplot_titles=(f'Сигнал - {name}', 'Log спектър', 'Cepstrum'))

        # Add the original time series plot
        fig.add_trace(go.Scatter(x=signal.index, y=signal, mode='lines', name='Сигнал'), row=1, col=1)

        fig.add_trace(go.Scatter(x=signal_freq[:len(signal_freq)//2], y=signal_log_spectrum[:len(signal_log_spectrum)//2], mode='lines', name='Log спектър'), row = 2, col = 1)

        # Add the FFT magnitude plot
        fig.add_trace(go.Scatter(x=signal_quefreq[:len(signal_quefreq)//2], y=signal_cepstrum[:len(signal_cepstrum)//2]*lifter[:len(lifter)//2] , mode='lines', name='Амплитуда на cepstrum'), row=3, col=1)

        # Update layout
        fig.update_xaxes(title_text='Време', row=1, col=1)
        fig.update_yaxes(title_text='Стойност', row=1, col=1)


        fig.update_xaxes(title_text='Честота (Hz)', row=2, col=1)
        fig.update_yaxes(title_text='Амплитуда', row=2, col=1)

        fig.update_xaxes(title_text='Q - Честота (s)', row=3, col=1)
        fig.update_yaxes(title_text='Амплитуда', row=3, col=1)
        fig.update_layout(height=800, width=1500, title_text='Сигнал, Log спектър и Cepstrum')

        return fig
    
    @staticmethod
    def diagnostic_model(df):

        def load_models():
            with open(r'D:\Repositories\msc-thesis\arima_model_de.pkl', 'rb') as pkl_file:
                de_model = pickle.load(pkl_file)
            with open(r'D:\Repositories\msc-thesis\arima_model_fe.pkl', 'rb') as pkl_file:
                fe_model = pickle.load(pkl_file)

            return de_model, fe_model
        
        def anomaly_detection(df, de_model, fe_model):
    
            de_signal = df['DE'].reset_index(drop = True)
            fe_signal = df['FE'].reset_index(drop = True)

            de_pred = de_model.predict(start=de_signal.index[0], end=de_signal.index[-1], dynamic = False)
            fe_pred = fe_model.predict(start=fe_signal.index[0], end=fe_signal.index[-1], dynamic = False)

            mse_de = np.mean((de_signal.values.reshape(-1, 1) - de_pred.values.reshape(-1, 1)) ** 2, axis = 1)
            mse_fe = np.mean((fe_signal.values.reshape(-1, 1) - fe_pred.values.reshape(-1, 1)) ** 2, axis = 1)
            avg_mse = (mse_de + mse_fe) / 2
            best_thr = 0.013882980550933777
            df['anomaly'] = np.where(avg_mse >= best_thr, 1, 0)

            return df

        de_model, fe_model = load_models()
        df = anomaly_detection(df, de_model, fe_model)
        anom_df = df[df['anomaly'] == 1]

        return anom_df
    
    @staticmethod
    def visualize_anomalies(df_anom):

        de = df_anom['DE']
        fe = df_anom['FE']

        fig = make_subplots(rows=2, cols=1, subplot_titles=('Сигнал - DE', 'Сигнал - FE'))

        # Add the original time series plot
        fig.add_trace(go.Scatter(x=de.index, y=de, mode='lines', name='Сигнал - DE'), row=1, col=1)

        fig.add_trace(go.Scatter(x=fe.index, y=fe, mode='lines', name='Сигнал - FE'), row=2, col=1)
        

        # Update layout
        fig.update_xaxes(title_text='Време', row=1, col=1)
        fig.update_yaxes(title_text='Стойност', row=1, col=1)


        fig.update_xaxes(title_text='Време', row=2, col=1)
        fig.update_yaxes(title_text='Стойност', row=2, col=1)

        fig.update_layout(height=800, width=1500, title_text='Сигнали - DE и FE')

        return fig

