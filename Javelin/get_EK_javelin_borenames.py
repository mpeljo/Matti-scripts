
import os
import sys

file_path = r'\\prod.lan\active\proj\futurex\East_Kimberley\Data\FieldworkAndPhotos\FieldData\Javelin_NMR'

# Connect to oracle using credentials stored in safe location
sys.path.append(r'H:\\Python\\Oracle\\\\')
import connect_to_oracle

oracon = connect_to_oracle.connect_to_oracle()
cur = oracon.cursor()

contents = os.listdir(file_path)
for item in contents:
    this_path = os.path.join(file_path, item)
    if os.path.isdir(this_path):
        # print(item)

        # Construct SQL query
        query = '''
        select
            b.borehole_id,
            b.borehole_name,
            b.location.sdo_point.x as lon,
            b.location.sdo_point.y as lat,
            b.elevation_value,
            d.code as uom,
            ed.code as datum
        from
            borehole.boreholes b
            join borehole.lu_uom d
            on b.elevation_uom_id = d.uom_id
            join borehole.lu_elevation_datums ed
            on b.elevation_datum_id = ed.elevation_datum_id
        where
            borehole_name in ('{}')
        '''.format(item)