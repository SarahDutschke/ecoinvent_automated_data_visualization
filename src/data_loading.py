import pandas as pd
import scipy.sparse as sp
from pypardiso import spsolve


path = "../data/raw"

red_orig = 'rgba(237,28,36, 1)'
red2_orig = 'rgba(237,28,36, 0.5)'
black_orig = 'rgba(0, 0, 0, 1)'
grey0_orig = 'rgba(0, 0, 0,  0.9)'
grey1_orig = 'rgba(0, 0, 0,  0.8)'
grey1B_orig = 'rgba(0, 0, 0,  0.7)'
grey2_orig = 'rgba(0, 0, 0,  0.6)'
grey2B_orig = 'rgba(0, 0, 0,  0.5)'
grey3_orig = 'rgba(0, 0, 0,  0.4)'
grey3B_orig = 'rgba(0, 0, 0,  0.3)'
grey4_orig = 'rgba(0, 0, 0,  0.2)'
grey5_orig = 'rgba(0, 0, 0,  0.1)'
white_orig = 'rgba(254, 254, 254,  1)'

hues_barplots = [red_orig, black_orig, grey3B_orig, grey2B_orig, red2_orig, grey5_orig]
hues_treemaps = ["rgb(119, 119, 119)", "rgb(255, 170, 170)", "rgb(0, 140, 100)", "rgb(180, 235, 200)"]
font_type = "Helvetica"
l_break = 3

def import_data(path):
    """
    This function imports the globally required libraries and the data for the three different system models.

    Required arguments:
    - path: string, path to where the csv files are stored in folders by system model,
        e.g. "../data/raw"

    Returns:
    - six matrices for each of the system models (A_public, B_public, C_public, ie_index, ee_index and LCIA_index)
    """
    # Import data
    A_public_cutoff = pd.read_csv(f"{path}/cutoff/A_public.csv", delimiter=";")
    A_public_apos = pd.read_csv(f"{path}/apos/A_public.csv", delimiter=";")
    A_public_consequential = pd.read_csv(f"{path}/consequential/A_public.csv", delimiter=";")

    B_public_cutoff = pd.read_csv(f"{path}/cutoff/B_public.csv", delimiter=";")
    B_public_apos = pd.read_csv(f"{path}/apos/B_public.csv", delimiter=";")
    B_public_consequential = pd.read_csv(f"{path}/consequential/B_public.csv", delimiter=";")

    C_public_cutoff = pd.read_csv(f"{path}/cutoff/C_public.csv", delimiter=";")
    C_public_apos = pd.read_csv(f"{path}/apos/C_public.csv", delimiter=";")
    C_public_consequential = pd.read_csv(f"{path}/consequential/C_public.csv", delimiter=";")

    ee_index_cutoff = pd.read_csv(f"{path}/cutoff/ee_index.csv", sep=";", index_col="index")
    ee_index_apos = pd.read_csv(f"{path}/apos/ee_index.csv", sep=";", index_col="index")
    ee_index_consequential = pd.read_csv(f"{path}/consequential/ee_index.csv", sep=";", index_col="index")

    ie_index_cutoff = pd.read_csv(f"{path}/cutoff/ie_index.csv", sep=";", encoding="latin1", index_col="index")
    ie_index_apos = pd.read_csv(f"{path}/apos/ie_index.csv", sep=";", encoding="latin1", index_col="index")
    ie_index_consequential = pd.read_csv(f"{path}/consequential/ie_index.csv",
                                         sep=";", encoding="latin1", index_col="index")

    LCIA_index_cutoff = pd.read_csv(f"{path}/cutoff/LCIA_index.csv", sep=";", index_col="index")
    LCIA_index_apos = pd.read_csv(f"{path}/apos/LCIA_index.csv", sep=";", index_col="index")
    LCIA_index_consequential = pd.read_csv(f"{path}/consequential/LCIA_index.csv", sep=";", index_col="index")

    return (A_public_cutoff, A_public_apos, A_public_consequential,
            B_public_cutoff, B_public_apos, B_public_consequential,
            C_public_cutoff, C_public_apos, C_public_consequential,
            ee_index_cutoff, ee_index_apos, ee_index_consequential,
            ie_index_cutoff, ie_index_apos, ie_index_consequential,
            LCIA_index_cutoff, LCIA_index_apos, LCIA_index_consequential)


