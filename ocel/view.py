from datetime import datetime
import pandas as pd

import pm4py
log = pm4py.read_xes('event_log1.xes')
df = pm4py.convert_to_dataframe(log)
print(df)