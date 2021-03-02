# Import libraries
import pandas as pd
import numpy as np

import data_loading as dl

hues_treemaps = dl.hues_treemaps


# Bar plots
def create_dfs_barplots(prod_index, method_index_list):
    """
    This function extracts all the required information for one product and several methods from the
    matrices and converts it into the format used for plotting by summing the impacts by 'flow compartment'.
    
    Required arguments:
    - system_model: str, select one of the following: 'cutoff', 'consequential', 'apos'.
    - prod_index: int, index of the product to be plotted from the ie_index matrix, e.g. 12759.
    - method_index_list: list of int, index of the LCIA method from the LCIA_index matrix.
        The most common ones are: [222, 485, 541] (or 540 in consequential).
    
    Returns:
    - a new dataframe containing the environmental impacts grouped by 'flow compartment'
    - two variables (chart_type_1, chart_type_2) that will be used for logging the
        different types of data sets in the plotting function.
    """
    # Import the data set according to the selected system model
    A_public_cor = dl.A_public_cor
    B_public = dl.B_public
    ee_index = dl.ee_index
    ie_index = dl.ie_index
    c_array = dl.c_array
    lcia = dl.lcia

    # Create auxiliary, empty DF
    em_df = pd.DataFrame()
    ip_df = pd.DataFrame()
    chart_type_1 = ""

    # Extract information on inputs, emissions for each product
    product_inputs = A_public_cor[A_public_cor["column"] == prod_index]
    product_inputs_details = ie_index.iloc[product_inputs["row"]]
    inputs_df = pd.merge(product_inputs_details, product_inputs,
                         left_on="index", right_on="row")
    product_emissions = B_public[B_public["column"] == prod_index]
    product_emissions_details = ee_index.iloc[product_emissions["row"]]
    emissions_df = pd.merge(product_emissions_details, product_emissions,
                            left_on="index", right_on="row")

    # Calculate impact scores in absolute and in % for each method for emissions and inputs
    for meth in method_index_list:
        score_by_meth = lcia[prod_index, meth]
        # Emissions: Extract the impact_abs and impact_% for each method
        em_scores_list = list(emissions_df["coefficient"] * c_array[emissions_df["row"], meth])
        em_scores = pd.DataFrame(em_scores_list, columns=[str(meth) + '_impact_abs'])
        em_scores[str(meth) + '_impact_%'] = em_scores[
                                                 str(meth) + '_impact_abs'] / abs(score_by_meth)
        em_df = pd.concat([em_df, em_scores], axis=1)
        # Inputs: Extract the impact_abs and impact_% for each method
        inputs_df_scores_list = list(-1 * inputs_df[
            "coefficient"] * lcia[[inputs_df["row"]], meth][0])
        inputs_df_scores = pd.DataFrame(inputs_df_scores_list,
                                        columns=[str(meth) + '_impact_abs'])
        inputs_df_scores[str(meth) + '_impact_%'] = inputs_df_scores[
                                                        str(meth) + '_impact_abs'] / abs(score_by_meth)
        ip_df = pd.concat([ip_df, inputs_df_scores], axis=1)

    # Gather input and emissions in one DF with impact_abs and impact_%
    clean_em_df = pd.concat([emissions_df, em_df], axis=1)
    clean_ip_df = pd.concat([inputs_df, ip_df], axis=1)
    clean_all_df = pd.concat([clean_ip_df, clean_em_df])

    # Classifying each row into 'flow compartments'
    clean_all_df['impact_cat'] = clean_all_df['compartment'].apply(
        lambda x: 'Inputs from environment' if x == 'natural resource'
        else 'Emissions to ' + str(x))
    clean_all_df['impact_cat'] = clean_all_df['impact_cat'].apply(
        lambda x: 'Inputs f. technosphere' if x == 'Emissions to nan'
        else x)
    # Group by and sum 'flow compartments' impact_% by method and round values
    clean_all_df_grouped = clean_all_df.groupby(['impact_cat']).sum().reset_index()
    grouped = clean_all_df_grouped.copy()
    for meth in method_index_list:
        # Check if data set is not empty
        try:
            grouped[str(meth) + '_impact_%'] = grouped[
                str(meth) + '_impact_%'].apply(lambda x: round(x * 100))
            grouped[str(meth) + '_abs'] = abs(grouped[str(meth) + '_impact_%'])
            grouped.loc[grouped[str(meth) + '_impact_%'] < 0, str(meth) + '_sign'] = int(-1)
            grouped.loc[grouped[str(meth) + '_impact_%'] > 0, str(meth) + '_sign'] = int(1)
            grouped.loc[grouped[str(meth) + '_impact_%'] == 0, str(meth) + '_sign'] = np.nan
            chart_type_1 = "2 - rescaled"

            # Check if rescaling is needed (i.e. if pos. and neg. values exist)
            if grouped[str(meth) + '_sign'].count() != abs(grouped[str(meth) + '_sign'].sum()):
                pos_imp = grouped[grouped[str(meth) + '_sign'] == 1]
                neg_imp = grouped[grouped[str(meth) + '_sign'] == -1]
                sum_pos_imp = pos_imp[str(meth) + '_abs'].sum()
                sum_neg_imp = neg_imp[str(meth) + '_abs'].sum()
                # Defines the rescaling base (i.e. the biggest absolute value of a 'flow compartment')
                if sum_neg_imp < sum_pos_imp:
                    max_sum_imp = sum_pos_imp
                else:
                    max_sum_imp = sum_neg_imp
                # Rescales, replaces NaN with 0 and rounds data
                grouped[str(meth) + '_scaled'] = grouped[str(meth) + '_abs'] / max_sum_imp * grouped[
                    str(meth) + '_sign'] * 100
                grouped[str(meth) + '_scaled'] = grouped[str(meth) + '_scaled'].fillna(0)
                grouped[str(meth) + '_scaled'] = round(grouped[str(meth) + '_scaled'], 0)
            # No rescaling necessary
            else:
                grouped[str(meth) + '_scaled'] = grouped[str(meth) + '_impact_%']
                chart_type_1 = '1 - normal'
        # Data set is empty: Create dummy row for empty plot
        except KeyError:
            grouped = pd.DataFrame(index=[0], columns=['row', 'column',
                                                       'coefficient', 'impact_cat'])
            for meth2 in method_index_list:
                grouped[str(meth2) + '_impact_abs'] = "error"
                grouped[str(meth2) + '_impact_%'] = "error"
                grouped[str(meth2) + "_sign"] = "error"
                grouped[str(meth2) + "_scaled"] = "error"
            chart_type_1 = "5 - no data"
    # Add product index and replace 'error' with NaN
    grouped['ref_prod'] = prod_index
    grouped = grouped.replace("error", False)

    # For stats/logging: check if positive and/or negative values
    list_sign = []
    for meth in method_index_list:
        list_sign = list_sign + list(grouped[str(meth) + '_sign'].values)
    if not list(filter(lambda number: number < 0, list_sign)):
        chart_type_2 = "positive only"
    else:
        chart_type_2 = "incl. negative"

    # Sorting values: important for order of 'flow compartment' labels while plotting
    grouped_copy = grouped.copy()
    sort_order = method_index_list[::-1]
    sort_columns = []
    for meth_r in sort_order:
        sort_columns.append(str(meth_r) + '_impact_%')
    grouped_sorted = grouped_copy.sort_values(by=sort_columns, ascending=False)

    return grouped_sorted, chart_type_1, chart_type_2


