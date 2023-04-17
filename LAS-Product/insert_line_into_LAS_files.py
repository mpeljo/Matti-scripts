
import os

las_path = r'\\prod.lan\active\proj\futurex\Legacy\Data\Processed\Geophysics\Electrical\Induction\\'
out_path = r'\\prod.lan\active\proj\futurex\Common\Working\Matti\cleaned_las\neils-final-with-proc-date\\'

tag_match = '~ASCII'
comment = 'Processed: 28 July 2021'

for root, _, files in os.walk(las_path):
    for name in files:
        inputfile = os.path.join(root, name)
        outputfile = os.path.join(out_path, name)
        with open(outputfile, 'w') as out, open(inputfile) as f:
            for line in f:
                if tag_match in line:
                    out.write(comment + '\n')
                out.write(line)

