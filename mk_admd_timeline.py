#!/usr/bin/env/python


from timetimer.timeline import Storyline

import os


unroll = lambda x: sum(map(unroll, x), []) if isinstance(x, list) else [x]

def worker_timelines(alltimeline):
    Tstart = list()

    Tinit1 = list()
    Sload1 = list()
    Srun1 = list()
    STclose1 = list()
    Trestart1 = list()

    Tinit2 = list()
    Sload2 = list()
    Srun2 = list()
    STclose2 = list()
    Trestart2 = list()

    Tinit3 = list()
    Sload3 = list()
    Srun3 = list()
    STclose3 = list()

    Tend = list()
    for i_wk in range(len(logfiles)):
        Tstart.append(alltimeline[0].durations[i_wk])

        tinit1.append(alltimeline[1].durations[i_wk+0])
        sload1.append(alltimeline[2][i_wk].durations[0])
        srun1.append(alltimeline[3][i_wk].durations[0])
        stclose1.append(alltimeline[4].durations[0])
        trestart1.append(alltimeline[5][i_wk].durations[0])

        tinit2.append(alltimeline[1].durations[i_wk+0])
        sload2.append(alltimeline[2][i_wk].durations[0])
        srun2.append(alltimeline[3][i_wk].durations[0])
        stclose2.append(alltimeline[4].durations[0])
        trestart2.append(alltimeline[5][i_wk].durations[0])

        Tinit3.append(alltimeline[1].durations[i_wk+1])
        Sload3.append(alltimeline[2][i_wk].durations[1])
        Srun3.append(alltimeline[3][i_wk].durations[1])
        STclose3.append(alltimeline[4].durations[1])

        Tend.append(alltimeline[6][i_wk].durations[0])
    return Tstart, Tinit1, Sload1, Srun1, STclose1, Trestart, Tinit2, Sload2, Srun2, STclose2, Tend

def average(alist):
    return reduce(lambda x,y: x+y, alist) / float(len(alist))

def variance(alist):
    avg = average(alist)
    return sum(map(lambda x: (x-avg)**2, alist)) / float(len(alist)-1)

def stdev(alist):
    return variance(alist)**0.5


