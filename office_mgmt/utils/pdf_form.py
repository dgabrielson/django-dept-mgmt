#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pdf_form.py


Purpose: Do a form fill on the Capital Asset Management Disposal form.

This script requires the pdftk tool.

This script assumes that "asset_disposal.pdf" is in the same
location, and that the relevant fields are keyed as follows:
    Text63  :   Faculty or School Name
    Text64  :   Department name
    Text65  :   Date
    Text66  :   Asset description, line 1
    Text67  :   Asset description, line 2
    Text68  :   Serial number(s)
    Text69  :   UM Property number
*   Text70  :   Date aquired
*   Text71  :   Purchase order number
*   Text72  :   Original cost
*   Text73  :   Original FOPAL or budget/grant charged
*   Text74-77   :   Condition checkboxes (Excellent=74,Good=75,Poor=76,Not working=77)       
    Text75  :   Good (working) checkbox.
    Text79  :   Offer for sale checkbox.    # 2010-03mar
    Text89  :   Room # of item
    Text90  :   Building of item
*   Text91  :   Reserve bid checkbox
*   Text92  :   Reserve bid dollars
*   Text93  :   Reserve bid cents
*   Text94  :   Best offer checkbox
    Text96  :   FOPAL to be credited.
    Text97  :   Contact name
    Text98  :   Contact phone number
    Text99  :   Contact email address.

To check the keys, run the pdf_ext module driver on the
asset_disposal.pdf file.

CHANGELOG:
    2010-Mar-16: Form changed.  'Offer for sale' checkbox id changed from Text78 to Text79
    2010-Mar-11: Modified to work with Django SITS
    2008-07-18: Added code to find the pdftk executable.


These forms change from time to time.  Check at
http://umanitoba.ca/admin/financial_services/cams/
to see if the form has been updated (can this check be automatic??)
    * pdftk PDFFILE burst # splits into individual pages
    * python pdf_ext.py PDFFILE # check form fields

See also the code in ~/stats-paperwork/purchasing/purchase_formfill.py

