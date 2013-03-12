
from monitor.helper import *
from math import fsum
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-f', dest='files', required=True, help='Input rates')
parser.add_argument('--out', '-o', dest='out', default=None, 
        help="Output png file for the plot.")

args= parser.parse_args()


''' Output of bwm-ng has the following format:
    unix_timestamp;iface_name;bytes_out;bytes_in;bytes_total;packets_out;packets_in;packets_total;errors_out;errors_in
    '''

traffics=['stag_prob_0_2_3_data', 'stag_prob_1_2_3_data', 'stag_prob_2_2_3_data',
        'stag_prob_0_5_3_data','stag_prob_1_5_3_data','stag_prob_2_5_3_data','stride1_data', 
        'stride2_data', 'stride4_data', 'stride8_data']

labels=['stag0(0.2,0.3)', 'stag1(0.2,0.3)', 'stag2(0.2,0.3)', 'stag0(0.5,0.3)',
        'stag1(0.5,0.3)', 'stag2(0.5,0.3)', 'stride1', 'stride2', 'stride4',
        'stride8']

traffics2=['random0_data', 'random1_data', 'random2_data', 'random0_bij_data', 'random1_bij_data', 
        'random2_bij_data', 'random_2_flows_data', 'random_3_flows_data', 'random_4_flows_data', 
        'hotspot_one_to_one_data']

def get_bisection_bw(input_file, pat_iface):
    pat_iface = re.compile(pat_iface)
    
    print input_file
    data = read_list(input_file)

    rate = {} 
    column = 3
        
    for row in data:
        try:
            ifname = row[1]
        except:
            break

        if ifname not in ['eth0', 'lo']:
            if not rate.has_key(ifname):
                rate[ifname] = []
            
            try:
                rate[ifname].append(float(row[column]) * 8.0 / (1 << 20))
            except:
                break
    vals = []
    for k in rate.keys():
        if pat_iface.match(k):       
            avg_rate = avg(rate[k][10:-10])
            print k,avg_rate
            vals.append(avg_rate)
            
    return fsum(vals)

def plot_results(args):

    fbb = 16. * 10  #160 mbps


    edge_sws = ['4_1_1']
    bb = { 'nonblocking' : {} }
    for t in traffics:
        input_file = args.files + '/nonblocking/%s/rate.txt' % t    
        vals = []
        for sw in edge_sws:
            vals.append(get_bisection_bw(input_file, sw))
        bb['nonblocking'][t] = fsum(vals)/fbb

    edge_sws = ['0_0_1', '0_1_1', '1_0_1', '1_1_1', '2_0_1','2_1_1', '3_0_1','3_2_1']
    bb['ecmp'] = {}
    for t in traffics:
        input_file = args.files + '/fattree-ecmp/%s/rate.txt' % t
        vals = []
        for sw in edge_sws:
            vals.append(get_bisection_bw(input_file, sw))
        bb['ecmp'][t] = fsum(vals)/fbb/2

    ind = np.arange(10)
    width = 0.2

    fig = plt.figure(1) 
    plt.ylim(0.0, 1.0)
    plt.ylabel('Normalized Average Bisection Bandwidth')
    
    # Nonblocking
    plt.xticks(ind + 3.5*width, labels, rotation=30)
    p1 = plt.bar(ind + 3.5*width, bb['nonblocking'].values(), width=width,
            color='blue')
    
    # FatTree + ECMP
    p2 = plt.bar(ind + 2.5*width, bb['ecmp'].values(), width=width, color='red')

    plt.legend([p1[0], p2[0]],['Non-blocking', 'ECMP'],loc='upper left')

    plt.savefig(args.out)

plot_results(args)
