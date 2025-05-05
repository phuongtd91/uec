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
        self.blocked_requests = 0  

    def initialize_network(self):  
        """Initialize network topo và available spectrum in link"""  
        self.links = {}  # Initialize link matrix W1-S-W2


        # input Links to stage W1
        for w in range(self.num_w_switches):  
            for i in range(self.num_w_switches):  
                self.links[(f'input_{i}', f'S_{w}')] = np.zeros(self.spectrum_slots, dtype=int)

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
                self.links[(f'W2_{w}', f'direction_{d}')] = np.zeros(self.spectrum_slots, dtype=int)


    def find_path(self, source, destination):  
        """find path from source to destination"""  
        source_switch = f'W1_{source // self.num_ports_per_switch}'  
        dest_switch = f'W2_{destination // self.num_ports_per_switch}'  

        available_paths = []  
        for s in range(self.num_s_switches):  
            s_switch = f'S_{s}'  
            path = [source_switch, s_switch, dest_switch]  
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

    def allocate_spectrum(self, path, slot_idx, requested_slots, connection_id):  
        """Spectrum allocation for connection"""  
        for i in range(len(path) - 1):  
            link = (path[i], path[i+1])  
            self.links[link][slot_idx:slot_idx+requested_slots] = connection_id  

    def release_spectrum(self, path, slot_idx, requested_slots):  
        """Release spectrum after connection ends"""  
        for i in range(len(path) - 1):  
            link = (path[i], path[i+1])  
            self.links[link][slot_idx:slot_idx+requested_slots] = 0  

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
    
       
    def run_simulation(self, traffic_file=None):  
        """  
        Chạy mô phỏng mạng EON  
        traffic_file: Đường dẫn đến file dữ liệu traffic để sử dụng  
        """  
        current_connections = {}  
        connection_id = 1  
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
                if time >= conn_info['end_time']:  
                    self.release_spectrum(conn_info['path'], conn_info['slot_idx'], conn_info['slots'])  
                    connections_to_remove.append(conn_id)  

            # Xóa các kết nối đã hết thời gian  
            for conn_id in connections_to_remove:
                # print(f'req da ket thuc: {current_connections}')  
                del current_connections[conn_id]  

            # Xử lý các yêu cầu kết nối mới từ file traffic  

                
            for (index, source, destination, requested_slots, t_req, t_hold) in traffic_data:  
                self.total_requests = index + 1  

                if time >= t_req:
                    # Tìm đường đi từ nguồn đến đích  
                    paths = self.find_path(source, destination)  
                    is_allocated = False  
                    
                    # Thử phân bổ khe phổ trên các đường đi tìm được  
                    for path in paths:  
                        # Kiểm tra tính khả dụng của phổ trên đường đi  
                        available_slots = self.check_spectrum_availability(path, requested_slots)  

                        if available_slots:  
                            # Sử dụng thuật toán First-Fit để chọn khe phổ  
                            slot_idx = self.first_fit_assignment(available_slots)  
                            # Phân bổ phổ cho kết nối  
                            self.allocate_spectrum(path, slot_idx, requested_slots, connection_id)  

                            # Tính thời gian kết thúc và lưu thông tin kết nối  
                            end_time = t_req + t_hold  
                            current_connections[connection_id] = {  
                                'path': path,  
                                'slot_idx': slot_idx,  
                                'slots': requested_slots,  
                                'end_time': end_time  
                            }
                            # print(f'{time} - {current_connections[connection_id]}')  
                            connection_id += 1  
                            is_allocated = True  
                            break  # Đã phân bổ thành công, không cần thử đường đi khác  
                    
                    # Nếu không thể phân bổ khe phổ cho yêu cầu, tăng số lượng yêu cầu bị chặn  
                    if not is_allocated:  
                        self.blocked_requests += 1  

            # Tính tỷ lệ chặn tại thời điểm hiện tại  
            if self.total_requests > 0:  
                blocking_ratio = self.blocked_requests / self.total_requests  
            else:  
                blocking_ratio = 0  
    
            # Lưu tỷ lệ chặn vào thống kê  
            blocking_stats.append(blocking_ratio)
        return blocking_stats
        # for time in range(simulation_time + 1):  
        #     print(f'time: {time}')
        #     connections_to_remove = []  
        #     for conn_id, conn_info in current_connections.items():  
        #         if time >= conn_info['end_time']:  
        #             self.release_spectrum(conn_info['path'], conn_info['slot_idx'], conn_info['slots'])  
        #             connections_to_remove.append(conn_id)  

        #     for conn_id in connections_to_remove:  
        #         del current_connections[conn_id]  

        #     if traffic_file:  
        #         for (index, source, destination, requested_slots, t_req, t_hold) in traffic_data:  
                    
                     
        #             if source == destination:  
        #                 continue  

        #             paths = self.find_path(source, destination)  
        #             is_allocated = False  
        #             for path in paths:  
        #                 available_slots = self.check_spectrum_availability(path, requested_slots)  

        #                 if available_slots:  
        #                     slot_idx = self.first_fit_assignment(available_slots)  
        #                     self.allocate_spectrum(path, slot_idx, requested_slots, connection_id)  

        #                     end_time = t_req + t_hold 
        #                     current_connections[connection_id] = {  
        #                         'path': path,  
        #                         'slot_idx': slot_idx,  
        #                         'slots': requested_slots,  
        #                         'end_time': end_time  
        #                     }  
        #                     connection_id += 1  
        #                     is_allocated = True  
        #                     break  
        #             if not is_allocated:  
        #                 self.blocked_requests += 1
            
        #     self.total_requests = index + 1
        #     print(f'request: {self.total_requests}')  
        #     if self.total_requests > 0:  
        #         blocking_ratio = self.blocked_requests / self.total_requests  
        #     else:  
        #         blocking_ratio = 0  
        #     blocking_stats.append(blocking_ratio)  

        # return blocking_stats


    def visualize_spectrum(self, link):  
        """Display link spectrum status"""  
        plt.figure(figsize=(12, 4))  
        plt.imshow([self.links[link]], aspect='auto', cmap='viridis')  
        plt.colorbar(label='Connection ID')  
        plt.xlabel('Spectrum Slot Index')  
        plt.title(f'Spectrum usage on link {link}')  
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


    
# Chạy thử mô phỏng  
if __name__ == "__main__":  
    # Initialize network node: 12 switch W, 12 switch S, 12 ports each switch  
    network = EON_Clos_Network(num_w_switches=3, num_s_switches=3, 
                               num_ports_per_switch=6, spectrum_slots=320)  
    traffic_file=r"E:\Phuongtd@UEC\EON\traffic_jpn12_10.txt"
    # Run simulation với tệp traffic  
    blocking_stats = network.run_simulation(traffic_file)   
    # print(blocking_stats)
    # Result  
    print(f"Total requests: {network.total_requests}")  
    print(f"Blocked request: {network.blocked_requests}")  
    if network.total_requests > 0:  
        print(f"Avg block probability: {network.blocked_requests / network.total_requests:.4f} %")  
    else:  
        print("Không có yêu cầu nào được thực hiện.")   


    # the status spectrum on a link  
    network.visualize_spectrum(('W1_0', 'S_0'))  
    
    # Plot the blocking probability   
    network.plot_blocking_probability(blocking_stats)  