import os
import csv
import sys
import json
import glob
import ephem
import signal
import codecs
import guano
import struct
import requests
import configparser
from astral.sun import sun
from astral import LocationInfo
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import time
from datetime import timedelta
from datetime import datetime as dt

class Talon:
    def __init__(self):
        pass

    def generate_timeseries_graph(self, events: list, outfile="timeseries.png", frequency=5, ymax=None):
        """
        Generate a frequency graph of supplied events.

        Args:
            events (list): A list of event dicts which we'll use to generate the graph.
            start_dt (datetime): The start time of data we wish to graph.
            stop_dt (datetime): The stop time of data we wish to graph.
            frequency (int): The time duration (minutes) we'll lump events into for the graph. 
            title (str): The title of the graph.
            ymax (int): Maximum height of the chart (minimum is the bucket with the most events).
            tz (str): The time zone of the data.
        """
        import math
        import matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.ticker as tck
        import matplotlib.dates as mdates

        matplotlib.use('agg')

        rollavg = []
        buckets = []
        totals = []
        labels = []

        evts = sorted(events, key=lambda d: d['dt'])
        start_dt = evts[0]['dt']
        stop_dt = evts[-1]['dt']
        
        title = ''

        # TODO: maxticks is 1000, so we need to ensure that we don't generate more than 1000 ticks
        # 
        if ymax is None:
            max_value = 0
        else:
            max_value = ymax

        # create the frequency buckets before we iterate events
        if frequency > 0:
            # print(f"(({stop_dt} - {start_dt}).total_seconds() / 60) / {frequency}")
            # print((stop_dt - start_dt).total_seconds())
            start = start_dt.replace(minute=0, second=0, microsecond=0)
            stop = stop_dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1, minutes=frequency)

            # TODO: need to adjust numbuckets to under 1000 which is maxticks,
            # need to adjust interval accordingly
            numbuckets = int(((stop - start).total_seconds() / 60) / frequency)
            interval = timedelta(minutes=frequency)

            # zero out start date so we can start on the hour and have our
            # x-axis labels look nice
            # cur = start_dt.replace(minute=0, second=0, microsecond=0)

            # initialize buckets
            for i in range(0, numbuckets):
                buckets.append(start)
                totals.append(0)

                tmp = start + interval

                for event in evts:
                    # if DEBUG:
                    #     print(f"({event['dt']} >= {start})={event['dt'] >= start} and ){event['dt']} < {tmp})={event['dt'] < tmp}")

                    if event['dt'] >= start and event['dt'] < tmp:
                        totals[i] += 1

                start = tmp

            # add datetime labels
            for bucket in buckets:
                labels.append(bucket)
                # print(bucket)

            # if DEBUG:
            #     print(f"numbuckets: {numbuckets}, interval: {interval}")

            #     for i in range(0, numbuckets):
            #         print(labels[i], totals[i])

        for i in range(numbuckets):
            # handle averaging the starting and ending buckets by making them 0
            if i == 0 or i == numbuckets-1:
                rollavg.append(0)
            else:
                rollavg.append((totals[i-1] + totals[i] + totals[i+1])/3)

        for i in rollavg:
            if i > max_value:
                max_value = math.ceil(i / 10.0) * 10

        title += f"{frequency * 3}-Minute Rolling Average"
        title += f"\n{buckets[0].strftime('%m/%d/%Y %H:%M:%S%z')} - {buckets[-1].strftime('%m/%d/%Y %H:%M:%S%z')}"

        fig, ax = plt.subplots(figsize=(32, 18))
        plt.grid()

        plt.ylim(0, max_value)

        # This trims the x-axis, which we don't necessarily want. May need
        # to turn this into an option (e.g., --x-trim)
        # plt.xlim(buckets[0], buckets[-1])
        plt.rcParams['timezone'] = 'US/Eastern'

        # Format the x-axis labels as dates
        # date_format = mdates.DateFormatter("%H:%M:%S", tz=pytz.timezone(tz))
        date_format = mdates.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(date_format)

        # TODO: For long time periods, switch to using hourlocator instead,
        # maybe try and keep the x-labels fewer than 30.
        # ax.xaxis.set_major_locator(mdates.HourLocator(byhour=2,interval=1))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0,30]))

        plt.xlabel('Time', fontsize=24, labelpad=30)
        plt.ylabel('Detections', fontsize=24, labelpad=30)
        plt.title(title, fontsize=32, pad=30)
        plt.xticks(fontsize=16, rotation=60)
        plt.yticks(fontsize=16)
        plt.plot(labels, rollavg)
        plt.fill_between(labels, rollavg, alpha=0.3)

        plt.savefig(outfile, pad_inches=0.5, bbox_inches='tight')
        plt.close()

class TalonConfigError(Exception):
    """A custom exception for specific errors in MyClass."""
    pass

class TalonFileNotFoundError(Exception):
    """A custom exception for specific errors in MyClass."""
    pass

class TalonConfig:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        
        self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                self.config = configparser.ConfigParser()
                # codecs is needed because the RØDE is unicode
                self.config.read_file(codecs.open(self.config_path, 'r', 'utf8'))
                # self.config.read(self.config_path)
            except configparser.ParsingError as e:
                print(f"Error parsing config, invalid value specified for: {e}")
                sys.exit(1)

class TalonGuanoFile:
    def __init__(self, wavfile, config, clear=False):
        self.config = config
        self.cur_gf = None
        self.old_gf = None
        self.wavfile = wavfile
        self.clear = clear
        self.filename = os.path.basename(self.wavfile)

        # We're assuming the name is underscore separated and
        # that the first field matches a section in the config
        self.station = self.filename.split('_')[0]

        # if the first field doesn't match, then raise a custom exception
        if self.station in self.config:
            self.timestamp = dt.strptime(str(self.filename), self.config[self.station]['file_format'])
            
            if 'NFC|Time Zone' in self.config[self.station]:
                self.tz = ZoneInfo(self.config[self.station]['NFC|Time Zone'])
                self.timestamp.astimezone(self.tz)
        else:
            raise TalonConfigError(f"Section not found in config file: {self.station}")

        # ensure the file exists before proceeding
        if os.path.exists(self.wavfile):
            self._load_guano()
        else:
            raise TalonFileNotFoundError(f"File not found: {self.wavfile}")

    def _load_guano(self):
        self.old_gf = guano.GuanoFile(self.wavfile)
        self.gf = guano.GuanoFile(self.wavfile)
        keys = []

        if len(self.gf.to_string()) > 0:
            for key, value in self.gf.items():
                keys.append(key)

            for key in keys:
                del(self.gf[key])

        if len(self.gf.to_string()) == 0:
            self.gf['Loc Elevation'] = self.config[self.station]['elevation']
            self.gf['Loc Position'] = (float(self.config[self.station]['latitude']), float(self.config[self.station]['longitude']))
            self.gf['Make'] = self.config[self.station]['Make']
            self.gf['Model'] = self.config[self.station]['Model']
            self.gf['Serial'] = self.config[self.station]['Serial']
            self.gf['Original Filename'] = self.filename
            self.gf['Note'] = self.config[self.station]['note']
            self.gf['Timestamp'] = self.timestamp
            self.gf['NFC|Moon Phase'] = ephem.Moon(self.timestamp).moon_phase
            self.gf['NFC|Station Name'] = self.config[self.station]['name']
            self.gf['NFC|Time Zone'] = self.config[self.station]['timezone']
            # self.gf['NFC|Temperature'] = 'NA'
            # self.gf['NFC|Humidity'] = 'NA'
            # self.gf['NFC|Wind Direction'] = 'NA'
            # self.gf['NFC|Wind Speed'] = 'NA'
            # self.gf['NFC|Pressure'] = 'NA'
            # self.gf['NFC|Visibility'] = 'NA'
            self.gf['NFC|Copyright'] = self.config[self.station]['copyright']
            self.gf['NFC|Location'] = self.config[self.station]['location']

    def write(self):
        self.gf.write(make_backup=False)
    
    def __str__(self):
        output = ""

        if len(self.old_gf.to_string()) > 0:
            output += "Old GUANO header\n"
            output += '-' * 60 + '\n'

            for key, value in self.old_gf.items():
                output += f"{key}: {value}\n"
        else:
            output += "No existing GUANO header detected.\n"

        output += "\nNew GUANO header\n"
        output += '-' * 60 + '\n'

        for key, value in self.gf.items():
            output += f"{key}: {value}\n"
        
        return output.strip()

