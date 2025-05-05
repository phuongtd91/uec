# -*- coding: utf-8 -*-  
"""  
Created on Thu Nov 16 00:47:05 2023  

@author: phamg  
"""  
import numpy as np  
from itertools import islice  
import os  

def generate_traffic(N, L, S, A, H, req_Max=10):  
    """  
    Generate traffic for an EON node with constraints on slot allocation.  
    
    Parameters:  
    -----------  
    N : int  
        Number of nodes in the network  
    L : int  
        Number of links  
    S : int  
        Maximum number of slots per link  
    A : float  
        Offered load  
    H : float  
        Average holding time  
    req_Max : int, optional  
        Maximum demand size (default: 10)  
        
    Returns:  
    --------  
    list  
        Generated traffic requests with properties [t_req, t_hold, t_exp, source, dest, lp_size, slot_indx]  
    """  
    # Set random seeds for reproducibility  
    seed1 = 42  
    seed2 = 123  
    np.random.seed(seed1)  
    
    # Calculate arrival rate based on the offered load and holding time  
    lam = A / H  
    
    # Number of requests to generate  
    M = 10000  
    
    # Arrays to store request information  
    t_req = np.zeros(M)  
    t_hold = np.zeros(M)  
    t_exp = np.zeros(M)  
    source = np.zeros(M, dtype=int)  
    dest = np.zeros(M, dtype=int)  
    lp_size = np.zeros(M, dtype=int)  
    slot_indx = np.zeros(M, dtype=int)  
    
    # Track active slots per source to avoid blocking  
    # Dictionary to track occupied slots for each source  
    occupied_slots = {src: [] for src in range(N)}  
    
    # Generate interarrival times - exponential distribution  
    np.random.seed(seed1)  
    interarrival = np.random.exponential(1/lam, M-1)  
    
    # Calculate arrival times  
    t_req[0] = 0  
    t_req[1:] = np.cumsum(interarrival)  
    
    # Generate holding times - exponential distribution  
    np.random.seed(seed2)  
    t_hold = np.random.exponential(H, M)  
    t_exp = t_req + t_hold  
    
    # Generate traffic requests  
    for i in range(M):  
        # Clean up expired requests from occupied_slots  
        current_time = t_req[i]  
        for src in range(N):  
            occupied_slots[src] = [(end_time, start_slot, size) for end_time, start_slot, size in occupied_slots[src]   
                                if end_time > current_time]  
        
        # Generate source and destination (ensuring they are different)  
        available_sources = list(range(N))  
        np.random.shuffle(available_sources)  
        
        # Try each potential source until finding one with available slots  
        found_valid_source = False  
        for src in available_sources:  
            # Generate a random destination different from source  
            possible_destinations = [d for d in range(N) if d != src]  
            if not possible_destinations:  
                continue  
                
            dst = np.random.choice(possible_destinations)  
            
            # Generate lightpath size (between 1 and req_Max)  
            size = np.random.randint(1, req_Max + 1)  
            
            # Find available slot index that doesn't overlap with existing traffic  
            available_slots = find_available_slots(occupied_slots[src], S, size)  
            
            if available_slots:  
                # Randomly select one of the available slots  
                selected_slot = np.random.choice(available_slots)  
                
                # Record the request  
                source[i] = src  
                dest[i] = dst  
                lp_size[i] = size  
                slot_indx[i] = selected_slot  
                
                # Add to occupied slots for this source  
                occupied_slots[src].append((t_exp[i], selected_slot, size))  
                
                found_valid_source = True  
                break  
        
        # If no valid source found, use a random source and destination but mark with invalid slot  
        if not found_valid_source:  
            src = np.random.randint(0, N)  
            dst = np.random.choice([d for d in range(N) if d != src])  
            size = np.random.randint(1, req_Max + 1)  
            
            # Use -1 to indicate this request couldn't be served  
            source[i] = src  
            dest[i] = dst  
            lp_size[i] = size  
            slot_indx[i] = -1  # Mark as blocked request  
    
    # Create result array  
    result = []  
    for i in range(M):  
        if slot_indx[i] >= 0:  # Only include valid requests  
            result.append((t_req[i], t_hold[i], t_exp[i], source[i], dest[i], lp_size[i], slot_indx[i]))  
    
    return result  

def find_available_slots(occupied, total_slots, size):  
    """  
    Find all available slot indices that can accommodate a lightpath of given size  
    
    Parameters:  
    -----------  
    occupied : list  
        List of tuples (end_time, start_slot, size) representing occupied slots  
    total_slots : int  
        Total number of slots in the link  
    size : int  
        Size of the lightpath to place  
    
    Returns:  
    --------  
    list  
        List of available starting slot indices  
    """  
    # Mark all slots that are currently occupied  
    occupied_ranges = []  
    for _, start, sz in occupied:  
        occupied_ranges.append((start, start + sz - 1))  
    
    # Sort by start position  
    occupied_ranges.sort()  
    
    # Find all available slots  
    available = []  
    last_end = -1  
    
    for start, end in occupied_ranges:  
        # Check if there's space before this range  
        if start - last_end - 1 >= size:  
            # Add all possible starting positions in this gap  
            for pos in range(last_end + 1, start - size + 1):  
                available.append(pos)  
        last_end = max(last_end, end)  
    
    # Check space after the last occupied range  
    if total_slots - last_end - 1 >= size:  
        for pos in range(last_end + 1, total_slots - size + 1):  
            available.append(pos)  
    
    return available  

