import pandas as pd
import numpy as np
import scipy.io


class CaseEduBearingData:

    def __init__(self):

        self.mat_file_loader = scipy.io.loadmat
        self.final_df = pd.DataFrame()



    def parse_all(self):

        pass