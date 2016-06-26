
import json
import fileinput
from toolbox import set_box_plot, set_figure_parameters, get_all_files

# class mote_info:
#     def __init__(self, mote_id, time):
#
# class active_slot:
#     def __init__(self, time, freq, id):
#         self.time = time
#         self.freq = freq
#         self.id = id

class net_schedule:
    def __init__(self, slotframe_length, n_active_slots, hopping_seq,m_slot_map):
        self.hopping_sequence=hopping_seq
        self.slotframe_length = slotframe_length
        self.active_slots = n_active_slots
        self.mote_slot_map = m_slot_map

class TSCH_hopping:
    def __init__(self,foldername):
        print('Creating a TSCH frame for %s' % foldername)

        # TODO define a variable size dictionary motes_list = {'mote_id' : network}

        files = get_all_files(foldername,folders=['schedules_lkngolden'])
        #print(files)

        self.schedules = []
        for file in files:
            self.schedules.append(self.load_schedule(file))

        self.mote_net_map = {}
        for idx,schedule in enumerate(self.schedules):
            for a_slot in schedule.active_slots:
                splitted_addr = a_slot['address'].split(":")
                self.mote_net_map.__setitem__(splitted_addr[-1],idx)

        print('all loaded')

    def load_schedule(self,file):
        print("Loading schedule "+file)

        # read and parse config
        config = read_config(file)

        active_slots = config["active_slots"]
        numserialrx = config["numserialrx"]
        numslotoff = config["numslotoff"]

        slotframe_length = len(active_slots) + numserialrx + numslotoff

        hopping_sequence = config["hopping_seq"].split(',')

        mote_slot_map = {}
        parsed_active_slots = []
        for idx,slot in enumerate(active_slots):
            #parsed_active_slots.append(active_slot(slot["slotOffset"],slot["channelOffset"],slot["address"]))
            parsed_active_slots.append({'slot_offset': slot["slotOffset"], 'channel_offset': slot["channelOffset"], 'address': slot["address"]})
            mote_slot_map.__setitem__(slot["address"].split(':')[-1],idx)

        return net_schedule(slotframe_length,parsed_active_slots,hopping_sequence,mote_slot_map)

        #app_enabled = config["app_enabled"]

        #app_type = config["app_type"]

        #app_dest_addr = config["app_dest_addr"]

    def find_mote_info(self, mote_id):
        target_schedule = self.schedules[self.mote_net_map.get(mote_id)]
        hopping_sequence = target_schedule.hopping_sequence
        mote_active_slot = target_schedule.active_slots[target_schedule.mote_slot_map.get(mote_id)]
        channel_offset = mote_active_slot['channel_offset']
        return hopping_sequence, channel_offset

    def calculate_frequency(self, mote_id, asn):
        hopping_sequence,channel_offset = self.find_mote_info(mote_id)
        asn_offset = asn % 16
        return 11 + int(hopping_sequence[(asn_offset+channel_offset)%16])




def read_config(fname):
    """
    Read configuration file as json object
    :param fname: file to read from
    :return: list of dicts
    """

    with open(fname) as data_file:
        data = json.load(data_file)

    # pprint(data)

    return data

if __name__ == '__main__':
    for i in range(1, 2):
        #filename= "../../WHData/Data/triagnosys/%d.log" % i
        foldername="../../WHData/Data/Schedules/"
        a = TSCH_hopping(foldername)

        mote_id = '0x1a'
        ASN = 1000
        freq = a.calculate_frequency(mote_id,ASN)

        print("The frequency used by "+mote_id+" to transmit in ASN %d" % ASN+" is %d " % freq)