def create_dfs_treemaps(prod_index, method_index):
    """
    This function extracts all the required information for one product from the
    matrices and converts it into the format used for plotting.

    Required arguments:
    - prod_index: int, index of the product to be plotted from the ie_index matrix, e.g. 12759.
    - method_index: int, index of the LCIA method from the LCIA_index matrix.
        The most common ones are: 222, 485, 541 (or 540 in consequential).
    
    Returns:
    - nine new dataframes: with all the positive / negative inputs / emissions, grouped and ungrouped,
        used to check if the positive or the negative maximum contributor needs to be
        broken down to the next level.
    """
    
    # Import the data set according to the selected system model
    A_public = dl.A_public
    B_public = dl.B_public
    ee_index = dl.ee_index
    ie_index = dl.ie_index
    c_array = dl.c_array
    lcia = dl.lcia

    # Gather information on the product
    product_info_raw = ie_index.iloc[prod_index]
    product_info = product_info_raw.copy()
    if len(product_info["activityName"]) > 115:
        if " " in product_info["activityName"][105:115]:
            index = product_info["activityName"][105:115].index(" ")
            product_info["activityName"] = product_info["activityName"][:105 + index] + "..."
        else:
            product_info["activityName"] = product_info["activityName"][:115] + "..."

    # Gather information on the inputs for this product
    product_inputs = A_public[A_public["column"] == prod_index]
    product_inputs = product_inputs.drop(product_inputs[product_inputs["row"] == prod_index].index)
    product_inputs_details = ie_index.iloc[product_inputs["row"]]
    inputs_df = pd.merge(product_inputs_details, product_inputs, left_on="index", right_on="row")

    # Calculate impact scores for these inputs
    in_scores = -1 * inputs_df["coefficient"] * lcia[inputs_df["row"], method_index]
    inputs_df["LCIAscore"] = in_scores
    inputs_df["scaled_scores"] = inputs_df["LCIAscore"]
    inputs_df["coefficient"] = abs(inputs_df["coefficient"])
    inputs_df["next_coefficient"] = inputs_df["coefficient"]
    inputs_df["chain"] = inputs_df["row"].astype(str)
    inputs_df = inputs_df.sort_values("LCIAscore", ascending=False).reset_index(drop=True)
    for i in range(len(inputs_df)):
        if "market for" in inputs_df.loc[i, "activityName"]:
            inputs_df.loc[i, "product"] = "[m] " + inputs_df.loc[i, "product"]
        elif "market group" in inputs_df.loc[i, "activityName"]:
            inputs_df.loc[i, "product"] = "[mg] " + inputs_df.loc[i, "product"]

    # Split into positive and negative input scores
    # for negative scores
    inputs_df_neg = inputs_df[inputs_df["LCIAscore"] < 0].sort_values("LCIAscore").reset_index(drop=True)
    inputs_df_neg["LCIAscore"] = abs(inputs_df_neg["LCIAscore"])
    inputs_df_neg["scaled_scores"] = abs(inputs_df_neg["scaled_scores"])
    inputs_df_neg_g = inputs_df_neg.groupby("product").sum().sort_values("LCIAscore", ascending=False).reset_index()
    inputs_df_neg_g["hues"] = hues_treemaps[2]
    # for positive scores
    inputs_df_pos = inputs_df[inputs_df["LCIAscore"] >= 0].sort_values("LCIAscore", ascending=False).reset_index(
        drop=True)
    inputs_df_pos_g = inputs_df_pos.groupby("product").sum().sort_values("LCIAscore", ascending=False).reset_index()
    inputs_df_pos_g["hues"] = hues_treemaps[0]

    # Gather information on the emissions for this product
    product_emissions = B_public[B_public["column"] == prod_index]
    product_emissions_details = ee_index.iloc[product_emissions["row"]]
    emissions_df = pd.merge(product_emissions_details, product_emissions, left_on="index", right_on="row")

    # Extract impact scores for these emissions
    em_scores = emissions_df["coefficient"] * c_array[product_emissions["row"], method_index]
    emissions_df["LCIAscore"] = em_scores
    emissions_df["scaled_scores"] = emissions_df["LCIAscore"]
    emissions_df["coefficient"] = abs(emissions_df["coefficient"])

    # Split into positive and negative emission scores
    # for negative scores
    em_df_neg = emissions_df[emissions_df["LCIAscore"] < 0].sort_values("LCIAscore").reset_index(drop=True)
    em_df_neg["LCIAscore"] = abs(em_df_neg["LCIAscore"])
    em_df_neg["scaled_scores"] = abs(em_df_neg["scaled_scores"])
    em_df_neg_g = em_df_neg.groupby("name").sum().sort_values("LCIAscore", ascending=False).reset_index()
    em_df_neg_g["hues"] = hues_treemaps[3]
    # for positive scores
    em_df_pos = emissions_df[emissions_df["LCIAscore"] >= 0].sort_values("LCIAscore", ascending=False).reset_index(
        drop=True)
    em_df_pos_g = em_df_pos.groupby("name").sum().sort_values("LCIAscore", ascending=False).reset_index()
    em_df_pos_g["hues"] = hues_treemaps[1]

    return (product_info, inputs_df_pos, inputs_df_pos_g, em_df_pos, em_df_pos_g,
            inputs_df_neg, inputs_df_neg_g, em_df_neg, em_df_neg_g)


