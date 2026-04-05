import pyarrow
import pandas as pd
from .utils import read_any, save_as 
from typing import Union
from ast import literal_eval
from numpy import nan,array
from os import listdir,makedirs
from os.path import join,relpath,dirname,isfile,isdir
from warnings import filterwarnings
filterwarnings("ignore")

def process_file(data_input: Union[str, pd.DataFrame] , file_format= None, to_list = False) -> pd.DataFrame:
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
    """
    
    try:
        data = read_any(data_input)
    except:
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
                print("-" * 50)



        elif len(data[data[ColName].apply(str).str.isnumeric()]) >= len(data[data[ColName].apply(str).str.isnumeric() == False]):

            print(f"WARNING:\nThis Dataset Name ({data_input.split('\\')[-1]}) Found numbers as {len(data[ColName].apply(type).unique())} in a column called ({ColName})\nPath : {data_input}")

            print(f"System : Trying to fix and converting the column as a Numerical Values...")
            data[ColName] = pd.to_numeric(data[ColName], errors='coerce')
            print("System : Done!")
            print("-" * 50)


        elif isinstance(First_Value , str) and First_Value.strip().startswith("["):
            if to_list:
                data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : list(literal_eval(x)) if pd.notna(x) else nan)
            else:
                data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : array(literal_eval(x)) if pd.notna(x) else nan)
            data.drop(ColName,inplace=True,axis=1)
            
    if file_format != None and file_format.strip().lower() in ['csv','txt','tsv','xls','xlsx','json','parquet','pkl','feather','db','sqlite']:
        save_as(data=data,ext=file_format)


    return data


def process_all_files(directory_path: str, output_dir="All CSV Files is Converted Here",file_format= "parquet",to_list = False) -> None:
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

                    df_converted = process_file(Sub_Item_Path)
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
