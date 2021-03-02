import numpy as np

import data_processing as dp
import helper_functions as hf


# List preparation for treemaps
def first_level_lists(product_info, inputs_df_pos_g, em_df_pos_g, inputs_df_neg_g, em_df_neg_g,
                      positives, negatives):
    """
    This function creates lists for plotting at the first level.

    Required arguments:
    - five dataframes created before, either with the create_dfs_treemaps function: product_info,
    inputs_df_pos_g, em_df_pos_g, inputs_df_neg_g, em_df_neg_g. The order varies depending on the plot type.
    - positives: the sum of all the positive values on the first level, created with the sum_values function
    - negatives: the sum of all the negative values on the first level, created with the sum_values function

    Returns:
    - five lists required for plotting: labels, ids, parents, values, colors
    - score: the LCIA score of the product
    """
    values = ([positives + negatives] +
              list(inputs_df_pos_g["scaled_scores"]) + list(em_df_pos_g["scaled_scores"]) +
              list(inputs_df_neg_g["scaled_scores"]) + list(em_df_neg_g["scaled_scores"]))

    labels = ([product_info["activityName"]] + list(inputs_df_pos_g["product"]) +
              list(em_df_pos_g["name"]) + list(inputs_df_neg_g["product"]) + list(em_df_neg_g["name"]))
    labels[1:] = hf.add_linebreaks(labels[1:])

    parents = ([""] + list((len(inputs_df_pos_g)) * [0]) + list((len(em_df_pos_g)) * [0]) +
               list((len(inputs_df_neg_g)) * [0]) + list((len(em_df_neg_g)) * [0]))

    colors = ([""] + list(inputs_df_pos_g["hues"]) + list(em_df_pos_g["hues"]) +
              list(inputs_df_neg_g["hues"]) + list(em_df_neg_g["hues"]))

    ids = list(range(0, len(labels)))

    score = positives - negatives

    return labels, ids, parents, values, colors, score


