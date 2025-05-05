import networkx as nx  
import matplotlib.pyplot as plt  
import matplotlib.patches as mpatches  

# Tạo đồ thị có hướng  
G = nx.DiGraph()  

# Định nghĩa số lượng switch mỗi stage  
num_switches = 4  # Từ 0 đến 3  
num_ports = 4     # Từ 0 đến 3  

# Thêm nút input  
for i in range(num_switches):  
    for j in range(num_ports):  
        input_node = f"input_{i}_{j}"  
        G.add_node(input_node, pos=(0, -i*1.5 - j*0.2), type='input')  

# Thêm nút cho các stage chính  
for i in range(num_switches):  
    G.add_node(f"w1_{i}", pos=(1, -i*1.5 - 0.5), type='switch')  
    G.add_node(f"s_{i}", pos=(2, -i*1.5 - 0.5), type='switch')  
    G.add_node(f"w2_{i}", pos=(3, -i*1.5 - 0.5), type='switch')  

# Thêm nút output  
for i in range(num_switches):  
    for j in range(num_ports):  
        output_node = f"output_{i}_{j}"  
        G.add_node(output_node, pos=(4, -i*1.5 - j*0.2), type='output')  

# Kết nối input đến W1  
for i in range(num_switches):  
    for j in range(num_ports):  
        G.add_edge(f"input_{i}_{j}", f"w1_{i}")  

# Kết nối W1 đến S (kết nối đầy đủ)  
for i in range(num_switches):  
    for j in range(num_switches):  
        G.add_edge(f"w1_{i}", f"s_{j}")  

# Kết nối S đến W2 (kết nối đầy đủ)  
for i in range(num_switches):  
    for j in range(num_switches):  
        G.add_edge(f"s_{i}", f"w2_{j}")  

# Kết nối W2 đến output  
for i in range(num_switches):  
    for j in range(num_ports):  
        G.add_edge(f"w2_{i}", f"output_{i}_{j}")  

# Lấy vị trí các nút  
pos = nx.get_node_attributes(G, 'pos')  

# Khởi tạo không gian vẽ  
plt.figure(figsize=(14, 12))  

# Vẽ cạnh  
nx.draw_networkx_edges(G, pos, arrows=True, alpha=0.7, arrowsize=10, width=0.8)  

# Vẽ nút input/output nhỏ  
input_nodes = [n for n in G.nodes() if n.startswith("input")]  
output_nodes = [n for n in G.nodes() if n.startswith("output")]  
nx.draw_networkx_nodes(G, pos, nodelist=input_nodes, node_size=20, node_color='lightblue', alpha=0.8)  
nx.draw_networkx_nodes(G, pos, nodelist=output_nodes, node_size=20, node_color='lightblue', alpha=0.8)  

# Vẽ nút switch hình vuông  
for stage in ["w1", "s", "w2"]:  
    nodes = [n for n in G.nodes() if n.startswith(stage)]  
    nx.draw_networkx_nodes(G, pos, nodelist=nodes,   
                          node_color='#4a90e2',   
                          node_size=2500,   
                          node_shape='s',  
                          edgecolors='black')  

# Vẽ nhãn đầy đủ cho switch  
switch_labels = {}  
for n in G.nodes():  
    if any(n.startswith(stage) for stage in ["w1", "s", "w2"]):  
        switch_labels[n] = n  # Sử dụng tên đầy đủ của node làm nhãn  

nx.draw_networkx_labels(G, pos, labels=switch_labels, font_size=10, font_color='white')  

# Thêm nhãn input và output  
for i in range(num_switches):  
    for j in range(num_ports):  
        # Nhãn input  
        input_node = f"input_{i}_{j}"  
        plt.text(pos[input_node][0] - 0.1, pos[input_node][1], f"{j+1}",   
                fontsize=9, color='blue', horizontalalignment='right')  
        
        # Nhãn output  
        output_node = f"output_{i}_{j}"  
        plt.text(pos[output_node][0] + 0.1, pos[output_node][1], f"{j+1}",   
                fontsize=9, color='blue', horizontalalignment='left')  

# Thêm tiêu đề  
plt.text(0, 0.5, "Input", fontsize=14)  
plt.text(1, 0.5, "stage W1", fontsize=14, horizontalalignment='center')  
plt.text(2, 0.5, "Stage S", fontsize=14, horizontalalignment='center')  
plt.text(3, 0.5, "Stage W2", fontsize=14, horizontalalignment='center')  
plt.text(4, 0.5, "Output direction", fontsize=14)  

# Xóa trục  
plt.axis('off')  
plt.tight_layout()  
plt.show()