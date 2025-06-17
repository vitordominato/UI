def garantir_colunas(df):
    """Garante todas as colunas essenciais para os leitos."""
    colunas = [
        'leito', 'nome', 'medico', 'equipe', 'especialidade', 'unidade', 'andar',
        # Coloque aqui todos os campos que usa na sua base
    ]
    if isinstance(df, list):
        import pandas as pd
        df = pd.DataFrame(df)
    for col in colunas:
        if col not in df.columns:
            df[col] = ""
    return df

def sanitize_dict(d):
    """Remove valores inválidos e padroniza campos vazios."""
    import numpy as np
    out = {}
    for k, v in d.items():
        if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
            out[k] = ""
        else:
            out[k] = v
    return out
