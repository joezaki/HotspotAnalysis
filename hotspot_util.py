import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def plotMeanData(
    agg_data,
    groupby,
    plot_var,
    datapoint_var='Filename',
    colors=["steelblue", "darkred"],
    plot_mode='bar',
    mean_line_color='black',
    marker_pattern_shape='',
    plot_datapoints=False,
    plot_datalines=False,
    y_range=None,
    y_title=None,
    plot_title=None,
    opacity=0.8,
    tick_angle=45,
    plot_width=350,
    plot_height=500,
    save_path=None,
    plot_scale=5
):
    """
    Parameters
    ==========
    agg_data : pandas dataframe
        aggregated pandas data frame where each mouse occupies one row
    groupby : str
        either 'ExpGroup' or 'Context' for what you'd like the data split up by
    plot_var : str
        column name to plot
    datapoint_var : str
        column name of individual datapoint variable. Default is 'Mouse'
    colors : list
        list of colors you would like used in plotting
    plot_mode : str
        one of 'bar' or 'point' where means are represented as bars or as points
    plot_datapoints, plot_datalines : boolean
        whether or not to plot individual datapoints, or individual datalines. Defaults are False.
    y_range : tuple
        tuple or min and max values of plot
    y_title : str
        y-axis title. Default is None.
    plot_title : str
        master title for the graph. Default is None.
    opacity : float
        opacity value for bars. Default is 0.8.
    tick_angle : int
        angle that text on x-axis is displayed at. Default is 45.
    plot_width, plot_height : int
        width and height of the entire plot. Defaults are 350 & 500, respectively.
    save_path : boolean
        an optional file path to save the plot. If save_path=None, plot will not be saved. Default is None.
    plot_scale : int
         how high of a resolution to save the plot as. Default is 5.
    """

    if plot_title == None:
        plot_title = groupby

    means = agg_data[[groupby, plot_var]].groupby(groupby).mean()[plot_var].sort_index()
    sems = agg_data[[groupby, plot_var]].groupby(groupby).sem()[plot_var].sort_index()
    names = means.index.values

    fig = go.Figure()
    if plot_mode == 'bar':
        fig.add_trace(
            go.Bar(
                x=names,
                y=means.values,
                error_y=dict(type="data", array=sems.values, visible=True),
                marker_color=colors,
                marker=dict(line=dict(width=1, color="black"), opacity=opacity),
                marker_pattern_shape=marker_pattern_shape
            )
        )
    elif (plot_mode == 'point') & (plot_datalines):
        fig.add_trace(
            go.Scatter(
                x=names,
                y=means.values,
                error_y=dict(type="data", array=sems.values, visible=True),
                mode='lines+markers',
                marker_color=colors,
                marker=dict(size=15, line=dict(width=1, color="black"), opacity=opacity),
                line=dict(color=mean_line_color, width=3)
            )
        )
    elif plot_mode == 'point':
        fig.add_trace(
            go.Scatter(
                x=names,
                y=means.values,
                error_y=dict(type="data", array=sems.values, visible=True),
                mode='markers',
                marker_color=colors,
                marker=dict(size=15, line=dict(width=1, color=mean_line_color), opacity=opacity),
            )
        )
    else:
        raise Exception("Invalid plot_mode. Must be one of 'bar' or 'point'.")
    if plot_datapoints:
        for sub in agg_data[datapoint_var].unique():
            sub_data = agg_data[agg_data[datapoint_var] == sub]
            fig.add_trace(
                go.Scatter(
                    x=sub_data[groupby].values,
                    y=sub_data[plot_var].values,
                    mode="markers",
                    marker=dict(color="black", opacity=0.4),
                    name=str(sub),
                )
            )
    if plot_datalines:
        for line in agg_data[datapoint_var].unique():
            line_data = agg_data[agg_data[datapoint_var] == line]
            line_data = line_data.iloc[line_data[groupby].argsort(),:]
            fig.add_trace(
                go.Scatter(
                    x=line_data[groupby].values,
                    y=line_data[plot_var].values,
                    mode="lines+markers",
                    line=dict(width=1),
                    marker=dict(color="black", opacity=0.4),
                    name=str(line),
                )
            )
    fig.update_layout(
        dragmode="pan",
        yaxis_title=y_title,
        font=dict(size=17),
        title_text=plot_title,
        autosize=False,
        width=plot_width,
        height=plot_height,
        template="simple_white",
        showlegend=False,
    )
    if tick_angle is not None:
        fig.update_xaxes(tickangle=tick_angle)
    fig.update_yaxes(range=y_range)
    if save_path is not None:
        if not os.path.exists(os.path.dirname(save_path)):
            os.mkdir(os.path.dirname(save_path))
        if save_path.split('.')[-1] != 'eps':
            fig.write_image(save_path, scale=plot_scale)
        else:
            fig.write_image(save_path, format=save_path.split('.')[-1])
    config = {
        'scrollZoom':True,
        'toImageButtonOptions': {
            'format': 'svg',
            'filename': 'custom_image',
            'height': plot_height,
            'width': plot_width,
            'scale':plot_scale
            }
            }
    fig.show(config=config)



