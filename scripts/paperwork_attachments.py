"""
This is site-stats utility script that requires either ./manage.py shell
Or direct activation:

. /www/sites/stats/venv/bin/activate
mkdir -p /www/__static/asset-disposal/`date +%Y`/`date +%m`/
pushd /www/__static/asset-disposal/`date +%Y`/`date +%m`/
DJANGO_SETTINGS_MODULE="stats.settings" \
PYTHONPATH="/www/sites/stats" \
python ~/paperwork_attachments.py 
popd
echo http://www.stats.umanitoba.ca/media/asset-disposal/`date +%Y`/`date +%m`/
"""
#######################
from __future__ import print_function, unicode_literals

#######################
import os
import shutil

from office_mgmt.models import Asset

attachment_list = []
for asset in Asset.objects.active().filter(status__exact="p"):
    if asset.property_number:
        name = "{}".format(asset.property_number)
    else:
        name = "{}".format(asset.serial_number)
    paperwork = asset.paperwork_set.active().filter(description__iexact="Sale photo")
    if paperwork.count() != 1:
        continue
    paperwork = paperwork.get()
    ext = os.path.splitext(paperwork.attachment.path)[-1]
    dst = name + ext
    print(dst, paperwork.attachment)
    shutil.copyfile(paperwork.attachment.path, dst)
    attachment_list.append(dst)

index_tmpl = """<!DOCTYPE html>
<html>
<head>
<title>{title}</title>
<style>
    body {{
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }}
</style>
</head>
<body>
<h1>{title}</h1>
{expanded_list}
</body>
</html>
"""

title = "Attachment list"
expanded_list = (
    "<ul>\n"
    + "\n".join(
        [
            '<li><a href="{0}">{1}</a></li>'.format(
                f, os.path.splitext(os.path.basename(f))[0]
            )
            for f in attachment_list
        ]
    )
    + "\n</ul>\n"
)

with open("index.html", "w") as f:
    f.write(index_tmpl.format(title=title, expanded_list=expanded_list))

print
