def read_traffic_data(file_path):  
    traffic_data = []
    max_total_time = 0  
    try:  
        with open(file_path, 'r') as file:  
            for line in file:  
                parts = line.strip().split()  
                if len(parts) >= 6:  # Phải có ít nhất 6 thông tin theo định dạng  
                    try:
                        index = int(parts[0][:-1])  # đọc index of traffic
                        source = int(parts[1])  # source node  
                        destination = int(parts[2])  # des node  
                        requested_slots = int(parts[3])  # req slots
                        index_slot = int(parts[4])  # index of slot in incoming request for the input link  
                        t_req = int(parts[5])  # time of request  
                        t_hold = int(parts[6])  # holding time of request  
                        
                        # Tính total_time và cập nhật max_total_time  
                        total_time = t_req + t_hold  
                        if total_time > max_total_time:  
                            max_total_time = total_time
                        
                        traffic_data.append((index, source, destination, requested_slots, index_slot, t_req, t_hold))  
                    except ValueError:  
                        print(f"Ignore invalid lines: {line}")  
    except FileNotFoundError:  
        print(f"File is not found: {file_path}")  
    except Exception as e:  
        print(f"Can not read file: {e}")  
    
    return traffic_data, max_total_time 

traffic_file=r"traffic_jpn12_10_updated.txt"

traffic_data, simulation_time = read_traffic_data(traffic_file)
total_slot = 0

def find_path(source, destination):
    """find path from source to destination"""
    input_link = f'in_{source % num_ports_per_switch}'
    source_switch = f'W1_{source // num_ports_per_switch}'
    dest_switch = f'W2_{destination // num_ports_per_switch}'
    output_link = f'out_{destination % num_ports_per_switch}'

    available_paths = []  
    for s in range(num_s_switches):  
        s_switch = f'S_{s}'  
        path = [input_link, source_switch, s_switch, dest_switch, output_link]
        available_paths.append(path)  
    return available_paths

num_ports_per_switch = 4    # Số cổng trên mỗi switch
num_s_switches = 4         # Số switch trong mạng
num_w_switches = 2         # Số switch trong mạng

for request in traffic_data:
    index, source, destination, requested_slots, index_slot, t_req, t_hold = request
    total_slot += requested_slots
    total_requests = index + 1

    path = find_path(source, destination)
    print(f"Request {index}: Path from {source} to {destination} with requested slots {requested_slots} at time {t_req} with holding time {t_hold}")
    print(f"Path: {path}")
print (total_slot)
# for time in range(simulation_time):  
#     active_request = []
#     for (index, source, destination, requested_slot, t_req, t_hold) in traffic_data:
#         total_requests = index + 1
        
#         end_time = t_req + t_hold
#         if end_time> time >= t_req:
#             print(f'{index} : {t_req} : {end_time}')
#             active_request.append(index)
#     print(f' time {time} co request {active_request}')

print(f'total.request: {total_requests}')