if __name__ == '__main__':

    outfile = 'admd.stdout'
    logfiles = list()

    def isworkerlog(filename):
        return filename.startswith('workers.') \
            and filename.endswith('.log')

    [logfiles.append(fn)
     for fn in os.listdir(os.getcwd())
     if isworkerlog(fn)]

    files = [outfile] + logfiles

    storyline = Storyline('ADMD Job',
                          'timetimer/admdjob.timeline')

    storyline.import_timestamps(*files)
    storyline.construct_timelines()

    #job_lifetime = storyline.segments['ADMDJob']['running'][0].durations

    #worker= storyline.segments['ADMDJob'][running][0].durations()
    #job_lifetime = storyline.segments['ADMDJob'][running][0].durations()

    exectimeline = [ ('Tstart',storyline.linkers['Tstart']),
                     ('Tinit',storyline.linkers['Tinit']),
                     ('Sload',storyline.segments['OpenMMRun']['Sload']),
                     ('Srun',storyline.segments['OpenMMRun']['Srun']),
                     ('STclose',storyline.linkers['STclose']),
                     ('Trestart',storyline.segments['Scheduler']['Trestart']),
                     ('Tend',storyline.segments['Scheduler']['Tend']) ]

    timelinelabels,alltimeline = zip(*exectimeline)

    n_per_series = [1,2,2,2,2,1,1]
    for i_wk in range(len(logfiles)):
        print "\nTIMELINE for Worker ", i_wk
        print timelinelabels[0], alltimeline[0].durations[i_wk]
        print timelinelabels[1], alltimeline[1].durations[i_wk+0]
        print timelinelabels[2], alltimeline[2][i_wk].durations[0]
        print timelinelabels[3], alltimeline[3][i_wk].durations[0]
        print timelinelabels[4], alltimeline[4].durations[0]
        print timelinelabels[5], alltimeline[5][i_wk].durations[0]
        print timelinelabels[1], alltimeline[1].durations[i_wk+1]
        print timelinelabels[2], alltimeline[2][i_wk].durations[1]
        print timelinelabels[3], alltimeline[3][i_wk].durations[1]
        print timelinelabels[4], alltimeline[4].durations[1]
        print timelinelabels[6], alltimeline[6][i_wk].durations[0]

    howmany = 2
    print "\nAVERAGE TIMELINE from ALL {0} Workers ".format(len(logfiles))
    print timelinelabels[0] + ''.join([' ' for _ in range(10-len(timelinelabels[0]))]), '{0:2.3f}'.format(average(alltimeline[0].durations))

    print timelinelabels[1] + ''.join([' ' for _ in range(10-len(timelinelabels[1]))]), '{0:2.3f}'.format(average(alltimeline[1].durations[::howmany]))
    print timelinelabels[2] + ''.join([' ' for _ in range(10-len(timelinelabels[2]))]), '{0:2.3f}'.format(average(map(lambda x: x.durations[0], alltimeline[2])))
    print timelinelabels[3] + ''.join([' ' for _ in range(10-len(timelinelabels[3]))]), '{0:2.3f}'.format(average(map(lambda x: x.durations[0], alltimeline[3])))
    print timelinelabels[4] + ''.join([' ' for _ in range(10-len(timelinelabels[4]))]), '{0:2.3f}'.format(average(alltimeline[4].durations[::howmany]))
    print timelinelabels[5] + ''.join([' ' for _ in range(10-len(timelinelabels[5]))]), '{0:2.3f}'.format(average(map(lambda x: x.durations[0], alltimeline[5])))

    print timelinelabels[1] + ''.join([' ' for _ in range(10-len(timelinelabels[1]))]), '{0:2.3f}'.format(average( [x for x in alltimeline[1].durations[1::howmany]]))#for3# if x<30] ))
    print timelinelabels[2] + ''.join([' ' for _ in range(10-len(timelinelabels[2]))]), '{0:2.3f}'.format(average(map(lambda x: x.durations[1], alltimeline[2])))
    print timelinelabels[3] + ''.join([' ' for _ in range(10-len(timelinelabels[3]))]), '{0:2.3f}'.format(average(map(lambda x: x.durations[1], alltimeline[3])))
    print timelinelabels[4] + ''.join([' ' for _ in range(10-len(timelinelabels[4]))]), '{0:2.3f}'.format(average(alltimeline[4].durations[1::howmany]))
    #for3#print timelinelabels[5] + ''.join([' ' for _ in range(10-len(timelinelabels[5]))]), '{0:2.3f}'.format(average(map(lambda x: x.durations[1], alltimeline[5])))

    #for3#print timelinelabels[1] + ''.join([' ' for _ in range(10-len(timelinelabels[1]))]), '{0:2.3f}'.format(average(alltimeline[1].durations[2::3]))
    #for3#print timelinelabels[2] + ''.join([' ' for _ in range(10-len(timelinelabels[2]))]), '{0:2.3f}'.format(average( [x.durations[2] for x in  alltimeline[2] if len(x.durations)>2] ))
    #for3#print timelinelabels[3] + ''.join([' ' for _ in range(10-len(timelinelabels[3]))]), '{0:2.3f}'.format(average( [x.durations[2] for x in  alltimeline[3] if len(x.durations)>2] ))
    #for3#print timelinelabels[4] + ''.join([' ' for _ in range(10-len(timelinelabels[4]))]), '{0:2.3f}'.format(average(alltimeline[4].durations[2::3]))

    print timelinelabels[6] + ''.join([' ' for _ in range(10-len(timelinelabels[6]))]), '{0:2.3f}'.format(average(map(lambda x: x.durations[0], alltimeline[6])))


    print "Read worker data into 'storyline' object "
    print "\nHave the following data objects in namespace: "
    print "storyline\njoblifetime\nexectimeline"

    print "Worker lifetimes:"
    for x in storyline.segments['Worker']['lifetime']:
        print x.durations[0]

    print "Average lifetime", average([ x.durations[0] for x in storyline.segments['Worker']['lifetime'] ])
