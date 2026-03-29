import pyarrow
import pandas as pd
from .utils import read_any, clean_values, _validate_cols, _validate_index,_parse_operator,_validate_condition,_save_as
from typing import Union
from ast import literal_eval
from numpy import nan,array
from os import listdir,makedirs
from os.path import join,relpath,dirname,isfile,isdir
from warnings import filterwarnings
filterwarnings("ignore")

class DeepCSV:

    def __init__(self, data_input : Union[str, pd.DataFrame],
                directory_path : str = None, 
                save_file_extension: str = 'parquet', 
                output_dir="All CSV Files is Converted Here") -> None:
        
        """
        Initial Cleaner class for deepCSV
        ---------------------------------
        NOTE: Enter The require Parameter When Initlize.

        Parameters
        ----------
        data_input : string or pd.DataFrame
            path for csv or xlsx file for process used in process_file()
        
        directry_path : path for directry to process multiple file
            used in process_all_files()
            DEFAULT : NONE

        output_directry: directry to save processed File
            used in process_all_files(), require in process_all_files()
        
        save_file_extension: file extension
            supported: `csv`, `xlsx`, `tsv`, `txt`, `parquet`, `pkl`, `json` and more read README.md for more information  
            
            DEFAULT : parquet
          
        return
        ------
        None

        Example
        -------
        >>> from deepcsv import DeepCSVer
        >>> cleaner = DeepCSV('file.csv', 'folder', 'parquet', 'saved')
        >>> df = cleaner.process_file()
        >>> cleaner.process_all_files()

        """

        self.data_input = data_input
        self.directory_path = directory_path
        self.save_file_extension = save_file_extension
        self.output_dir = output_dir

        

    def process_file(self, data_another = None) -> pd.DataFrame:
        """
        Parses string representations of lists in DataFrame columns to actual NumPy arrays.
    
        Parameters
        ----------
        data_input : str or pd.DataFrame
            Path to the CSV/XLSX file or an existing DataFrame |  Already Given
    
        Returns
        -------
        pd.DataFrame
            Processed DataFrame with list strings converted to NumPy arrays,
            mixed types fixed, and original columns renamed if arrays are extracted.

        NOTE: Already Given Parameters when Initlized Class
    
       
        """
        
        data_input = data_another # To Check if input is from process_all_file()

        if data_another is None: # For Classes Class, ft. process_all_file()
            data_input = self.data_input # Its called By User
            

        save_file_extension = self.save_file_extension
        
        try:
            data = read_any(data_input)
        except Exception as e:
            print(f"Error: {e}")
            data = data_input

        for ColName in data.columns:
            
            First_Value = data[ColName].iloc[0]

            if len(data[ColName].apply(type).unique()) >= 2:


                sample = (data[data[ColName].apply(type) == str][ColName].head(2)).values

                if len(sample) > 0 and isinstance(sample[0],str) and sample[0][0].strip().isnumeric():

                    print(f"WARNING:\nThis Dataset Name ({data_input.split('\\')[-1]}) Found {len(data[ColName].apply(type).unique())} Mixed DataType in a column called ({ColName})\nPath : {data_input}")
                    print(f"System : This column have These types: {data[ColName].apply(type).unique()}")
                    print(f"System : Trying to fix the column as a Float to be have only one datatype...")
    
                    data[ColName] = pd.to_numeric(data[ColName], errors='coerce')
                    print("System : Done!")

            elif isinstance(First_Value , str) and First_Value.strip().startswith("["):
                
                data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : array(literal_eval(x)) if pd.notna(x) else nan)
                data.drop(ColName,inplace=True,axis=1)
                
        if save_file_extension.strip().lower() in ['csv','txt','tsv','xls','xlsx','json','parquet','pkl','feather','db','sqlite']:
            _save_as(data=data,ext=save_file_extension)
        return data


    def process_all_files(self) -> None:
        """
        Recursively processes all CSV and XLSX files in a directory,
        converts array strings to NumPy arrays, and saves as Parquet files.
    
        Parameters
        ----------
        directory_path : str
            Root directory path to search for CSV/XLSX files.
        
        output_dir : str, default 'All CSV Files is Converted Here'
            Folder name where converted files will be saved.

        NOTE: Already Given Parameters when Initlized Class
    
        Returns
        -------
        None

        Example
        -------
        >>> from deepcsv import DeepCSVer
        >>> cleaner = DeepCSV(directory_path, output_dir)
        >>> cleaner.process_all_file

        """

        

        base_output = join(self.directory_path, self.output_dir)
        all_folders = [self.directory_path]
        
        makedirs(base_output,exist_ok=True)
        
        while all_folders: # Itrate Though Folders and Sub Folders

            Curr_Path = all_folders.pop(0)

            for item_name in listdir(Curr_Path):
                    
                Sub_Item_Path = join(Curr_Path,item_name)
                    
                if isfile(Sub_Item_Path) and (Sub_Item_Path.split(".")[-1].strip().lower() in ['csv','txt','tsv','xls','xlsx','json','parquet','pkl','feather','db','sqlite']):
                        
                    print(f"{Sub_Item_Path} File Is Processing Now...")

                    df_converted = self.process_file(data_another=Sub_Item_Path)
                    df_converted.reset_index(drop=True,inplace=True)

                    rel_path = relpath(Sub_Item_Path, self.directory_path)
                    output = join(base_output,rel_path)
                    if "List" in df_converted.columns[-1]:
                        print(Sub_Item_Path)
                        makedirs(dirname(output),exist_ok=True)
                        _save_as(data=df_converted,
                                current_dir=output.replace(f".{Sub_Item_Path.split(".")[-1].strip().lower()}", f".{self.save_file_extension}"),
                                ext=self.save_file_extension)

                elif isdir(Sub_Item_Path):

                    all_folders.append(Sub_Item_Path)

            
