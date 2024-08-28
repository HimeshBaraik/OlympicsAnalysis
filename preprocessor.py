import pandas as pd

def preprocess(df, region_df):
    #global df, region_df
    # summer olympics:
    df = df[df['Season'] == 'Summer']
    # merge region df:
    df = df.merge(region_df, on='NOC', how = 'left')
    # drop_dup:
    df.drop_duplicates(inplace=True)
    # onehotEncoding:
    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis = 1)

    return df
