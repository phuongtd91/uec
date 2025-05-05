import random
import numpy as np

# Constants
M = 10000  # Maximum number of demands
N = 12  # Number of Nodes
L = 34  # Number of directed Links
S = 320  # Maximum of slots per link
A = 600  # Traffic load
H = 10  # 1/mu average holding time
req_Max = 8  # Maximum demand size
K = 100 #?? the gap between each traffic


def main():
    t_req = [0] * (M + 1)  # +1 for t_req[i+1] access in the loop
    t_hold = [0] * M
    t_exp = [0] * M

    hops = [[0 for _ in range(N)] for _ in range(N)]
    link = [[0 for _ in range(N)] for _ in range(N)]

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
        with open(f"traffic_jpn12_{M}.txt", "w") as ofs1:
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

                # Generate source and destination
                source[i] = random.randint(0, N - 1)
                dest[i] = random.randint(0, N - 1)

                # slot_indx[i] = random.randint(0, S - lp_size[i])

                # Generate slot index
                '''
                Nếu source[j] == source[i] và slot_indx[j] in range (slot_indx[j], slot_indx[j] + lp_size[j]):
                    thì generate lại slot_indx[j]
                Hoặc không để cho nó giống nhau
                '''
                same_sources = list(filter(lambda x: x[1] == source[i], list_data))
                if same_sources:
                    same_source = same_sources[-1]
                    # print(same_source)
                    try:
                        slot_indx[i] = random.randint(0, S - same_source[1] - same_source[4])
                    except:
                        slot_indx[i] = random.randint(0, S - lp_size[i])
                else:
                    slot_indx[i] = random.randint(0, S - lp_size[i])

                # Ensure source and destination are different
                # while source[i] == dest[i]:
                #     dest[i] = random.randint(0, N - 1)

                # Calculate expiration time
                t_exp[i] = t_req[i] + t_hold[i]

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