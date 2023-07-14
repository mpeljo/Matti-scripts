import requests
import os

import settings

filename = 'testfile.zip'

filepath = os.path.join(settings.SHADOW_OPS_DIR, filename)

url = r'https://ga-gdl-data-store-nonprod.s3.ap-southeast-2.amazonaws.com/ingested/ce5fcbaa-bc15-4ce9-a538-c4f72a87cba8/GA%20Strategy%202028%20Update_FA2.zip?AWSAccessKeyId=ASIA25OBBEJNR7QU7SUD&Expires=1687766615&Signature=7Pp6Suf1rTaxdkAMh8cZiAkh5TI%3D&X-Amzn-Trace-Id=Root%3D1-6498f1f7-10f8f29a0735052a0503e6a6%3BParent%3D2c9814621a4a6ea8%3BSampled%3D0%3BLineage%3D1dc76971%3A0&x-amz-security-token=IQoJb3JpZ2luX2VjENL%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDmFwLXNvdXRoZWFzdC0yIkgwRgIhALt%2BF3mcuoBxr2Xk3v7lXcYFaltdpmbTnxSvBLxJShtRAiEAmX85GR%2BDmcC912D5SJnsp6bSTOq6pMiMVVXWBF2CtQsqhgMIOxAAGgw3NTA0MTM0ODg3MzEiDOVvDwxqRDPk%2B2IosSrjAr8WPKaDuKiLoA55MCdv5%2B6%2BTcD%2BLbOu6cwu6GU8Dy7EU%2Fr66fe%2BQxo4s3Lk0XqRnpOnyp48NwJywadNMmcjqJfC71tqSonDASlimBe%2FYU%2BFpd8xmVu3ilWCWEUEZV5wb9UI0JkjUyfD0arJcpfFS%2F8rVlWJHdfmGCfA75qL6SjsLQCH9XG9%2B6oYaP6GCIcihynJDNSKrxLwEqMd1woKZz8EoqHNZdkIIy2%2FFKpRSo7Bk2rJt9X3dKuIan37cJ5Dvsy746XV3Tnkq4IaELk42gkbS64%2FktciUYMHKg5e%2FxFshGEn621z0%2BD47OORBv8S9aifpNbwJ93BQKCFXGNOZx931hF6lyVLP5g1v%2F4PtFMbXFS6455ilf%2F0jzVm%2BB4FDQ9NdKD9c9uxx9zFCV3b%2B%2BQXZcvF4VlTlcuucVD4Q4jVkW%2B3u%2BYIwZRs6EkPs4gG9dNF1jR%2FuwZN2QexxUbAp7X8Q%2FswpODjpAY6nAEllgrr1at4dFUIXINdxTau3w3qDdRRWgpQb5wP%2BbdN5SbbGLFrc%2F1dPM7aUKGsJ6zMA%2BN63mef5768%2FFcnP8ls8%2FBDtoQqiq3Zn3KdTUyuSTXoUGGY7Ayq4eCmxxy8jypvMN5Ly0lUVPz6JoHcY6ld2z7HlRubKl9J6yJNO8Ke5Jli7dtRqy3q7U05kmbUlxkA1qhw3sO7oidk3JU%3D'

r = requests.get(url, stream=True)

with open(filepath, 'wb') as fd:
    for chunk in r.iter_content(chunk_size=128):
        fd.write(chunk)
        