def generate_traffic_small(N=12, L=18, S=400, A=80, H=10, req_Max=10):  
    """  
    Generate a smaller traffic dataset for testing  
    """  
    # Similar to generate_traffic but with fewer requests  
    seed1 = 42  
    seed2 = 123  
    np.random.seed(seed1)  
    
    lam = A / H  
    M = 100  # Reduced number for testing  
    
    t_req = np.zeros(M)  
    t_hold = np.zeros(M)  
    t_exp = np.zeros(M)  
    source = np.zeros(M, dtype=int)  
    dest = np.zeros(M, dtype=int)  
    lp_size = np.zeros(M, dtype=int)  
    slot_indx = np.zeros(M, dtype=int)  
    
    # Track active slots per source  
    occupied_slots = {src: [] for src in range(N)}  
    
    # Generate interarrival times  
    np.random.seed(seed1)  
    interarrival = np.random.exponential(1/lam, M-1)  
    
    t_req[0] = 0  
    t_req[1:] = np.cumsum(interarrival)  
    
    # Generate holding times  
    np.random.seed(seed2)  
    t_hold = np.random.exponential(H, M)  
    t_exp = t_req + t_hold  
    
    # Generate traffic requests  
    for i in range(M):  
        # Clean up expired requests  
        current_time = t_req[i]  
        for src in range(N):  
            occupied_slots[src] = [(end_time, start_slot, size) for end_time, start_slot, size in occupied_slots[src]   
                                if end_time > current_time]  
        
        # Try all possible sources until finding one with available slots  
        available_sources = list(range(N))  
        np.random.shuffle(available_sources)  
        
        found_valid_source = False  
        for src in available_sources:  
            possible_destinations = [d for d in range(N) if d != src]  
            if not possible_destinations:  
                continue  
                
            dst = np.random.choice(possible_destinations)  
            size = np.random.randint(1, req_Max + 1)  
            
            available_slots = find_available_slots(occupied_slots[src], S, size)  
            
            if available_slots:  
                selected_slot = np.random.choice(available_slots)  
                
                source[i] = src  
                dest[i] = dst  
                lp_size[i] = size  
                slot_indx[i] = selected_slot  
                
                occupied_slots[src].append((t_exp[i], selected_slot, size))  
                
                found_valid_source = True  
                break  
        
        if not found_valid_source:  
            src = np.random.randint(0, N)  
            dst = np.random.choice([d for d in range(N) if d != src])  
            size = np.random.randint(1, req_Max + 1)  
            
            source[i] = src  
            dest[i] = dst  
            lp_size[i] = size  
            slot_indx[i] = -1  # Mark as blocked  
    
    # Create result array  
    result = []  
    for i in range(M):  
        if slot_indx[i] >= 0:  # Only include valid requests  
            result.append((t_req[i], t_hold[i], t_exp[i], source[i], dest[i], lp_size[i], slot_indx[i]))  
    
    return result  

def save_traffic_to_file(traffic, filename):  
    """  
    Save the generated traffic to a text file  
    
    Parameters:  
    -----------  
    traffic : list  
        List of traffic requests  
    filename : str  
        Name of the output file  
    """  
    with open(filename, 'w') as f:  
        # Write header  
        f.write("t_req\tt_hold\tt_exp\tsource\tdest\tlp_size\tslot_indx\n")  
        
        # Write data  
        for req in traffic:  
            f.write(f"{req[0]:.6f}\t{req[1]:.6f}\t{req[2]:.6f}\t{int(req[3])}\t{int(req[4])}\t{int(req[5])}\t{int(req[6])}\n")  

def generate_multiple_traffic_files(output_dir="traffic_data", N=12, L=18, S=400, req_Max=10):  
    """  
    Generate multiple traffic files with different load values  
    
    Parameters:  
    -----------  
    output_dir : str  
        Directory to save the output files  
    N : int  
        Number of nodes  
    L : int  
        Number of links  
    S : int  
        Maximum slots per link  
    req_Max : int  
        Maximum demand size  
    """  
    # Create output directory if it doesn't exist  
    if not os.path.exists(output_dir):  
        os.makedirs(output_dir)  
    
    # Generate traffic for different load values  
    load_values = [60, 70, 80, 90, 100, 110, 120]  
    H = 10  # Holding time  
    
    for A in load_values:  
        # Generate traffic  
        traffic = generate_traffic(N, L, S, A, H, req_Max)  
        
        # Create filename: traffic_N12_L18_S400_A{load}.txt  
        filename = f"traffic_N{N}_L{L}_S{S}_A{A}.txt"  
        filepath = os.path.join(output_dir, filename)  
        
        # Save to file  
        save_traffic_to_file(traffic, filepath)  
        
        print(f"Generated traffic file: {filename} with {len(traffic)} requests")  

# Test the modified code  
if __name__ == "__main__":  
    # Generate a small set of traffic for testing  
    traffic_small = generate_traffic_small()  
    save_traffic_to_file(traffic_small, "traffic_small_test.txt")  
    print(f"Generated small test traffic file with {len(traffic_small)} requests")  
    
    # Generate traffic files for different load values  
    generate_multiple_traffic_files()