def plotAcrossGroups(
    agg_data,
    groupby,
    separateby,
    plot_var,
    colors,
    title,
    datapoint_var="Filename",
    y_range=None,
    plot_mode='bar',
    mean_line_color='black',
    marker_pattern_shape='',
    plot_datapoints=False,
    plot_datalines=False,
    y_title=None,
    text_size=20,
    opacity=0.8,
    plot_width=600,
    plot_height=600,
    tick_angle=45,
    scale_y=True,
    h_spacing=0.2,
    save_path=None,
    plot_scale=5
):
    """
    Plot multiple bar plots (one for each unique type in 'separateby') with multiple bars on each plot (one bar for each unique type in 'groupby')
    """
    # Note that the separating variable must be of type pd.Categorical(ordered=True), such that its unique values can be sorted
    # This can be done by: agg_data[separateby] = pd.Categorical(agg_data[separateby], categories=['list','of','unique','values'], ordered=True)
    subplot_titles = agg_data[separateby].unique().sort_values()
    fig = make_subplots(
        cols=len(subplot_titles), subplot_titles=subplot_titles, horizontal_spacing=h_spacing, shared_yaxes=scale_y
    )
    for i, val in enumerate(agg_data[separateby].unique().sort_values()):
        sub_data = agg_data[agg_data[separateby] == val]
        means = sub_data[[groupby, plot_var]].groupby(groupby).mean()[plot_var].sort_index()
        sems = sub_data[[groupby, plot_var]].groupby(groupby).sem()[plot_var].sort_index()
        xlabels = means.index.values
        if plot_mode == 'bar':
            fig.add_trace(
                go.Bar(
                    x=xlabels,
                    y=means[xlabels].values,
                    error_y=dict(type="data", array=sems.values, visible=True),
                    marker_color=colors,
                    marker=dict(line=dict(width=1, color="black"), opacity=opacity),
                    marker_pattern_shape=marker_pattern_shape
                ),
                row=1,
                col=i + 1,
            )
        elif (plot_mode == 'point') & (plot_datalines):
            fig.add_trace(
                go.Scatter(
                    x=xlabels,
                    y=means[xlabels].values,
                    error_y=dict(type="data", array=sems.values, visible=True),
                    mode='lines+markers',
                    marker_color=colors,
                    marker=dict(size=15, line=dict(width=1, color="black"), opacity=opacity),
                    line=dict(color=mean_line_color, width=4)
                ),
                row=1,
                col=i + 1,
            )
        elif plot_mode == 'point':
            fig.add_trace(
                go.Scatter(
                    x=xlabels,
                    y=means[xlabels].values,
                    error_y=dict(type="data", array=sems.values, visible=True),
                    mode='markers',
                    marker_color=colors,
                    marker=dict(size=15, line=dict(width=1, color=mean_line_color), opacity=opacity)
                ),
                row=1,
                col=i + 1,
            )
        else:
            raise Exception("Invalid plot_mode. Must be one of 'bar' or 'point'.")
        if plot_datapoints:
            for point in sub_data[datapoint_var].unique():
                point_data = sub_data[sub_data[datapoint_var] == point]
                fig.add_trace(
                    go.Scattergl(
                        x=point_data[groupby].values,
                        y=point_data[plot_var].values,
                        mode="markers",
                        marker=dict(color="black", opacity=0.4),
                        name=str(point),
                    ),
                    row=1,
                    col=i + 1,
                )
        if plot_datalines:
            for line in sub_data[datapoint_var].unique():
                line_data = sub_data[sub_data[datapoint_var] == line]
                line_data = line_data.iloc[line_data[groupby].argsort(),:]
                fig.add_trace(
                    go.Scatter(
                        x=line_data[groupby].values,
                        y=line_data[plot_var].values,
                        mode="lines+markers",
                        line=dict(width=1),
                        marker=dict(color="black", opacity=0.4),
                        name=str(line),
                    ),
                    row=1,
                    col=i + 1,
                )
    fig.add_hline(y=0, row=1, col='all', line_width=1, opacity=1, line_color='black')
    fig.update_layout(
        dragmode="pan",
        yaxis_title=y_title,
        font=dict(size=text_size),
        title_text=title,
        autosize=False,
        width=plot_width,
        height=plot_height,
        template="simple_white",
        showlegend=False,
    )
    if tick_angle is not None:
        fig.update_xaxes(tickangle=tick_angle)
    if y_range is not None:
        fig.update_yaxes(range=y_range)
    if save_path is not None:
        if not os.path.exists(os.path.dirname(save_path)):
            os.mkdir(os.path.dirname(save_path))
        if save_path.split('.')[-1] != 'eps':
            fig.write_image(save_path, scale=plot_scale)
        else:
            fig.write_image(save_path, format=save_path.split('.')[-1])
    config = {
        'scrollZoom':True,
        'toImageButtonOptions': {
            'format': 'svg',
            'filename': 'custom_image',
            'height': plot_height,
            'width': plot_width,
            'scale':plot_scale
            }
            }
    fig.show(config=config)

