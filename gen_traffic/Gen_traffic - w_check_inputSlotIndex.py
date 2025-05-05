import random
import numpy as np

# Constants
M = 10000       # Maximum number of demands
N = 16          # Number of Nodes
L = 34          # Number of directed Links
S = 320         # Maximum of slots per link
A = 500         # Traffic load
H = 10          # 1/mu average holding time
req_Max = 8     # Maximum demand size
K = 100         # the gap between each traffic to ensure no traffic come in the same time.

def main():
    t_req = [0] * (M + 1)  # +1 for t_req[i+1] access in the loop
    t_hold = [0] * M
    t_exp = [0] * M

    max_hold = 0

    seed1 = 123
    seed2 = 125

    slot_indx = [0] * M
    lp_size = [0] * M
    source = [0] * M
    dest = [0] * M

    # Random generators setup
    mu = 1.0 / H  # for exponentially-distributed duration with mean H=1/mu
    inter_arr = H / A  # Inter-arrival time for poisson distribution A=H/inter_arr

    random.seed(seed2)
    np.random.seed(seed1)

    # Open output file
    try:
        list_data = []
        active_traffic = {src: [] for src in range(N)}  # Track active traffic for each source

        with open(f"traffic_jpn12_{A}_01.txt", "w") as ofs1:
            # Initialize first arrival time
            t_req[0] = 0

            for i in range(M):
                # Generate holding time (exponential distribution)
                temp1 = np.random.exponential(1 / mu)
                t_hold[i] = int(K * temp1) + 1

                if max_hold < t_hold[i]:
                    max_hold = t_hold[i]

                # Generate arrival interval (Poisson)
                arr_int = np.random.poisson(K * inter_arr)

                # Generate traffic demand size
                lp_size[i] = random.randint(1, req_Max)
                # lp_size[i] = 30
                # Generate source and destination

                source[i] = random.randint(0, N - 1)
                dest[i] = random.randint(0, N - 1)


                # Generate slot index
                while True:
                    valid_slot_found = False
                    for _ in range(100):  # Try 100 times to find a valid slot
                        candidate_slot = random.randint(0, S - lp_size[i])
                        # Check if the candidate slot overlaps with active traffic
                        if all(
                            not (candidate_slot < t[0] and candidate_slot + lp_size[i] > t[0])
                            for t in active_traffic[source[i]]
                        ):
                            slot_indx[i] = candidate_slot
                            valid_slot_found = True
                            break

                    if valid_slot_found:
                        break
                    else:
                        # If no valid slot is found, randomly select another source
                        source[i] = random.randint(0, N - 1)

                # Calculate expiration time
                t_exp[i] = t_req[i] + t_hold[i]

                # Update active traffic for the source
                active_traffic[source[i]].append((slot_indx[i], lp_size[i], t_exp[i]))
                # Remove expired traffic
                active_traffic[source[i]] = [
                    t for t in active_traffic[source[i]] if t[2] > t_req[i]
                ]

                # Write to file
                list_data.append([i, source[i], dest[i], lp_size[i], slot_indx[i], t_req[i], t_hold[i]])
                ofs1.write(f"{i}: {source[i]} {dest[i]} {lp_size[i]} {slot_indx[i]} {t_req[i]} {t_hold[i]}\n")

                # Calculate next arrival time
                t_req[i + 1] = t_req[i] + arr_int

    except IOError:
        print("Cannot open input_demands1 file")
        return 1


if __name__ == "__main__":
    main()