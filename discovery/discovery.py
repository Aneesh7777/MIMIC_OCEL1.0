from datetime import datetime
import pandas as pd
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'  # Adjust the path accordingly

from pm4py.objects.conversion.log import converter as xes_converter
from pm4py.objects.log.importer.xes import importer as xes_importer

import pm4py
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.importer.jsonocel import importer as jsonocel_importer
from pm4py.objects.ocel.util import attributes_names

ocel = pm4py.read_ocel_xml("output2.xmlocel")
object_types = pm4py.ocel_get_object_types(ocel)
attribute_names = pm4py.ocel_get_attribute_names(ocel)
# ocpn = pm4py.ocel.discover_ocdfg(ocel)
# pm4py.vis.view_ocdfg(ocpn)
ocpn = pm4py.discover_oc_petri_net(ocel)
pm4py.view_ocpn(ocpn)