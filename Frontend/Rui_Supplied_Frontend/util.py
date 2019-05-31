# if a file extension is not listed, the system will not upload the file
import pandas as pd
ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preview_csv(filename, rows):
	'''
	this function will return a JSON file
	containing the first 5 lines of a CSV file
	'''
	# read csv file
	df = pd.read_csv(filename)
	# this will return the total length of your CSV file
	total_len = len(df)
	csv_values = []
	# if length is less than 5
	if total_len < 5:
		csv_values = df.values.tolist()
	else:
		csv_values = df.head(n=rows).values.tolist()

	# grad column names
	col_names = df.columns.tolist()
	return col_names, csv_values

def threshold_process_method(filename, col_name, lower_threshold, upper_threshold):
	'''
	this function will process a csv file and find values that are more than
	upper threshold or less than lower threshold
	'''
	df = pd.read_csv(filename)
	df_upper = df[df[col_name]>=lower_threshold]
	df_qualified = df_upper[df_upper[col_name]<=upper_threshold]

	df_outlier1 = df[df[col_name]<lower_threshold]
	df_outlier2 = df[df[col_name]>upper_threshold]
	# first is within thresholds, second is outlier df
	return df_qualified.to_json(), pd.concat([df_outlier1, df_outlier2]).to_json()