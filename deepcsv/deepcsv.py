import pyarrow
import pandas as pd
from typing import Union, Optional
from ast import literal_eval
from numpy import nan,array
from os import listdir,makedirs
from os.path import join,relpath,dirname,isfile,isdir
from warnings import filterwarnings
from typing import Union
filterwarnings("ignore")

def _validate_cols(cols, data):
    """
    Validates that columns is a non-empty list and all columns exist in the dataframe.
    """
    if not isinstance(cols, list):
        raise TypeError("cols must be a list. Example: ['age', 'name']")
    if len(cols) < 1:
        raise RuntimeError("cols must have at least 1 column.")
 
    missing = [col for col in cols if col not in data.columns]
    if missing:
        raise ValueError(f"These columns are not in the dataframe: {missing}")
 
 
def _validate_index(index, data,reset_indx=False):
    """
    Validates that index is a non-empty list and all indexes exist in the dataframe.
    """
    if reset_indx:
        data.reset_index(drop=True,inplace=True)

    if not isinstance(index, list):
        raise TypeError("index must be a list. Example: [0, 1, 2]")
    if len(index) < 1:
        raise RuntimeError("index must have at least 1 value.")
 
    missing = [i for i in index if i not in data.index]
    if missing:
        raise ValueError(f"These indexes are not in the dataframe: {missing}")
 

