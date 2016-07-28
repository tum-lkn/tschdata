import matplotlib.pyplot as plt
import numpy
from dataprocessing.basic_processor import BasicProcessor
from dataprocessing.toolbox import set_figure_parameters,set_box_plot
from dataprocessing.tsch_hopping_calculator import TSCHopping

set_figure_parameters()

def print_dataset_parameters():
    """
    TODO print all parameters nicely
    :return:
    """
    tot_packets = []
    duration = []
    tot_per_node_packets = []
    tot_per_channel_packets = []

    measurements_mote_lists = []
    measurements_channels_lists = []
    for i in range(1, 4):
        print("\n")

        d = BasicProcessor(filename="../../../WHData/Data/2008/Logs/%d.log" % i,
                   format="WHITENING")
        #LKN_measurements_190716

        tp=d.get_number_of_packets()
        dur = d.get_total_duration() / 60  # in minutes
        nodes_occurrences=d.get_seen_nodes()
        channels_occurrences=d.get_seen_channels()

        print("File log: %d.log" % i)
        print("Total duration [min]:\n", dur)
        print("Total number of packets:\n", tp)

        #print("Nodes occurrences:\n",nodes_occurrences)
        #print("Channels occurrences:\n", channels_occurrences)
        tot_avg_node_occurr = numpy.mean(list(nodes_occurrences.values()))
        tot_avg_channel_occurr = numpy.mean(list(channels_occurrences.values()))

        measurements_mote_lists.append(list(nodes_occurrences.values()))
        measurements_channels_lists.append(list(channels_occurrences.values()))

        print("Nodes occurrences (avg):\n", tot_avg_node_occurr)
        print("Channels occurrences (avg):\n", tot_avg_channel_occurr)

        tot_packets.append(tp)
        duration.append(dur)
        tot_per_channel_packets.append(tot_avg_channel_occurr)
        tot_per_node_packets.append(tot_avg_node_occurr)

    print("\n")
    print(duration)
    print(tot_per_node_packets)
    print(tot_per_channel_packets)
    print(tot_packets)

    fig = plt.figure()
    # Create an axes instance
    ax = fig.add_subplot(111)
    # Create the boxplot
    bp = ax.boxplot(measurements_mote_lists+measurements_channels_lists)
    set_box_plot(bp)

    ax.set_xticklabels(['Motes - Rnd', 'Ch - Rnd', 'Motes - White', 'Ch - White','Motes - Gld','Ch - Gld'])
    plt.title("Motes Channels occurrencies")
    plt.grid(True)
    plt.show()

def plot_channel_drops():
    """
    Test basic performance parameters for whitening measurements
    :return:
    """

    max_retxs = [4,1,4]
    for idx, label in enumerate(['Random', 'Whitelist', 'Golden']):
        p = BasicProcessor(filename="../../../WHData/Data/2008/Logs/%d.log" % (idx+1, ),
                       format="WHITENING")

        avg,ci = p.plot_windowed_channels_reliabilities("../../../WHData/Data/2008/Schedules/schedules_%d" % (idx+1,  )
                                                        ,max_retxs[idx], n_windows=50)
        # print(avg)
        # print(ci)
        # eb = plt.errorbar(x=[i for i in range(len(avg))], y=avg, yerr=ci, label=label, lw=1.5, capsize=10)
        # eb[-1][0].set_linewidth(1.5)
        #
        #p.plot_channels_reliability("../../../WHData/Data/2008/Schedules/schedules_%d" % (idx+1,  ),max_retxs[idx])

        # D=p.get_seen_nodes()
        #
        # plt.bar(range(len(D)), D.values(), align='center')
        # plt.xticks(range(len(D)), D.keys())

    plt.show()


def plot_per_mote_rel():
    """
    Test basic performance parameters for whitening measurements
    :return:
    """

    plt.figure()

    for idx, label in enumerate(['Random', 'Whitelist', 'Golden']):
        p = BasicProcessor(filename="../../../WHData/Data/2008/Logs/%d.log" % (idx+1, ),
                       format="WHITENING")

        p.correct_timeline()
        avg, ci = p.plot_motes_reliability(burst_size=11)
        print(avg)
        print(ci)
        eb = plt.errorbar(x=[i for i in range(len(avg))], y=avg, yerr=ci, label=label, lw=1.5, capsize=10)
        eb[-1][0].set_linewidth(1.5)


    plt.legend(loc=0)
    plt.grid(True)
    plt.show()

def plot_latencies():
    """
    TODO
    :return:
    """
    pass


def check_hopping(log_folder,schedule_folder):
    """
    Checks that frequencies in the log file are consistent with the specified schedule
    :param log_folder:
    :param schedule_folder:
    :return:
    """
    p = BasicProcessor(filename=log_folder,format="WHITENING")
    a = TSCHopping(schedule_folder)

    theoretical_freq = []
    measured_freq = []

    freq_mismatch = 0
    for pkt in p.packets:
        for hop in pkt.hop_info:
            f_th = a.calculate_frequency(hop['addr'], pkt.asn_last)
            f_meas = hop['freq']

            if f_meas != f_th:
                freq_mismatch += 1

            theoretical_freq.append(f_th)
            measured_freq.append(f_meas)
    print("[whitening.check_hopping]: There are %i frequencies mismatch\n" % freq_mismatch)

    return theoretical_freq, measured_freq


def plot_hopping():
    plt.figure()

    for idx, label in enumerate(['Random', 'Whitelist', 'Golden']):

        theoretical_freq, measured_freq = check_hopping("../../../WHData/Data/2008/Logs/%d.log" % (idx + 1,),
                                                        "../../../WHData/Data/2008/Schedules/schedules_%d" % (idx+1, ))

        #plt.figure()
        #plt.plot([theoretical_freq,measured_freq])
        # plt.plot(measured_freq)

    return


def boxplot_motes(motes_occurrencies):


    return

def check_timestamp():
    p = BasicProcessor(filename="../../../WHData/Data/2008/Logs/1.log",
                       format="WHITENING")

    prev_timestamp = 0;
    for pkt in p.packets:
        timestamp = int(pkt.timestamp)

        # Todo how to handle timestamp objects?
        if prev_timestamp < timestamp:
            prev_timestamp = timestamp
        else:
            print("Error")

    return


if __name__ == '__main__':
    plot_channel_drops()
    #check_timestamp()
    #print_dataset_parameters()
    #plot_per_mote_rel()
    #plot_hopping()

