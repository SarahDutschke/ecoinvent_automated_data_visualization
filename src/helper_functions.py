import numpy as np
from itertools import chain


# Helper functions for treemaps
def plot_type_definition(inputs_df_pos_g, em_df_pos_g, inputs_df_neg_g, em_df_neg_g):
    """
    This function evaluates what type of next level plotting is required.
    It takes in the dataframes and checks if the total of all the values is negative,
    positive or zero

    Required arguments:
    - four dataframes: inputs_df_pos_g, em_df_pos_g, inputs_df_neg_g, em_df_neg_g
        created in preprocess_dataset_groupsort or next_level_processing function

    Returns:
    - plot_type: string, one of the following: "zero", "pos", "neg"
    """
    plot_type = ""
    # Check if 'zero'
    if (sum(inputs_df_pos_g["scaled_scores"]) + sum(em_df_pos_g["scaled_scores"]) +
            sum(inputs_df_neg_g["scaled_scores"]) + sum(em_df_neg_g["scaled_scores"]) == 0):
        plot_type = "zero"
    # Check if 'pos'
    elif (sum(inputs_df_pos_g["scaled_scores"]) + sum(em_df_pos_g["scaled_scores"]) >=
          sum(inputs_df_neg_g["scaled_scores"]) + sum(em_df_neg_g["scaled_scores"])):
        plot_type = "pos"
    # Check if 'neg'
    elif (sum(inputs_df_pos_g["scaled_scores"]) + sum(em_df_pos_g["scaled_scores"]) <
          sum(inputs_df_neg_g["scaled_scores"]) + sum(em_df_neg_g["scaled_scores"])):
        plot_type = "neg"

    return plot_type


def shorten_product_name(inputs_df_pos_g, positives, negatives, prev_labels):
    """
    This function caps the product name to a maximum number of characters depending
    on the size of the main contributor.

    Required arguments:
    - four dataframes: inputs_df_pos_g, em_df_pos_g, inputs_df_neg_g, em_df_neg_g
        created in preprocess_dataset_groupsort or next_level_processing function
    - total positive and negative values created with the sum_values function
    - prev_labels: list of strings, labels from the previous level

    Returns:
    - prev_labels: list of strings, labels from the previous level with the name of the
    max contributor capped to a maximum length
    """
    # For non-empty DFs and main contributor over 90%, caps the product label to a maximum length of 130 char
    if (not inputs_df_pos_g.empty and
            inputs_df_pos_g.loc[0, "scaled_scores"] / (positives + negatives + np.exp(-30)) > 0.9):
        if len(prev_labels[0]) > 130:
            prev_labels[0] = prev_labels[0][:125] + "..."
    # For non-empty DFs and main contributor between 80-90%, caps the product label to a maximum length of 115 char
    elif (not inputs_df_pos_g.empty and
          inputs_df_pos_g.loc[0, "scaled_scores"] / (positives + negatives + np.exp(-30)) > 0.8):
        if len(prev_labels[0]) > 115:
            prev_labels[0] = prev_labels[0][:110] + "..."
    # For non-empty DFs and main contributor between 70-80%, caps the product label to a maximum length of 90 char
    elif (not inputs_df_pos_g.empty and
          inputs_df_pos_g.loc[0, "scaled_scores"] / (positives + negatives + np.exp(-30)) > 0.7):
        if len(prev_labels[0]) > 90:
            prev_labels[0] = prev_labels[0][:85] + "..."
    # For non-empty DFs and main contributor between 60-70%, caps the product label to a maximum length of 75 char
    elif (not inputs_df_pos_g.empty and
          inputs_df_pos_g.loc[0, "scaled_scores"] / (positives + negatives + np.exp(-30)) > 0.6):
        if len(prev_labels[0]) > 75:
            prev_labels[0] = prev_labels[0][:70] + "..."
    # For other DF, caps the product label to a maximum length of 65 char
    elif not inputs_df_pos_g.empty:
        if len(prev_labels[0]) > 65:
            prev_labels[0] = prev_labels[0][:60] + "..."
    else:
        prev_labels = prev_labels

    return prev_labels


def add_linebreaks(labels):
    """
    This function adds line breaks to the product name to fit the labels better into the
    boxes of the treemap.

    Required arguments:
    - labels: list of strings, created either in the first_level_lists or the append_nextlevel_lists
    function

    Returns:
    - labels: list of strings, with line breaks in all the longer strings
    """
    for i in range(len(labels)):
        labels[i] = labels[i].replace("<br>", " ")
        labels[i] = labels[i].replace("< ", "<")
        labels[i] = labels[i].replace("> ", ">")
        labels[i] = labels[i].replace(" um", "um")
        labels[i] = labels[i].replace("tetrachlorodibenzo-p-dioxin", "tetrachlo- rodibenzo-p-dioxin")
        if len(labels[i]) > 20:
            if " " in labels[i][15:20]:
                split_1 = labels[i][15:20].replace(" ", "<br>", 1)
                labels[i] = labels[i][:15] + split_1 + labels[i][20:]
            elif " " in labels[i][10:15]:
                split_1 = labels[i][10:15].replace(" ", "<br>", 1)
                labels[i] = labels[i][:10] + split_1 + labels[i][15:]
        if len(labels[i][23:]) > 20:
            if " " in labels[i][38:43]:
                split_2 = labels[i][38:43].replace(" ", "<br>", 1)
                labels[i] = labels[i][:38] + split_2 + labels[i][43:]
            elif " " in labels[i][33:38]:
                split_2 = labels[i][33:38].replace(" ", "<br>", 1)
                labels[i] = labels[i][:33] + split_2 + labels[i][38:]
        if len(labels[i][46:]) > 20:
            if " " in labels[i][61:66]:
                split_3 = labels[i][61:66].replace(" ", "<br>", 1)
                labels[i] = labels[i][:61] + split_3 + labels[i][66:]
            elif " " in labels[i][56:61]:
                split_3 = labels[i][56:61].replace(" ", "<br>", 1)
                labels[i] = labels[i][:56] + split_3 + labels[i][61:]
        if len(labels[i][69:]) > 20:
            if " " in labels[i][84:89]:
                split_4 = labels[i][84:89].replace(" ", "<br>", 1)
                labels[i] = labels[i][:84] + split_4 + labels[i][89:]
            elif " " in labels[i][79:84]:
                split_4 = labels[i][79:84].replace(" ", "<br>", 1)
                labels[i] = labels[i][:79] + split_4 + labels[i][84:]

        split_label = labels[i].split("<br>")
        splits = []
        for s in split_label:
            if len(s) > 15:
                s = s.replace(", ", ",<br>", 1)
                splits.append(s)
            else:
                splits.append(s)
        labels[i] = "<br>".join(splits)

    return labels


