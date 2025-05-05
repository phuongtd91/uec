def get_active_requests_at_time(traffic_data, time_point):  
    """  
    Trả về danh sách các request đang hoạt động tại thời điểm time_point.  
    Một request được coi là đang hoạt động nếu time_point nằm trong khoảng từ t_req đến t_req + t_hold.  
    
    Args:  
        traffic_data: Danh sách các bản ghi giao thông, mỗi bản ghi có dạng (index, source, destination, requested_slots, t_req, t_hold)  
        time_point: Thời điểm cần kiểm tra  
    
    Returns:  
        List các request đang hoạt động tại thời điểm time_point  
    """  
    active_requests = []  
    
    for request in traffic_data:  
        index, source, destination, requested_slots, t_req, t_hold = request  
        end_time = t_req + t_hold  
        
        # Kiểm tra xem request có hoạt động tại thời điểm time_point không  
        if t_req <= time_point <= end_time:  
            active_requests.append(request)  
    
    return active_requests  

def print_active_requests(active_requests, time_point):  
    """  
    In ra danh sách các request đang hoạt động  
    """  
    print(f"\nThời điểm t = {time_point}: Có {len(active_requests)} request đang hoạt động:")  
    if len(active_requests) > 0:  
        print("ID | Source | Dest | Slots | Start | Hold | End")  
        print("-" * 50)  
        
        for req in active_requests:  
            index, source, destination, requested_slots, t_req, t_hold = req  
            end_time = t_req + t_hold  
            print(f"{index:2d} | {source:6d} | {destination:4d} | {requested_slots:5d} | {t_req:5d} | {t_hold:4d} | {end_time:3d}")  

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

def print_active_requests_over_time(traffic_data, max_time):  
    """  
    In ra các request đang hoạt động tại mỗi thời điểm từ 0 đến max_time  
    
    Args:  
        traffic_data: Danh sách các bản ghi giao thông  
        max_time: Thời điểm tối đa cần kiểm tra  
    """  
    print("\n=== DANH SÁCH CÁC REQUEST ĐANG HOẠT ĐỘNG THEO THỜI GIAN ===")  
    
    for time_point in range(max_time + 1):  
        active_requests = get_active_requests_at_time(traffic_data, time_point)  
        print_active_requests(active_requests, time_point)  

# Ví dụ sử dụng:  
def main():  
    # Đọc dữ liệu từ file  
    traffic_file = r"E:\Phuongtd@UEC\EON\traffic_jpn12_10.txt"  
    
    traffic_data, max_time = read_traffic_data(traffic_file)  
    print(f"Đã đọc {len(traffic_data)} request từ file, thời gian tối đa: {max_time}")  
    
    # In ra các request đang hoạt động theo thời gian từ 0 đến max_time  
    print_active_requests_over_time(traffic_data, max_time)  

if __name__ == "__main__":  
    main()