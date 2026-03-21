import os
import pandas as pd
from ast import literal_eval

def ConvertListStrToList(data):
    Data_Col = data.columns
    for ColName in Data_Col:
        if type(data[ColName][0]) == str and data[ColName][0].startswith("["):
            data[f"{ColName.capitalize()}List"] = data[ColName].apply(lambda x : literal_eval(x) if pd.notna(x) else x )
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
                    print(Sub_Item_Path)
                    df = pd.read_csv(Sub_Item_Path)
                    df_converted = ConvertListStrToList(df)

                    rel_path = os.path.relpath(Sub_Item_Path, WorkDirectoryPath)
                    output = os.path.join(base_output,rel_path)
                    os.makedirs(os.path.dirname(output),exist_ok=True)

                    df_converted.to_csv(output)


                elif os.path.isdir(Sub_Item_Path):

                    all_folders.append(Sub_Item_Path)

        else:
            break
