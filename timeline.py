#!/usr/bin/env/python




class Timeseries(list):
    def __init__(self, owner=None):
        super(Timeseries, self).__init__()
        self._owner = owner

    def set_owner(self, owner):
        if self._owner is None:
            self._owner = owner
        else:
            print("Timeseries instance owned by ", self._owner)

    @property
    def owner(self):
        return self._owner

    def add_timepoint(self, timepoint):

        if isinstance(timepoint, Timepoint) \
        and timepoint.owner == self.owner:
            idx = 0
            try:
                while timepoint.time > self[idx].time:
                    idx += 1
            except IndexError:
                pass

            super(Timeseries, self).insert(idx, timepoint)

        else:
            raise TypeError

    def append(self, timepoint):
        raise AttributeError(
            "Append Timepoint using methods add or add_timepoint")

    def insert(self, *args):
        raise AttributeError(
            "Insert Timepoint using methods add or add_timepoint")

    def add(self, timepoint):
        self.add_timepoint(timepoint)

    def print_timeseries(self):
        print "\nTimeseries for Owner: ", self.owner
        for tp in self:
            print tp


# TODO Storyline.data/segments&owner becomes timelines
class Storyline(object):
    def __init__(self, name, constructorfile=None):
        self.name = name
        self.data = dict()
        self.linkers = dict()
        self.segments = dict()
        self.timelines = dict()

        if constructorfile is not None:
            self.import_constructor(constructorfile)

        self._built = False

    @property
    def owners(self):
        return set(self.data.keys()).intersection(set(self.segments.keys()))

    @staticmethod
    def read_timestamps(filename):
        timeseriess = dict()
        with open(filename, 'r') as file:
            for line in file:
               if line.startswith('TIMER'):
                   Tp = Timepoint(*line.split()[1:])
                   if Tp is not None:
                       if Tp.owner not in timeseriess:
                           timeseriess.update({Tp.owner: Timeseries(Tp.owner)})
                       timeseriess[Tp.owner].add(Tp)

        return timeseriess

    def import_timestamps(self, *filenames):
        for filename in filenames:
            timeseriess = self.read_timestamps(filename)
            for owner, timeseries in timeseriess.items():
                if owner in self.data:
                    # if have one owner :: multi file can do this
                    #[self.data[owner].add(tp) for tp in timeseries]
                    # with    one owner :: one file then duplicated
                    # owner names will result in separate timelines
                    self.data[owner].append(timeseries)
                else:
                    self.data.update({owner: list()})
                    self.data[owner].append(timeseries)

    @staticmethod
    def read_constructor(constructorfile):

        def clean_split(string, key, maxsplit=99):
            return [_ for _ in
                    map(lambda x: x.strip(),
                    string.strip().split(key,maxsplit))]
        
        with open(constructorfile, 'r') as constructor:
            owner = None
            segments = dict()
            segments.update({'linkers': dict()})

            for line in constructor:
                if line.startswith('#'):
                    continue

                unstrrped = line.split(':')
                if len(unstrrped) == 2:
                    field, values = clean_split(line, ':')

                    if field == 'Timeline':
                        if len(values.split(',')) != 1 or values.find(' ') >= 0:
                            print "Error reading timeline, line was: ",line

                        else:
                            owner = values
                            if owner not in segments:
                                segments.update({owner: dict()})

                    elif len(values.split(',')) == 2:
                        start, end = clean_split(values, ',')

                        segment = Segment(field)
                        segment.owner = owner
                        segment.starting = start
                        segment.ending = end
                        segments[owner].update({field: [segment]})

                elif len(unstrrped) == 6 \
                and (len(unstrrped[2]) == 0 and len(unstrrped[4]) == 0):
                    field, values = clean_split(line, ':', 1)
                    _start, _end = clean_split(values, ',')
                    ownerstart, nothing, start = clean_split(_start, ':')
                    ownerend, nothing, end = clean_split(_end, ':')

                    linker = Segment(field)
                    linker.owner = (ownerstart, ownerend)
                    linker.starting = start
                    linker.ending = end
                    segments['linkers'].update({field: linker})

        return segments

    def import_constructor(self, constructorfile):

        segmentss = self.read_constructor(constructorfile)

        for owner, segments in segmentss.items():
            if all(x in segments for x in ['startup', 'shutdown']):
                self.segments.update({owner: segments})
            elif owner == 'linkers':
                [self.linkers.update({linkname: segment})
                 for linkname, segment in segments.items()]

    def construct_timelines(self):

        if self._built == False:
            self.build_segments()
            self.link_timelines()
            self._built == True

    def build_segments(self):

        for owner in self.owners:
            duplication = len(self.data[owner])
            [[self.segments[owner][segname].append(
              self.segments[owner][segname][0].copy())
              for _ in range(duplication-1)]
             for segname in self.segments[owner]]

            for idx, timeseries in enumerate(self.data[owner]):
                for timepoint in timeseries:
                    for segname, segments in self.segments[owner].items():
                        if timepoint.belongsto(segments[idx]):
                            segments[idx].set(timepoint)

    def link_timelines(self):

        def set_links(timeseries, inner, linker):
            for timepoint in timeseries:
                if timepoint.belongsto(linker):
                    linker.set(timepoint)

                    ilinkers = list()
                    for ts in inner:
                        for tp in ts:
                            if tp.belongsto(linker) \
                            and tp.time > timepoint.time:
                                ilinkers.append(tp)
                                break

                    linker.set(ilinkers)

        for linkname, linker in self.linkers.items():
            print '\n\n_______\nLINKER:|\n-------'
            print linkname
            print linker.owner
            print linker

            midx = False
            ownerstart, ownerend = linker.owner

            if len(self.data[ownerstart]) < len(self.data[ownerend]) \
            and len(self.data[ownerstart]) == 1:
                inner = self.data[ownerend]
                outer = self.data[ownerstart]

            elif len(self.data[ownerstart]) > len(self.data[ownerend]) \
            and len(self.data[ownerend]) == 1:
                outer = self.data[ownerend]
                inner = self.data[ownerstart]

            elif len(self.data[ownerstart]) == len(self.data[ownerend]):
                inner = self.data[ownerend]
                outer = self.data[ownerstart]
                midx = True

            if midx:
                for idx,timeseries in enumerate(outer):
                    # TODO move set_links attribute to segment (linker)
                    #      or subclass it
                    set_links(timeseries, [inner[idx]], linker)

            else:
                set_links(outer[0], inner, linker)


