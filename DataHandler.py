from datetime import datetime, timedelta
import numpy as np
import pandas as pd


class DataHandler:
    def __init__(self, sample_rate=10, no_of_channels=4, samples_per_frame=5, data_size_unit=10,
                 no_of_slow_data=9, auto_save_hours=12, **kwargs):
        self.sample_rate = sample_rate  # 10  # samples per second
        self.no_of_channels = no_of_channels  # 4 nidaq channels
        self.samples_per_frame = samples_per_frame  # data per sample

        self.data_size_unit = data_size_unit  # 10

        self.no_of_slow_data = no_of_slow_data  # 9
        # Temp_air1, temp_water, flowrate_mass, density, flow_temp, flowrate_vol, vfd_freq, motor running state, valve state
        # valve control by checking statue of slow_data[8], careful!!
        self.slow_data = np.zeros(self.no_of_slow_data)

        self.data = np.zeros((self.data_size_unit, self.no_of_channels + self.no_of_slow_data))
        self.data_time = np.zeros(self.data_size_unit, dtype='float')
        # self.current_data_size = self.data_size_unit

        # data_info --> [ptr, data_size_unit, current_data_size]
        self.data_info = np.array([0, self.data_size_unit, self.data_size_unit])

        self.auto_save_hours = auto_save_hours
        self.auto_save_time = datetime.now() + timedelta(hours=self.auto_save_hours)

        self.checkSave = False

    def data_refresh(self):
        # clear memory
        self.data_info = np.array([0, self.data_size_unit, self.data_size_unit])
        # self.slow_data = np.zeros(self.no_of_slow_data)

        self.data = np.zeros((self.data_size_unit, self.no_of_channels + self.no_of_slow_data))
        self.data_time = np.zeros(self.data_size_unit, dtype='float')
        return self.data, self.data_time, self.data_info

    def set_data(self, ave_data):
        self.data[self.data_info[0], :self.no_of_channels] = ave_data
        self.data[self.data_info[0], self.no_of_channels:] = self.slow_data
        self.data_time[self.data_info[0]] = datetime.now().timestamp()

        self.data_info[0] += 1
        self.check_save()
        if self.data_info[0] >= self.data_info[2]:
            self.data, self.data_time, self.data_info = self.expand_data()

        # print("setdata")
        # print(self.slow_data)
        # print(self.data)

    def save_data(self):
        date_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        save = np.concatenate((self.data_time.reshape(-1, 1), self.data), axis=1)
        data_df = pd.DataFrame(save,
                               columns=['Time', 'Temperature in', 'Temperature out', 'Pressure in (kPa)',
                                        'Pressure out (kPa)',
                                        'Temperature air', 'Temperature water',
                                        'Mass flow rate (kg/s)', 'Density (kg/m3)', 'Flow temperature',
                                        'Volume flow rate (L/s)',
                                        'VFD frequency (Hz)', 'FC pump running state', 'Auto valve state'])

        # Temp_air1, temp_water, flowrate_mass, density, flow_temp, flowrate_vol, vfd_freq, motor running state, valve state

        # data_df.Time = data_df.Time.apply(lambda x: datetime.fromtimestamp(x))
        data_df['Time'] = data_df['Time'].apply(datetime.fromtimestamp)
        # print(data_df)
        compression_opts = dict(method='zip', archive_name=date_str + '.csv')
        data_df.to_csv(date_str + '.zip', index=False, compression=compression_opts)

    def set_check_save(self, status):
        self.checkSave = status

    def check_save(self):
        time_now = datetime.now()
        if self.checkSave & (self.auto_save_time <= time_now):
            # save data and refresh memory per auto_save_hours
            self.save_data()  # autosave
            self.data, self.data_time, self.data_info = self.data_refresh()
            self.auto_save_time = time_now + timedelta(hours=self.auto_save_hours)
            # print(self.auto_save_time)

    def expand_data(self):
        # expand memory
        temp_data = self.data
        self.data = np.zeros((self.data_info[2] + self.data_info[1], self.no_of_channels + self.no_of_slow_data))
        self.data[:self.data_info[2], :] = temp_data

        temp_time = self.data_time
        self.data_time = np.zeros(self.data_info[2] + self.data_info[1], dtype='float')
        self.data_time[:self.data_info[2]] = temp_time
        self.data_info[2] += self.data_info[1]

        return self.data, self.data_time, self.data_info