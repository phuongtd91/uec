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
                        t_req = int(parts[4])  # time of request  
                        t_hold = int(parts[5])  # holding time of request  
                        
                        # Tính total_time và cập nhật max_total_time  
                        total_time = t_req + t_hold  
                        if total_time > max_total_time:  
                            max_total_time = total_time
                        
                        traffic_data.append((index, source, destination, requested_slots, t_req, t_hold))  
                    except ValueError:  
                        print(f"Ignore invalid lines: {line}")  
    except FileNotFoundError:  
        print(f"File is not found: {file_path}")  
    except Exception as e:  
        print(f"Can not read file: {e}")  
    
    return traffic_data, max_total_time 

traffic_file=r"E:\Phuongtd@UEC\EON\traffic_jpn12_10.txt"

traffic_data, simulation_time = read_traffic_data(traffic_file)

for time in range(simulation_time):  
    active_request = []
    for (index, source, destination, requested_slot, t_req, t_hold) in traffic_data:
        total_requests = index + 1
        
        end_time = t_req + t_hold
        if end_time> time >= t_req:
            print(f'{index} : {t_req} : {end_time}')
            active_request.append(index)
    print(f' time {time} co request {active_request}')

print(f'total.request: {total_requests}')