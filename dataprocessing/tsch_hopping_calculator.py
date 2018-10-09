
import json
from dataprocessing.toolbox import get_all_files, Schedule


class TSCHopping:
    def __init__(self,full_path):
        print('Creating a TSCH hopper for %s' % full_path)

        foldername = full_path.split("/")[-1]
        folderpath = full_path[:-len(foldername)]
        files = get_all_files(folderpath,folders=[foldername])

        self.schedules = []
        for file in files:
            self.schedules.append(self.load_schedule(file))

        self.mote_net_map = {}
        for idx,schedule in enumerate(self.schedules):
            for a_slot in schedule.active_slots:
                mote_id = int(a_slot['address'].split(":")[-1][-2:],16)
                self.mote_net_map.__setitem__(mote_id,idx)


    def load_schedule(self,file):

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
            parsed_active_slots.append({'slot_offset': slot["slotOffset"], 'channel_offset': slot["channelOffset"], 'address': slot["address"]})
            mote_id = int(slot['address'].split(":")[-1][-2:], 16)
            mote_slot_map.__setitem__(mote_id,idx)

        return Schedule(len(active_slots),numslotoff,numserialrx,parsed_active_slots,hopping_sequence,mote_slot_map)

    def find_mote_info(self, mote_id):
        target_schedule = self.schedules[self.mote_net_map.get(mote_id)]
        hopping_sequence = target_schedule.hopping_sequence
        mote_active_slot = target_schedule.active_slots[target_schedule.mote_slot_map.get(mote_id)]
        channel_offset = mote_active_slot['channel_offset']
        return hopping_sequence, channel_offset

    def calculate_frequency(self, mote_id, asn):
        hopping_sequence,channel_offset = self.find_mote_info(mote_id)
        asn_offset = asn % 16
        return int(hopping_sequence[(asn_offset+channel_offset)%16])+11

    def calculate_dropped_frequency(self, mote_id, n_frames_ago, asn_last):
        target_schedule = self.schedules[self.mote_net_map.get(mote_id)]
        return self.calculate_frequency(mote_id, asn_last-n_frames_ago*target_schedule.frame_length)
