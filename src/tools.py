import csv

def csv_to_dict(dataPath,headers):
	headersLen = len(headers)
	output = {}
	with open(dataPath, 'r', newline='') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter = ',')
		csv_headers = []
		for row in csv_reader:
			csv_headers.append(row)
			break
		csv_headers = csv_headers[0]
		index_dict = {}
		for header in headers:
			if header in csv_headers:
				idx = csv_headers.index(header)
				index_dict[header] = idx
				output[header] = []
		next(csv_reader)
		for row in csv_reader:
			if len(row) == headersLen:
				for header, idx in index_dict.items():
					output[header].append(row[idx])
	return output