def append_nextlevel_lists(inputs_df_pos_g, inputs_df_pos_g_2, em_df_pos_g_2, inputs_df_neg_g_2, em_df_neg_g_2,
                           values, prev_labels, parents, colors, level, positives, negatives,
                           preprev_labels=None, first_labels=None, second_labels=None, third_labels=None):
    """
    This function takes the lists defined before in the first_level_lists function or in a previous use of this same
    function and appends the next level.

    Required arguments:
    - five dataframes: inputs_df_pos_g, inputs_df_pos_g_2, em_df_pos_g_2, inputs_df_neg_g_2, em_df_neg_g_2 created
    with the create_dfs_treemaps or the create_nextlevel_dfs function for plotting the previous and
    the current level. The order varies depending on the plot_type.
    - four lists created at the previous level: values, prev_labels, parents, colors
    - level: int, the level at which the function currently is (between 2-6)
    - positives: the sum of all the positive values on the first level, created with the sum_values function
    - negatives: the sum of all the negative values on the first level, created with the sum_values function

    Optional arguments:
    - preprev_labels: list of strings, the labels created for plotting the level before the previous one.
    - first_labels: list of strings, the labels created at the first level.
    - second_labels: list of strings, the labels created at the second level.
    - third_labels: list of strings, the labels created at the third level.

    Returns:
    - current_labels: list of strings, the labels of only the current level
    - five lists for plotting: labels, ids, parents, values, colors
    """
    if preprev_labels is None:
        preprev_labels = []
    if first_labels is None:
        first_labels = []
    if second_labels is None:
        second_labels = []
    if third_labels is None:
        third_labels = []

    # Values
    for i in list(inputs_df_pos_g_2["scaled_scores"]):
        values.append(i)
    for i in list(em_df_pos_g_2["scaled_scores"]):
        values.append(i)
    for i in list(inputs_df_neg_g_2["scaled_scores"]):
        values.append(i)
    for i in list(em_df_neg_g_2["scaled_scores"]):
        values.append(i)

    if level == 2:
        values[0] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) + sum(em_df_neg_g_2["scaled_scores"]))
        values[1] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) + sum(em_df_neg_g_2["scaled_scores"]))

    elif level == 3:
        values[0] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) + sum(em_df_neg_g_2["scaled_scores"]))
        values[1] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) + sum(em_df_neg_g_2["scaled_scores"]))
        values[len(first_labels)] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) +
                                          sum(em_df_neg_g_2["scaled_scores"]))
    elif level == 4:
        values[0] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) + sum(em_df_neg_g_2["scaled_scores"]))
        values[1] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) + sum(em_df_neg_g_2["scaled_scores"]))
        values[len(first_labels)] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) +
                                          sum(em_df_neg_g_2["scaled_scores"]))
        values[len(second_labels)] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) +
                                           sum(em_df_neg_g_2["scaled_scores"]))
    elif level == 5:
        values[0] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) + sum(em_df_neg_g_2["scaled_scores"]))
        values[1] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) + sum(em_df_neg_g_2["scaled_scores"]))
        values[len(first_labels)] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) +
                                          sum(em_df_neg_g_2["scaled_scores"]))
        values[len(second_labels)] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) +
                                           sum(em_df_neg_g_2["scaled_scores"]))
        values[len(third_labels)] += 2 * (sum(inputs_df_neg_g_2["scaled_scores"]) +
                                          sum(em_df_neg_g_2["scaled_scores"]))

    # Labels
    # Adjust line breaks
    if level == 2:
        prev_labels[1] = prev_labels[1].replace("<br>", " ")
        prev_labels[1] = prev_labels[1].replace("[m]", "market for")
        prev_labels[1] = prev_labels[1].replace("[mg]", "market group for")
        prev_labels[1:] = hf.shorten_product_name(inputs_df_pos_g, positives, negatives, prev_labels[1:])
    else:
        prev_labels[0] = prev_labels[0].replace("<br>", " ")
        prev_labels[0] = prev_labels[0].replace("[m]", "market for")
        prev_labels[0] = prev_labels[0].replace("[mg]", "market group for")
        prev_labels = hf.shorten_product_name(inputs_df_pos_g, positives, negatives, prev_labels)

    current_labels = (hf.add_linebreaks(list(inputs_df_pos_g_2["product"])) +
                      hf.add_linebreaks(list(em_df_pos_g_2["name"])) +
                      hf.add_linebreaks(list(inputs_df_neg_g_2["product"])) +
                      hf.add_linebreaks(list(em_df_neg_g_2["name"])))

    labels = list(preprev_labels) + list(prev_labels) + list(current_labels)

    # Parents
    max_contr_index = [1, len(first_labels), len(second_labels), len(third_labels)]

    i = 0
    while i < len(inputs_df_pos_g_2):
        parents.append(max_contr_index[level - 2])
        i += 1
    i = 0
    while i < len(em_df_pos_g_2):
        parents.append(max_contr_index[level - 2])
        i += 1
    i = 0
    while i < len(inputs_df_neg_g_2):
        parents.append(max_contr_index[level - 2])
        i += 1
    i = 0
    while i < len(em_df_neg_g_2):
        parents.append(max_contr_index[level - 2])
        i += 1

    # Colors
    for i in list(inputs_df_pos_g_2["hues"]):
        colors.append(i)
    for i in list(em_df_pos_g_2["hues"]):
        colors.append(i)
    for i in list(inputs_df_neg_g_2["hues"]):
        colors.append(i)
    for i in list(em_df_neg_g_2["hues"]):
        colors.append(i)

    ids = list(range(0, len(labels)))

    return current_labels, labels, ids, parents, values, colors


