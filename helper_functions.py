import pandas as pd

class HelperFunctions:
    '''
    A class to keep utility functions as static methods.
    '''
    @staticmethod
    def process_mat_to_csv(mat_data):
        '''
        Method that checks for the useful columns in .mat files for the case.edu data.
        Args:
            mat_data, dict, dictionary of the MATLAB workspace.
        Returns:
            final_df, pd.DataFrame(), the useful information from the MATLAB workspace
        '''
        arr_df = {}
        final_df = pd.DataFrame()
        for key in mat_data:
            if key[:2] != '__':
                print(key)
                if key[-3:] != 'RPM':
                    tmp_arr = mat_data[key].reshape(-1)
                    arr_df.update({key : tmp_arr})
            else:
                print('Not a useful key')
        try:
            final_df = pd.DataFrame(arr_df)
            return final_df
        except ValueError:
            return pd.DataFrame()
