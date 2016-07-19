import matplotlib.pyplot as plt

from basic_processor import BasicProcessor


def plot_normalized_delay_per_application():
    """
    Plot delay for scenario / application: normalized per hop
    :return:
    """

    # --- folder one --- #
    folder = os.getcwd() + '/../' + 'tdma/'

    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    files = sorted(files)

    d_tdma = []

    for filename in files:
        p = BasicProcessor(filename=folder+filename)
        d_tdma.append(p.get_all_delays(motes=[2, 3, 4, 5, 6, 7, 8], normalized=True))
        d_tdma.append(p.get_all_delays(motes=[9, 10, 11], normalized=True))

    # --- folder two --- #
    folder = os.getcwd() + '/../' + 'shared/'

    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    files = sorted(files)

    d_shared = []

    for filename in files:
        p = BasicProcessor(filename=folder+filename)
        d_shared.append(p.get_all_delays(motes=[2, 3, 4, 5, 6, 7, 8], normalized=True))
        d_shared.append(p.get_all_delays(motes=[9, 10, 11], normalized=True))

    # --- folder two --- #

    fig = plt.figure(figsize=(7.5, 5.7))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    ax0 = fig.add_subplot(gs[0])
    bp_tdma = ax0.boxplot(d_tdma, showmeans=True, showfliers=False)

    x_axis = list(range(9))
    labels = ['', 'I(P)', 'I(B)', 'II(P)', 'II(B)', 'III(P)', 'III(B)', 'IV(P)', 'IV(B)']
    plt.xticks(x_axis, labels)

    # ylim((0, 4))
    grid(True)

    # plt.xlabel('Data set')
    plt.ylabel('Delay, s')

    set_box_plot(bp_tdma)

    ax1 = fig.add_subplot(gs[1])
    bp_shared = ax1.boxplot(d_shared, showmeans=True, showfliers=False)

    # ylim((0, 0.2))
    grid(True)

    # plt.xlabel('Data set')
    labels = ['', 'V(P)', 'V(B)', 'VI(P)', 'VI(B)', 'VII(P)', 'VII(B)', 'VIII(P)', 'VIII(B)']
    plt.xticks(x_axis, labels)

    plt.ylabel('Delay, s')

    set_box_plot(bp_shared)

    savefig('../../SGMeasurements/pics/app_delay.pdf', format='pdf', bbox='tight')
    show()


def plot_all_retx():
    """

    :return:
    """
    for folder in ['../tdma/', '../shared/']:
        files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
        files = sorted(files)
        for filename in files:
            p = BasicProcessor(filename=folder+filename)
            p.plot_retx()
    plt.show()


def plot_all_delays(cdf=False):
    """
    Plot delay for all packets, on the scenario basis
    :return:
    """
    # --- folder one --- #
    folder = os.getcwd() + '/../' + 'tdma/'

    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    files = sorted(files)

    d = []

    for filename in files:
        p = BasicProcessor(filename=folder+filename)
        d.append(p.get_all_delays())

    # --- folder two --- #
    folder = os.getcwd() + '/../' + 'shared/'

    files = [f for f in os.listdir(folder) if isfile(join(folder, f))]
    files = sorted(files)

    for filename in files:
        p = BasicProcessor(filename=folder+filename)
        d.append(p.get_all_delays())

    # --- folder two --- #

    if not cdf:

        figure(figsize=(7.5, 4))

        bp = boxplot(d, showmeans=True, showfliers=False)

        ylim((0, 2.5))
        grid(True)

        x_axis = list(range(9))
        labels = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
        plt.xticks(x_axis, labels)

        plt.xlabel('Data set')
        plt.ylabel('End-to-end delay, s')

        set_box_plot(bp)

        savefig('../../sgpaper/pics/all_delay.pdf', format='pdf', bbox='tight')
        show()
    else:

        figure(figsize=(7.5, 4))

        for data_set in d:

            ecdf = sm.distributions.ECDF(data_set)

            x = np.linspace(min(data_set), max(data_set))
            y = ecdf(x)

            plt.step(x, y)

            plt.xlim((0, 2.5))

        plt.show()


