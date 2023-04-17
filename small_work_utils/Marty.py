import csv

outfile = r"C:\Users\u25834\Desktop\MORPH_Bore_data_formatted.csv"

with open(outfile, 'w') as outputfile:
    with open (r"C:\Users\u25834\Desktop\MORPH_Bore_Test.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        #line_count = 0
        for row in csv_reader:
            bore = row[0]
            depth = row[1]
            for output_line in range(1):
                line = ('{}, 0\n'.format(bore))
                outputfile.write(line)
                line = ('{}, {}\n'.format(bore, depth))
                outputfile.write(line)