class TalonWAVFile:
    def __init__(self, filename, section=None, taxonomy=None, clear=False, debug=False):
        self.metadata = {}
        self._filename = filename
        self._section = section
        self._taxonomy = taxonomy
        self.metadata['Section'] = {}
        self.metadata['File Name'] = os.path.basename(self._filename)
        self.metadata['Events'] = []
        self._guano = None
        self.riff_hdr_sz = 12
        self._debug = debug

        if self._section:
            self._curtz = ZoneInfo(self._section['timezone'])
            self._timestamp = dt.strptime(str(os.path.basename(self._filename)), self._section['file_format'])
            self._timestamp.astimezone(self._curtz)

            for key in section:
                self.metadata['Section'][key] = section[key]

        if os.path.exists(self._filename):
            self.metadata['Modified Time'] = dt.fromtimestamp(os.stat(self._filename).st_mtime).isoformat()
            self._read_header()

    def GetEvents(self):
        self._get_events()

    def SaveEvents(self):
        self._save_ta_events()

    def _get_chunk(self, fp):
        chunk = []
        data = fp.read(8)

        if len(data) == 8:
            chunk_id = data[0:4].decode()
            chunk_sz = int.from_bytes(data[4:8], byteorder='little')

            # if chunk_sz is odd, then we need to add 1 to account
            # for the null padding byte
            chunk_sz += chunk_sz % 2
            chunk = [ chunk_id, chunk_sz ]

        return chunk

    def _json_serializer(self, obj):
        # keep datetimes natively in the dict, but auto convert them
        # to iso formatted datetimes for printing or json dumping
        if isinstance(obj, (dt)):
            return obj.isoformat()

        # any byte strings we get from the various chunks will be non-
        # printable, so convert them to hex in a format similar to xxd
        if isinstance(obj, (bytes)):
            return obj.hex(' ', 2)

        raise TypeError ("Type %s not serializable" % type(obj))

        try:
            with open(self._filename, 'rb') as f:
                data = f.read(self.riff_hdr_sz)

                self.metadata['Actual Size'] = os.stat(self._filename).st_size
                self.metadata['File Type'] = data[0:4].decode()
                self.metadata['Reported Size'] = int.from_bytes(data[4:8], byteorder='little') + 8
                self.metadata['Format'] = data[8:12].decode()

                if self.metadata['File Type'] == 'RIFF' and self.metadata['Format'] == 'WAVE':
                    cur_chunk = self._get_chunk(f)

                    while cur_chunk:
                        if cur_chunk[1] > 0:
                            if cur_chunk[0] == 'fmt ':
                                data = f.read(cur_chunk[1])

                                self.metadata['fmt'] = {}

                                if self._debug:
                                    self.metadata['fmt']['Chunk Name'] = cur_chunk[0]
                                    self.metadata['fmt']['Chunk Size'] = cur_chunk[1]
        
                                self.metadata['fmt']['Format'] = int.from_bytes(data[0:2], byteorder='little')
                                self.metadata['fmt']['Channels'] = int.from_bytes(data[2:4], byteorder='little')
                                self.metadata['fmt']['Frequency'] = int.from_bytes(data[4:8], byteorder='little')
                                self.metadata['fmt']['Bytes/sec'] = int.from_bytes(data[8:12], byteorder='little')
                                self.metadata['fmt']['Bytes/blc'] = int.from_bytes(data[12:14], byteorder='little')
                                self.metadata['fmt']['Bits/smp'] = int.from_bytes(data[14:16], byteorder='little')
                            elif cur_chunk[0] == 'guan':
                                data = f.read(cur_chunk[1])
                                # TODO: create a method to write guano data ourselves, probably
                                # at the end of the file
                                self._guano = guano.GuanoFile.from_string(data)

                                gd = {}

                                # we can read the guano data ourselves now
                                for item in data.decode().split('\n'):
                                    if len(item) > 0:
                                        key, val = item.split(': ')

                                        # parse namespaces as dicts
                                        if '|' in key:
                                            key, subkey = key.split('|')

                                            if key not in gd:
                                                gd[key] = {}
                                            
                                            gd[key][subkey] = val
                                        else:
                                            gd[key] = val

                                self.metadata['guan'] = gd
                            elif cur_chunk[0] == 'data':
                                # don't need to read the entire data chunk into memory
                                # as it may be very large, just record the size and
                                # skip to the next chunk
                                offset = f.tell()
                                f.seek(cur_chunk[1], 1)

                                self.metadata['data'] = {}
                                self.metadata['data']['Offset'] = offset

                                if self._debug:
                                    self.metadata['data']['Chunk Name'] = cur_chunk[0]
    
                                self.metadata['data']['Chunk Size'] = cur_chunk[1]
                            elif cur_chunk[0] == 'bext':
                                data = f.read(cur_chunk[1])

                                bext_date = data[320:330].decode()
                                bext_time = data[330:338].decode()
                                # self.bext_start = dt.fromisoformat(f'{bext_date} {bext_time}')

                                self.metadata['bext'] = {}

                                if self._debug:
                                    self.metadata['bext']['Chunk Name'] = cur_chunk[0]
                                    self.metadata['bext']['Chunk Size'] = cur_chunk[1]
        
                                self.metadata['bext']['Originator'] = data[256:287].decode().split('\x00')[0]
                                self.metadata['bext']['Originator Date'] = data[320:330].decode().split('\x00')[0]
                                self.metadata['bext']['Originator Time'] = data[330:338].decode().split('\x00')[0]
                                self.metadata['bext']['End Time'] = f'{bext_date} {bext_time}'
                            elif cur_chunk[0] == 'cue ':
                                data = f.read(cur_chunk[1])

                                self.metadata['cue'] = {}

                                if self._debug:
                                    self.metadata['cue ']['Chunk Name'] = cur_chunk[0]
                                    self.metadata['cue ']['Chunk Size'] = cur_chunk[1]
                            elif cur_chunk[0] == 'LIST':
                                data = f.read(cur_chunk[1])
                                fp = 0

                                self.metadata['LIST'] = {}

                                if self._debug:
                                    self.metadata['LIST']['Chunk Name'] = cur_chunk[0]
                                    self.metadata['LIST']['Chunk Size'] = cur_chunk[1]
                                
                                if data[fp:fp+4].decode() == 'INFO':
                                    self.metadata['LIST']['INFO'] = {}
                                    fp += 4

                                    while fp < cur_chunk[1]:

                                        cur_name = data[fp:fp+4].decode()
                                        cur_size = int.from_bytes(data[fp+4:fp+8], byteorder='little')
                                        cur_data = data[fp+8:fp+8+cur_size].decode()

                                        self.metadata['LIST']['INFO'][cur_name] = {}

                                        if self._debug:
                                            self.metadata['LIST']['INFO'][cur_name]['Chunk Name'] = cur_name
                                            self.metadata['LIST']['INFO'][cur_name]['Chunk Size'] = cur_size
        
                                        self.metadata['LIST']['INFO'][cur_name]['Chunk Data'] = cur_data.split('\x00')[0]

                                        fp += cur_size + 8
                            elif cur_chunk[0] == 'wamd':
                                data = f.read(cur_chunk[1])

                                self.metadata['wamd'] = {}

                                if self._debug:
                                    self.metadata['wamd']['Chunk Name'] = cur_chunk[0]
                                    self.metadata['wamd']['Chunk Size'] = cur_chunk[1]
                            elif cur_chunk[0] == 'id3 ':
                                data = f.read(cur_chunk[1])

                                self.metadata['id3'] = {}
                                
                                if self._debug:
                                    self.metadata['id3']['Chunk Name'] = cur_chunk[0]
                                    self.metadata['id3']['Chunk Size'] = cur_chunk[1]
                            elif cur_chunk[0] == 'iXML ':
                                data = f.read(cur_chunk[1])

                                self.metadata['iXML'] = {}

                                if self._debug:
                                    self.metadata['iXML']['Chunk Name'] = cur_chunk[0]
                                    self.metadata['iXML']['Chunk Size'] = cur_chunk[1]
                            else:
                                f.seek(cur_chunk[1], 1)

                            cur_chunk = self._get_chunk(f)
                        else:
                            print(f'Warning {cur_chunk[0]} chunk with a size of 0 detected in {self.metadata["File Name"]}')

                            # TODO: Handle this better as cur_chunk[0] may be binary data and thus unsafe
                            self.metadata[cur_chunk[0]] = {}
                            self.metadata[cur_chunk[0]]['Chunk Size'] = cur_chunk[1]
                            break

                self.metadata['Duration'] = self.metadata['data']['Chunk Size'] / self.metadata['fmt']['Bytes/sec']
        except FileNotFoundError:
            print(f"Error: File '{self._filename}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def __str__(self):
        events = self.metadata['Events']

        for event in events:
            event['dt'] = event['dt'].isoformat()

        return json.dumps(self.metadata, indent=4, sort_keys=True)

    def to_dict(self):
        return {
            "File name": self.file_name
        }

    def _get_events(self, force=False):
        nh_ext = '_detections.csv'
        bn_ext ='.BirdNET.selection.table.txt'
        ta_ext = '_talon.csv'

        dest_path, filename = os.path.split(self._filename)
        filename, extension = os.path.splitext(filename)

        bn_file = os.path.join(dest_path, str(filename) + bn_ext)
        nh_file = os.path.join(dest_path, str(filename) + nh_ext)
        ta_file = os.path.join(dest_path, str(filename) + ta_ext)

        # print(len(self.metadata['Events']))
        self._get_nh_events(nh_file)
        # print(len(self.metadata['Events']))
        self._get_bn_events(bn_file)
        # print(len(self.metadata['Events']))
        self._get_ta_events(ta_file)
        # print(len(self.metadata['Events']))

        important_dates = {}

        for event in self.metadata['Events']:
            curdate = event['dt'].date()
            eventtime = event['dt']

            if curdate not in important_dates:
                important_dates[curdate] = {}

                location=LocationInfo(name='', region='', timezone=self._section['timezone'], latitude=self._section['latitude'], longitude=self._section['longitude'])
                important_dates[curdate]['astrodawn'] = sun(location.observer, date=curdate, dawn_dusk_depression=18, tzinfo=self._curtz)['dawn'].replace(microsecond=0)
                important_dates[curdate]['astrodusk'] = sun(location.observer, date=curdate, dawn_dusk_depression=18, tzinfo=self._curtz)['dusk'].replace(microsecond=0)
                important_dates[curdate]['sunset'] = sun(location.observer, date=curdate, tzinfo=self._curtz)['sunset'].replace(microsecond=0) + timedelta(minutes=20)
                important_dates[curdate]['sunrise'] = sun(location.observer, date=curdate, tzinfo=self._curtz)['sunrise'].replace(microsecond=0) - timedelta(minutes=40)

            # astrodawn/astrodusk are calculated for the day of each event, which means
            # we're comparing against a non-contiguous range of time (e.g., the end of
            # last night or the beginning of tonight)
            if eventtime >= important_dates[curdate]['sunset'] or eventtime < important_dates[curdate]['sunrise']:
                if eventtime >= important_dates[curdate]['astrodusk'] or eventtime < important_dates[curdate]['astrodawn']:
                    event['protocol'] = "nfc"
                else:
                    event['protocol'] = "noc"
            else:
                event['protocol'] = "day"

            event['station'] = self._section.name
            # self.metadata['Events'] = sorted(self.metadata['Events'], key=lambda d: d['dt'])

        self.metadata['Events'] = sorted(self.metadata['Events'], key=lambda d: d['dt'])

    def _get_nh_events(self, nh_file):
        if os.path.exists(nh_file):
            with open(nh_file) as f:
                for det in [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]:
                    try:
                        delta = timedelta(seconds=float(det['start_sec']))
                        abstime = self._timestamp + delta

                        if not abstime.tzinfo:
                            abstime = abstime.astimezone(self._curtz)

                        # add relative, to the wav file, start time
                        mins, secs = divmod(float(det['start_sec']), 60)
                        hours, mins = divmod(mins, 60)
                        start_rel = f"{int(hours):02d}:{int(mins):02d}:{secs:05.2f}"

                        if det['predicted_category'] in self._taxonomy:
                            common_name = self._taxonomy[det['predicted_category']]
                        else:
                            common_name = det['predicted_category']

                        self.metadata['Events'].append(
                            { 
                                'filename': str(self._filename),
                                'dt': abstime,
                                'start_rel': start_rel,

                                'start': float(det['start_sec']),
                                'stop': float(det['end_sec']),
                                'engine': 'nh',
                                'species_code': det['predicted_category'],
                                'common_name': common_name,
                                'probability': float(det['prob']),

                                'orig_start': float(det['start_sec']),
                                'orig_stop': float(det['end_sec']),
                                'orig_engine': 'nh',
                                'orig_species': det['predicted_category'],
                                'orig_common_name': common_name,
                                'orig_probability': float(det['prob']),

                                'disposition': 'unconfirmed',
                                'overridden': False,
                                'curated': False
                            }
                        )

                    except TypeError as e:
                        print(f"TypeError: {e}")
        else:
            if self._debug:
                print(f"Unable to locate: {nh_file}")

    def _get_bn_events(self, bn_file):
        if os.path.exists(bn_file):
            with open(bn_file) as f:
                for det in [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True, delimiter='\t')]:
                    try:
                        delta = timedelta(seconds=float(det['Begin Time (s)']))
                        abstime = self._timestamp + delta

                        if not abstime.tzinfo:
                            abstime = abstime.astimezone(self._curtz)

                        # add relative, to the wav file, start time
                        mins, secs = divmod(float(det['Begin Time (s)']), 60)
                        hours, mins = divmod(mins, 60)
                        start_rel = f"{int(hours):02d}:{int(mins):02d}:{secs:05.2f}"

                        if det['Species Code'] in self._taxonomy:
                            common_name = self._taxonomy[det['Species Code']]
                        else:
                            common_name = det['Common Name']

                        self.metadata['Events'].append(
                            {
                                'filename': str(self._filename),
                                'dt': abstime,
                                'start_rel': start_rel,

                                'start': float(det['Begin Time (s)']),
                                'stop': float(det['End Time (s)']),
                                'engine': 'bn',
                                'species_code': det['Species Code'],
                                'common_name': common_name,
                                'probability': float(det['Confidence']),
                                
                                'orig_start': float(det['Begin Time (s)']),
                                'orig_stop': float(det['End Time (s)']),
                                'orig_engine': 'bn',
                                'orig_species': det['Species Code'],
                                'orig_common_name': common_name,
                                'orig_probability': float(det['Confidence']),

                                'disposition': 'unconfirmed',
                                'overridden': False,
                                'curated': False
                            }
                        )

                    except TypeError as e:
                        print(f"TypeError: {e}")
                        print(det)

    def _get_ta_events(self, ta_file):
        if os.path.exists(ta_file):
            remove_list = []

            try:
                with open(ta_file) as f:
                    for det in [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]:
                            delta = timedelta(seconds=float(det['start']))
                            abstime = self._timestamp + delta
                            det_orig_start = float(det['orig_start'])
                            det_orig_stop = float(det['orig_stop'])

                            if not abstime.tzinfo:
                                abstime = abstime.astimezone(self._curtz)

                            # add relative, to the wav file, start time
                            mins, secs = divmod(float(det['start']), 60)
                            hours, mins = divmod(mins, 60)
                            start_rel = f"{int(hours):02d}:{int(mins):02d}:{secs:05.2f}"

                            if det['species_code'] in self._taxonomy:
                                common_name = self._taxonomy[det['species_code']]
                            else:
                                common_name = det['common_name']

                            # iterate all events and remove any that are overridden by the user
                            for event in self.metadata['Events']:
                                if det_orig_start == event['start'] and det_orig_stop == event['stop'] and det['orig_engine'] == event['engine'] and det['orig_species'] == event['species_code']:
                                    # print(f"{det_orig_start}={event['start']}, {det_orig_stop}={event['stop']}, {det['orig_engine']}={event['engine']}, {det['orig_species']}={event['species_code']}, {common_name}")

                                    # print(len(self.metadata['Events']))
                                    remove_list.append(event)
                                    # self.metadata['Events'].remove(event)
                                    # print(len(self.metadata['Events']))


                            
                            if det['overridden'] == 'True':
                                engine = 'ta'
                            elif det['orig_engine'] != '':
                                engine = det['orig_engine']

                            cur = { 
                                    'filename': det['filename'],
                                    'dt': abstime,
                                    'start_rel': start_rel,

                                    'start': float(det['start']),
                                    'stop': float(det['stop']),
                                    'engine': engine,
                                    'species_code': det['species_code'],
                                    'common_name': common_name,
                                    'probability': float(det['probability']),

                                    'orig_start': float(det['orig_start']),
                                    'orig_stop': float(det['orig_stop']),
                                    'orig_engine': det['orig_engine'],
                                    'orig_species': det['orig_species'],
                                    'orig_common_name': det['orig_common_name'],
                                    'orig_probability': float(det['orig_probability']),

                                    'disposition': det['disposition'],
                                    'overridden': (det['overridden'] == 'True'),
                                    'curated': True
                            }

                            self.metadata['Events'].append(cur)

                for item in remove_list:
                    self.metadata['Events'].remove(item)
            except TypeError as e:
                print(f"TypeError: {e}")
            except KeyError as e:
                print(f"Error processing {ta_file}: {e}")

    def _save_ta_events(self):
        # TODO: when saving events, remove any unconfirmed which have an old_engine of nh/bn
        # also, don't add a new entry when updating a ta event, just overwrite that row
        dest_path, filename = os.path.split(self._filename)
        filename, extension = os.path.splitext(filename)
        ta_file = os.path.join(dest_path, str(filename) + '_talon.csv')

        # ta_fields = [ 'filename', 'dt', 'probability', 'species_code', 'engine', 'start', 'start_rel', 'stop', 'common_name', 'disposition', 'orig_dt', 'orig_species_code', 'orig_engine', 'orig_station' ]

        ta_fields = [ 'filename', 'dt', 'probability', 'species_code', 'engine', 'start', 'start_rel', 'stop', 'common_name', 'disposition', 'orig_dt', 'orig_species_code', 'orig_engine', 'orig_station' ]
        events = [d for d in self.metadata['Events'] if d['engine'] in [ 'nh' ]]

        print(events)

        # with open(ta_file, "w", newline="") as file:
        #     writer = csv.DictWriter(file, fieldnames=ta_fields)
        #     writer.writeheader()

        #     # for ev in events:
        #     #     print(ev)
        #     #     writer.writerow(ev)

        #     writer.writerows(events)

    def _write_guano_data(self, write=False):
        keys = []

        # delete all existing guano data
        if len(self._guano.to_string()) > 0:
            for key, value in self._guano.items():
                keys.append(key)

            for key in keys:
                del(self._guano[key])

        if len(self._guano.to_string()) == 0:
            self._guano['Loc Elevation'] = self._section['elevation']
            self._guano['Loc Position'] = (float(self._section['latitude']), float(self._section['longitude']))
            self._guano['Make'] = self._section['Make']
            self._guano['Model'] = self._section['Model']
            self._guano['Serial'] = self._section['Serial']
            self._guano['Original Filename'] = self._filename
            self._guano['Note'] = self._section['note']
            self._guano['Timestamp'] = self._timestamp
            self._guano['NFC|Moon Phase'] = ephem.Moon(self._timestamp).moon_phase
            self._guano['NFC|Station Name'] = self._section['name']
            self._guano['NFC|Time Zone'] = self._section['timezone']
            # self._guano['NFC|Temperature'] = 'NA'
            # self._guano['NFC|Humidity'] = 'NA'
            # self._guano['NFC|Wind Direction'] = 'NA'
            # self._guano['NFC|Wind Speed'] = 'NA'
            # self._guano['NFC|Pressure'] = 'NA'
            # self._guano['NFC|Visibility'] = 'NA'
            self._guano['NFC|Copyright'] = self._section['copyright']
            self._guano['NFC|Location'] = self._section['location']

            for key, value in self._guano.items():
                print(f"{key}: {value}")

            if write:
                pass
                # self._guano.write(make_backup=False)

    def extract_audio(self, event, clip_len, clipdir, full_height=False, graph=False, force=False, debug=False, silent=False):
        wavelen = self.metadata['Duration']
        dur_sec = event['stop'] - event['start']
        filename = f"{event['dt'].strftime('%Y%m%d-%H%M%S%z')}-{event['engine']}-{event['species_code']}.WAV"
        outpath = os.path.join(clipdir, f"{filename}")
        
            # print(clip_len)
            # print(round(clip_len * 4)/4.0)
            # print(.25 * (clip_len//.25))
        
        if not os.path.exists(outpath) or force:
            if not os.path.exists(clipdir):
                # race condition with multiprocessing where one 'thread' creates
                # the dir after another one determines it doesn't exist so, we'll
                # wrap it in a try/except and just pass on the error
                try:
                    os.mkdir(clipdir)
                except FileExistsError:
                    pass

            if not silent:
                print(f"Extracting audio from {event['dt'].strftime('%Y-%m-%d-%H:%M:%S')} - {(event['dt']+timedelta(seconds=dur_sec)).strftime('%Y-%m-%d-%H:%M:%S')} to {filename}")

            start = event['start']

            if dur_sec > clip_len:
                clip_len = dur_sec

            # expand the audio clip from dur_sec to clip_len, ensuring
            # the clip is centered in the new duration
            if dur_sec < clip_len:
                padding = dur_sec / 2

                # clip occurs at the beginning of file, add padding to
                # the end even though it means it won't be centered
                if start < padding:
                    start = 0
                # clip occurs at teh end of the file, add padding to the
                # beginning even though it means it won't be centered
                elif (wavelen - event['stop']) < padding:
                    start = wavelen - clip_len
                # clip occurs in the middle of the file somewhere, just
                # try to center it.
                else:
                    start = (start + (dur_sec / 2)) - (clip_len / 2)

            secs_per_byte = 1 / self.metadata['fmt']['Bytes/sec']
            chunk_size  = int(round(clip_len/secs_per_byte, 0))
            chunk_start = self.metadata['data']['Offset'] + int(round(start/secs_per_byte, 0))
            file_size = chunk_size + 44

            # print(f"filename={clipfile}, start={start}, end={start+clip_len}, chunk_start={chunk_start} - {hex(chunk_start)}, chunk_size={chunk_size}")

            # TODO: Ensure all the chunks are properly padded
            # maybe also add GUANO header
            header  = struct.pack('4s', b'RIFF')
            header += struct.pack('<l', file_size)
            header += struct.pack('4s', b'WAVE')
            header += struct.pack('4s', b'fmt ')
            header += struct.pack('<l', 16)
            header += struct.pack('<h', self.metadata['fmt']['Format'])
            header += struct.pack('<h', self.metadata['fmt']['Channels'])
            header += struct.pack('<l', self.metadata['fmt']['Frequency'])
            header += struct.pack('<l', self.metadata['fmt']['Bytes/sec'])
            header += struct.pack('<h', self.metadata['fmt']['Bytes/blc'])
            header += struct.pack('<h', self.metadata['fmt']['Bits/smp'])
            header += struct.pack('4s', b'data')
            header += struct.pack('<l', chunk_size)

            with open(self._filename, 'rb') as f:
                f.seek(chunk_start)
                data = f.read(chunk_size)

            with open(outpath, 'wb') as f:
                f.write(header)
                f.write(data)

        # print(f"{filename}: {graph}")
        if graph:
            self._generate_graph(event, filename, clipdir, full_height, force, debug, silent)

    def _spec_y_formatter(self, x, pos):
        'The two args are the value and tick position'
        return '%1.1fk' % (x/1000)

    def _generate_graph(self, event, wavefile, clipdir, full_height=False, force=False, debug=False, silent=False):
        """
        Generate a spectrograph of the supplied event.

        Args:
            event (dict): An event dict which we'll use to generate the spectrograph.
            clip_dir (str): Name of the directory to store graphs in (default: clips).
            title (str): The title of the graph.
            force (bool): Whether or not to overwrite the clip file if it already exists. 
        """

        # wavelen = self.metadata['Duration']
        dur_sec = event['stop'] - event['start']
        filename = f"{event['dt'].strftime('%Y%m%d-%H%M%S%z')}-{event['engine']}-{event['species_code']}.PNG"
        outpath = os.path.join(clipdir, f"{filename}")

        if not os.path.exists(outpath) or force:
            if not silent:
                print(f"Generating graph from {event['dt'].strftime('%Y-%m-%d-%H:%M:%S')} - {(event['dt']+timedelta(seconds=dur_sec)).strftime('%Y-%m-%d-%H:%M:%S')} to {filename}")

            # these libraries take nearly 1.0s to import, which makes the cli
            # app seem very sluggish, so we'll only import them when necessary.
            # no risk of duplicate imports as python should only return a
            # reference to the first instance of an imported module.
            import numpy as np
            import librosa
            import matplotlib
            import matplotlib.pyplot as plt
            from matplotlib.ticker import FormatStrFormatter as fsf

            height = 24000

            if full_height:
                height=None

            # Use high quality backend for rendering PNGs
            matplotlib.use('agg')

            # ta means a user has overridden the entry, or added one manually.
            if event['engine'] == 'ta':
                title = f"{event['common_name']}\n{event['dt'].strftime('%Y-%m-%d %H:%M:%S%z')}\n"
            else:
                # setup full engine names for the title
                if event['engine'] == 'bn':
                    engine = 'BirdNet'
                else:
                    engine = 'Nighthawk'

                # newline at the end add a bit of extra space before the graph, makes the title look centered vertically
                if event['overridden']:
                    # if the event is overridden then it's misleading to include engine/probability
                    title = f"{event['common_name']}\n{event['dt'].strftime('%Y-%m-%d %H:%M:%S%z')}\n"
                else:
                    title = f"{event['common_name']} ({engine} - {event['probability']*100:-5.2f}%)\n{event['dt'].strftime('%Y-%m-%d %H:%M:%S%z')}\n"

            if not os.path.exists(os.path.join(clipdir, filename)) or force:
                # load audio file
                hl = 32
                wl = 512

                # without sr= set, it resamples to 22050hz
                # with sr=None set, it uses the native sampling rate
                data, sr = librosa.load(os.path.join(clipdir, wavefile), sr=height)
                duration = len(data) / sr

                db = librosa.amplitude_to_db(np.abs(librosa.stft(data, hop_length=hl, win_length=wl)), ref=np.max)
                plt.figure(figsize=(32, 18), dpi=100)
                plt.rcParams['font.size'] = 24
                librosa.display.specshow(db, sr=sr, fmax=1000, x_axis='time', y_axis='linear', cmap='gray_r', hop_length=hl)
                plt.title(title)
                plt.xlabel('Time (s)')
                plt.ylabel('Frequency (Hz)')
                plt.yticks()
                plt.minorticks_on()
                plt.xticks()

                interval = 1000

                if sr > 24000:
                    interval = 2000

                # plt.rc(('xtick.major', 'ytick.major',), width=20, size=250)
                plt.gca().tick_params('both', length=10, width=2, which='major')
                plt.gca().tick_params('both', length=5, width=2, which='minor')
                plt.yticks(np.arange(0, sr/2+interval, interval), fontsize=18)
                plt.gca().yaxis.set_major_formatter(self._spec_y_formatter)
                plt.xticks(np.arange(0, duration+.25, .25), fontsize=18)
                plt.gca().xaxis.set_major_formatter('{x:.2f}')
                
                # Note: Hide every other label, might be useful at some point
                # for label in plt.gca().yaxis.get_ticklabels()[::2]:
                #     label.set_visible(False)

                # Note: Add copyright to the graph somewhere
                # plt.text(0, 0, '© 2025 Your Name/Organization', 
                #         horizontalalignment='right',
                #         verticalalignment='bottom',
                #         fontsize=25,
                #         color='black',
                #         alpha=1)

                # Save spectrogram as image
                plt.savefig(os.path.join(clipdir, filename), bbox_inches='tight', pad_inches=0.5)
                plt.close()
            else:
                if self._debug:
                    print('File exists, skipping. Use the --force option to regenerate the spectrograph.')