def plot_all_reliabilities():
    """
    Plot packet delivery ratio for all data sets
    :return:
    """
    rel = []
    avg = []
    f = open('seqn.csv', 'a+')
    wr = csv.writer(f, quoting=csv.QUOTE_ALL)

    for filename in get_all_files(gl_dump_path):
        p = BasicProcessor(filename=filename)
        p.correct_timeline(clean_all=False)
        p.plot_timeline(writer=wr)
        r, w = p.plot_reliability(return_result=True)
        rel.append(r)
        avg.append(w)

    f.close()

    plt.figure(figsize=(7.5, 3.5))
    bp = plt.boxplot(rel, flierprops={'linewidth':1.5}, showmeans=True)

    plt.hlines(0.95, xmin=0, xmax=9, linestyles='--', linewidth=1, label='0.95')
    x_axis = list(range(9))
    labels = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']

    plt.xticks(x_axis, labels)
    plt.grid(True)
    plt.ylim((0.35, 1.1))
    plt.legend(loc=4)

    plt.ylabel('PDR')

    set_box_plot(bp)

    plt.show()


def print_dataset_parameters():
    folders= ('tdma','shared')
    files= ('1-1-no_interference','2-1-interference','3-1-induced_interference','4-1-high_load')
    #files= ('no_interference','interference','induced_interference','high_load')

    tot_packets=[]
    duration=[]
    tot_per_node_packets=[]
    tot_per_channel_packets = []

    # create subplots
    # f, axs = plt.subplots(2,3)
    # f.subplots_adjust(hspace=0)

    k=1;
    for i,folder in enumerate(folders):
        for j,file in enumerate(files):

            path = gl_dump_path + folder + '/' + file + '.log'
            print(path)

            d = LogProcessor(filename=path)

            tp=d.get_total_packets()
            dur = d.get_total_duration() / 60  # in minutes
            nodes_occurrences=d.get_seen_nodes()
            channels_occurrences=d.get_seen_channels()
            links,link_occurrences=d.get_seen_links()
            links, link_rssis = d.get_seen_links(type="RSSI")


            print("\n")
            print(folder+'-'+file)

            print("Total duration [min]:\n", dur)
            print("Total number of packets:\n", tp)

            #print("Nodes occurrences:\n",nodes_occurrences)
            #print("Channels occurrences:\n", channels_occurrences)
            tot_avg_node_occurr = numpy.mean(list(nodes_occurrences.values()))
            tot_avg_channel_occurr = numpy.mean(list(channels_occurrences.values()))

            print("Nodes occurrences (avg):\n", tot_avg_node_occurr)
            print("Channels occurrences (avg):\n", tot_avg_channel_occurr)

            tot_packets.append(tp)
            duration.append(dur)
            tot_per_channel_packets.append(tot_avg_channel_occurr)
            tot_per_node_packets.append(tot_avg_node_occurr)

            p = TopologyLogProcessor(filename=path)


            #plt.figure(figsize=(15, 4))
            fig=plt.figure()
            # if folder is 'tdma':
            #     fig.suptitle(folder.upper() + '-' + file)
            # else:
            #     fig.suptitle(folder.title() + '-' + file)

            datafile = cbook.get_sample_data(os.getcwd()+"/images/LKN_plan_v0.3.jpg")

            #ax=plt.subplot(2,3,k)
            #ax.set_title((folder+'-'+file).title())
            k += 1
            img = imread(datafile)
            plt.imshow(img)#, zorder=0, extent=[0, 24.0, -1, 2.0])

            if j is 2:
                p.plot_sg_colormap(nodes=list(nodes_occurrences.keys()),node_weights=list(nodes_occurrences.values())
                            ,links=links,link_weights=link_occurrences,boolIF=True)
            else:
                p.plot_sg_colormap(nodes=list(nodes_occurrences.keys()), node_weights=list(nodes_occurrences.values())
                            , links=links, link_weights=link_occurrences, boolIF=False)

            # p.plot_sg_multi_colormap(nodes=list(nodes_occurrences.keys()),
            #                       node_weights=list(nodes_occurrences.values()),links1=links,
            #                      link_weights1=link_occurrences,links2=links,link_weights2=link_rssis)
            plt.tight_layout()
            plt.savefig("images/topology_colormap_"+folder+'_'+file+"FINAL.pdf", format='pdf')

            #break
        #break

    print(duration)
    print(tot_per_node_packets)
    print(tot_per_channel_packets)
    print(tot_packets)

    # plt.tight_layout()
    # plt.savefig("images/all_topologies_colormap.png")
    plt.show()