# TODO event subclass timeseries to capture start/stop occurances
class Segment(object):
    def __init__(self, name, single=False):
        super(Segment, self).__init__()
        self.name = name
        self._repeat = not single
        self._linker = False
        self._starting = None
        self._ending = None
        self._owner = None
        self.ready = False
        # format will become list of start,stop tuples
        #        tuple if no repeat/is single
        self._occurances = list()
        self._next = [[None, None] for _ in range(2)]
        self._durations = None
        self._average_duration = None
        self._variance_duration = None
        self._stdev_duration = None

    def __iter__(self):
        return self._occurances.__iter__()

    def copy(self):
        from copy import deepcopy
        return deepcopy(self)

    @property
    def count(self):
        return len(self._occurances)

    @property
    def duration_average(self):
        if not self._average_duration:
            self._average_duration = sum(self.durations) / self.count
        return self._average_duration

    @property
    def duration_variance(self):
        if not self._variance_duration:
            avg = self.duration_average*1.0
            self._variance_duration = sum(map(
                lambda x: (x-avg)**2, self.durations)) / (self.count-1)

        return self._variance_duration

    @property
    def duration_stdev(self):
        if not self._stdev_duration:
            from math import sqrt
            var = self.duration_variance
            self._stdev_duration = sqrt(var)

        return self._stdev_duration

    def add_occurance(self):
        nextone = self._next.pop(0)

        if isinstance(nextone[0], list):
            outer = nextone[1]
            inner = nextone[0]

        elif isinstance(nextone[1], list):
            inner = nextone[1]
            outer = nextone[0]

        else:
            # fixing  out of order here
            if nextone[1].time < nextone[0].time:
                nextone[1] = None
                self._next.insert(0, nextone)
                return
            else:
                inner = [nextone[1]]
                outer = nextone[0]

        [self._occurances.append([outer,inr]) for inr in inner]
        self._next.append([None, None])

    @property
    def cyclic(self):
        return self.start == self.end

    @property
    def islinker(self):
        return bool(1-len(self.owner))

    @property
    def points(self):
        return [self.start, self.end]

    def set(self, timepoint):

        if not timepoint:
            return

        if self.cyclic:
            if self.start == timepoint.description \
            and self.end == timepoint.description:
                if self._next[0][0] is None:
                    self._next[0][0] = timepoint
                else:
                    self._next[0][1] = timepoint
                    self._next[1][0] = timepoint

        else:
            if isinstance(timepoint, list):
                description = timepoint[0].description
            else:
                description = timepoint.description

            if self.start == description:
                if self._next[0][0]:
                    self._next[1][0] = timepoint
                else:
                    self._next[0][0] = timepoint

            if self.end == description:
                if self._next[0][1]:
                    self._next[1][1] = timepoint
                else:
                    if isinstance(self._next[1][0], Timepoint) \
                    and isinstance(timepoint, Timepoint) \
                    and self._next[1][0].time < timepoint.time:
                        self._next[1][1] = timepoint
                        self._next.pop(0)
                        self._next.append([None,None])
                    else:
                        self._next[0][1] = timepoint

        if sum(map(lambda x: bool(x), self._next[0])) == 2:
            self.add_occurance()

    @property
    def durations(self):
        if self._durations is None:
            self._durations = map(lambda (x,y): y.time-x.time, self._occurances)

        return self._durations

    @property
    def start(self):
        return self.owner[0] + ' ' + self.starting

    @property
    def end(self):
        return '{0} {1}'.format(
            self.owner[0] if len(self.owner)==1 else self.owner[1],
            self.ending)

    @property
    def starting(self):
        return self._starting

    @starting.setter
    def starting(self, label):
        if self._starting is None:
            self._starting = label
            if self._ending is not None:
                self.ready = True
        else:
            print("Segment starting point is set")

    @property
    def ending(self):
        return self._ending

    @ending.setter
    def ending(self, label):
        if self._ending is None:
            self._ending = label
            if self._starting is not None:
                self.ready = True
        else:
            print("Segment ending point is set")

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, *owners):
        if self._owner is None:
            if isinstance(owners, tuple) and len(owners[0]) == 2 \
            and len(owners) == 1 and owners[0][0] != owners[0][1]:
                self._owner = owners[0]

            elif len(owners) == 1:
                self._owner = tuple(owners)
        else:
            print("Segment owner is set")


class Timepoint(object):
    def __new__(cls, *args, **kwargs):
        try:
            float(args[-1])
            return super(Timepoint, cls).__new__(cls, *args, **kwargs)

        except ValueError as e:
            print "Could not create new <Timepoint> due to error: "
            print e

    def __init__(self, *args):
        super(Timepoint, self).__init__()
        self._owner = args[0]
        self._key = args[1:-1]
        self._stamp = args[-1]

    def belongsto(self, segment):
        return self.description in segment.points

    @property
    def event(self):
        return ' '.join(self._key)

    @property
    def description(self):
        return ' '.join([self.owner, self.event])

    def __str__(self):
        return ' '.join([self.description, self._stamp])

    @property
    def owner(self):
        return self._owner

    @property
    def time(self):
        return float(self._stamp)