def sort_datasets(prod_index, method_index):
    """
    This function sorts the datasets based on different conditions and feeds them to the required
    list creation function.

    Required inputs:
    - prod_index: int, the index of the product to be plotted
    - method_index: int, the index of the LCIA method to be used.
        Most common methods are 222, 485 and 541 (540 for IPCC in consequential).

    Returns:
    - five lists that are required for plotting this specific dataset. The list names are: labels, ids,
    parents, values, colors
    - level: int, the level at which plotting takes place (between 1-6)
    - score: float, the LCIA score of the product
    - plot_type: string, refers to the last level of plotting, can be either "pos" for positive,
    "neg" for negative or "zero" for datasets which have no inputs / emissions or where all of them evaluate to zero.
    - labels_5: list of strings, the labels used for the fifth/sixth level of plotting (if it applies,
    else a list with one empty string).
    """
    labels_5 = [""]
    level = 1  # Level 1

    (product_info, inputs_df_pos, inputs_df_pos_g, em_df_pos, em_df_pos_g, inputs_df_neg, inputs_df_neg_g,
     em_df_neg, em_df_neg_g) = dp.create_dfs_treemaps(prod_index, method_index)

    positives_1 = hf.sum_values(inputs_df_pos_g, em_df_pos_g)
    negatives_1 = hf.sum_values(inputs_df_neg_g, em_df_neg_g)

    plot_type = hf.plot_type_definition(inputs_df_pos_g, em_df_pos_g, inputs_df_neg_g, em_df_neg_g)

    if plot_type == "pos":
        labels_1, ids, parents, values, colors, score = first_level_lists(product_info,
                                                                          inputs_df_pos_g, em_df_pos_g,
                                                                          inputs_df_neg_g, em_df_neg_g,
                                                                          positives_1, negatives_1)
        first_labels = labels_1.copy()

    elif plot_type == "neg":
        labels_1, ids, parents, values, colors, score = first_level_lists(product_info,
                                                                          inputs_df_neg_g, em_df_neg_g,
                                                                          inputs_df_pos_g, em_df_pos_g,
                                                                          positives_1, negatives_1)
        first_labels = labels_1.copy()

    else:
        values = [0, 0]
        labels_1 = ["", ""]
        ids = [0, 1]
        parents = ["", 0]
        colors = ["white", "white"]
        score = values[0]
        first_labels = labels_1.copy()

    # If the LCIA score is 0:
    if plot_type == "zero":

        values = values
        labels = labels_1
        parents = parents
        colors = colors
        ids = ids
        score = score

    # If the data frame has no negative scores, only emissions or the max contributor is small:
    elif ((inputs_df_pos_g.empty or inputs_df_pos_g["scaled_scores"][0] /
           (positives_1 + negatives_1 + np.exp(-30)) < 0.5) and
          (inputs_df_neg_g.empty or inputs_df_neg_g["scaled_scores"][0] /
           (positives_1 + negatives_1 + np.exp(-30)) < 0.5)):

        values = values
        labels = labels_1
        parents = parents
        colors = colors
        ids = ids
        score = score

    # If there is no exception at first level:
    else:
        level += 1  # Level 2

        # Process data for plotting
        (inputs_df_pos_2, inputs_df_pos_g_2, em_df_pos_2, em_df_pos_g_2,
         inputs_df_neg_2, inputs_df_neg_g_2, em_df_neg_2, em_df_neg_g_2
         ) = dp.create_nextlevel_dfs(inputs_df_pos, inputs_df_pos_g, inputs_df_neg,
                                     inputs_df_neg_g, method_index, positives_1, negatives_1)

        positives_2 = hf.sum_values(inputs_df_pos_g, em_df_pos_g, inputs_df_pos_g_2, em_df_pos_g_2)
        negatives_2 = hf.sum_values(inputs_df_neg_g, em_df_neg_g, inputs_df_neg_g_2, em_df_neg_g_2)

        plot_type = hf.plot_type_definition(inputs_df_pos_g_2, em_df_pos_g_2, inputs_df_neg_g_2, em_df_neg_g_2)

        if plot_type == "pos":

            (labels_2, labels, ids, parents, values, colors
             ) = append_nextlevel_lists(inputs_df_pos_g, inputs_df_pos_g_2, em_df_pos_g_2,
                                        inputs_df_neg_g_2, em_df_neg_g_2,
                                        values, labels_1, parents, colors, level,
                                        positives_1, negatives_1)
            second_labels = labels.copy()

        else:
            (labels_2, labels, ids, parents, values, colors
             ) = append_nextlevel_lists(inputs_df_neg_g, inputs_df_neg_g_2, em_df_neg_g_2,
                                        inputs_df_pos_g_2, em_df_pos_g_2,
                                        values, labels_1, parents, colors, level,
                                        positives_1, negatives_1)
            second_labels = labels.copy()

        # If the data frame has only emissions or a small max contributor:
        if ((inputs_df_pos_g_2.empty or inputs_df_pos_g_2["scaled_scores"][0] /
             (positives_2 + negatives_2 + np.exp(-30)) < 0.5) and
                (inputs_df_neg_g_2.empty or inputs_df_neg_g_2["scaled_scores"][0] /
                 (positives_2 + negatives_2 + np.exp(-30)) < 0.5)):

            values = values
            labels = labels
            parents = parents
            colors = colors
            ids = ids
            score = score

        # If there is no exception at second level:
        else:
            level += 1  # Level 3

            # Process data for plotting
            (inputs_df_pos_3, inputs_df_pos_g_3, em_df_pos_3, em_df_pos_g_3,
             inputs_df_neg_3, inputs_df_neg_g_3, em_df_neg_3, em_df_neg_g_3,
             ) = dp.create_nextlevel_dfs(inputs_df_pos_2, inputs_df_pos_g_2, inputs_df_neg_2,
                                         inputs_df_neg_g_2, method_index, positives_2, negatives_2)

            positives_3 = hf.sum_values(inputs_df_pos_g, em_df_pos_g, inputs_df_pos_g_2, em_df_pos_g_2,
                                        inputs_df_pos_g_3, em_df_pos_g_3)
            negatives_3 = hf.sum_values(inputs_df_neg_g, em_df_neg_g, inputs_df_neg_g_2, em_df_neg_g_2,
                                        inputs_df_neg_g_3, em_df_neg_g_3)

            plot_type = hf.plot_type_definition(inputs_df_pos_g_3, em_df_pos_g_3, inputs_df_neg_g_3, em_df_neg_g_3)

            if plot_type == "pos":
                labels_3, labels, ids, parents, values, colors = append_nextlevel_lists(inputs_df_pos_g_2,
                                                                                        inputs_df_pos_g_3,
                                                                                        em_df_pos_g_3,
                                                                                        inputs_df_neg_g_3,
                                                                                        em_df_neg_g_3,
                                                                                        values, labels_2, parents,
                                                                                        colors,
                                                                                        level, positives_2, negatives_2,
                                                                                        labels_1, first_labels)
                third_labels = labels.copy()

            else:
                labels_3, labels, ids, parents, values, colors = append_nextlevel_lists(inputs_df_neg_g_2,
                                                                                        inputs_df_neg_g_3,
                                                                                        em_df_neg_g_3,
                                                                                        inputs_df_pos_g_3,
                                                                                        em_df_pos_g_3,
                                                                                        values, labels_2, parents,
                                                                                        colors,
                                                                                        level, positives_2, negatives_2,
                                                                                        labels_1, first_labels)
                third_labels = labels.copy()

            # If only emissions or small max contributor:
            if ((inputs_df_pos_g_3.empty or inputs_df_pos_g_3["scaled_scores"][0] /
                 (positives_3 + negatives_3 + np.exp(-30)) < 0.5) and
                    (inputs_df_neg_g_3.empty or inputs_df_neg_g_3["scaled_scores"][0] /
                     (positives_3 + negatives_3 + np.exp(-30)) < 0.5)):

                values = values
                labels = labels
                parents = parents
                colors = colors
                ids = ids
                score = score

            else:
                level += 1  # Level 4

                # Process data for plotting
                (inputs_df_pos_4, inputs_df_pos_g_4, em_df_pos_4, em_df_pos_g_4,
                 inputs_df_neg_4, inputs_df_neg_g_4, em_df_neg_4, em_df_neg_g_4,
                 ) = dp.create_nextlevel_dfs(inputs_df_pos_3, inputs_df_pos_g_3, inputs_df_neg_3,
                                             inputs_df_neg_g_3, method_index, positives_3, negatives_3)

                positives_4 = hf.sum_values(inputs_df_pos_g, em_df_pos_g, inputs_df_pos_g_2, em_df_pos_g_2,
                                            inputs_df_pos_g_3, em_df_pos_g_3, inputs_df_pos_g_4, em_df_pos_g_4)
                negatives_4 = hf.sum_values(inputs_df_neg_g, em_df_neg_g, inputs_df_neg_g_2, em_df_neg_g_2,
                                            inputs_df_neg_g_3, em_df_neg_g_3, inputs_df_neg_g_4, em_df_neg_g_4)

                plot_type = hf.plot_type_definition(inputs_df_pos_g_4, em_df_pos_g_4,
                                                    inputs_df_neg_g_4, em_df_neg_g_4)

                if plot_type == "pos":
                    (labels_4, labels, ids, parents, values, colors
                     ) = append_nextlevel_lists(inputs_df_pos_g_3, inputs_df_pos_g_4, em_df_pos_g_4,
                                                inputs_df_neg_g_4, em_df_neg_g_4,
                                                values, labels_3, parents, colors,
                                                level, positives_3, negatives_3,
                                                labels_1 + labels_2, first_labels, second_labels)

                else:
                    (labels_4, labels, ids, parents, values, colors
                     ) = append_nextlevel_lists(inputs_df_neg_g_3, inputs_df_neg_g_4, em_df_neg_g_4,
                                                inputs_df_pos_g_4, em_df_pos_g_4,
                                                values, labels_3, parents, colors,
                                                level, positives_3, negatives_3,
                                                labels_1 + labels_2, first_labels, second_labels)

                    # If only emissions or small max contributor:
                if ((inputs_df_pos_g_4.empty or inputs_df_pos_g_4["scaled_scores"][0] /
                     (positives_4 + negatives_4 + np.exp(-30)) < 0.5) and
                        (inputs_df_neg_g_4.empty or inputs_df_neg_g_4["scaled_scores"][0] /
                         (positives_4 + negatives_4 + np.exp(-30)) < 0.5)):

                    values = values
                    labels = labels
                    parents = parents
                    colors = colors
                    ids = ids
                    score = score

                else:
                    level += 1  # Level 5

                    # Process data for plotting
                    (inputs_df_pos_5, inputs_df_pos_g_5, em_df_pos_5, em_df_pos_g_5,
                     inputs_df_neg_5, inputs_df_neg_g_5, em_df_neg_5, em_df_neg_g_5,
                     ) = dp.create_nextlevel_dfs(inputs_df_pos_4, inputs_df_pos_g_4, inputs_df_neg_4,
                                                 inputs_df_neg_g_4, method_index, positives_4, negatives_4)

                    positives_5 = hf.sum_values(inputs_df_pos_g, em_df_pos_g, inputs_df_pos_g_2, em_df_pos_g_2,
                                                inputs_df_pos_g_3, em_df_pos_g_3, inputs_df_pos_g_4, em_df_pos_g_4,
                                                inputs_df_pos_g_5, em_df_pos_g_5)
                    negatives_5 = hf.sum_values(inputs_df_neg_g, em_df_neg_g, inputs_df_neg_g_2, em_df_neg_g_2,
                                                inputs_df_neg_g_3, em_df_neg_g_3, inputs_df_neg_g_4, em_df_neg_g_4,
                                                inputs_df_neg_g_5, em_df_neg_g_5)

                    plot_type = hf.plot_type_definition(inputs_df_pos_g_5, em_df_pos_g_5,
                                                        inputs_df_neg_g_5, em_df_neg_g_5)

                    if plot_type == "pos":
                        (labels_5, labels, ids, parents, values, colors
                         ) = append_nextlevel_lists(inputs_df_pos_g_4, inputs_df_pos_g_5, em_df_pos_g_5,
                                                    inputs_df_neg_g_5, em_df_neg_g_5,
                                                    values, labels_4, parents, colors, level,
                                                    positives_4, negatives_4, labels_1 + labels_2 + labels_3,
                                                    first_labels, second_labels, third_labels)

                    else:
                        (labels_5, labels, ids, parents, values, colors
                         ) = append_nextlevel_lists(inputs_df_neg_g_4, inputs_df_neg_g_5, em_df_neg_g_5,
                                                    inputs_df_pos_g_5, em_df_pos_g_5,
                                                    values, labels_4, parents, colors, level,
                                                    positives_4, negatives_4, labels_1 + labels_2 + labels_3,
                                                    first_labels, second_labels, third_labels)

                    # If only emissions or small max contributor:
                    if ((inputs_df_pos_g_5.empty or inputs_df_pos_g_5["scaled_scores"][0] /
                         (positives_5 + negatives_5 + np.exp(-30)) < 0.6) and
                            (inputs_df_neg_g_5.empty or inputs_df_neg_g_5["scaled_scores"][0] /
                             (positives_5 + negatives_5 + np.exp(-30)) < 0.6)):

                        values = values
                        labels = labels
                        parents = parents
                        colors = colors
                        ids = ids
                        score = score

                    else:
                        level += 1  # Level 6

                        values = values
                        labels = labels
                        parents = parents
                        colors = colors
                        ids = ids
                        score = score

    return labels, ids, parents, values, colors, level, score, plot_type, labels_5
