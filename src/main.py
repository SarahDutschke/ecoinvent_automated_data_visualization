import plotting_functions as pf

# If both product_index_list and sample_size are None, the plotting is done for the entire database.
system_model = "cutoff"
method_index_list = [485, 222, 541]
product_index_list = [1581, 1159, 13648, 307]
sample_size = 10

pf.pdf_plotting(system_model, method_index_list, sample_size, product_index_list=None,
                save_fig=True, show_fig=False, verbose=True)
