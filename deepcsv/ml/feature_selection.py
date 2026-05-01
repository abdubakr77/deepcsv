import pandas as pd
# from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier,GradientBoostingRegressor,GradientBoostingClassifier
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score


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

            def auto_alpha_tuned():
                if len(df) <= 10000:
                    alpha=0.1
                elif len(df) <= 100000:
                    alpha=1.0
                else:
                    alpha=5.0
                return alpha
            
            model = model = Ridge(alpha=auto_alpha_tuned())

            X = df_copy.drop(target, axis=1)
            y = df_copy[target]

            best_score = cross_val_score(model, X , y, cv=5).mean()

            for colname in list(X.columns):

                temp_X = X.drop(columns=[colname])

                score = cross_val_score(model, temp_X, y, cv=5).mean()
                print(best_score)
                print(score)
                if score >= best_score:
                    X = temp_X
                    best_score = score

            result = pd.concat([X, y], axis=1)
            return result