
import os
import lasio

file_path = r'\\prod.lan\active\proj\futurex\Legacy\Data\Processed\Geophysics\Electrical\Induction'
out_path = r'\\prod.lan\active\proj\futurex\Common\Working\Matti\cleaned_las\fix_las-a039\\'

well = ''
eno = ''
inst = ''
tag_match = 'A039'
new_tag = 'A034'
date_match = 'Processed: 28 July 2021'
new_date = 'Processed: 06 August 2021'

for root, _, files in os.walk(file_path):
    for name in files:
        inputfile = os.path.join(root, name)
        outputfile = os.path.join(out_path, name)
        lasfile = lasio.read(inputfile)
        well = lasfile.well.WELL.value
        eno = lasfile.well.UWI.value
        inst = lasfile.params.INSTRUMENT_NAME.value
        if 'A039' in inst:
            print('{}, \t{}, \t{}, \t{}'.format(name, well, eno, inst))
            with open(outputfile, 'w') as out, open(inputfile) as f:
                for line in f:
                    if tag_match in line:
                        print('Change {}'.format(line))
                        line = line.replace(tag_match, new_tag, 1)
                        print('Changed {}'.format(line))
                    if date_match in line:
                        print('Update {}'.format(line))
                        line = line.replace(date_match, new_date, 1)
                        print('Updated {}'.format(line))
                        print('klasdfhj')
                    out.write(line)



"""
for root, _, files in os.walk(las_path):
    for name in files:
        inputfile = os.path.join(root, name)
        outputfile = os.path.join(out_path, name)
        with open(outputfile, 'w') as out, open(inputfile) as f:
            for line in f:
                if tag_match in line:
                    line.replace(tag_match, new_tag, 1)
                out.write(line)
"""