def sum_values(inputs_df_pos_g, em_df_pos_g,
               inputs_df_pos_g_2=None, em_df_pos_g_2=None,
               inputs_df_pos_g_3=None, em_df_pos_g_3=None,
               inputs_df_pos_g_4=None, em_df_pos_g_4=None,
               inputs_df_pos_g_5=None, em_df_pos_g_5=None):
    """
    Function description:
    This function sums up either all the positive or all the negative values on all the levels, without duplicating
    the values of the maximum contributors at each level.

    Required arguments:
    - inputs_df_pos_g: pandas dataframe containing either the positive or the negative inputs on the first level
    - em_df_pos_g: pandas dataframe containing either the positive or the negative emissions on the first level

    Optional arguments:
    - pandas dataframes for inputs on all other levels
    - pandas dataframes for emissions on all other levels

    Returns:
    - the variable 'summed_values' which contains the sum of the scores of all the positive or negative
        inputs and emissions.
    """
    summed_values = 0

    if inputs_df_pos_g_5 is not None:
        inputs_df_pos_g_4 = inputs_df_pos_g_4[1:]
        if not inputs_df_pos_g_5.empty:
            summed_values += sum(inputs_df_pos_g_5["scaled_scores"])
        if not em_df_pos_g_5.empty:
            summed_values += sum(em_df_pos_g_5["scaled_scores"])

    if inputs_df_pos_g_4 is not None:
        inputs_df_pos_g_3 = inputs_df_pos_g_3[1:]
        if not inputs_df_pos_g_4.empty:
            summed_values += sum(inputs_df_pos_g_4["scaled_scores"])
        if not em_df_pos_g_4.empty:
            summed_values += sum(em_df_pos_g_4["scaled_scores"])

    if inputs_df_pos_g_3 is not None:
        inputs_df_pos_g_2 = inputs_df_pos_g_2[1:]
        if not inputs_df_pos_g_3.empty:
            summed_values += sum(inputs_df_pos_g_3["scaled_scores"])
        if not em_df_pos_g_3.empty:
            summed_values += sum(em_df_pos_g_3["scaled_scores"])

    if inputs_df_pos_g_2 is not None:
        inputs_df_pos_g = inputs_df_pos_g[1:]
        if not inputs_df_pos_g_2.empty:
            summed_values += sum(inputs_df_pos_g_2["scaled_scores"])
        if not em_df_pos_g_2.empty:
            summed_values += sum(em_df_pos_g_2["scaled_scores"])

    if not inputs_df_pos_g.empty:
        summed_values += sum(inputs_df_pos_g["scaled_scores"])
    if not em_df_pos_g.empty:
        summed_values += sum(em_df_pos_g["scaled_scores"])

    return summed_values


def split_into_subitems(a, n):
    """
    Splits items into pieces, after n subitems.
    Function is used in "split_method_name" function.

    Required arguments:
    - a: list, data to be split
    - n: int, determines after how many words the string will be split

    Returns:
    - a: list of strings split into subitems
    """
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def split_method_name(n, unlisted_items):
    """
    Splits items into pieces, after n subitems and adds a line break ('<br>') and reconcatenates the items.
    Function uses "split_into_subitems" function.

    Required arguments:
    - n: int, determines after how many words (subitems) the item will be split and where '<br>' will be entered.
    - unlisted_items: list, simple list of strings.

    Returns:
    - new_list_joined: list of strings with line breaks added in
    """

    list_items = []
    split_list = []
    join_list = []
    new_list_joined = []

    for i in range(len(unlisted_items)):
        broken_item = unlisted_items[i].split(' ')
        list_items.append(broken_item)

    for item in list_items:
        counter = 0

        if (len(item) // n) == 1:
            split_item = list(split_into_subitems(item, n - 1))
            split_item.insert(1, ["<br>"])
            split_list.append(split_item)
        else:
            split_item = list(split_into_subitems(item, (len(item) // n)))
            for n2 in range((len(item) // n)):
                split_item.insert((1 + counter), ["<br>"])
                counter += 2
            split_list.append(split_item)

    for item2 in split_list:
        ex2 = chain.from_iterable(item2)
        join_list.append(list(ex2))

    for each in join_list:
        new_item = " ".join(each)
        new_list_joined.append(new_item)

    return new_list_joined
