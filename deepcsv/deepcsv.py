import pyarrow
import os
import warnings
import numpy as np
import pandas as pd
from ast import literal_eval
warnings.filterwarnings("ignore")

def ConvertListStrToList(File_Path):

    data = pd.read_csv(File_Path)
    for ColName in data.columns:
        
        First_Value = data[ColName].iloc[0]

        if len(data[ColName].apply(type).unique()) >= 2:


            sample = (data[data[ColName].apply(type) == str][ColName].head(2)).values

            if len(sample) > 0 and isinstance(sample[0],str) and sample[0][0].strip().isnumeric():

                print(f"WARNING:\nThis Dataset Name ({File_Path.split("\\")[-1]}) Found {len(data[ColName].apply(type).unique())} Mixed DataType  in a column called ({ColName})\nPath : {File_Path}")
                print(f"System : This column have These types: {data[ColName].apply(type).unique()}")
                print(f"System : Trying to fix the column as a Float to be have only one datatype...")

                data[ColName] = pd.to_numeric(data[ColName], errors='coerce')
                print("System : Done!")

        elif isinstance(First_Value , str) and First_Value.strip().startswith("["):
            
            data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : literal_eval(x) if pd.notna(x) else np.nan)
            data.drop(ColName,inplace=True,axis=1)

    return data


def ReadAllCSVData(WorkDirectoryPath):

    base_output = os.path.join(WorkDirectoryPath, "All CSV Data is Converted Here")
    all_folders = [WorkDirectoryPath]
    
    os.makedirs(base_output,exist_ok=True)
    
    while True:

        if all_folders:

            Curr_Path = all_folders.pop(0)

            for item_name in os.listdir(Curr_Path):
                
                Sub_Item_Path = os.path.join(Curr_Path,item_name)
                
                if os.path.isfile(Sub_Item_Path) and (Sub_Item_Path.endswith(".csv") or Sub_Item_Path.endswith(".xlsx")):
                    
                        

                    df_converted = ConvertListStrToList(Sub_Item_Path)
                    df_converted.reset_index(drop=True,inplace=True)

                    rel_path = os.path.relpath(Sub_Item_Path, WorkDirectoryPath)
                    output = os.path.join(base_output,rel_path)
                    if "List" in df_converted.columns[-1]:
                        print(Sub_Item_Path)
                        os.makedirs(os.path.dirname(output),exist_ok=True)
                        df_converted.to_parquet(output.replace(".csv", ".parquet"))

                    print("-"*50)

                elif os.path.isdir(Sub_Item_Path):

                    all_folders.append(Sub_Item_Path)

        else:
            break
