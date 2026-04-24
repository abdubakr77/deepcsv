import pandas as pd


def auto_fs(df: pd.DataFrame , target, model=None , mode="fast" , corr_threshold=0.3):

    if target is None:
        # Soon For Unsupervised
        pass

    else:
        if mode == "fast":

            column_to_keep=[]
            df_corr = df.corr()
            target_idx_incorr = df_corr.index.get_indexer([target])[0]

            if target in df.columns:
                df_target = df[target]
                df = df.drop(target,axis=1)

            for colname in df.columns:
                if abs(df_corr[colname].iloc[target_idx_incorr]) > abs(corr_threshold):
                    column_to_keep.append(colname)
                    
    result = pd.concat([df[column_to_keep],df_target],axis=1)
    return result

    