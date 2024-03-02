import matplotlib.pyplot as plt
import networkx as nx

# Assuming the rest of your code above this point remains the same
import matplotlib.pyplot as plt
import networkx as nx
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
import networkx as nx
import matplotlib.pyplot as plt

# Load the .xes event log
log_path = 'event_log1.xes'  # Update this path to your .xes file location
log = xes_importer.apply(log_path)

# Initialize the graph
G = nx.DiGraph()

# Initialize dictionaries to hold the counts of connections (for labels)
activity_counts = {}
subject_to_hadm = {}
hadm_to_activity = {}
transfer_to_activity = {}

# Iterate through the log to populate the dictionaries and add nodes/edges to the graph
for trace in log:
    subject_id = trace.attributes.get('subject_id', None)
    hadm_id = trace.attributes.get('hadm_id', None)
    subject_to_hadm_key = ('S', 'H')
    subject_to_hadm[subject_to_hadm_key] = subject_to_hadm.get(subject_to_hadm_key, 0) + 1
    
    for event in trace:
        transfer_id = event.get('transfer_id', None)
        activity_name = event['concept:name']
        activity_key = activity_name[:10]  # Shorten the name for simplicity
        
        # Update activity count
        activity_counts[activity_key] = activity_counts.get(activity_key, 0) + 1
        
        # Update hadm_to_activity and transfer_to_activity
        hadm_to_activity_key = ('H', activity_key)
        transfer_to_activity_key = ('T', activity_key)
        
        hadm_to_activity[hadm_to_activity_key] = hadm_to_activity.get(hadm_to_activity_key, 0) + 1
        transfer_to_activity[transfer_to_activity_key] = transfer_to_activity.get(transfer_to_activity_key, 0) + 1

# Add nodes for unique entities
G.add_node('H', label='HADM_ID')
G.add_node('S', label='SUBJECT_ID')
G.add_node('T', label='TRANSFER_ID')

# Add nodes for each activity with count as part of the label
for activity, count in activity_counts.items():
    G.add_node(activity, label=f"{activity}\nCount: {count}")

# Add edges with counts as labels
G.add_edges_from([(k[0], k[1], {'label': str(v)}) for k, v in subject_to_hadm.items()])
G.add_edges_from([(k[0], k[1], {'label': str(v)}) for k, v in hadm_to_activity.items()])
G.add_edges_from([(k[0], k[1], {'label': str(v)}) for k, v in transfer_to_activity.items()])

# # Draw the graph
# pos = nx.spring_layout(G)  # You can experiment with different layouts
# nx.draw(G, pos, with_labels=True, node_size=1500, node_color='lightblue', font_size=8, font_weight='bold')
# edge_labels = nx.get_edge_attributes(G, 'label')
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
# plt.show()

# First, compute an automatic layout for all nodes
pos = nx.spring_layout(G, k=1.0, iterations=50)

# Then, manually adjust positions for 'S', 'H', and 'T' to prevent overlapping
# The specific values here may need adjustment based on your graph's overall layout and size
# These are example coordinates and should be adjusted to fit your visualization needs
pos['S'] = (-0.25, 0.25)  # Example position for 'S'
pos['H'] = (0, 0.25)   # Example position for 'H', adjust x and y to place it relative to 'S'
pos['T'] = (0.25, 0.25)   # Example position for 'T', adjust x and y to place it relative to 'H'

# Adjust the figure size to provide more space for the spread-out layout
plt.figure(figsize=(14, 10))

# Prepare node labels, now including counts directly in the labels for 'S', 'H', and 'T'
node_labels = {node: data['label'] for node, data in G.nodes(data=True)}

# Draw the graph with updated node labels and manually adjusted positions
nx.draw(G, pos, labels=node_labels, with_labels=True, node_size=2500, node_color='lightblue', font_size=12, font_weight='bold', alpha=0.75)

# Save the plot to a file
plt.savefig('network_graph_adjusted_positions.png', format='png', dpi=300)

# Show plot
plt.show()