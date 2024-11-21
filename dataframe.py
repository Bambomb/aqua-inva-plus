import pandas as pd

def create_dataframe(file_path):
    """Crée un dataframe à partir d'un fichier .csv"""
    data= pd.read_csv(file_path,delimiter=";",encoding='latin1')
    data = data.drop(columns=['source','references','code_observation'], errors='ignore')
    data = data.dropna()
    return data