def create_nextlevel_dfs(inputs_df_pos, inputs_df_pos_g, inputs_df_neg, inputs_df_neg_g,
                         method_index, positives, negatives):
    """
    This function checks if the positive or the negative maximum contributor needs to be
    broken down to the next level. Then it extracts the required information for all the
    grouped inputs that make up this maximum contributor.

    Required arguments:
    - system_model: str, select one of the following: 'cutoff', 'consequential', 'apos'.
    - four dataframes: inputs_df_pos, inputs_df_pos_g, inputs_df_neg, inputs_df_neg_g
        from create_dfs_treemaps function.
    - prod_index: int, the index of the product to be plotted.
    - method_index: int, the LCIA method used.
    - positives: the sum of all the positive values on whatever level the function is used from sum_values function.
    - negatives: the sum of all the negative values on whatever level the function is used from sum_values function.

    Returns:
    - eight new dataframes with all the positive / negative inputs / emissions to be used for
        plotting the maximum contributor on the next level.
    """
    # Check that DF is not empty and if main contributor is positive and above 50%
    if (not inputs_df_pos_g.empty and not inputs_df_pos_g["scaled_scores"][0] /
            (positives + negatives + np.exp(-30)) < 0.5):
        grouped_inputs = inputs_df_pos[inputs_df_pos["product"] == inputs_df_pos_g.iloc[0]["product"]
                                       ]["chain"].tolist()
        inputs_df_pos_2_list = []
        em_df_pos_2_list = []
        inputs_df_neg_2_list = []
        em_df_neg_2_list = []

        # For all subproducts run the create_dfs_treemaps function
        for i in grouped_inputs:
            # Uses a unique identifier via 'chain' from create_dfs_treemaps function to
            # define the index of the max contributor
            prod = inputs_df_pos[inputs_df_pos["chain"] == f"{i}"]["row"].tolist()
            (product_info_2, inputs_df_pos_2, inputs_df_pos_g_2, em_df_pos_2,
             em_df_pos_g_2, inputs_df_neg_2, inputs_df_neg_g_2, em_df_neg_2,
             em_df_neg_g_2) = create_dfs_treemaps(prod[0], method_index)

            # For positive inputs: Add previous coefficients, next coefficients of the main contributor
            # and scaled scores to the df_2
            inputs_df_pos_2["prev_coefficient"] = inputs_df_pos[inputs_df_pos["chain"] == f"{i}"
                                                                ]["next_coefficient"].tolist() * len(inputs_df_pos_2)
            inputs_df_pos_2["next_coefficient"] = inputs_df_pos_2["prev_coefficient"] * inputs_df_pos_2["coefficient"]
            inputs_df_pos_2["scaled_scores"] = inputs_df_pos_2["LCIAscore"] * inputs_df_pos_2["prev_coefficient"]
            inputs_df_pos_2["chain"] = inputs_df_pos_2["row"].astype(str) + "_" + str(i)

            # For positive emissions: Add previous coefficients, next coefficients of the main contributor
            # and scaled scores to the df_2
            em_df_pos_2["prev_coefficient"] = inputs_df_pos[inputs_df_pos["chain"] == f"{i}"
                                                            ]["next_coefficient"].tolist() * len(em_df_pos_2)
            em_df_pos_2["next_coefficient"] = em_df_pos_2["prev_coefficient"] * em_df_pos_2["coefficient"]
            em_df_pos_2["scaled_scores"] = em_df_pos_2["LCIAscore"] * em_df_pos_2["prev_coefficient"]
            # Create lists for all positive input and emissions for all products that make up the max contributor
            inputs_df_pos_2_list.append(inputs_df_pos_2)
            em_df_pos_2_list.append(em_df_pos_2)

            # For negative inputs: Add previous coefficients, next coefficients of the main contributor
            # and scaled scores to the df_2
            inputs_df_neg_2["prev_coefficient"] = inputs_df_pos[inputs_df_pos["chain"] == f"{i}"
                                                                ]["next_coefficient"].tolist() * len(inputs_df_neg_2)
            inputs_df_neg_2["next_coefficient"] = inputs_df_neg_2["prev_coefficient"] * inputs_df_neg_2["coefficient"]
            inputs_df_neg_2["scaled_scores"] = inputs_df_neg_2["LCIAscore"] * inputs_df_neg_2["prev_coefficient"]
            inputs_df_neg_2["chain"] = inputs_df_neg_2["row"].astype(str) + "_" + str(i)

            # For negative emissions: Add previous coefficients, next coefficients of the main contributor
            # and scaled scores to the df_2
            em_df_neg_2["prev_coefficient"] = inputs_df_pos[inputs_df_pos["chain"] == f"{i}"
                                                            ]["next_coefficient"].tolist() * len(em_df_neg_2)
            em_df_neg_2["next_coefficient"] = em_df_neg_2["prev_coefficient"] * em_df_neg_2["coefficient"]
            em_df_neg_2["scaled_scores"] = em_df_neg_2["LCIAscore"] * em_df_neg_2["prev_coefficient"]

            # Create lists for all negative input and emissions for all products that make up the max contributor
            inputs_df_neg_2_list.append(inputs_df_neg_2)
            em_df_neg_2_list.append(em_df_neg_2)

        # Add lists to DFs and define hue:
        # for positive inputs:
        inputs_df_pos_2 = pd.concat(inputs_df_pos_2_list)
        inputs_df_pos_2 = inputs_df_pos_2.sort_values("scaled_scores", ascending=False).reset_index()
        inputs_df_pos_g_2 = inputs_df_pos_2.groupby("product").sum("scaled_scores").sort_values(
            "scaled_scores", ascending=False).reset_index()
        inputs_df_pos_g_2["hues"] = hues_treemaps[0]
        # for positive emissions:
        em_df_pos_2 = pd.concat(em_df_pos_2_list)
        em_df_pos_g_2 = em_df_pos_2.groupby("name").sum().reset_index()
        em_df_pos_g_2["hues"] = hues_treemaps[1]
        # for negative inputs:
        inputs_df_neg_2 = pd.concat(inputs_df_neg_2_list)
        inputs_df_neg_2 = inputs_df_neg_2.sort_values("scaled_scores", ascending=False).reset_index()
        inputs_df_neg_g_2 = inputs_df_neg_2.groupby("product").sum("scaled_scores").sort_values(
            "scaled_scores", ascending=False).reset_index()
        inputs_df_neg_g_2["hues"] = hues_treemaps[2]
        # for negative emissions:
        em_df_neg_2 = pd.concat(em_df_neg_2_list)
        em_df_neg_g_2 = em_df_neg_2.groupby("name").sum().reset_index()
        em_df_neg_g_2["hues"] = hues_treemaps[3]

    # Check if main contributor is negative
    else:
        grouped_inputs = inputs_df_neg[inputs_df_neg["product"] == inputs_df_neg_g.iloc[0]["product"]
                                       ]["chain"].tolist()

        inputs_df_pos_2_list = []
        em_df_pos_2_list = []
        inputs_df_neg_2_list = []
        em_df_neg_2_list = []
        # For all subproducts run the create_dfs_treemaps function
        for i in grouped_inputs:
            # Uses a unique identifier via 'chain' from create_dfs_treemaps function to define
            # the index of the max contributor
            prod = inputs_df_neg[inputs_df_neg["chain"] == f"{i}"]["row"].tolist()
            (product_info_2, inputs_df_pos_2, inputs_df_pos_g_2, em_df_pos_2,
             em_df_pos_g_2, inputs_df_neg_2, inputs_df_neg_g_2, em_df_neg_2,
             em_df_neg_g_2) = create_dfs_treemaps(prod[0], method_index)

            # For negative inputs: Add previous coefficients, next coefficients of the main contributor
            # and scaled scores to the df_2
            inputs_df_neg_2["prev_coefficient"] = inputs_df_neg[inputs_df_neg["chain"] == f"{i}"
                                                                ]["next_coefficient"].tolist() * len(inputs_df_neg_2)
            inputs_df_neg_2["next_coefficient"] = inputs_df_neg_2["prev_coefficient"] * inputs_df_neg_2["coefficient"]
            inputs_df_neg_2["scaled_scores"] = inputs_df_neg_2["LCIAscore"] * inputs_df_neg_2["prev_coefficient"]
            inputs_df_neg_2["chain"] = inputs_df_neg_2["row"].astype(str) + "_" + str(i)

            # For negative emissions: Add previous coefficients, next coefficients of the main contributor
            # and scaled scores to the df_2
            em_df_neg_2["prev_coefficient"] = inputs_df_neg[inputs_df_neg["chain"] == f"{i}"
                                                            ]["next_coefficient"].tolist() * len(em_df_neg_2)
            em_df_neg_2["next_coefficient"] = em_df_neg_2["prev_coefficient"] * em_df_neg_2["coefficient"]
            em_df_neg_2["scaled_scores"] = em_df_neg_2["LCIAscore"] * em_df_neg_2["prev_coefficient"]

            # Create lists for all negative input and emissions for all products that make up the max contributor
            inputs_df_neg_2_list.append(inputs_df_neg_2)
            em_df_neg_2_list.append(em_df_neg_2)

            # For positive inputs: Add previous coefficients, next coefficients of the main contributor
            # and scaled scores to the df_2
            inputs_df_pos_2["prev_coefficient"] = inputs_df_neg[inputs_df_neg["chain"] == f"{i}"
                                                                ]["next_coefficient"].tolist() * len(inputs_df_pos_2)
            inputs_df_pos_2["next_coefficient"] = inputs_df_pos_2["prev_coefficient"] * inputs_df_pos_2["coefficient"]
            inputs_df_pos_2["scaled_scores"] = inputs_df_pos_2["LCIAscore"] * inputs_df_pos_2["prev_coefficient"]
            inputs_df_pos_2["chain"] = inputs_df_pos_2["row"].astype(str) + "_" + str(i)

            # For positive emissions: Add previous coefficients, next coefficients of the main contributor
            # and scaled scores to the df_2
            em_df_pos_2["prev_coefficient"] = inputs_df_neg[inputs_df_neg["chain"] == f"{i}"
                                                            ]["next_coefficient"].tolist() * len(em_df_pos_2)
            em_df_pos_2["next_coefficient"] = em_df_pos_2["prev_coefficient"] * em_df_pos_2["coefficient"]
            em_df_pos_2["scaled_scores"] = em_df_pos_2["LCIAscore"] * em_df_pos_2["prev_coefficient"]

            # Create lists for all positive input and emissions for all products that make up the max contributor
            inputs_df_pos_2_list.append(inputs_df_pos_2)
            em_df_pos_2_list.append(em_df_pos_2)

        # Add lists to DFs and define hue:
        # for negative inputs:
        inputs_df_neg_2 = pd.concat(inputs_df_neg_2_list)
        inputs_df_neg_2 = inputs_df_neg_2.sort_values("scaled_scores", ascending=False).reset_index()
        inputs_df_neg_g_2 = inputs_df_neg_2.groupby("product").sum("scaled_scores").sort_values(
            "scaled_scores", ascending=False).reset_index()
        inputs_df_neg_g_2["hues"] = hues_treemaps[2]
        # for negative emissions:
        em_df_neg_2 = pd.concat(em_df_neg_2_list)
        em_df_neg_g_2 = em_df_neg_2.groupby("name").sum().reset_index()
        em_df_neg_g_2["hues"] = hues_treemaps[3]
        # for positive inputs:
        inputs_df_pos_2 = pd.concat(inputs_df_pos_2_list)
        inputs_df_pos_2 = inputs_df_pos_2.sort_values("scaled_scores", ascending=False).reset_index()
        inputs_df_pos_g_2 = inputs_df_pos_2.groupby("product").sum("scaled_scores").sort_values(
            "scaled_scores", ascending=False).reset_index()
        inputs_df_pos_g_2["hues"] = hues_treemaps[0]
        # for positive emissions:
        em_df_pos_2 = pd.concat(em_df_pos_2_list)
        em_df_pos_g_2 = em_df_pos_2.groupby("name").sum().reset_index()
        em_df_pos_g_2["hues"] = hues_treemaps[1]

    return (inputs_df_pos_2, inputs_df_pos_g_2, em_df_pos_2, em_df_pos_g_2,
            inputs_df_neg_2, inputs_df_neg_g_2, em_df_neg_2, em_df_neg_g_2)