"""
#######################
from __future__ import print_function, unicode_literals

import datetime

#######################
import os
import sys
import tempfile

from .. import conf
from .fdfgen import forge_fdf

# These should probably be in some kind of settings file...

UNIT_NAME = conf.get("asset:unit_name")
CONTACT_PERSON = conf.get("asset:default_contact")
FOPAL = conf.get("asset:fopal_to_be_credited")

IGNORE_LIST = ["", "n/a", "None", "???"]

PDFTK = None
for f in [
    "/sw/bin/pdftk",  # fink
    "/usr/bin/pdftk",  # ubuntu
    "/usr/local/bin/pdftk",  # MacOS X native
    "/opt/bin/pdftk",  # a possible location
    "/opt/local/bin/pdftk",  # macports
]:
    if os.path.exists(f):
        PDFTK = f
        break


def absolute_path(fragment):
    """
    Set up an absolute path relative to this file, pointing to the given fragment.
    """
    return os.path.normpath(os.path.join(os.path.split(__file__)[0], fragment)).replace(
        "\\", "/"
    )


MASTER_FORM = absolute_path("../static/office_mgmt/pdf/asset_disposal-2010-03mar.pdf")

#######################################################################
# TURN FIELDS INTO A PDF


def fields_to_fdf(fields, fdf_file):
    """
    Write out the given fields to the given fdf file object.
    """
    fdf = forge_fdf("", fields, [], [], [])
    fdf_file.write(fdf.encode("utf-8"))


def form_fill_disposal_pdf(fields_dict):
    """
    Take the given fields and return the PDF data stream.
    """
    if PDFTK is None:
        return None

    fields = sorted(fields_dict.items())

    fdf = tempfile.NamedTemporaryFile(suffix=".fdf")
    fields_to_fdf(fields, fdf)
    fdf.flush()
    pdf = tempfile.NamedTemporaryFile(suffix=".pdf")

    cmd = '"%s" "%s" fill_form "%s" output "%s"' % (
        PDFTK,
        MASTER_FORM,
        fdf.name,
        pdf.name,
    )
    os.system(cmd)
    pdf.seek(0)

    return pdf.read()


#######################################################################


def general_form_fields():
    """
    Do general form fields
    """
    fields = {}
    fields["Text63"] = UNIT_NAME[0]
    fields["Text64"] = UNIT_NAME[1]
    fields["Text65"] = datetime.date.today().strftime("%Y-%b-%d")
    fields["Text79"] = "X"  # always offer for sale, by default
    fields["Text96"] = FOPAL
    fields["Text97"] = CONTACT_PERSON[0]
    fields["Text98"] = CONTACT_PERSON[1]
    fields["Text99"] = CONTACT_PERSON[2]
    return fields


def do_room_fields(room):
    return {"Text89": room.number, "Text90": room.building}


#######################################################################
# COMPUTERS


def make_fields_from_computer(record):
    """
    This provides updated and more descriptive field information
    based on the given computer record.
    """
    desc = []
    if record.processor is not None and record.processor.lower() not in IGNORE_LIST:
        desc.append(record.processor + " CPU")
    if record.ram is not None and record.ram.lower() not in IGNORE_LIST:
        desc.append(record.ram + " RAM")
    if record.harddrive is not None and record.harddrive not in IGNORE_LIST:
        desc.append(record.harddrive + " HD")
    if (
        record.operating_system is not None
        and record.operating_system not in IGNORE_LIST
    ):
        desc.append(record.operating_system)
    desc_line2 = ", ".join(desc)

    fields = {}
    if record.hardware:
        fields["Text66"] = record.hardware
    if desc_line2:
        fields["Text67"] = desc_line2
    if record.room:
        fields.update(do_room_fields(record.room))

    return fields


def computer_disposal_form(computer):
    """
    Return the PDF data for a computer disposal.
    """
    fields = make_fields_from_computer(computer)
    return form_fill_disposal_pdf(fields)


#######################################################################
# GENERAL ASSETS

CONDITION_MAP = {  # map current conditions to a text field
    "A": "Text74",
    "B": "Text75",
    "C": "Text76",
    "D": "Text77",
}


def make_fields_from_asset(record):
    """
    Text70  :   Date aquired
    Text71  :   Purchase order number
    Text72  :   Original cost
    Text73  :   Original FOPAL or budget/grant charged
    Text74-77   :   Condition checkboxes (Excellent=74,Good=75,Poor=76,Not working=77)       
    Text91  :   Reserve bid checkbox
    Text92  :   Reserve bid dollars
    Text93  :   Reserve bid cents
    Text94  :   Best offer checkbox
    """
    fields = general_form_fields()
    if record.room:
        fields.update(do_room_fields(record.room))

    fields["Text66"] = record.description
    fields["Text68"] = record.serial_number
    if record.property_number:
        fields["Text69"] = str(record.property_number)

    if record.date_acquired:
        fields["Text70"] = record.date_acquired.strftime("%Y-%b-%d")
    if record.purchase_order_number:
        fields["Text71"] = record.purchase_order_number
    if record.original_cost:
        fields["Text72"] = record.original_cost
    if record.original_fopal:
        fields["Text73"] = record.original_fopal

    if record.current_condition:
        field = CONDITION_MAP.get(record.current_condition, None)
        if field is not None:
            fields[field] = "X"

    if record.reserve_bid:
        fields["Text91"] = "X"
        amount = float(record.reserve_bid.strip().lstrip("$"))
        dollars = str(int(amount))
        cents = str(int(100 * (amount - int(amount))))
        while len(cents) < 2:
            cents = "0" + cents
        if dollars:
            fields["Text92"] = dollars
        if cents and cents != "00":
            fields["Text93"] = cents
    else:
        fields["Text94"] = "X"

    try:
        computer = record.computer_set.get()
    except record.computer_set.all().model.DoesNotExist:  # Needs to be general Object DNE.
        pass
    else:
        fields.update(make_fields_from_computer(computer))

    return fields


def asset_disposal_form(asset):
    """
    Return the PDF data for an asset disposal.
    """
    fields = make_fields_from_asset(asset)
    return form_fill_disposal_pdf(fields)


#######################################################################
#
