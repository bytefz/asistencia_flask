import pandas as pd
import numpy as np

from pathlib import Path
from pandas import DataFrame
from pandas.errors import DtypeWarning
import datetime as dt
from datetime import datetime
import random

class DataConverter:
    
    @staticmethod
    def _reader_excel(data: Path) -> DataFrame:
        """Function to read a excel file
        
        Keyword arguments:
        data -- from class Path
        Return: Return a DataFrame
        """
        
        return pd.read_excel(data)
    
    @staticmethod
    def _reader_csv(data: Path) -> DataFrame:
        """Function to read a .csv file
        
        Keyword arguments:
        data -- file path
        Return: Return a DataFrame
        """
        
        return pd.read_csv(data)
    
    @staticmethod
    def _reader_dat(data: Path) -> DataFrame:
        """
        Function to read data from .dat file.
        
        Keyword arguments:
        argument -- description
        Return: Return a dataframe.
        """ 
    
        return pd.read_csv(data, sep='\t', header=None)
    
    @staticmethod
    def _to_format_time(data: Path, columns: list[str], format_time: str) -> None | DataFrame:
        """Function to format datetime to a specific format
        
        Keyword arguments:
        data    -- File path(.csv, .xlsx, .dat)
        columns -- Name columns with datetime object
        Return: Return None if it's not a accepted format. 
                Else, return a DataFrame
        """
        
        format_file = str(data).split(".")[-1]
        
        match format_file:
            case "csv":
                data = DataConverter._reader_csv(data)
                
            case "xlsx":
                data = DataConverter._reader_excel(data)
                
            case "dat":
                data = DataConverter._reader_data(data)
                
            case _:
                raise DtypeWarning(f"It's not an accepted format.")

        i = 0
        while i < len(columns):
            data[columns[i]] = pd.to_datetime(data[columns[i]], format=format_time)
            i+=1

        return data

    @staticmethod
    def _to_excel_file(data: DataFrame, filename="data"):
        """Function to convert a DataFrame to Excel file
        
        Keyword arguments:
        data -- File Path
        Return: A Excel File
        """
        
        if isinstance(data, DataFrame):
            data.to_excel(f"{filename}.xlsx")
        else:
            raise DtypeWarning("It's not a DataFrame")
    
    @staticmethod

    def _change_values(_time:object):
        """
        Function to update
        """
        TIME_TOLERANCE = datetime(1900, 1, 1, 10,0,0)
        TIME_MIN = datetime(1900, 1, 1, 8,20,0)
        TIME_MAX = datetime(1900, 1, 1, 8,40,0)
        
        time_converted = datetime.strptime(_time, "%H:%M:%S %p")

        if TIME_MAX < time_converted:
            # Si está en el rango aceptado
            while time_converted < TIME_TOLERANCE:
                # Si no es la hora de salida o almuerzo
                if time_converted < TIME_TOLERANCE:
                    time_converted = datetime.strptime(_time, "%H:%M:%S %p")
                    time_rand = random.randint(0, 100)
                    to_early = dt.timedelta(minutes=time_rand)
                    time_converted = time_converted - to_early
                if TIME_MIN < time_converted < TIME_MAX:
                    time_converted = time_converted.strftime("%H:%M:%S %p")
                    return time_converted

        time_converted = time_converted.strftime("%H:%M:%S %p") 
        return time_converted

class DataManagment:
    
    dat_file = None
    
    @staticmethod
    def _delete_files(path: Path):
        """Function to delete files from a directory
        path -- Path to delete elements
        """
        try:
            files_in_filesdir = path.glob("*.*")
            
            # Delete elements
            list(map(lambda f: f.unlink(), files_in_filesdir))
            return True
        except BaseException as e:
            print(f"Error: {e}")
            return False
    
    @staticmethod
    def put_columns(data: DataFrame,_columns: list):
        """Function to add name columns to Dataframe
        
        Keyword arguments:
        data     -- DataFrame object
        _columns -- Name columns tuple
        Return: None
        """
        data.columns = _columns

    @staticmethod
    def delete_columns_by_index(data: DataFrame, _columns: list):
        """Function to delete columns on Dataframe
        
        Keyword arguments:
        data     -- DataFrame object
        _columns -- Name columns tuple
        Return: None
        """
        
        data.drop(data.columns[_columns], inplace=True, axis=1)
        return data
    
    @staticmethod
    def join_data():
        pass
    
    
    # def __call__(self, *args: Any, **kwds: Any) -> Any:
    #     pass



if __name__ == "__main__":
    DataConverter("Hola.py")