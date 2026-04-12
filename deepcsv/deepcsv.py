import pyarrow
import pandas as pd
from .utils import read_any, save_as
from deepcsv import utils
from typing import Union
from ast import literal_eval
from numpy import nan,array,ndarray
from os import listdir,makedirs
from os.path import join,relpath,dirname,isfile,isdir
from warnings import filterwarnings
filterwarnings("ignore")

def process_file(data_input: Union[str, pd.DataFrame], file_format: str = None, auto_fix: bool = False, to_list: bool = False, deep_check: bool = False, col_name:  Union[str, list] = "all") -> pd.DataFrame:
    """
    Parses string representations of lists in DataFrame columns to actual NumPy arrays.
 
    Parameters
    ----------
    data_input:  str or pd.DataFrame
                 Path to the CSV/XLSX file or an existing DataFrame.

    file_format: str
                 Saves a DataFrame to a file with the specified format.

    to_list:     False -> (Array) is better
                 True  -> it will convert to list 

    auto_fix:    False -> (Default)
                 True  -> It will detects and fixes columns
                 Apply auto_fix function with processing in one time

    deep_check:  bool, optional (default=False)
                 If True, recursively parses nested lists and dicts
                 stored as strings inside arrays.
                 May be slower on large datasets.
 
    Returns
    -------
    pd.DataFrame
        Processed DataFrame with list strings converted to NumPy arrays,
        mixed types fixed, and original columns renamed if arrays are extracted.
 
    Examples
    --------
    >>> df = process_file('path/to/file.csv')
    >>> df = process_file(my_dataframe)
    >>> df = process_file(my_dataframe , save_format="parquet")
    >>> df = process_file(my_dataframe , save_format="parquet", to_list = True)
    >>> df = process_file(my_dataframe , deep_check = True)
    """
    
    def _parse_value_(x, to_list=False):
        """Recursively parse a single value - handles str, list, dict, numpy array."""

        print("⚠️  Deep Check is enabled — recursively parsing nested lists/dicts. This may take longer on large datasets.")

        # String that looks like a list or dict
        if isinstance(x, str):
            stripped = x.strip()
            if stripped.startswith("[") or stripped.startswith("{"):
                try:
                    parsed = literal_eval(stripped)
                    return _parse_value_(parsed, to_list=to_list)  # recurse on result
                except (ValueError, SyntaxError):
                    return x  # return as-is if can't parse
            return x  # plain string, leave it
        
        # List or numpy array -> go deeper into each element
        elif isinstance(x, (list, ndarray)):
            parsed_items = [_parse_value_(item, to_list=to_list) for item in x]
            return parsed_items if to_list else array(parsed_items, dtype=object)
        
        # Dict -> go deeper into each value
        elif isinstance(x, dict):
            return {k: _parse_value_(v, to_list=to_list) for k, v in x.items()}
        
        # Numbers, None, etc. -> return as-is
        return x
            
    
    try:
        data = read_any(data_input)
    except:
        data = data_input

    if auto_fix:
        print("Now Trying to detects and fixes columns with mixed data types And process Numbers strings to float in a DataFrame.")
        data = utils.auto_fix(data_input=data,col_name=col_name)

    if col_name == data.columns or col_name.strip() in data.columns:
        
            ColName=col_name
            First_Value = data[ColName].iloc[0]


            if isinstance(First_Value , str) and (First_Value.strip().startswith("[") or First_Value.strip().startswith("{")):
                print(f"Found A column ({ColName}) Have lists string.\nNow Trying to parses string representations of lists in DataFrame columns to actual NumPy arrays.")
                if to_list:
                    if deep_check:
                        data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : _parse_value_(x,to_list=to_list) if pd.notna(x) else nan)
                    else:
                        data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : list(literal_eval(x)) if pd.notna(x) else nan)

                else:
                    
                    if deep_check:
                        data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : _parse_value_(x,to_list=to_list) if pd.notna(x) else nan)
                    else:
                        data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : array(literal_eval(x)) if pd.notna(x) else nan)

                data.drop(ColName,inplace=True,axis=1)
                print("Done!")
                print("-"*50)




    elif col_name == "all":
        for ColName in data.columns:
            
            First_Value = data[ColName].iloc[0]


            if isinstance(First_Value , str) and (First_Value.strip().startswith("[") or First_Value.strip().startswith("{")):
                print(f"Found A column ({ColName}) Have lists string.\nNow Trying to parses string representations of lists in DataFrame columns to actual NumPy arrays.")
                if to_list:
                    if deep_check:
                        data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : _parse_value_(x,to_list=to_list) if pd.notna(x) else nan)
                    else:
                        data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : list(literal_eval(x)) if pd.notna(x) else nan)

                else:
                    
                    if deep_check:
                        data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : _parse_value_(x,to_list=to_list) if pd.notna(x) else nan)
                    else:
                        data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : array(literal_eval(x)) if pd.notna(x) else nan)

                data.drop(ColName,inplace=True,axis=1)
                print("Done!")
                print("-"*50)

    else:
        raise NameError and ValueError("There is Input Column Name maybe not found in your Data Columns, Please Check the column name!")
            
    if file_format != None and file_format.strip().lower() in ['csv','txt','tsv','xls','xlsx','json','parquet','pkl','feather','db','sqlite']:
        save_as(data=data,ext=file_format)


    return data


