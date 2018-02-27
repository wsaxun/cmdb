# -*- coding: utf-8 -*-
import os


def create_daemon():
    try:
        if os.fork() > 0:
            raise SystemExit(1)
    except OSError:
        print "fork #1 failed"
        raise SystemExit(1)

    os.chdir('/')
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            print "pid = %d\n" % (pid)
            raise SystemExit(0)
    except OSError:
        print "fork #2 failed"
        raise SystemExit(1)


if __name__ == '__main__':
    create_daemon()
