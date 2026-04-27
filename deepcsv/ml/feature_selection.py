import pandas as pd
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier,GradientBoostingRegressor,GradientBoostingClassifier
from sklearn.model_selection import cross_val_score,train_test_split


def auto_fs(df: pd.DataFrame , target, model=None , mode="balanced" , corr_threshold=0.3):

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
        
        elif mode == "balanced":
            df_copy = df.copy()

            model = RandomForestRegressor()
            X = df_copy.drop(target, axis=1)
            y = df_copy[target]

            best_score = cross_val_score(model, X, y, cv=3).mean()

            for colname in list(X.columns):

                temp_X = X.drop(columns=[colname])

                score = cross_val_score(model, temp_X, y, cv=3).mean()
                print(best_score)
                print(score)
                if score >= best_score:
                    X = temp_X
                    best_score = score

            result = pd.concat([X, y], axis=1)
            return result