def read_any(file_path: str) -> pd.DataFrame:
    """
    Reads a file and returns it as a pandas DataFrame.
    Automatically detects the format from the file extension.
 
    Parameters
    ----------
    file_path : str
        Path to the file. Supported extensions:
        - .csv, .txt  → pd.read_csv()
        - .tsv        → pd.read_csv(sep='\\t')
        - .xls, .xlsx → pd.read_excel()
        - .json       → pd.read_json()
        - .parquet    → pd.read_parquet()
        - .pkl        → pd.read_pickle()
        - .feather    → pd.read_feather()
        - .db, .sqlite → pd.read_sql()
 
    Returns
    -------
    pd.DataFrame
 
    Raises
    ------
    ValueError
        If the file extension is not supported.
 
    Examples
    --------
    >>> df = read_any("data/users.csv")
    >>> df = read_any("reports/sales.xlsx")
    >>> df = read_any("warehouse/orders.parquet")
    """
    ext = file_path.split('.')[-1].lower()
    if ext in ['csv','txt']:
        return pd.read_csv(file_path)
    elif ext == 'tsv':
        return pd.read_csv(file_path, sep='\t')
    elif ext in ['xls', 'xlsx']:
        return pd.read_excel(file_path)
    elif ext == 'json':
        return pd.read_json(file_path)
    elif ext == 'parquet':
        return pd.read_parquet(file_path)
    elif ext == 'pkl':
        return pd.read_pickle(file_path)
    elif ext == 'feather':
        return pd.read_feather(file_path)
    elif ext in ['db',"sqlite"]:
        return pd.read_sql(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def process_file(data_input: Union[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Parses string representations of lists in DataFrame columns to actual NumPy arrays.

    (data_input: Union[str, pd.DataFrame]) -> pd.DataFrame

    This function reads a CSV file or takes a DataFrame, scans each column for string values
    starting with '[', and converts them to NumPy arrays for fast and lightweight processing.
    It also detects mixed data types in columns and attempts to convert them to numeric (float) for consistency.

    Parameters:
        data_input (Union[str, pd.DataFrame]): Path to the CSV file or the DataFrame itself.

    Returns:
        pd.DataFrame: The processed DataFrame with list strings converted to NumPy arrays, mixed types fixed with a warning message, and original columns renamed if arrays are extracted.

    Examples:
        ### Process a CSV file
        df = process_file('path/to/file.csv')

        ### Process an existing DataFrame
        df = process_file(my_dataframe)
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

                print(f"WARNING:\nThis Dataset Name ({data_input.split("\\")[-1]}) Found {len(data[ColName].apply(type).unique())} Mixed DataType in a column called ({ColName})\nPath : {data_input}")
                print(f"System : This column have These types: {data[ColName].apply(type).unique()}")
                print(f"System : Trying to fix the column as a Float to be have only one datatype...")

                data[ColName] = pd.to_numeric(data[ColName], errors='coerce')
                print("System : Done!")

        elif isinstance(First_Value , str) and First_Value.strip().startswith("["):
            
            data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : array(literal_eval(x)) if pd.notna(x) else nan)
            data.drop(ColName,inplace=True,axis=1)

    return data


def process_all_files(directory_path: str, output_dir="All CSV Files is Converted Here") -> None:
    """
    Recursively processes all CSV and XLSX files in a directory, converts array strings to NumPy arrays,
    and saves as Parquet files if array columns are present.

    (directory_path: str) -> None

    This function traverses the directory tree starting from directory_path, finds all .csv and .xlsx files,
    applies parse_lists to each for array conversion and type fixing, and saves the result as .parquet files
    in a subdirectory 'All CSV Files is Converted Here' only if the DataFrame contains new array columns.

    Parameters:
        directory_path (str): The root directory path to search for CSV/XLSX files.
        output_dir (str): The Folder name that will be save all files inside

    Returns:
        None: Files are saved to a directory 'All CSV Files is Converted Here'.

    Examples:
        # Process all CSV files in a directory
        process_all_files('/path/to/directory',"Converted Files")
    """

    base_output = join(directory_path, output_dir)
    all_folders = [directory_path]
    
    makedirs(base_output,exist_ok=True)
    
    while True:

        if all_folders:

            Curr_Path = all_folders.pop(0)

            for item_name in listdir(Curr_Path):
                
                Sub_Item_Path = join(Curr_Path,item_name)
                
                if isfile(Sub_Item_Path) and (Sub_Item_Path.endswith(".csv") or Sub_Item_Path.endswith(".xlsx")):
                    
                    print(f"{Sub_Item_Path} File Is Processing Now...")

                    df_converted = process_file(Sub_Item_Path)
                    df_converted.reset_index(drop=True,inplace=True)

                    rel_path = relpath(Sub_Item_Path, directory_path)
                    output = join(base_output,rel_path)
                    if "List" in df_converted.columns[-1]:
                        print(Sub_Item_Path)
                        makedirs(dirname(output),exist_ok=True)
                        df_converted.to_parquet(output.replace(".csv", ".parquet"))

                        print(f"Done!")
                        print("-"*50)

                elif isdir(Sub_Item_Path):

                    all_folders.append(Sub_Item_Path)

        else:
            break

def clean_values(data_input= Union[str, pd.DataFrame],
                 cols: Optional[list] = None,
                 ax_0: bool = False,
                 index: Optional[list] = None,
                 all_cols_except: Optional[list] = None):
    """
    Clean a dataframe by removing nulls, specific index, or specific columns.
 
    Parameters:
    -----------
    data_input      : file path or dataframe
    cols            : list of columns to apply on
    ax_0            : if True → drop rows with nulls in selected cols
                      if False → drop the cols themselves
    index           : list of row indexes to drop
    all_cols_except : apply on all columns except these
    """
 
    try:
        data = read_any(data_input)
    except Exception:
        data = data_input
  

    if cols is not None:
        _validate_cols(cols, data)
        target_cols = cols
 
    elif all_cols_except is not None:
        if not isinstance(all_cols_except, list):
            raise TypeError("all_cols_except must be a list.")
        target_cols = [col for col in data.columns if col not in all_cols_except]
 
    else:
        target_cols = list(data.columns)
 

    if index is not None:
        _validate_index(index, data)
        data.drop(index=index, inplace=True)

    else:
        if cols is not None or all_cols_except is not None:
            if ax_0:
                data.dropna(axis=0, subset=target_cols, inplace=True)
            else:
                cols_to_drop = [col for col in target_cols if data[col].isnull().all()]
                data.drop(columns=cols_to_drop, inplace=True)
        else:
            data.dropna(axis=1, inplace=True)
 
    return data