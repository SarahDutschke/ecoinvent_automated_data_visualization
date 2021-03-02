import pandas as pd
from plotly import graph_objects as go
import plotly.io as pio
import os
from xlwt import Workbook
from datetime import date
import time
import math
from random import sample

import data_loading as dl
import data_processing as dp
import helper_functions as hf
import list_preparation as lp


def create_barplots(system_model, prod_list, n, method_index_list, save_fig=False, show_fig=False, verbose=True):
    """
    This function creates bar plots for several products based on the lists created before
    (create_dfs_barplots function), optionally saves them as png and/or shows them and logs the progress.

    Required arguments:
    - system_model: string, the name of the system model to be used.
        Possible options are: "cutoff", "apos", "consequential"
    - prod_list: list of int, list of indices of the product to plot from the ie_index matrix, e.g. 12759
    - method_index_list: list of int, list of indices of the LCIA method from the LCIA_index matrix
        The most common ones are: [222, 485, 541] (or 540 in consequential).

    Optional arguments:
    - save_fig: bool, if True, figures are saved to the defined folder. Default is True.
    - show_fig: bool, if True, figures are shown in a separate browser window. Default is False.

    Returns:
    - figures that can be shown in a browser window, saved to a folder or both.
    - an excel file which logs the progress of the plotting
    """
    # Settings for plot size, annotation locations:
    font_type = dl.font_type
    hues_barplots = dl.hues_barplots
    white_orig = dl.white_orig
    black_orig = dl.black_orig
    grey3_orig = dl.grey3_orig

    f_width = 500
    f_height = 400
    margin_l = 130
    margin_r = 10
    margin_t = 80
    margin_b = 80
    t_size = 18
    y_size = 14
    an_width = 152
    x_sp_diff1 = -0.89
    x_sp_diff2 = -0.67
    x_sp_start = 0.121
    y_space1 = -0.22
    y_space2 = -0.31

    # Set up the logging / plots folder
    if not os.path.exists("../logs"):
        os.mkdir("../logs")
    if not os.path.exists("../plots"):
        os.mkdir("../plots")
    # Set up logging
    it = 1
    start_time = time.time()
    today = date.today()

    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')
    sheet1.write(0, 0, "number")
    sheet1.write(0, 1, "prod_index")
    sheet1.write(0, 2, "method_index_list")
    sheet1.write(0, 3, "system_model")
    sheet1.write(0, 4, "plot_type_1")
    sheet1.write(0, 5, "plot_type_2")
    sheet1.write(0, 6, "fig_name")
    sheet1.write(0, 7, "time")
    sheet1.write(0, 8, "title_name")

    # Import DF per product index:
    for prod_index in prod_list:
        grouped_sorted, chart_type_1, chart_type_2 = dp.create_dfs_barplots(prod_index, method_index_list)
        fig_name = f"barplot_s{system_model}_p{prod_index}_m{method_index_list}.png"

        # split title into 1,2,3 lines depending on the total length
        ie_index = dl.ie_index
        title_simple = ["Main impact sources by method for '" + str(
            ie_index.iloc[grouped_sorted["ref_prod"][0]]['activityName']) + " (" + str(
            ie_index.iloc[grouped_sorted["ref_prod"][0]]['geography']) + ")'"]
        title_len = len(title_simple[0].split(' '))
        title_split2 = hf.split_method_name(title_len // 2, title_simple)
        title_split3 = hf.split_method_name(title_len // 3, title_simple)
        if title_len > 12:
            title_name = "<b>" + title_split3[0] + "</b>"
            title_height = 0.95
        elif title_len > 4:
            title_name = "<b>" + title_split2[0] + "</b>"
            title_height = 0.93
        else:
            title_name = "<b>" + title_simple[0] + "</b>"
            title_height = 0.93

        # Create y_data arrays, split method name after n_words
        lcia_df = dl.lcia_df
        create_y_data_array = []
        for meth in method_index_list:
            create_y_data = lcia_df.iloc[:, meth].name
            create_y_data_array.append(create_y_data)
        y_data_w_breaks = hf.split_method_name(n, create_y_data_array)
        y_data = y_data_w_breaks

        # Check for empty, semi-empty and zero score data sets and logs them:
        list_of_sums = []
        for meth in method_index_list:
            list_of_sums.append(grouped_sorted[str(meth) + '_impact_abs'].sum())
        if all(list_of_sums) == 0:
            list_of_sums_fil = len([sum_meth for sum_meth in list_of_sums if sum_meth == 0])
            if len(list_of_sums) > 1:
                if not len([sum_meth for sum_meth in list_of_sums if sum_meth == 0]) & list_of_sums_fil > 2:
                    chart_type_1 = '3 - semi-empty'
                else:
                    if math.isnan(grouped_sorted.row[0]):
                        chart_type_1 = '5 - no data'
                    else:
                        chart_type_1 = '4 - zero score'
            else:
                chart_type_1 = 'check'

        # For empty data sets, plot empty plot
        if math.isnan(grouped_sorted.row[0]) | any(list_of_sums) == 0:
            fig = go.Figure()
            fig.update_layout(
                xaxis=dict(showgrid=False, showline=True, showticklabels=False, zeroline=False, domain=[0.15, 1]),
                yaxis=dict(visible=True, showgrid=False, showline=True, showticklabels=False, zeroline=True, ),
                autosize=False, width=f_width, height=f_height, barmode='relative', paper_bgcolor=white_orig,
                plot_bgcolor=white_orig, margin=dict(l=margin_l, r=margin_r, t=margin_t, b=margin_b),
                showlegend=False,
                title={'text': title_name,
                       'y': title_height, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
                       'font': dict(family=font_type, size=t_size, color=black_orig)})
            annotations = []
            annotations.append({'y': 0.5, 'x': 0.9, 'xref': 'paper', 'yref': 'paper',
                                "text": '<i>This product has no impact scores</i>', "width": 250, "showarrow": False,
                                "font": {"family": font_type, "size": 14, "color": black_orig}})
            for yd in y_data:
                fig.add_trace(go.Bar(y=[yd], orientation='h'))
                annotations.append(dict(xref='paper', yref='y', x=0.14, y=yd,
                                        xanchor='right', text=str(yd),
                                        font=dict(family=font_type, size=y_size, color=black_orig),
                                        showarrow=False, align='right'))
            fig.update_layout(annotations=annotations)

            # Save plot as png if selected
            if save_fig:
                fig.write_image(f"../plots/" + str(fig_name))

            # Collect data points required for logging
            sheet1.write(it, 0, it)
            sheet1.write(it, 1, int(prod_index))
            sheet1.write(it, 2, str(method_index_list))
            sheet1.write(it, 3, system_model)
            sheet1.write(it, 4, chart_type_1)
            sheet1.write(it, 5, chart_type_2)
            sheet1.write(it, 6, fig_name)
            sheet1.write(it, 7, time.strftime('%H:%M:%S', time.localtime()))
            sheet1.write(it, 8, title_name)
            if verbose:
                if it % 500 == 0:
                    print(f"{it} barplots done")
            it += 1

            # Show plot in browser if selected
            if show_fig:
                pio.renderers.default = 'browser'
                fig.show()
            else:
                pass

        # Plot bar chart for normal, rescaled, semi-empty data sets:
        else:
            # List 'flow compartments', needed for annotations later
            top_label_list = []
            [top_label_list.append(cat) for cat in grouped_sorted['impact_cat'].values]

            # Chose color scale for the 'flow compartments'
            hues_barplots = hues_barplots

            # Import x_data form DF from create_dfs_barplots function and round data
            create_x_data_array = []
            for meth in method_index_list:
                create_x_data = grouped_sorted[str(meth) + '_scaled'].tolist()
                create_x_data_round = [int(val) for val in create_x_data]
                create_x_data_array.append(create_x_data_round)
            x_data = create_x_data_array

            # Create and format figure, adding one trace per method
            fig = go.Figure()
            for i in range(0, len(x_data[0])):
                for xd, yd in zip(x_data, y_data):
                    fig.add_trace(go.Bar(x=[xd[i]], y=[yd], orientation='h', width=0.8,
                                         marker=dict(color=hues_barplots[i],
                                                     line=dict(color=hues_barplots[i], width=0.5))))
            fig.update_layout(
                xaxis=dict(showgrid=False, showline=True, showticklabels=False, zeroline=False, domain=[0.15, 1]),
                yaxis=dict(visible=True, showgrid=False, showline=True, showticklabels=False, zeroline=True),
                autosize=False, width=f_width, height=f_height, barmode='relative', paper_bgcolor=white_orig,
                plot_bgcolor=white_orig, margin=dict(l=margin_l, r=margin_r, t=margin_t, b=margin_b),
                showlegend=False,
                title={'text': title_name,
                       'y': title_height, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
                       'font': dict(family=font_type, size=t_size, color=black_orig)},
                # Add vertical line (axis) to separate positive and negative values
                shapes=[{"type": "line", "xref": "x", "yref": "paper",
                         "x0": 0, "y0": 0, "x1": 0, "y1": 1,
                         "line": dict(color=grey3_orig, width=3, )}])

            # Add labels and %-values
            annotations = []
            for ix_l, (yd, xd) in enumerate(zip(y_data, x_data)):
                # Labeling the y-axis
                annotations.append(dict(xref='paper', yref='y', x=0.14, y=yd,
                                        xanchor='right', text=str(yd),
                                        font=dict(family=font_type, size=y_size, color=black_orig),
                                        showarrow=False, align='right'))

                # Comment annotation for 'semi-empty' plots: (x=0.14 for overlapping h-line, otherwise x=0.18)
                if list_of_sums[ix_l] == 0:
                    annotations.append(dict(xref='paper', yref='y', x=0.18, y=yd, bgcolor=white_orig,
                                            width=300, height=80,
                                            text="<i>no impacts based on this method</i>",
                                            font=dict(family=font_type, size=y_size, color=black_orig),
                                            showarrow=False, align='center'))
                else:
                    pass

                # Dividing into positive and negative datasets (x-axis), sorting, chosing top_n values
                pos_xd = [pos for pos in xd if (pos >= 5)]
                neg_xd = [neg for neg in xd if (neg < -5)]
                if len(pos_xd + neg_xd) <= 2:
                    pos_xd = [pos for pos in xd if (pos >= 10)]
                    neg_xd = [neg for neg in xd if (neg < -10)]
                else:
                    pass
                xd_pos_sor = sorted([x for x in pos_xd], reverse=True)
                xd_neg_sor = sorted([x for x in neg_xd])
                # Showing only the top n_values depending on the available space
                top_4_pos = xd_pos_sor[:4]
                top_3_pos = xd_pos_sor[:3]
                top_2_pos = xd_pos_sor[:2]
                top_4_neg = xd_neg_sor[:4]
                top_3_neg = xd_neg_sor[:3]
                top_2_neg = xd_neg_sor[:2]
                # Create DF for isin_function for top_n values
                pos_xd_df = pd.DataFrame(pos_xd)
                neg_xd_df = pd.DataFrame(neg_xd)
                # Preparation for available space
                sum_pos = sum(pos_xd)
                count_pos = sum(1 for item in pos_xd if item > 0)
                sum_neg = sum(neg_xd)
                count_neg = sum(1 for item in neg_xd if item < 0)
                # Set threshold for number of %-labels per space
                threshold1 = 45
                threshold2 = 40

                # Chose %-labels to be shown based on available space
                # For positive values
                if count_pos == 0:
                    top_pos_val = []
                else:
                    if sum_pos / count_pos > threshold1:
                        top_pos_val = top_4_pos
                    elif sum_pos / count_pos > threshold2:
                        top_pos_val = top_3_pos
                    else:
                        top_pos_val = top_2_pos
                # For negative values
                if count_neg == 0:
                    top_neg_val = []
                else:
                    if -sum_neg / count_neg > threshold1:
                        top_neg_val = top_4_neg
                    elif -sum_neg / count_neg > threshold2:
                        top_neg_val = top_3_neg
                    else:
                        top_neg_val = top_2_neg

                # Check for empty (positive / negative) lists
                if not any(top_pos_val):
                    check_pos = []
                else:
                    check_pos = pos_xd_df[0].isin(top_pos_val)
                if not any(top_neg_val):
                    check_neg = []
                else:
                    check_neg = neg_xd_df[0].isin(top_neg_val)

                # Set labeling start to zero
                space_pos = 0
                space_neg = 0

                # Label top %-values for bars (x_axis) for positive values
                for a0 in range(0, len(pos_xd)):
                    # don't show if 0%
                    if pos_xd[a0] == 0:
                        pass
                    else:
                        if check_pos[a0] & any(check_pos.to_list()):
                            annotations.append(dict(xref='x', yref='y', x=space_pos + (pos_xd[a0] / 2), y=yd,
                                                    text=str(pos_xd[a0]) + '%',
                                                    # texttemplate = "%{pos_xd[a0]:.%}",
                                                    font=dict(family=font_type,
                                                              size=y_size, color=white_orig), showarrow=False))
                            space_pos += pos_xd[a0]
                        else:
                            space_pos += pos_xd[a0]
                # Label top %-values for bars (x_axis) for negative values
                for b0 in range(0, len(neg_xd)):
                    if check_neg[b0] & any(check_neg.to_list()):
                        annotations.append(dict(xref='x', yref='y', x=space_neg + (neg_xd[b0] / 2), y=yd,
                                                text=str(neg_xd[b0]) + '%', font=dict(family=font_type,
                                                                                      size=y_size, color=white_orig),
                                                showarrow=False))
                        space_neg += neg_xd[b0]
                    else:
                        space_neg += neg_xd[b0]

            # Count number of labels and divided into 1st and 2nd line 'flow compartment' labels
            top_label_ix1 = len(top_label_list) // 2
            top_label_list1 = top_label_list[0:top_label_ix1]
            top_label_list2 = top_label_list[top_label_ix1:]
            # Loop for 1st line 'flow compartment' labels
            x_space1 = x_sp_start
            for ix, (cat1) in enumerate(top_label_list1):
                annotations.append(
                    {'y': y_space1, 'x': x_space1, 'xref': 'paper', 'yref': 'paper',
                     "text": str(cat1), "bgcolor": hues_barplots[ix], "width": an_width, "showarrow": False,
                     "font": {"family": font_type, "size": y_size, "color": white_orig}})
                x_space1 -= x_sp_diff1
            # Loop for 2nd line 'flow compartment' labels
            # in case of 3 labels:
            if len(top_label_list2) > 2:
                x_space2 = -0.33
                for ix, (cat2) in enumerate(top_label_list2):
                    annotations.append(
                        {'y': y_space2, 'x': x_space2, 'xref': 'paper', 'yref': 'paper',
                         "text": str(cat2), "bgcolor": hues_barplots[ix + top_label_ix1], "width": an_width,
                         "showarrow": False,
                         "font": {"family": font_type, "size": y_size, "color": white_orig}})
                    x_space2 -= x_sp_diff2
            else:
                x_space2 = x_sp_start
                for ix, (cat2) in enumerate(top_label_list2):
                    annotations.append({'y': y_space2, 'x': x_space2, 'xref': 'paper', 'yref': 'paper',
                                        "text": str(cat2), "bgcolor": hues_barplots[ix + top_label_ix1],
                                        "width": an_width,
                                        "showarrow": False,
                                        "font": {"family": font_type, "size": y_size, "color": white_orig}})
                    x_space2 -= x_sp_diff1

            # X_axis title annotation:
            annotations.append(
                {'y': -0.1, 'x': 0.55, 'xref': 'paper', 'yref': 'paper',
                 "text": "Flow Compartments", "showarrow": False,
                 "font": {"family": font_type, "size": y_size, "color": black_orig}})

            fig.update_layout(annotations=annotations)

            # Save plot as png if selected
            if save_fig:
                fig.write_image(f"../plots/" + str(fig_name))

            # Collect data points required for logging
            sheet1.write(it, 0, it)
            sheet1.write(it, 1, int(prod_index))
            sheet1.write(it, 2, str(method_index_list))
            sheet1.write(it, 3, system_model)
            sheet1.write(it, 4, chart_type_1)
            sheet1.write(it, 5, chart_type_2)
            sheet1.write(it, 6, fig_name)
            sheet1.write(it, 7, time.strftime('%H:%M:%S', time.localtime()))
            sheet1.write(it, 8, title_name)
            if verbose:
                if it % 500 == 0:
                    print(f"{it} barplots done")
            it += 1

            # Show plot in browser if selected
            if show_fig:
                pio.renderers.default = 'browser'
                fig.show()
            else:
                pass

    wb.save(f"../logs/barplots_{system_model}_{today.strftime('%d-%m-%Y')}_\
{time.strftime('%H:%M:%S', time.localtime())}.xls")

    # Print time required for running the script
    if verbose:
        print("--- {0} seconds --- for {1} datasets".format(time.time() - start_time, len(prod_list)))


def create_treemaps(system_model, product_index_list, method_index_list, save_fig=True, show_fig=False, verbose=True):
    """
    This function plots treemaps based on the lists created before and logs the progress.

    Required arguments:
    - product_index_list: list of int, contains indices of the products to be plotted
    - method_index_list: list of int, contains indices of LCIA methods to be used; most common are: 222, 485, 541
    (or 540 for IPCC in consequential)
    - system_model: string, one of "cutoff", "apos", "consequential"

    Optional arguments:
    - save_fig: bool, if True, figures are saved to the defined folder. Default is True.
    - show_fig: bool, if True, figures are shown in a separate browser window. Default is False.

    Returns:
    - figures that can be shown in a browser window, saved to a folder or both.
    - an excel file which logs the progress of the plotting
    """
    hues_treemaps = dl.hues_treemaps

    # Set up the logging
    i = 1
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')
    sheet1.write(0, 0, "number")
    sheet1.write(0, 1, "prod_index")
    sheet1.write(0, 2, "method_index")
    sheet1.write(0, 3, "system_model")
    sheet1.write(0, 4, "level")
    sheet1.write(0, 5, "plot_type")
    sheet1.write(0, 6, "error_message")
    sheet1.write(0, 7, "time")

    # Plot and log
    for prod_index in product_index_list:
        for method_index in method_index_list:
            try:
                (labels, ids, parents, values, colors, level, score, plot_type, labels_5
                 ) = lp.sort_datasets(prod_index, method_index)

                annotations = [{"x": -0.0035, "y": 0.995, "xref": 'x domain', "yref": 'y domain',
                                "text": 'For this assessment method there are no impacts or credits. \
Therefore no plot is rendered.',
                                "font": {"family": dl.font_type, "size": 16, "color": 'black'},
                                "showarrow": False},
                               {"x": 0.01, "y": -0.052, "xref": 'x domain', "yref": 'y domain',
                                "text": 'Impact from inputs',
                                "font": {"family": dl.font_type, "size": 12, "color": 'white'},
                                "bgcolor": hues_treemaps[0],
                                "width": 135,
                                "height": 13,
                                "showarrow": False},
                               {"x": 0.18, "y": -0.052, "xref": 'x domain', "yref": 'y domain',
                                "text": 'Impact from emissions',
                                "font": {"family": dl.font_type, "size": 12, "color": 'black'},
                                "bgcolor": hues_treemaps[1],
                                "width": 135,
                                "height": 13,
                                "showarrow": False},
                               {"x": 0.433, "y": -0.052, "xref": 'x domain', "yref": 'y domain',
                                "text": 'Credits from inputs',
                                "font": {"family": dl.font_type, "size": 12, "color": 'white'},
                                "bgcolor": hues_treemaps[2],
                                "width": 135,
                                "height": 13,
                                "showarrow": False},
                               {"x": 0.603, "y": -0.052, "xref": 'x domain', "yref": 'y domain',
                                "text": 'Credits from emissions',
                                "font": {"family": dl.font_type, "size": 12, "color": 'black'},
                                "bgcolor": hues_treemaps[3],
                                "width": 135,
                                "height": 13,
                                "showarrow": False},
                               {"x": 0.01, "y": -0.1, "xref": 'x domain', "yref": 'y domain',
                                "text": 'For plots containing credits the impact score equals the impact minus \
the credits.',
                                "font": {"family": dl.font_type, "size": 12, "color": 'black'},
                                "showarrow": False},
                               {"x": 0.01, "y": -0.18, "xref": 'x domain', "yref": 'y domain', "align": "left",
                                "text": f'Plotting of the production chain may not have reached optimum depth due \
to space constraints. For further information on the maximum contributor<br>check the \
following dataset: {labels_5[0].replace("<br>", " ")}.',
                                "font": {"family": dl.font_type, "size": 12, "color": 'black'},
                                "showarrow": False},
                               ]

                if plot_type == "zero":
                    annot = annotations[0:1]
                elif level == 6:
                    annot = annotations[1:7]
                else:
                    annot = annotations[1:6]

                fig = go.Figure(go.Treemap(
                    labels=labels,
                    ids=ids,
                    parents=parents,
                    values=values,
                    marker_colors=colors,
                    marker={"depthfade": True},
                    branchvalues="total",
                    textfont={"family": dl.font_type, "size": 16},
                    texttemplate="%{label}<br>%{value:.2e} | %{percentRoot}",
                    outsidetextfont={"color": "black"},
                    root={"color": "rgb(226, 226, 226)"},
                    tiling={"packing": "squarify", "squarifyratio": 1, "pad": 0},
                    marker_pad={"t": 25, "l": 4, "r": 4, "b": 4},
                    marker_line={"color": "white", "width": 1}
                    ))

                LCIA_index = dl.LCIA_index
                fig.update_layout(uniformtext={"minsize": 16, "mode": 'hide'},
                                  title={
                                      'text': f"LCIA method: {LCIA_index.iloc[method_index]['method']}, \
{LCIA_index.iloc[method_index]['category']}, {LCIA_index.iloc[method_index]['indicator']} | Score: {score:,.2e}",
                                      'y': 0.88,
                                      'x': 0.08,
                                      'xanchor': 'left',
                                      'yanchor': 'top',
                                      "font": {"color": "black", "family": dl.font_type, "size": 18}},
                                  autosize=False,
                                  width=1000,
                                  height=600,
                                  annotations=annot
                                  )
                error_message = "None"

                if save_fig:
                    # create image folder
                    if not os.path.exists("../plots"):
                        os.mkdir("../plots")

                    fig.write_image(f"../plots/treemap_{system_model}_p{prod_index}_m{method_index}.png")

                if show_fig:
                    pio.renderers.default = 'browser'
                    fig.show()

            except Exception as e:
                error_message = str(e)
                level = 0
                plot_type = "error"

            sheet1.write(i, 0, i)
            sheet1.write(i, 1, int(prod_index))
            sheet1.write(i, 2, method_index)
            sheet1.write(i, 3, system_model)
            sheet1.write(i, 4, level)
            sheet1.write(i, 5, plot_type)
            sheet1.write(i, 6, error_message)
            sheet1.write(i, 7, time.strftime("%H:%M:%S", time.localtime()))
            if verbose:
                if i % 500 == 0:
                    print(f"{i} treemaps done")
            i = i + 1

    if not os.path.exists("../logs"):
        os.mkdir("../logs")

    today = date.today()
    wb.save(f"../logs/treemaps_{system_model}_{today.strftime('%d-%m-%Y')}_\
{time.strftime('%H:%M:%S', time.localtime())}.xls")
    if verbose:
        print(f"Plotting of treemaps for {len(product_index_list)} datasets is complete.")


def pdf_plotting(system_model, method_index_list, sample_size=None, product_index_list=None,
                 save_fig=True, show_fig=False, verbose=True):
    """
    This function combines all the previous functions to select the system model
    and plot barplots and treemaps with one command.

    Required arguments:
    - system_model: string, one of "cutoff", "apos", "consequential"
    - method_index_list: list of int, contains indices of the methods to be used

    Optional arguments:
    - sample_size: int, if specified, the function plots randomly sampled datasets.
    - product_index_list: list of int, contains indices of the products to be plotted
    - save_fig: bool, if True, figures are saved to the defined folder. Default is True.
    - show_fig: bool, if True, figures are shown in a separate browser window. Default is False.
    - verbose: bool, if True, print statements on the progress of the plotting are shown. Default is True.

    If products are specified, this selection overrides the sample size.
    If neither of these arguments is specified, all the datasets for the specific
        system model are plotted.

    Returns:
    - barplots and treemaps that can be shown in a browser window, saved to a folder or both.
    - two excel files which log the progress of the plotting of barplots and treemaps
    """
    try:
        dl.select_system_model(system_model, dl.A_public_cutoff, dl.A_public_apos, dl.A_public_consequential,
                               dl.A_public_cor_cutoff, dl.A_public_cor_apos, dl.A_public_cor_consequential,
                               dl.B_public_cutoff, dl.B_public_apos, dl.B_public_consequential,
                               dl.C_public_cutoff, dl.C_public_apos, dl.C_public_consequential,
                               dl.ee_index_cutoff, dl.ee_index_apos, dl.ee_index_consequential,
                               dl.ie_index_cutoff, dl.ie_index_apos, dl.ie_index_consequential,
                               dl.LCIA_index_cutoff, dl.LCIA_index_apos, dl.LCIA_index_consequential,
                               dl.c_array_cutoff, dl.c_array_apos, dl.c_array_consequential,
                               dl.lcia_cutoff, dl.lcia_apos, dl.lcia_consequential,
                               dl.lcia_df_cutoff, dl.lcia_df_apos, dl.lcia_df_consequential)

        ie_index = dl.ie_index

        if product_index_list is None:
            if sample_size is not None:
                product_index_list = sample(list(ie_index.index.values), sample_size)
            else:
                product_index_list = list(ie_index.index.values)

        # Create the plots
        l_break = dl.l_break
        if verbose:
            print(f"Creating barplots for {len(product_index_list)} datasets")
        create_barplots(system_model, product_index_list, l_break, method_index_list, save_fig, show_fig, verbose)
        if verbose:
            print(f"Creating treemaps for {len(product_index_list)} datasets in {len(method_index_list)} different methods")
        create_treemaps(system_model, product_index_list, method_index_list, save_fig, show_fig, verbose)

    except NameError:
        print(f"Error: '{system_model}' is not a valid system model name.")
        print("Please select one of the following: 'cutoff', 'apos', 'consequential'.")
