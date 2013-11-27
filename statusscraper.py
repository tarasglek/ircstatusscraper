#!/usr/bin/python
import inotifyx, re, sys, copy, os.path
import time
import json
import subprocess
"""
TODO: 
* Add bugzilla status
* Add bsmedberg-info, particularly for 'next' section
"""

def writeJSON(filename, obj):
    # try to make a directory if can't open a file for writing
    try:
        f = open(filename, 'w')
    except IOError:
        os.makedirs(os.path.dirname(filename))
        f = open(filename, 'w')
    f.write(json.dumps(obj))
    f.close()
    print "Wrote " + filename

class Week:
    def __init__(self, fname):
        self.fname = fname
        self.nicks = {}
        self.changed = False

    def processLine(self, line):
        m = re.search('^([^ ]+) <.([^ ]+)> (rogerroger|status)[0-9]?. (.+)', line)
        if m != None:
            [strdate, nick, botname, status] = m.groups()
            date = copy.copy(self.date)
            date.insert(2, strdate)
            strdate = " ".join(date)
            unix_time = int(time.mktime(time.strptime(strdate, '%b %d %H:%M %Y')))
            update = [unix_time, status]
            try:
                self.nicks[nick].append(update)
            except KeyError:
                self.nicks[nick] = [update]
            print [nick, status]
            self.changed = True
            subprocess.call(["/home/taras/work/standup/scripts/standup-cmd",
                             "localhost:5000",
                             "1234",
                             nick,
                             "perf",
                             status])
            return True
        m = re.search('^--- (Log opened|Day changed) [^ ]+ (.+)', line)
        if m != None:
            date_components = m.groups()[1].split(' ')
            if len(date_components) == 4:
                del date_components[2]
            self.date = date_components
            return False
        print line        
        return False

    def dump(self):
        self.changed = False
        return self.nicks

class Weeks:
    def __init__(self, outdir):
        self.weeks = {}
        self.outdir = outdir
    
    def processLine(self, line, weekid):
        try:
            week = self.weeks[weekid]
        except KeyError:
            week = Week(weekid)
            self.weeks[weekid] = week
        return week.processLine(line)

    def dump(self):
        changed = False
        for weekid, week in self.weeks.iteritems():
            if not week.changed:
                continue
            writeJSON(os.path.join(OUTDIR, weekid + ".json"), week.dump())
            changed = True

        if changed:
            writeJSON(os.path.join(OUTDIR, "weeks.json"), self.weeks.keys())

[LOG, OUTDIR] =  sys.argv[1:]
weeks = Weeks(OUTDIR)
ifd = inotifyx.init()
log = inotifyx.add_watch(ifd, LOG, inotifyx.IN_MODIFY|inotifyx.IN_ATTRIB|inotifyx.IN_DELETE_SELF|inotifyx.IN_MOVE_SELF)
f = open(LOG)
sessions = set()
prefix = ''
while True:
    line = f.readline()
    if line == '':
        weeks.dump()
        # we've reached end of log, inotify avoids polling for growth
        # suspend if after 60seconds after activity in auth log stopped, there are still 0 ssh sessions
        ls = []
        while len(ls) == 0:
            ls = inotifyx.get_events(ifd, 60)
            if len(ls) + len(sessions) == 0:
                """nothing changed in 60s"""
                continue
        """for e in ls:
            print e.get_mask_description()"""
        continue
    """Buffer incomplete reads(eg irssi flushes timestamp first)"""
    if line[-1] != '\n':
        prefix += line
        continue
    weeks.processLine(prefix + line.strip(), os.path.basename(LOG))
    prefix = ''