def calculate_impact_scores(A_public_cutoff, A_public_apos, A_public_consequential,
                            B_public_cutoff, B_public_apos, B_public_consequential,
                            C_public_cutoff, C_public_apos, C_public_consequential,
                            ee_index_cutoff, ee_index_apos, ee_index_consequential,
                            ie_index_cutoff, ie_index_apos, ie_index_consequential,
                            LCIA_index_cutoff, LCIA_index_apos, LCIA_index_consequential):
    """
    This function performs the calculation of lcia scores for all three system models.

    Required arguments:
    - six matrices for each of the system models (A_public, B_public, C_public, ie_index, ee_index and LCIA_index)

    Returns:
    - the C-Matrix in array form for each of the system models
    - the lcia-Matrix with the scores of all the products for each of the system models
    """
    # Remove values in the diagonal
    # Lcia scores for the cutoff matrices
    A_cutoff = sp.coo_matrix((A_public_cutoff["coefficient"], (A_public_cutoff["row"],
                                                               A_public_cutoff["column"]))).tocsc()
    A_public_cor_cutoff = A_public_cutoff.loc[A_public_cutoff["row"] != A_public_cutoff["column"]].copy()

    B_cutoff = sp.coo_matrix((B_public_cutoff["coefficient"], (B_public_cutoff["row"],
                                                               B_public_cutoff["column"])),
                             shape=(len(ee_index_cutoff), len(ie_index_cutoff)))
    lci_cutoff = spsolve(A_cutoff.transpose(), B_cutoff.transpose())
    C_cutoff = sp.coo_matrix((C_public_cutoff["coefficient"], (C_public_cutoff["row"],
                                                               C_public_cutoff["column"])),
                             shape=(len(LCIA_index_cutoff), len(ee_index_cutoff)))
    c_array_cutoff = C_cutoff.transpose().toarray()
    lcia_cutoff = lci_cutoff * C_cutoff.transpose()

    LCIA_index_cutoff['method_long'] = LCIA_index_cutoff[LCIA_index_cutoff.columns[:-1]].apply(
        lambda x: ", ".join(x.astype(str)), axis=1)
    lcia_df_cutoff = pd.DataFrame(data=lcia_cutoff[:, :],
                                  columns=LCIA_index_cutoff['method_long'].values)

    # Lcia scores for the apos matrices
    A_apos = sp.coo_matrix((A_public_apos["coefficient"], (A_public_apos["row"],
                                                           A_public_apos["column"]))).tocsc()
    A_public_cor_apos = A_public_apos.loc[A_public_apos["row"] != A_public_apos["column"]].copy()

    B_apos = sp.coo_matrix((B_public_apos["coefficient"], (B_public_apos["row"],
                                                           B_public_apos["column"])),
                           shape=(len(ee_index_apos), len(ie_index_apos)))
    lci_apos = spsolve(A_apos.transpose(), B_apos.transpose())
    C_apos = sp.coo_matrix((C_public_apos["coefficient"], (C_public_apos["row"],
                                                           C_public_apos["column"])),
                           shape=(len(LCIA_index_apos), len(ee_index_apos)))
    c_array_apos = C_apos.transpose().toarray()
    lcia_apos = lci_apos * C_apos.transpose()

    LCIA_index_apos['method_long'] = LCIA_index_apos[LCIA_index_apos.columns[:-1]].apply(
        lambda x: ", ".join(x.astype(str)), axis=1)
    lcia_df_apos = pd.DataFrame(data=lcia_apos[:, :],
                                columns=LCIA_index_apos['method_long'].values)

    # Lcia scores for the apos matrices
    A_consequential = sp.coo_matrix((A_public_consequential["coefficient"], (A_public_consequential["row"],
                                                                             A_public_consequential["column"]))).tocsc()
    A_public_cor_consequential = A_public_consequential.loc[
        A_public_consequential["row"] != A_public_consequential["column"]].copy()

    B_consequential = sp.coo_matrix((B_public_consequential["coefficient"], (B_public_consequential["row"],
                                                                             B_public_consequential["column"])),
                                    shape=(len(ee_index_consequential), len(ie_index_consequential)))
    lci_consequential = spsolve(A_consequential.transpose(), B_consequential.transpose())
    C_consequential = sp.coo_matrix((C_public_consequential["coefficient"], (C_public_consequential["row"],
                                                                             C_public_consequential["column"])),
                                    shape=(len(LCIA_index_consequential), len(ee_index_consequential)))
    c_array_consequential = C_consequential.transpose().toarray()
    lcia_consequential = lci_consequential * C_consequential.transpose()

    LCIA_index_consequential['method_long'] = LCIA_index_consequential[LCIA_index_consequential.columns[:-1]].apply(
        lambda x: ", ".join(x.astype(str)), axis=1)
    lcia_df_consequential = pd.DataFrame(data=lcia_consequential[:, :],
                                         columns=LCIA_index_consequential['method_long'].values)

    return (A_public_cor_cutoff, c_array_cutoff, lcia_cutoff, LCIA_index_cutoff, lcia_df_cutoff,
            A_public_cor_apos, c_array_apos, lcia_apos, LCIA_index_apos, lcia_df_apos,
            A_public_cor_consequential, c_array_consequential, lcia_consequential, LCIA_index_consequential,
            lcia_df_consequential)


