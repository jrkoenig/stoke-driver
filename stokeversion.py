import socket, subprocess, sys, os, threading, time, shutil, re

class StokeVersion(object):
    def __init__(self, h, path, origin):
        self.built = False
        self.built_success = False
        self.git_hash = h
        self.path = path
        self.users = 0
        self.origin = origin
    def acquire(self):
        if not self.built:
            self._build()
        self.users += 1
        if self.built_success:
            return os.path.abspath(os.path.join(self.path, "bin/stoke"))
        else:
            return None
    def release(self):
        self.users -= 1
    def _build(self):
        print "Building in dir ", self.path
        try:
            print 'Git fetching...'
            subprocess.check_call(['git','fetch', self.origin], cwd=self.path)
            print 'Checking out revision...'
            subprocess.check_call(['git','checkout','--force', self.git_hash],
              cwd = self.path)
            print 'Updating submodules...'
            subprocess.check_call(['git','submodule','update'], cwd = self.path)
            print 'Making...'
            retcode = subprocess.call(['make', '-j', '10'], cwd = self.path)
            self.built_success = (retcode == 0)
            print 'Done.', "Built sucessfully" if self.built_success else "Failed."
        finally:
            print 'Build process complete.'
            self.built = True

class BuildCache(object):
    """Global Daemon State"""
    def __init__(self, origin = 'ssh://jrkoenig@mrwhite/home/jrkoenig/expt/stoke', build_root = "./builds"):
        self.commits = {}
        self.build_root = build_root
        self.origin = origin
        self.most_recent = ""
    def scan(self):
        for d in os.listdir(self.build_root):
            if re.match("[0-9a-fA-F]+", d):
                directory = os.path.join(self.build_root, d)
                self.commits[d] = StokeVersion(d, directory, self.origin)
                self.most_recent = directory
    def get_by_hash(self, hash):
        if hash not in self.commits:
            try:
                newdir = os.path.join(self.build_root, hash)
                os.mkdir(newdir)
                subprocess.check_call(['git','clone',self.origin,'./'],cwd=newdir)
                self.commits[hash] = StokeVersion(hash, os.path.abspath(newdir), self.origin)
                most_recent = newdir
            except Exception as e:
                print e
                return None
        return self.commits[hash]
