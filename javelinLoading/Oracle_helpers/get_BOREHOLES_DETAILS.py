# get_BOREHOLES_DETAILS.py
import os
import os.path

paths_file = './March_2023_vectorfiles.txt'
javelin_path = r'\\prod.lan\active\proj\dcd\Data\FieldworkAndPhotos\FieldData\Javelin_NMR'

excludes = (
    'Water_Tank_Calibrations',
    'Processed',
)

with open(paths_file, 'w') as pf:
    for dirpath, dirnames, filenames in os.walk(javelin_path):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        for filename in [f for f in filenames if f.endswith('_1Dvectors_uniform.txt')]:
            vectors_path = os.path.join(dirpath, filename)
            pf.write(vectors_path)
            pf.write('\n')

"""
Subsequently,
--https://stackoverflow.com/questions/6074201/using-like-in-an-oracle-in-clause
SELECT borehole_id, borehole_name
FROM borehole.boreholes b
WHERE EXISTS (
    SELECT 1
    FROM TABLE (sys.ora_mining_varchar2_nt(
    '%GW036806%',
    '%GW036842%',
    '%GW036852%',
    '%GW036853%',
    '%GW036883%',
    '%GW036884%',
    '%GW036885%',
    '%GW036941%',
    '%GW036942%',
    '%GW040872%',
    '%GW040873%',
    '%GW098195%',
    '%GW098196%',
    '%GW098197%',
    '%GW098199%',
    '%GW098201%',
    '%GW098203%'))
    WHERE b.borehole_name LIKE column_value
);

Output:
867094	GW036806.2.2
867096	GW036852.2.2
867097	GW036853.3.3
867098	GW036884.1.1
867099	GW036885.1.1
867100	GW036941.2.2
867101	GW036942.2.2
867102	GW040872.3.3
867103	GW040873.3.3
867104	GW098195.1.1
867105	GW098196.1.1
867106	GW098197.2.2
867107	GW098199.2.2
867108	GW098201.1.1
867110	GW098203.1.1
"""
