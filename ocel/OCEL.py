import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

# Assuming you have an XES event log file named 'your_event_log.xes'
event_log_path = 'event_log1.xes'

# Import the event log
event_log = xes_importer.apply(event_log_path)

# Specify the necessary columns
activity_column = 'concept:name'
timestamp_column = 'time:timestamp'
object_types = ['subject_id','hadm_id','transfer_id']

# Print information about the event log
print("Event Log Information:")
print("Number of traces:", len(event_log))
print("Number of events:", sum(len(trace) for trace in event_log))

# Convert the event log to an Object-Centric Event Log (OCEL)
ocel_result = pm4py.convert.convert_log_to_ocel(event_log, activity_column, timestamp_column, object_types)

# Print information about the OCEL
print("\nOCEL Information:")
print("Number of objects:", len(ocel_result.objects))
print("Number of events in the OCEL:", len(ocel_result.events))

# Specify the output OCEL XML file path
ocel_xml_output_path = 'output2.xmlocel'

# Export the OCEL to XML format
pm4py.write_ocel(ocel_result, ocel_xml_output_path)

print(f"\nOCEL saved to: {ocel_xml_output_path}")