def process_all_files(directory_path: str, output_dir="All CSV Files is Converted Here",file_format= "parquet",auto_fix = False,to_list = False, deep_check=False) -> None:
    """
    Recursively processes all CSV and XLSX files in a directory,
    converts array strings to NumPy arrays, and saves as Parquet files.
 
    Parameters
    ----------
    directory_path : str
        Root directory path to search for CSV/XLSX files.

    output_dir : str, default 'All CSV Files is Converted Here'
        Folder name where converted files will be saved.

    file_format: str
        Saves a DataFrame to a file with the specified format for every file.

    auto_fix:    False -> (Default)
        Apply auto_fix function with processing in one time

    to_list:     False -> (Array) is better
                 True  -> it will convert to list 

    deep_check:  bool, optional (default=False)
                 If True, recursively parses nested lists and dicts
                 stored as strings inside arrays.
                 May be slower on large datasets.

    Returns
    -------
    None
 
    Examples
    --------
    >>> process_all_files('/path/to/directory')
    >>> process_all_files('/path/to/directory', output_dir="Converted Files")
    >>> process_all_files('/path/to/directory', output_dir="Converted Files", file_format="tsv")
    """

    base_output = join(directory_path, output_dir)
    all_folders = [directory_path]
    
    makedirs(base_output,exist_ok=True)
    
    while True:

        if all_folders:

            Curr_Path = all_folders.pop(0)

            for item_name in listdir(Curr_Path):
                
                Sub_Item_Path = join(Curr_Path,item_name)
                
                if isfile(Sub_Item_Path) and (Sub_Item_Path.split(".")[-1].strip().lower() in ['csv','txt','tsv','xls','xlsx','json','parquet','pkl','feather','db','sqlite']):
                    
                    print(f"{Sub_Item_Path} File Is Processing Now...")

                    df_converted = process_file(Sub_Item_Path,auto_fix=auto_fix,deep_check=deep_check)
                    df_converted.reset_index(drop=True,inplace=True)

                    rel_path = relpath(Sub_Item_Path, directory_path)
                    output = join(base_output,rel_path)
                    if "List" in df_converted.columns[-1]:
                        print(Sub_Item_Path)
                        makedirs(dirname(output),exist_ok=True)
                        save_as(data=df_converted,
                                current_dir=output.replace(f".{Sub_Item_Path.split(".")[-1].strip().lower()}", f".{file_format}"),
                                ext=file_format,to_list=to_list)

                elif isdir(Sub_Item_Path):

                    all_folders.append(Sub_Item_Path)

        else:
            break
