import matplotlib.pyplot as plt
import networkx as nx

# Initialize the graph
G = nx.DiGraph()

# Position dictionary
pos = {}

# Variables for positioning
current_x_subject = 0  # Start positioning for subject nodes
subject_y = 3  # Y-level for subject nodes
hadm_y = 2  # Y-level for HADM nodes
transfer_y = 1  # Y-level for transfer nodes
transfer_spacing = 1.0  # Increase spacing between individual transfers

# Add subject nodes and their positions
for i, subject_id in enumerate(data["subject_id"]):
    pos[subject_id] = (current_x_subject, subject_y)
    G.add_node(subject_id, label=f"S{i+1}")
    # Adjust current_x_subject based on the number of transfers to avoid overlap
    current_x_subject += (len(data["transfer_ids"][i]) * transfer_spacing) + 2

# Reset for HADM and Transfer nodes
current_x_hadm = 0  # Reset positioning for HADM nodes

# Add HADM and transfer nodes, including edges from subjects to HADMs and transfers
for i, (hadm_id, transfer_ids) in enumerate(zip(data["hadm_id"], data["transfer_ids"])):
    subject_id = data["subject_id"][i]
    # Calculate HADM position based on the subject position, slightly offset
    pos[hadm_id] = (current_x_hadm, hadm_y)
    G.add_node(hadm_id, label=f"H{i+1}")
    G.add_edge(subject_id, hadm_id)  # Add edge between subject and HADM
    
    # Calculate Transfer positions
    for j, transfer_id in enumerate(transfer_ids):
        transfer_pos_x = current_x_hadm + (j * transfer_spacing) - ((len(transfer_ids) - 1) * transfer_spacing / 2)
        pos[transfer_id] = (transfer_pos_x, transfer_y)
        G.add_node(transfer_id, label=f"T{i+1}.{j+1}")
        G.add_edge(hadm_id, transfer_id)  # Add edge between HADM and transfer
        G.add_edge(subject_id, transfer_id)  # Add edge between subject and transfer for direct relationships

    # Update current_x_hadm for the next HADM node, based on transfers
    current_x_hadm += (len(transfer_ids) * transfer_spacing) + 2

# Draw the graph with updated node positions and labels
plt.figure(figsize=(14, 8))
nx.draw(G, pos, with_labels=True, labels=nx.get_node_attributes(G, 'label'), node_size=1000, font_size=10, node_color="lightblue", font_weight="bold")
plt.title("Enhanced Visualization of Subject, HADM, and Transfer Relationships")
plt.axis('off')
plt.show()