class TalonSchedule():
    def __init__(self, latitude, longitude, timezone, name, curdate, hours=-1, duration=3600, debug=False):
        self._timezone = timezone
        self._name = name
        self._latitude = latitude
        self._longitude = longitude
        self._duration = duration
        self._date = curdate
        self._curtz = ZoneInfo(self._timezone)
        self._debug = debug
        self._utc = ZoneInfo("UTC")
        self._orig_date = curdate.astimezone(self._curtz)

        self.initialize()

        self._start = self._date.astimezone(self._curtz)
        self._stop = None
        self._tomorrow = self.MidnightLocal + timedelta(seconds=86400)

        self._count = 1
        self._limit = hours

        self._initial = True
        self._debug = True

    def initialize(self):
        location=LocationInfo(name=self._name, timezone=self._timezone, latitude=self._latitude, longitude=self._longitude)

        self.AstronomicalDawn = sun(location.observer, date=self._date, dawn_dusk_depression=18, tzinfo=self._utc)['dawn'].replace(microsecond=0)
        self.AstronomicalDawn = self.AstronomicalDawn.astimezone(self._utc)
        self.Noon = dt.combine(self._date, time(12,0,0)).astimezone(self._utc).replace(microsecond=0)
        self.AstronomicalDusk = sun(location.observer, date=self._date, dawn_dusk_depression=18, tzinfo=self._utc)['dusk'].replace(microsecond=0)
        self.AstronomicalDusk = self.AstronomicalDusk.astimezone(self._utc)

        self.AstronomicalDawnLocal = self.AstronomicalDawn.astimezone(self._curtz)
        self.NoonLocal = dt.combine(self._date, time(12,0,0)).astimezone(self._curtz).replace(microsecond=0)
        self.AstronomicalDuskLocal = self.AstronomicalDusk.astimezone(self._curtz)
        self.MidnightLocal = dt.combine(self._date, time(0,0,0)).astimezone(self._curtz).replace(microsecond=0)

        self.Midnight = self.MidnightLocal.astimezone(self._utc).replace(microsecond=0)

        # print(self._orig_date + timedelta(hours=self._limit):)

    def __str__(self):
        output = ""

        output += f"Location Details\n"
        output += f'-' * 58 + '\n'
        output += f"Name      : {self._name}\n"
        # output += f"Region    : {self.Region}\n"
        output += f"TimeZone  : {self._timezone}\n"
        output += f"Latitude  : {self._latitude}\n"
        output += f"Longitude : {self._longitude}\n"
        output += f"Date      : {self._date}\n\n"

        output += f"Time Zone: UTC\n"
        output += f'-' * 58 + '\n'
        output += f"Midnight          : {self.Midnight.strftime('%Y%m%d %H:%M:%S %Z')}\n"
        output += f"Astronomical Dawn : {self.AstronomicalDawn.strftime('%Y%m%d %H:%M:%S %Z')}\n"
        output += f"Noon              : {self.Noon.strftime('%Y%m%d %H:%M:%S %Z')}\n"
        output += f"Astronomical Dusk : {self.AstronomicalDusk.strftime('%Y%m%d %H:%M:%S %Z')}\n\n"

        output += f"Time Zone: {self._timezone}\n"
        output += f'-' * 58 + '\n'
        output += f"Midnight          : {self.MidnightLocal.strftime('%Y%m%d %H:%M:%S %Z')}\n"
        output += f"Astronomical Dawn : {self.AstronomicalDawnLocal.strftime('%Y%m%d %H:%M:%S %Z')}\n"
        output += f"Noon              : {self.NoonLocal.strftime('%Y%m%d %H:%M:%S %Z')}\n"
        output += f"Astronomical Dusk : {self.AstronomicalDuskLocal.strftime('%Y%m%d %H:%M:%S %Z')}"

        return output

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            protocol = ""
            curdur = self._duration

            # the first pass through we are likely dealing with a partial
            # duration, so we need to truncate the initial duration so we
            # align on the expected boundaries (e.g., top of every hour).
            if self._initial:
                self._initial = False

                # calculation time remaining in current window
                curdur = self._duration - (self._start.minute * 60 + self._start.second - self._duration) % self._duration

            # today @ Midnight to Astronomical Dawn
            if self.MidnightLocal <= self._start < self.AstronomicalDawnLocal:
                window = (self.AstronomicalDawnLocal - self._start).total_seconds()
                protocol = "NFC"

                if curdur >= window:
                    curdur = window

            # Astronomical Dawn to Noon
            elif self.AstronomicalDawnLocal <= self._start < self.Noon:
                window = (self.Noon - self._start).total_seconds()
                protocol = "DAY"

                if curdur > window:
                    curdur = window
                else:
                    curdur = self._duration - (self._start.minute * 60 + self._start.second - self._duration) % self._duration
                    
            # Noon to Astronomical Dusk
            elif self.Noon <= self._start < self.AstronomicalDuskLocal:
                window = (self.AstronomicalDuskLocal - self._start).total_seconds()
                protocol = "DAY"

                if curdur >= window:
                    curdur = window

            # Astronomical Dusk to tomorrow @ Midnight
            elif self.AstronomicalDuskLocal <= self._start < self._tomorrow:
                window = (self._tomorrow - self._start).total_seconds()
                protocol = "NFC"

                if curdur > window:
                    curdur = window
                else:
                    curdur = self._duration - (self._start.minute * 60 + self._start.second - self._duration) % self._duration
            else:
                # we'll never make it here
                raise StopIteration

            self._stop = (self._start + timedelta(seconds=curdur)).replace(microsecond=0)
 
            old_start = self._start
            self._start = self._stop

            # we've hit midnight, re-initialize for the next day
            # and check to see if we should stop iterating
            if self._start >= self._tomorrow:
                self._date = self._start
                self.initialize()

                self._start = self.MidnightLocal
                self._tomorrow = self.MidnightLocal + timedelta(seconds=86400)

            # if limit is -1 then never stop iterating
            if self._limit >= 0 and (self._start >= self._orig_date + timedelta(hours=self._limit + 1)):
                raise StopIteration

            result = {
                "protocol": protocol,
                "start": old_start,
                "stop": self._stop,
                "duration": curdur
            }

            return result

