import pandas as pd
import numpy as np
import scipy.io
import yaml_parser
import os
from helper_functions import HelperFunctions

class CaseEduBearingData:
    '''
    Class to parse case.edu bearing data from .mat to .csv file and save it.
    https://engineering.case.edu/bearingdatacenter/download-data-file - link to download the data
    Methods:
    process_fault_data_to_csv() - processes the data where the bearing has a fault
    process_normal_data_to_csv() - process the normal bearing data, without a fault
    main() - the main function, where all methods are called 
    '''
    def __init__(self):
        '''
        The initializer method for the class. 
        Initializes two attributes, the mat_file_loader, which is used to read .mat files in python
        and the data_catalog consisting of paths and names for the files to be used as constants.
        Args:
            None
        Returns:
            None
        '''
        self.mat_file_loader = scipy.io.loadmat # the function to read the .mat file
        self.data_catalog = yaml_parser.YAMLParser.read_yaml_file('D:\Repositories\msc-thesis\constants\data_catalog.yaml') # load the .mat files paths and names

    def process_fault_data_to_csv(self, save = True, return_df = False):
        '''
        Method to process the fault data. Combining name variants, it looks for existing files and parses the useful data, to a .csv file.
        Args:
            save = True, bool, whether to save the result or not
            return = False, bool, whether to return the df or not
        Return:
            int, 1, 0 | dfs, list, list of pd.DataFrame
        '''
        fault_data_paths = self.data_catalog['case_edu_bearing_data']['fault_data'] # get the fault data paths
        processed_fault_data = self.data_catalog['case_edu_bearing_data']['processed_fault_data'] # get the target folder for the .csv
        base_path = fault_data_paths['base_path'] # get the base path for the fault data
        base_save_path = processed_fault_data['folder'] # get the target base path, where the .csv files will be saved
        if return_df: # check if return_df is True
            dfs = [] # initialize the dataframe list to be returned
        try:
            for folder in fault_data_paths['folders']: # iterate through the folder names 
                for diameter in fault_data_paths['diameters']: # iterate through the diameters
                    for hp in fault_data_paths['HPs']: # iterate through the horse powers
                        for rpm in fault_data_paths['RPMs']: # iterate through the rpms
                            for file_type in fault_data_paths['file_types']: # iterate through the file types
                                name = f"{diameter}_{hp}HP_{rpm}RPM_{file_type}" # get the name of the current combination
                                path = f"{base_path}{folder}/{name}{fault_data_paths['extension']}" # get the file extension
                                if os.path.exists(path): # check if the file exists
                                    mat_data = self.mat_file_loader(path) # load the .mat file
                                    df = HelperFunctions.process_mat_to_csv(mat_data) # process the .mat to pandas.DataFrame()
                                    if df.empty: # check if the pandas.DataFrame() is empty
                                        print(f"{name} is empty. Continuing...")
                                        continue
                                    else:
                                        df['fault_diameter'] = diameter # assign the diameter value to a column
                                        df['horse_power'] = hp # assign the horse power value to a column
                                        df['rounds_per_minute'] = rpm # assign the rpm value to a column
                                        if folder[4:7] == 'fan': # check if the file is reffering to a fan end
                                            df['fault_end'] = 'fan_end' # assign the fault end value to a column
                                            df['samples_per_second'] = 48000 # assign the samples per second value to a column
                                        else:
                                            if folder[:3] == '12k': # check the samples per second
                                                df['fault_end'] = 'drive_end' # assign the fault end value to a column
                                                df['samples_per_second'] = 12000 # assign the samples per second value to a column
                                            elif folder[:3] == '48k':
                                                df['fault_end'] = 'drive_end' # assign the fault end value to a column
                                                df['samples_per_second'] = 48000 # assign the samples per second value to a column
                                        if (save) and (return_df == False): # check whether to only save/return or safe and return the data
                                            df.to_csv(f"{base_save_path}{folder}/{name}{processed_fault_data['extension']}", index = False) # save the data
                                        elif (save == False) and (return_df):
                                            dfs.append(df) # append the pd.DataFrame() to a list 
                                        elif (save) and (return_df):
                                            df.to_csv(f"{base_save_path}{folder}/{name}{processed_fault_data['extension']}", index = False)
                                            dfs.append(df)
                                else:
                                    print(f"{path} does not exists. Continuing...")
            if return_df:
                return dfs # return the list of dataframes
            else:
                return 1 # if the method was a success, return 1
        except:
            return 0 # if the method failed, return 0

    def process_normal_data_to_csv(self, save = True, return_df = False):
        '''
        Method to process the normal data from .mat to .csv file.
        Args:
            save = True, bool, whether to save the result or not
            return = False, bool, whether to return the df or not
        Return:
            int, 1, 0 | dfs, list, list of pd.DataFrame
        '''
        normal_data_paths = self.data_catalog['case_edu_bearing_data']['normal_data']['raw_paths'] # get the raw normal data paths
        processed_normal_data = self.data_catalog['case_edu_bearing_data']['normal_data']['processed_paths'] # get the target paths for the parsed data
        rpms = self.data_catalog['case_edu_bearing_data']['normal_data']['rpms'] # get the possible rpms
        hps = self.data_catalog['case_edu_bearing_data']['normal_data']['hps'] # get the possible horse powers
        if return_df: # check if return_df is True
            dfs = [] # initialize the dataframe list to be returned

        try:
            for path, rpm, hp, save_path in zip(normal_data_paths, rpms, hps, processed_normal_data): # iterate through the paths, rounds_per_minute, horse powers and target paths
                mat_data = self.mat_file_loader(path) # load the .mat data
                df = HelperFunctions.process_mat_to_csv(mat_data) # parse the .mat data to a pandas.DataFrame()
                df['fault_diameter'] = 0 # assign the fault diameter to a column, 0 because this is non-fault data
                df['horse_power'] = hp # assign the horse power value to a column
                df['rounds_per_minute'] = rpm # assign the rounds per minute to a column
                df['fault_end'] = np.nan # NaN, because this is non-fault data
                df['samples_per_second'] = 12000 # assign the samples per second to a column
                if (save) and (return_df == False): # check whether to save/return or save and return the data
                    df.to_csv(save_path, index = False) # save the data
                elif (save) and (return_df):
                    df.to_csv(save_path, index = False)
                    dfs.append(df) # append dataframe to the list that will be returned
                elif (save == False) and (return_df):
                    dfs.append(df)
        
            if return_df:
                return dfs # return the list of all dataframes
            else:
                return 1 # if the method was a success, return 1
        except:
            return 0 # if the method failed, return 0
        
    def create_final_datasets(self):
        pass
        
    def main(self):
        '''
        The main function of the parser, using the default arguments of the other methods,
        this will parse and save the raw .mat files to .csv ones.
        Args:
            None
        Returns:
            None
        '''
        fault_data_status = self.process_fault_data_to_csv() # parse the fault data
        if fault_data_status:
            print("Fault data parsing done! Data saved!")
        else:
            print("Fault data could not be parsed! Data not saved!")
        normal_data_status = self.process_normal_data_to_csv() # parse the normal data
        if normal_data_status:
            print("Normal data parsing done! Data saved!")
        else:
            print("Normal data could not be parsed! Data not saved!")


if __name__ == '__main__': # if the function is called within this file, execute this
    case_edu_parser = CaseEduBearingData() # Initialize the class' object
    case_edu_parser.main() # call the main method of the class