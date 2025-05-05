#define M 100000         // Maximum number of demands

#define N 12            	// Number of Nodes. 
#define L 34		// Number of directed Links.
#define S 50		// Number of slots per link 	400

#define A 500		// Traffic load
#define H 10		// 1/mu average holding time
#define req_Max 6	// Maximum demand size			16

#define K 100

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <random>

using namespace std;

int main(void)
{
	int t_req[M], t_hold[M], t_exp[M];
	
	int hops[N][N];
	int link[N][N];

	int max_hold;
	
	unsigned seed1 = 123;
	unsigned seed2 =  125;

	int lp_size[M], source[M], dest[M];
	
	int i,j;
	int arr_int;
	double temp1;
	
	double mu = 1/double(H);  // for exponentially-distributed duration with mean H=1/mu
	double inter_arr = double(H)/A;  // Inter-arrival time for poisson distribution A=H/inter_arr
	
	srand (seed2);	// Use srand = time(NULL) to generate data that change every time
	
	default_random_engine generator (seed1);
	poisson_distribution<int> next_arr(K*inter_arr);  // 100* to clock the steps to a 10ms, does not change A, 
	exponential_distribution<double> hold_time(mu);	  // A = 100*H/100*inter_arriv 
	uniform_int_distribution<int> traff_dist(1, req_Max);
	
	ofstream ofs1;
    	ofs1.open("traffic_jpn12_.txt");
	if(!ofs1){
		cout<< "Cannot open input_demands1 file"<<endl;
		return 1;
	}
	
	//ofs1 << "mu and inter:=" << mu <<", "<<  inter_arr<< endl;
	//ofs1 << "LP number, s, d, size, Arrival time, holding time:=" << endl;
	
	max_hold = 0;
	t_req[0]= 0;
	
	for (int i=0; i<M; ++i){
		temp1 = hold_time(generator);
		t_hold[i] = int(K*temp1)+1;							//100*
		if(max_hold < t_hold[i]) max_hold = t_hold[i];
		arr_int = next_arr(generator);
		lp_size[i] = traff_dist(generator);
		source[i] = rand() %N;
		dest[i] = rand() %N;
			while(source[i] == dest[i]) dest[i] = rand() %N;
		t_exp[i] = t_req[i] + t_hold[i];
		ofs1 << i  << ": "<< source[i]  <<" " << dest[i]  <<" " << lp_size[i]  <<" " << t_req[i] <<" " << t_hold[i] << endl;
		t_req[i+1]= t_req[i] + arr_int;
	}
	
	//ofs1 << ":;"<< endl << endl;
	ofs1.close();
}