(A_public_cutoff, A_public_apos, A_public_consequential,
 B_public_cutoff, B_public_apos, B_public_consequential,
 C_public_cutoff, C_public_apos, C_public_consequential,
 ee_index_cutoff, ee_index_apos, ee_index_consequential,
 ie_index_cutoff, ie_index_apos, ie_index_consequential,
 LCIA_index_cutoff, LCIA_index_apos, LCIA_index_consequential) = import_data(path)

(A_public_cor_cutoff, c_array_cutoff, lcia_cutoff, LCIA_index_cutoff, lcia_df_cutoff,
 A_public_cor_apos, c_array_apos, lcia_apos, LCIA_index_apos, lcia_df_apos,
 A_public_cor_consequential, c_array_consequential, lcia_consequential, LCIA_index_consequential, lcia_df_consequential
 ) = calculate_impact_scores(A_public_cutoff, A_public_apos, A_public_consequential,
                             B_public_cutoff, B_public_apos, B_public_consequential,
                             C_public_cutoff, C_public_apos, C_public_consequential,
                             ee_index_cutoff, ee_index_apos, ee_index_consequential,
                             ie_index_cutoff, ie_index_apos, ie_index_consequential,
                             LCIA_index_cutoff, LCIA_index_apos, LCIA_index_consequential)


def select_system_model(system_model, A_public_cutoff, A_public_apos, A_public_consequential,
                        A_public_cor_cutoff, A_public_cor_apos, A_public_cor_consequential,
                        B_public_cutoff, B_public_apos, B_public_consequential,
                        C_public_cutoff, C_public_apos, C_public_consequential,
                        ee_index_cutoff, ee_index_apos, ee_index_consequential,
                        ie_index_cutoff, ie_index_apos, ie_index_consequential,
                        LCIA_index_cutoff, LCIA_index_apos, LCIA_index_consequential,
                        c_array_cutoff, c_array_apos, c_array_consequential,
                        lcia_cutoff, lcia_apos, lcia_consequential,
                        lcia_df_cutoff, lcia_df_apos, lcia_df_consequential):
    """
    This function selects one of the three system models and assigns global variable names accordingly.

    Required arguments:
    - system_model: string, one of either "cutoff", "apos" or "consequential"
    - six matrices for each of the system models (A_public, B_public, C_public, ie_index, ee_index and LCIA_index)
    - the C-Matrix in array form for each of the system models
    - the lcia-Matrix with the scores of all the products for each of the system models

    Returns:
    - no returns, because the variable names are declared globally
    """
    global A_public
    global A_public_cor
    global B_public
    global C_public
    global ee_index
    global ie_index
    global LCIA_index
    global c_array
    global lcia
    global lcia_df

    if system_model == "cutoff":
        A_public = A_public_cutoff
        A_public_cor = A_public_cor_cutoff
        B_public = B_public_cutoff
        C_public = C_public_cutoff
        ee_index = ee_index_cutoff
        ie_index = ie_index_cutoff
        LCIA_index = LCIA_index_cutoff
        c_array = c_array_cutoff
        lcia = lcia_cutoff
        lcia_df = lcia_df_cutoff

    elif system_model == "apos":
        A_public = A_public_apos
        A_public_cor = A_public_cor_apos
        B_public = B_public_apos
        C_public = C_public_apos
        ee_index = ee_index_apos
        ie_index = ie_index_apos
        LCIA_index = LCIA_index_apos
        c_array = c_array_apos
        lcia = lcia_apos
        lcia_df = lcia_df_apos

    elif system_model == "consequential":
        A_public = A_public_consequential
        A_public_cor = A_public_cor_consequential
        B_public = B_public_consequential
        C_public = C_public_consequential
        ee_index = ee_index_consequential
        ie_index = ie_index_consequential
        LCIA_index = LCIA_index_consequential
        c_array = c_array_consequential
        lcia = lcia_consequential
        lcia_df = lcia_df_consequential

    return