class TalonWeatherGridError(Exception):
    """A custom exception for specific errors in MyClass."""
    pass

class TalonWeatherStationError(Exception):
    """A custom exception for specific errors in MyClass."""
    pass

class TalonWeatherObservationError(Exception):
    """A custom exception for specific errors in MyClass."""
    pass

class TalonWeatherTimeoutError(Exception):
    """A custom exception for specific errors in MyClass."""
    pass

class TalonWeather:
    def __init__(self, latitude, longitude, timezone, uscs=True, timeout=15, cacheexpiry=15, cachedir=None, stationid=None, debug=True):
        self._timeout = timeout
        self._debug = debug
        self._observations = None
        self._forecast = None
        self._latitude = latitude
        self._longitude = longitude
        self._timezone = timezone
        self._uscs = uscs
        self._cacheexpiry = cacheexpiry

        self._cache_enabled = False

        self._curtz = ZoneInfo(self._timezone)
        self._grid_url = f"https://api.weather.gov/points/{self._latitude},{self._longitude}"

        self._timestamp = None
        self._stationid = stationid
        self._temperature = None
        self._humidity = None
        self._wind_dir = None
        self._wind_speed = None
        self._wind_chill = None
        self._pressure = None
        self._visibility = None
        self._conditions = None

        self._cachedir = cachedir
        self._wind_dir_num = [ 0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5, 360 ]
        self._wind_dir_txt = [ 'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']

        self.load()

    def list_stations(self):
        self._list_stations()

    def _list_stations(self):
        try:
            # Using NOAA / NWS as a weather source
            # weather.gov data is based on grids (2.5km x 2.5km). the first call gets the grid
            # for a set of gps coordinates. the returned document contains api urls for other
            # services (e.g., forecast). We are using it to retrieve a list of stations for the
            # grid, which we can then use to get a list of observations for a specific station.
            grid_response = requests.get(url=self._grid_url, timeout=self._timeout)
            station_list = []

            if grid_response.ok:
                grid_data = grid_response.json()

                # get stations for this grid
                station_response = requests.get(url=grid_data['properties']['observationStations'], timeout=self._timeout)

                if station_response.ok:
                    station_data = station_response.json()

                    for station in station_data['features']:
                        station_list.append((station['properties']['stationIdentifier'], station['properties']['name'], station['properties']['elevation'], station['properties']['distance']))

                    print(f"ID      Dist.    Elev.     Name")

                    for st in station_list:
                        if self._uscs:
                            if st[2]['unitCode'] == 'wmoUnit:m':
                                e = st[2]['value'] * 3.28084
                                elevation = f"{e:7.2f}ft"

                            if st[3]['unitCode'] == 'wmoUnit:m':
                                d = st[3]['value'] * 3.28084 / 5280
                                distance = f"{d:7.2f}mi"
                        else:
                            e = st[2]['value']
                            elevation = f"{e:7.2f}m,"

                            d = st[3]['value'] / 1000
                            distance = f"{d:7.2f}km"

                        print(f"{st[0]:5} {distance} {elevation}  {st[1]}")
                else:
                    raise TalonWeatherStationError()
            else:
                raise TalonWeatherGridError()
        except requests.exceptions.ConnectionError as e:
            raise TalonWeatherTimeoutError(f"Time out contacting weather.gov: {e}")
        except requests.exceptions.ReadTimeout as e:
            raise TalonWeatherTimeoutError(f"Time out reading data from weather.gov: {e}")

    def load(self):
        self._load_observations()
        self._load_forecasts()

    def _load_forecasts(self, curdt=None):
        if self._cache_enabled:
            file_list = glob.iglob(os.path.join(self._cachedir, f'F_{self._stationid}_*.json'))
            new_list = []

            # get the file name without extension, then split into an array
            for cachefile in file_list:
                cur = Path(cachefile).stem
                new_list.append([cachefile] + cur.split('_')[1:])

            new_list = sorted(new_list, key=lambda x: x[2])

            # if we have a cachefile for this stationid, then load the latest
            # otherwise download a new set of observations
            if len(new_list) > 0:
                if curdt:
                    for cf in new_list:
                        start = dt.strptime(cf[3], "%Y%m%d-%H%M%S%z")
                        stop = dt.strptime(cf[4], "%Y%m%d-%H%M%S%z")

                        if stop > curdt > start:
                            with open(cf[0], 'r') as f:
                                self._forecast = json.load(f)

                            break
                else:
                    cachefile = new_list[-1][0]
                    cache_stat = os.stat(cachefile)
                    cache_age = (dt.now().timestamp() - cache_stat.st_mtime) / 60

                    if (cache_age >= self._cacheexpiry):
                        self._get_forecast()
                    else:
                        with open(cachefile, 'r') as f:
                            self._forecast = json.load(f)
            else:
                self._get_forecast()
        else:
            self._get_forecast()

    def _load_observations(self, curdt=None):
        if self._cache_enabled:
            file_list = glob.iglob(os.path.join(self._cachedir, f'O_{self._stationid}_*.json'))
            new_list = []

            # get the fine name without extension, then split into an array
            for cachefile in file_list:
                cur = Path(cachefile).stem
                new_list.append([cachefile] + cur.split('_'))

            new_list = sorted(new_list, key=lambda x: x[2])

            # if we have a cachefile for this stationid, then load the latest
            # otherwise download a new set of observations
            if len(new_list) > 0:
                if curdt:
                    for cf in new_list:
                        start = dt.strptime(cf[3], "%Y%m%d-%H%M%S%z")
                        stop = dt.strptime(cf[4], "%Y%m%d-%H%M%S%z")

                        if stop > curdt > start:
                            with open(cf[0], 'r') as f:
                                self._observations = json.load(f)

                            break
                else:
                    cachefile = new_list[-1][0]
                    cache_stat = os.stat(cachefile)
                    cache_age = (dt.now().timestamp() - cache_stat.st_mtime) / 60

                    if (cache_age >= self._cacheexpiry):
                        self._get_observations()
                    else:
                        with open(cachefile, 'r') as f:
                            self._observations = json.load(f)
            else:
                self._get_observations()
        else:
            self._get_observations()

    def update(self, force=False):
        self._get_observations(force)
        self._get_forecast(force)

    def _get_forecast(self, force=False):
        try:
            # Using NOAA / NWS as a weather source
            # weather.gov data is based on grids (2.5km x 2.5km). the first call gets the grid
            # for a set of gps coordinates. the returned document contains api urls for other
            # services (e.g., forecast). We are using it to retrieve a list of stations for the
            # grid, which we can then use to get a list of observations for a specific station.
            grid_response = requests.get(url=self._grid_url, timeout=self._timeout)

            if grid_response.ok:
                grid_data = grid_response.json()

                # get stations for this grid
                forecast_response = requests.get(url=grid_data['properties']['forecastHourly'])

                if forecast_response.ok:
                    self._forecast = forecast_response.json()
                
                    if self._cache_enabled and self._forecast is not None:
                        self._commit()
                else:
                    raise TalonWeatherStationError()
            else:
                raise TalonWeatherGridError()
        except requests.exceptions.ConnectionError as e:
            raise TalonWeatherTimeoutError(f"Time out contacting weather.gov: {e}")

    def _get_observations(self, force=False):
        observation_url = None

        try:
            # Using NOAA / NWS as a weather source
            # weather.gov data is based on grids (2.5km x 2.5km). the first call gets the grid
            # for a set of gps coordinates. the returned document contains api urls for other
            # services (e.g., forecast). We are using it to retrieve a list of stations for the
            # grid, which we can then use to get a list of observations for a specific station.
            grid_response = requests.get(url=self._grid_url, timeout=self._timeout)

            if grid_response.ok:
                grid_data = grid_response.json()

                # get stations for this grid
                station_response = requests.get(url=grid_data['properties']['observationStations'], timeout=self._timeout)

                if station_response.ok:
                    station_data = station_response.json()

                    if self._stationid:
                        for station in station_data['features']:
                            if station['properties']['stationIdentifier'] == self._stationid:
                                observation_url = f"{station['properties']['@id']}/observations"

                    if not observation_url:
                        # [0] is the first station, which should be the closest to the provided
                        # gps coordinates
                        observation_url = f"{station_data['features'][0]['id']}/observations"

                    observation_response = requests.get(url=observation_url, timeout=self._timeout)

                    if observation_response.ok:
                        self._observations = observation_response.json()

                        if self._cache_enabled and self._observations is not None:
                            self._commit()
                    else:
                        raise TalonWeatherObservationError()
                else:
                    raise TalonWeatherStationError()
            else:
                raise TalonWeatherGridError()
        except requests.exceptions.ConnectionError as e:
            raise TalonWeatherTimeoutError(f"Time out contacting weather.gov: {e}")

    def commit(self):
        self._commit()

    def _commit(self):
        first_dt = dt.fromisoformat(self._observations['features'][-1]['properties']['timestamp'])
        last_dt = dt.fromisoformat(self._observations['features'][0]['properties']['timestamp'])

        start = dt.strftime(first_dt, "%Y%m%d-%H%M%S%z")
        stop = dt.strftime(last_dt, "%Y%m%d-%H%M%S%z")
        stationid = self._observations['features'][0]['properties']['stationId']
        # cachefile = os.path.join(self._cachedir, f"{stationid}_{start}_{stop}.json")

        obs_cachefile = os.path.join(self._cachedir, f"O_{stationid}_{start}_{stop}.json")

        if self._observations is not None:
            with open(obs_cachefile, 'w') as f:
                f.write(json.dumps(self._observations))

        for_cachefile = os.path.join(self._cachedir, f"F_{stationid}_{start}_{stop}.json")

        if self._forecast is not None:
            with open(for_cachefile, 'w') as f:
                f.write(json.dumps(self._forecast))

    def _populate(self):
        self._station = self._observations['features'][-1]['properties']['stationName']

        obs = self._observations['features'][-1]['properties']

        self._temperature = obs['temperature']['value']

        obsdt = dt.fromisoformat(obs['timestamp'])
        self._timestamp = obsdt.astimezone(ZoneInfo("UTC")).astimezone(self._curtz)

        if self._temperature is not None:
            if obs['temperature']['unitCode'] == 'wmoUnit:degC':
                if self._uscs:
                    self._temperature = self._temperature * 1.8 + 32
            # we assume that if it's not Celsius then we're dealing with Fahrenheit
            else:
                if not self._uscs:
                    self._temperature = (self._temperature - 32) / 1.8

        self._wind_speed = obs['windSpeed']['value']

        if self._wind_speed is not None:
            if obs['windSpeed']['unitCode'] == 'wmoUnit:km_h-1':
                if self._uscs:
                    self._wind_speed = self._wind_speed / 1.609344
            else:
                if not self._uscs:
                    self._wind_speed = self._wind_speed * 1.609344

        self._wind_chill = obs['windChill']['value']

        if self._wind_chill is not None:
            if obs['windChill']['unitCode'] == 'wmoUnit:degC':
                if self._uscs:
                    self._wind_chill = self._wind_chill * 1.8 + 32
            # we assume that if it's not Celsius then we're dealing with Fahrenheit
            else:
                if not self._uscs:
                    self._wind_chill = (self._wind_chill - 32) / 1.8

        self._pressure = obs['barometricPressure']['value']

        if self._pressure is not None:
            if obs['barometricPressure']['unitCode'] == 'wmoUnit:Pa':
                if self._uscs:
                    self._pressure = self._pressure / 100
            else:
                if not self._uscs:
                    self._pressure = self._pressure * 100

        self._visibility = obs['visibility']['value']

        if self._visibility is not None:
            if obs['visibility']['unitCode'] == 'wmoUnit:m':
                if self._uscs:
                    self._visibility = round(self._visibility / 1609.344, 2)
            # else:
            #     if not self._uscs:
            # unknown what other unit it might be, miles, feet, etc.

        self._humidity = obs['relativeHumidity']['value']

        if self._humidity is not None:
            self._humidity = round(self._humidity, 2)

        self._wind_dir = obs['windDirection']['value']
        self._conditions = obs['textDescription']

    def __str__(self):
        output = ''

        output += f"{self._station}\n"

        output += f"Time Stamp  : {self._timestamp}\n"
        output += f"Temperature : {self._temperature}\n"
        output += f"Humidity    : {self._humidity}\n"
        output += f"Wind Chill  : {self._wind_chill}\n"
        output += f"Wind Speed  : {self._wind_speed}\n"
        output += f"Wind Dir.   : {self._wind_dir}\n"
        output += f"Pressure    : {self._pressure}\n"
        output += f"Visibility  : {self._visibility}\n"
        output += f"Conditions  : {self._conditions}\n"

        return output.strip()

    def forecast_table(self, samples=12):
        output = ""
        tmp = ""

        i = 0
        max = 0
        fcitems = []

        now = dt.now().astimezone(self._curtz)

        for fc in self._forecast['properties']['periods']:
            fcdt = dt.fromisoformat(fc['startTime'])
            fcdt = fcdt.astimezone(ZoneInfo("UTC")).astimezone(self._curtz)

            if fcdt >= now:
                windspd, windunit = fc['windSpeed'].split(' ')
                # * 1.8 + 32
                dewpt = self._get_temp(fc['dewpoint'])

                tmp = f"{fcdt.strftime('%Y-%m-%d %H:%M:%S')}  {fc['temperature']:>6.2f}{fc['temperatureUnit']}  {fc['relativeHumidity']['value']:>6.2f}%  {float(windspd):>5.2f} {windunit} {fc['windDirection']:<2}  {dewpt:>7} {fc['probabilityOfPrecipitation']['value']:>5.2f}%  {fc['shortForecast']}\n"
                fcitems.append(tmp)

                if len(tmp) > max:
                    max = len(tmp)

                # output += tmp

                if i >= samples:
                    break
                else:
                    i += 1

        # output = 'Hourly Forecast\n' + '-' * (max - 1) + '\n' + output

        for fc in fcitems[::-1]:
            output += fc

        return output.strip()

    def observation_table(self, samples=12):
        output = ""
        i = 1
        max = 0
        cond_max = 0

        data = ""
        station = f"Weather Station: {self._observations['features'][0]['properties']['stationName']}\n"
        # output += '-' * 106 + '\n'

        for obs in self._observations['features']:
            cond_len = len(obs['properties']['textDescription'])

            if cond_len > cond_max:
                cond_max = cond_len

            if i >= samples:
                break
            else:
                i += 1

        i = 0

        for obs in self._observations['features']:
            obsdt = dt.fromisoformat(obs['properties']['timestamp'])
            obsdt = obsdt.astimezone(ZoneInfo("UTC")).astimezone(self._curtz)

            if obs['properties']['temperature']['value'] is not None:
                temp = self._get_temp(obs['properties']['temperature'])
            else:
                temp = '------'

            if obs['properties']['windChill']['value'] is not None:
                windchill = self._get_wind_chill(obs['properties']['windChill'])
            else:
                windchill = '------'

            if obs['properties']['relativeHumidity']['value'] is not None:
                humidity = self._get_humidity(obs['properties']['relativeHumidity'])
            else:
                humidity = '------'

            if obs['properties']['windSpeed']['value'] is not None:
                wind_spd = self._get_wind_speed(obs['properties']['windSpeed'])
            else:
                wind_spd = '---------'
    
            if obs['properties']['windDirection']['value'] is not None:
                wind_dir = self._get_wind_direction(obs['properties']['windDirection'])
            else:
                wind_dir = '---'

            if obs['properties']['barometricPressure']['value'] is not None:
                pressure = self._get_pressure(obs['properties']['barometricPressure'])
            else:
                pressure = '------------'
            
            if obs['properties']['visibility']['value'] is not None:
                visibility = self._get_visibility(obs['properties']['visibility'])
            else:
                visibility = '--------'

            conditions = obs['properties']['textDescription']
            cloud_layers = self._get_cloud_layers(obs['properties']['cloudLayers'])
            ccl = f"{conditions:<{cond_max}}  {cloud_layers:<}"

            tmp = f"{obsdt.strftime('%Y-%m-%d %H:%M:%S')}  {temp:>7} {humidity:>8} {wind_spd:>10} {wind_dir:<3} {windchill:>7} {pressure:>13} {visibility:>9}  {ccl:<}\n"
            data += tmp

            if len(tmp) > max:
                max = len(tmp)

            if i >= samples:
                break
            else:
                i += 1

        # output  = station
        # output += 'Current Conditions\n'
        # output += '-' * (max - 1) + '\n'
        output += data

        return output.strip()

    def get_obs(self, cur_dt=None, now=False):
        best_obs = None
        output = ""

        if cur_dt:
            self._load_obs(cur_dt)

        newest_dt = dt.fromisoformat(self._observations['features'][0]['properties']['timestamp']).astimezone(self._curtz)
        oldest_dt = dt.fromisoformat(self._observations['features'][-1]['properties']['timestamp']).astimezone(self._curtz)

        if now:
            cur_dt = newest_dt

        # print(f"{newest_dt} >= {cur_dt} >= {oldest_dt} = {newest_dt >= cur_dt >= oldest_dt}")
        if newest_dt >= cur_dt >= oldest_dt:
            timestamps = []

            for obs in self._observations['features']:
                timestamps.append(dt.fromisoformat(obs['properties']['timestamp']))

            best_idx, _ = min(enumerate(timestamps), key=lambda x: abs(x[1] - cur_dt))
            obs = self._observations['features'][best_idx]

            obsdt = dt.fromisoformat(obs['properties']['timestamp'])
            obsdt = obsdt.astimezone(ZoneInfo("UTC")).astimezone(self._curtz)

            if obs['properties']['temperature']['value'] is not None:
                temp = self._get_temp(obs['properties']['temperature'])
            else:
                temp = '------'

            if obs['properties']['windChill']['value'] is not None:
                windchill = self._get_wind_chill(obs['properties']['windChill'])
            else:
                windchill = '------'

            if obs['properties']['relativeHumidity']['value'] is not None:
                humidity = self._get_humidity(obs['properties']['relativeHumidity'])
            else:
                humidity = '------'

            if obs['properties']['windSpeed']['value'] is not None:
                wind_spd = self._get_wind_speed(obs['properties']['windSpeed'])
            else:
                wind_spd = '---------'
    
            if obs['properties']['windDirection']['value'] is not None:
                wind_dir = self._get_wind_direction(obs['properties']['windDirection'])
            else:
                wind_dir = '---'

            if obs['properties']['barometricPressure']['value'] is not None:
                pressure = self._get_pressure(obs['properties']['barometricPressure'])
            else:
                pressure = '------------'
            
            if obs['properties']['visibility']['value'] is not None:
                visibility = self._get_visibility(obs['properties']['visibility'])
            else:
                visibility = '--------'

            conditions = obs['properties']['textDescription']
            cloud_layers = self._get_cloud_layers(obs['properties']['cloudLayers'])

            stationid = obs['properties']['stationId']

            output += f"Station ID: {stationid}, Date: {obsdt.strftime('%Y-%m-%d')}, Time: {obsdt.strftime('%H:%M:%S')}, Temperature: {temp}, Wind Chill: {windchill}, Humidity: {humidity}, Wind Speed: {wind_spd} {wind_dir}, Pressure: {pressure}, Visibility: {visibility}, Conditions: {conditions}, Cloud Layers: {cloud_layers}"

        return output

    def _get_temp(self, cur):
        if cur['value'] is not None:
            if cur['unitCode'] == 'wmoUnit:degC':
                if self._uscs:
                    val = cur['value'] * 1.8 + 32
                    unit = 'F'
                else:
                    val = cur['value']
                    unit = 'C'
            
            output = f"{val:.2f}{unit}"
        else:
            output = None

        return output

    def _get_wind_chill(self, cur):
        if cur['value'] is not None:
            if cur['unitCode'] == 'wmoUnit:degC':
                if self._uscs:
                    val = cur['value'] * 1.8 + 32
                    unit = 'F'
                else:
                    val = cur['value']
                    unit = 'C'
            
            output = f"{val:.2f}{unit}"
        else:
            output = None

        return output

    def _get_humidity(self, cur):
        if cur['value'] is not None:
            output = f"{cur['value']:.2f}%"
        else:
            output = "N/A"

        return output

    def _get_wind_speed(self, cur):
        if cur['value'] is not None:
            if cur['unitCode'] == 'wmoUnit:km_h-1':
                if self._uscs:
                    output = f"{cur['value'] * 0.6213711922:.2f} mph"
                else:
                    output = f"{cur['value']:.2f} km/h"
        else:
            output = "N/A"

        return output

    def _get_wind_direction(self, cur):
        if cur['value'] is not None:
            idx, _ = min(enumerate(self._wind_dir_num), key=lambda x: abs(x[1] - cur['value']))
            output = self._wind_dir_txt[idx]
        else:
            output = "N/A"

        return output

    def _get_pressure(self, cur):
        if cur['value'] is not None:
            if self._uscs:
                # convert to millibars
                output = f"{cur['value'] * 0.01:.2f} mbar"
            else:
                output = f"{cur['value']} Pa"
        else:
            output = "N/A"

        return output

    def _get_visibility(self, cur):
        if cur['value'] is not None:
            if self._uscs:
                output = f"{cur['value'] / 1000 * 0.6213711922:.2f} mi"
            else:
                output = f"{cur['value'] / 1000:.2f} km"
        else:
            output = "N/A"

        return output

    def _get_cloud_layers(self, cur):
        output = ""

        for layer in cur:
            if layer['base']['value'] is not None:
                if self._uscs:
                    height = layer['base']['value'] * 3.28084
                    output += f"{layer['amount']}:{height:6.2f}ft,"
                else:
                    height = layer['base']['value']
                    output += f"{layer['amount']}:{height:6.2f}m,"

        # remove trailing comma
        output = output[:-1]

        return output
    
    @property
    def humidity(self):
        return self._humidity

    @property
    def observations(self):
        return self._observations
