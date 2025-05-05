import numpy as np  
import time  
import matplotlib.pyplot as plt  
from matplotlib import font_manager  
from collections import defaultdict  

class EON_Clos_Network:  

    def __init__(self, num_w_switches, num_s_switches, num_ports_per_switch, spectrum_slots=320):
        """  
        Initialize structure Clos 3 stage (W-S-W) for EON  
        
        Parameters:  
        - num_w_switches: number of switchs in Wide stage (W)  
        - num_s_switches: number of switchs in Spine stage(S)  
        - num_ports_per_switch: number of ports each switch  
        - spectrum_slots: number of spectrum slot each link  
        """  
        self.num_w_switches = num_w_switches  
        self.num_s_switches = num_s_switches  
        self.num_ports_per_switch = num_ports_per_switch  
        self.spectrum_slots = spectrum_slots  

        # Initialize links and spectrums
        self.initialize_network()  

        # statistical  
        self.total_requests = 0
        self.external_blocked_count = 0
        self.internal_blocked_count = 0


    def initialize_network(self):  
        """Initialize network topo và available spectrum in link"""  
        self.links = {}  # Initialize link matrix W1-S-W2


        # input Links to stage W1
        for w in range(self.num_w_switches):  
            for i in range(self.num_w_switches):  
                self.links[(f'in_{i}', f'W1_{w}')] = np.zeros(self.spectrum_slots, dtype=int)

        # Links from stage W1 to stage S  
        for w in range(self.num_w_switches):  
            for s in range(self.num_s_switches):  
                self.links[(f'W1_{w}', f'S_{s}')] = np.zeros(self.spectrum_slots, dtype=int)  

        # Links from stage S to stage W2  
        for s in range(self.num_s_switches):  
            for w in range(self.num_w_switches):  
                self.links[(f'S_{s}', f'W2_{w}')] = np.zeros(self.spectrum_slots, dtype=int)  

        # Output direction from stage W2 to calculate the external block probability
        for w in range(self.num_w_switches):
            for d in range(self.num_w_switches):
                self.links[(f'W2_{w}', f'out_{d}')] = np.zeros(self.spectrum_slots, dtype=int)


    def find_path(self, source, destination):
        """find path from source to destination"""
        input_link = f'in_{source % self.num_ports_per_switch}'
        source_switch = f'W1_{source // self.num_ports_per_switch}'
        dest_switch = f'W2_{destination // self.num_ports_per_switch}'
        output_link = f'out_{destination % self.num_ports_per_switch}'

        available_paths = []  
        for s in range(self.num_s_switches):  
            s_switch = f'S_{s}'  
            path = [input_link, source_switch, s_switch, dest_switch, output_link]
            available_paths.append(path)  
        return available_paths

    def check_spectrum_availability(self, path, requested_slots):  
        """Check available spectrums in path"""  
        available_slots = []  
        for slot_idx in range(self.spectrum_slots - requested_slots + 1):  
            is_available = True

            for i in range(len(path) - 1):  
                link = (path[i], path[i+1])  
                spectrum_segment = self.links[link][slot_idx:slot_idx+requested_slots]  
                
                if np.any(spectrum_segment):  
                    is_available = False  
                    break

            if is_available:  
                available_slots.append((slot_idx, slot_idx + requested_slots - 1))  
        
        return available_slots  

    def allocate_spectrum(self, path, slot_idx, requested_slots, connection_id, slot_index):
        """Spectrum allocation for connection"""  
        for i in range(len(path) - 1):
            if i == 0:  # First link
                first_link = (path[i], path[i+1])
                print(f'first_link: {first_link}\n')
                self.links[first_link][slot_index : slot_index + requested_slots] = connection_id
                print(f'allocate to input LINK: {first_link} : {connection_id} \n')
                print(f'slot_index of first link: {slot_index}\n')
            elif i == 2:  # Third link
                third_link = (path[i], path[i+1])
                # Use the slot index from the second link
                second_link = (path[i-1], path[i])
                print(f'second_link: {second_link}\n')
                # Check if the slot index is valid for the third link
                slot_idx = slot_idx  # Ensure slot_idx is reused from the second link
                print(f'slot_idx of second link: {slot_idx}\n')
                self.links[third_link][slot_idx : slot_idx + requested_slots] = connection_id
                print(f'third_link: {third_link}\n')    
                print(f'slot_index of third link: {slot_idx}\n')
                print(f'allocate to third LINK: {third_link} : {connection_id} \n')
            else:  # Other links
                link = (path[i], path[i+1])
                self.links[link][slot_idx : slot_idx + requested_slots] = connection_id
                print(f'slot_index of  link {i}: {slot_idx}\n')
                print(f'allocate to LINK: {link} : {connection_id} \n')
                print(f"link after allocate: {self.links[(path[i], path[i+1])]}=")

    def release_spectrum(self, path, slot_idx, requested_slots):  
        """Release spectrum after connection ends"""  
        for i in range(len(path) - 1):  
            link = (path[i], path[i+1])  
            self.links[link][slot_idx : slot_idx + requested_slots] = 0  

    def first_fit_assignment(self, available_slots):  
        """First-Fit  to allocate the first available slot"""  
        if available_slots:  
            return available_slots[0][0]  
        return None  

    def read_traffic_data(self, file_path):  
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
    
       
    def run_simulation(self, traffic_file=None):  
        """  
        Chạy mô phỏng mạng EON  
        traffic_file: Đường dẫn đến file dữ liệu traffic để sử dụng  
        """  
        current_connections = {}  
        # connection_id = 1  
        blocking_stats = []  
        
        # If there is a traffic file path, read data from the file  
        if traffic_file:  
            traffic_data, simulation_time = self.read_traffic_data(traffic_file)  
            print(f'total_time: {simulation_time}')
        else:
            print("No traffic file was found")
       
        # Simulation over time 
        for time in range(simulation_time + 1):  
            # Xử lý các kết nối đã hết thời gian  
            connections_to_remove = []  
            for conn_id, conn_info in current_connections.items():  
                if time == conn_info['end_time']:  
                    self.release_spectrum(conn_info['path'], conn_info['slot_idx'], conn_info['slots'])  
                    connections_to_remove.append(conn_id)  
                    print(f'{time} time to release connection {conn_id} in {conn_info["path"]}')
            # Xóa các kết nối đã hết thời gian  
            for conn_id in connections_to_remove:
                # print(f'req da ket thuc: {current_connections}')  
                del current_connections[conn_id] 
            # print(len(current_connections)  )   

            # Xử lý các yêu cầu kết nối mới từ file traffic  

                
            for (index, source, destination, requested_slots, slot__index, t_req, t_hold) in traffic_data:
                self.total_requests = index + 1
                connection_id = index + 1
                
                # Kiểm tra thời gian yêu cầu kết nối
                if time == t_req:
                    # Tìm đường đi từ nguồn đến đích  
                    paths = self.find_path(source, destination)  
                    is_allocated = False

                    # Check output direction to calculate the external block probability
                    last_link= paths[-1][-2:]
                    print(f'last_link: {last_link}')
                    available_slots = self.check_spectrum_availability(last_link, requested_slots)
                    if not available_slots:
                        # print(f"request {index} was external blocked ")
                        self.external_blocked_count += 1
                        continue

                    print(f'{time}: {source} to {destination} - paths : {paths}')
                    # Thử phân bổ khe phổ trên các đường đi tìm được  
                    for path in paths:
                        # Kiểm tra tính khả dụng của phổ trên đường đi
                        
                        print(f'Time {time} : input link: {paths[0][:2]} : {connection_id} \n {self.links[(path[0], path[1])]}')
                        available_slots = self.check_spectrum_availability(path, requested_slots)  

                        if available_slots:  
                            # Sử dụng thuật toán First-Fit để chọn khe phổ  
                            slot_idx = self.first_fit_assignment(available_slots)
                            print(f'path: {path} - slot_idx = {slot_idx}')  
                            # Phân bổ phổ cho kết nối  
                            self.allocate_spectrum(path, slot_idx, requested_slots, connection_id, slot__index)

                            # print(f"input link after allocate: {self.links[(path[0], path[1])]}=")
                            # Tính thời gian kết thúc và lưu thông tin kết nối  
                            end_time = t_req + t_hold  
                            current_connections[connection_id] = {  
                                'path': path,  
                                'slot_idx': slot_idx,  
                                'slots': requested_slots,  
                                'end_time': end_time  
                            }
                            
                            # print(f'{time} - {current_connections[connection_id]}')  
                            # connection_id += 1  
                            is_allocated = True  
                            break  # Đã phân bổ thành công, không cần thử đường đi khác  
                    # print(f' inprocess: {current_connections}')
                    # Nếu không thể phân bổ khe phổ cho yêu cầu, tăng số lượng yêu cầu bị chặn  
                    if not is_allocated:
                        # print(f"request {index} was internal blocked ")  
                        self.internal_blocked_count += 1

            # Tính tỷ lệ chặn tại thời điểm hiện tại  
            if self.total_requests > 0:  
                blocking_ratio = (self.internal_blocked_count + self.external_blocked_count) / self.total_requests
            else:  
                blocking_ratio = 0  
    
            # Lưu tỷ lệ chặn vào thống kê  
            blocking_stats.append(blocking_ratio)
        return blocking_stats
 


    def visualize_spectrum(self, link):  
        """Display link spectrum status"""  
        plt.figure(figsize=(12, 4))  
        plt.imshow([self.links[link]], aspect='auto', cmap='viridis')  
        plt.colorbar(label='Connection ID')  
        plt.xlabel('Spectrum Slot Index')  
        plt.title(f'Spectrum usage on link {link}')
        plt.yticks([])  
        plt.grid(False)  
        plt.show()  
    
    def plot_blocking_probability(self, blocking_stats):  
        """Plot the blocking probability over time"""  
        plt.figure(figsize=(10, 6))  
        plt.plot(blocking_stats)  
        plt.xlabel('Time')  
        plt.ylabel('Blocking Probability')  
        plt.title('Blocking Probability over Time')  
        plt.grid(True)  
        plt.show()  

    def print_spectrum_status_at_time(self, link, time):
        """
        In ra trạng thái các khe phổ của một liên kết tại một thời điểm nhất định.
        
        Args:
            link (tuple): Liên kết cần kiểm tra, ví dụ ('in_0', 'W1_0').
            time (int): Thời điểm cần kiểm tra.
        """
        print(f"Time {time}: Spectrum status on link {link}:")
        if link in self.links:
            spectrum_status = self.links[link]
            print("Spectrum slots:")
            print(" ".join(map(str, spectrum_status)))
        else:
            print(f"Link {link} does not exist in the network.")
    
# Chạy thử mô phỏng  
if __name__ == "__main__":  
    # Initialize network node: 12 switch W, 12 switch S, 12 ports each switch  
    network = EON_Clos_Network(num_w_switches=4, num_s_switches=4, 
                               num_ports_per_switch=4, spectrum_slots=320)
    #traffic_file= r"traffic_jpn12_10_updated.txt"
    traffic_file= r"traffic_jpn12_500_01.txt"


    # Run simulation với tệp traffic  
    blocking_stats = network.run_simulation(traffic_file)   
    # print(blocking_stats)
    # Result  
    print(f"Total requests: {network.total_requests}")  
    print(f"External Blocked request: {network.external_blocked_count}")
    print(f"Internal Blocked request: {network.internal_blocked_count}")
    if network.total_requests > 0:
        print(f"Avg block probability: {(network.external_blocked_count + network.internal_blocked_count) / network.total_requests * 100:.4f} %")
    else:  
        print("No connection was found.")   


    # the status spectrum on a link  
    network.visualize_spectrum(('in_0', 'W1_0'))  
    network.print_spectrum_status_at_time(('in_0', 'W1_0'), 26968)

    # Plot the blocking probability   
    network.plot_blocking_probability(blocking_stats)
