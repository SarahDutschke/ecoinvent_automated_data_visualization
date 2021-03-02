# Automated data visualization and reporting with ecoinvent

![](fertilizers_slider_3.7_2.jpg)

This repository documents the deliverables of a capstone project of Propulsion Academy's Data Science program, which were elaborated by Angela Niederberger and Sarah Dutschke in collaboration with ecoinvent. The information presented here is not approved for any kind of commercial use.

Project Team
-----------

[Sarah Dutschke](https://www.linkedin.com/in/sarah-dutschke/), 
[Angela Niederberger](https://www.linkedin.com/in/angela-niederberger/)

Supervisors
-----------

[Marie Bocher](linkedin.com/in/marie-bocher-8b6b5562), 
[Albin Plathottathil](https://www.linkedin.com/in/albin-plathottathil/), 
[Nitin Kumar](https://www.linkedin.com/in/drnitinkumar)

Partners
 -------
 [ecoinvent](https://www.ecoinvent.org/) is a not-for-profit association that provides the world’s most consistent and transparent life cycle inventory database to a wide range of companies, government organizations and universities.

[Propulsion Academy](https://propulsion.academy/) is a coding and data science academy offering a variety of full-time, part-time, and corporate programs to motivated learners looking to enhance their careers with technology.

Project description
-------------------
Organisations increasingly look to understand the end-to-end impact a product has on the environment. For this purpose, ecoinvent provides a comprehensive life cycle assessment database to thousands of companies such as Toyota, Lego and Procter & Gamble as well as government organisations and universities. Though the data sets are comprehensible on their own, the underlying calculations and methods used to estimate environmental impacts can be complex and overwhelming to understand for most people.

In this project, Angela Niederberger and Sarah Dutschke helped ecoinvent make their holistic reports more user friendly by adding data visualizations representing the impacts and network structure of production chains. The main challenges were to make those visualisations fit for about 60’000 diverse data sets in a uniform way, displaying only the most relevant information statically. The python script produced in this project will be integrated into ecoinvent’s automatic pdf generator, thereby reaching thousands of clients.

Project Milestones
-------------------
### Milestone 1
 Impact visualization: Improve the table showing impact score, by adding a chart that shows the most significant contributors ('flow compartments'). Use data calculated from our release script, provided as csv files. This chart should allow to identify which part of the supply chain is responsible for impact score on the commonly used impact assessment methods.


 ### Milestone 2
 Network structure visualization: Add a treemap plot for each method to show the main contributors (impacts and emissions). It should display as many levels as necessary until the main impact contributor is below 50%. However, the limit of levels to diplay is five, due to space constraints. The data was provided as csv files and individual scores are calculated in the scripts.
 
 ### Milestone 3
 Transform the exploratory analysis results from the previous milestones into a high quality documented code that can run on a large amount of datasets and integrate flawlessly into the existing release pipeline.
 
 Outcomes
 ---------
As the final outcome of the capstone project, we consolidated all of our code into a python module containing six different scripts. With the help of these, the bar plots and treemaps for the entire data base can be created with one command. The run time per system model (~20'000 data sets) is estimated to be around 10 hours (without the use of an external CPU).

A recording of the final presentation of these results can be accessed [here](https://drive.google.com/file/d/1Jh67n0SGt3aIAk883NEZUIKCw5ZzZ4Sh/view?usp=sharing) and the project was also covered in this [blog post](https://propulsion.academy/blog/data-science-abschlussprojekte-batch-13).

Requirements
------------
The libraries required to run this product are the following:
- numpy
- pandas
- plotly, version 4.14.3 or newer
- pypardiso
- scipy
- xlwt

Repository Structure
------------
    ├── README.md       <- top-level README file for anybody interested in this project
    ├── logs            <- new dir, created automatically, contains generated log for barplot and treemap generation
    ├── plots           <- new dir, created automatically, contains generated example plots in png format
    └── src             <- contains the following python scripts required for plotting
        ├── data_loading.py         <- Adjust general settings here (path, font_type, hues, etc.) and find script for data import 
        ├── data_processing.py      <- Script to preprocess data for both barplots and treemaps.
        ├── helper_functions.py     <- Script for auxiliary functions
        ├── list_preparation.py     <- Script for further data processing for treemaps.
        ├── main.py                 <- Main script to produce barplots and treemaps in png format while generating a log in excel/csv.
        └── plotting_functions.py   <- Script with subfunctions to plot barcharts and/or treemaps while generating a log in excel/csv.


Further information
------------
Explanation of different [system models](https://www.ecoinvent.org/database/system-models-in-ecoinvent-3/system-models-in-ecoinvent-3.html) 
[Example reports pdf] (https://www.ecoinvent.org/support/documents-and-files/example-datasets/example-datasets.html)
