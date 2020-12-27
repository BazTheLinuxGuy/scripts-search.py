#!/usr/bin/env python
r"""
    This program searches through a directory of executables,
    such as /usr/bin or /usr/libexec, and looks for programs
    that are written in modern "scripting" languages, such as Bourne-shell
    scripting, Perl, or Python. 
"""

DEBUG = 0


# import regex
import argparse
import logging
from time import sleep
from collections import namedtuple
import stat
import sys
import os
import readline

__author__ = "Bryan A. Zimmer"
__date_of_this_notation__ = "Sunday, December 20, 2020. 5:00 AM"
__updated__ = "Tuesday December 22, 2020 8:30 PM"
__program_name__ = "scripts-search.py"


global scriptinfo
scriptinfo = namedtuple("scriptinfo", "name  type  size")

def parse_args(program):
    r"""The purpose of args here is to get the input directory/ies
    and the output directory where the results of this program will go.
    There is the matter of naming the output files, but that is better
    done elsewhere. Here, we will stick to the command line args."""
    #    program = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(
        description="Parse command line for the program."
    )

    parser.add_argument(
        "-i",
        "--inputdir",
        required=True,
        help="The 'bin' directory to search for scriptis in.",
    )

    parser.add_argument(
        "-o",
        "--outputdir",
        required=True,
        help="The directory to put this program's output into.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        required=False,
        help="Increase program verbosity, One, two or none.",
    )

    parser.add_argument(
        "-r",
        "--report",
        required=False,
        action="store_true",
        default=False,
        help="Statistics on the scripts we find.",
    )

    parser.add_argument(
        "-s",
        "--sortby",
        default="size",
        required=False,
        choices=["name", "type", "size"],
        help="Sort output file by name,size,or type.",
    )

    #    parser.parse_args(['-vvv'])
    #    Namespace(verbose=3)

    args = parser.parse_args()
    return args


class Script:

    global scriptinfo

    datatype = "single script info"

    def __init__(self, name, type, size):
        self.name = name
        self.type = type
        self.size = size
        if DEBUG:
            print(f"type = {type}")
            sleep(0.5)
        if "ELF" in type:
            return
        self.type = self.type.rstrip()
        try:
            n = self.type.index(":")
        except ValueError:
            n = 0
        else:
            n += 2  # skip over colon and following space
        finally:
            x = len(self.type)

        ptype = self.type[n:x]
        ptype = ptype.rstrip()
        if DEBUG:
            print(f"ptype = {ptype}")
            sleep(0.5)
        self.type = ptype
        self.script = scriptinfo(
            name=self.name, type=self.type, size=self.size
        )


### -------- End of class Script -------- ###


class Scripts:

    global args
    global scriptinfo

    datatype = "aggregation of scripts"

    def __init__(self):
        self.scripts = []
        self.len = 0

    def add(self, script):
        self.scripts.append(script)
        self.len += 1

    def numscripts(self):
        return len(self.scripts)

    def writefile(self, sfile):
        
        if args.sortby == "name":
            newlist = sorted(self.scripts, key=lambda script: script.name)
            sfile += "-by-name.csv"
        elif args.sortby == "size":
            newlist = sorted(self.scripts, key=lambda script: script.size)
            sfile += "-by-size.csv"
        elif args.sortby == "type":
            newlist = sorted(self.scripts, key=lambda script: script.type)
            sfile += "-by-type.csv"

        self.sfile = sfile
        os.chdir(args.outputdir)

        # write header for .csv file
        with open(self.sfile, "w") as f:
            s1 = "Program Name"
            s2 = "Program Type"
            s3 = "Size in Bytes"
            s = s1 + "," + s2 + "," + s3 + "\n"
            f.write(s)

            for eachscript in newlist:
                s1 = eachscript.name
                s1 = s1.rstrip()
                s1 = s1.replace(",", "-")

                s2 = eachscript.type
                s2 = s2.rstrip()
                s2 = s2.replace(",", "-")  # change commas to hyphens
                try:
                    n = s2.index("- ")
                    s2 = s2[0:n]
                except ValueError:
                    pass

                s3 = str(eachscript.size)
                s3 = s3.rstrip()
                s3 = s3.replace(",", "-")

                s = s1 + "," + s2 + "," + s3 + "\n"
                f.write(s)

            if args.verbose:
                print(f"Finished writing {self.sfile}")

        n = self.numscripts()
        if args.verbose:
            print(
                f'==> ** Processing complete, {n} scripts found. **',
                end='\n\n',
            )
        return sfile  

### ------- End of Class Scripts ---------- ###


def process_programs(programs, scripts):

    global symlinks
    symlinks = []

    statinfo = namedtuple(
        "statinfo",
        "st_mode  st_ino  st_dev  "
        "st_nlink  st_uid  st_gid  st_size  t_atime  "
        "st_mtime  st_ctime",
    )

    programs.sort(key=str.lower)
    # programs is now in alphabetical order.

    for program in programs:
        try:
            program = program.rstrip()
            if args.verbose == 1:
                print("Working on {}".format(program).ljust(60), end="\r")
            try:
                statinfo = os.stat(program)
            except FileNotFoundError:
                continue
            else:
                size = statinfo.st_size
                if DEBUG:
                    print(f"size of {program} is {size}")
            command = "file " + program
            p = os.popen(command)
            line = p.read()
            line = line.rstrip()
            ptype = line
            p.close()

            #            command = 'whatis ' + program  # + ' > /dev/null'
            #            p = os.popen(command)
            #            line = p.readline()
            #            line = line.rstrip()
            #            whatis = line
            #            p.close()
            #
            #            try:
            #                x = whatis.index('- ')
            #            except ValueError:
            #                pass
            #            else:
            #                x += 2
            #                whatis = whatis[x:]

            if ("binary" in ptype) or ("ELF" in ptype):
                continue
            if "symbolic" in ptype:
                symlinks.append((program, ptype, size))
                continue
            if ("ASCII" in ptype) or ("script" in ptype) or ("text" in ptype):
                script = Script(program, ptype, size)
                scripts.add(script)

        except FileNotFoundError:
            continue

    return scripts.scripts


def startup_housekeeping():
    global args
    
    output = args.outputdir
    inputdir = args.inputdir
    if output.endswith(os.sep):
        args.outputdir = output[0:-1]
    #    if args.verbose:
    #        print(f'output={output}')
    #        print(f'args.outputdir = {args.outputdir}')
    #        print('args.inputdir = {}'.format(args.inputdir))
    hyphen = "-"
    sfile = "scripts-in"
    #    inputdir = regex.sub(os.sep, replace, args.inputdir[0])
    inputdir = inputdir.replace(os.sep, hyphen)
    sfile = sfile + inputdir

    #    if args.verbose > 0:
    #        print("The output file(s) will be written to:")
    #        print(args.outputdir + os.sep + sfile + "...")

    #        k=input('Press [Enter] to continue: ')

    return sfile


def report_module(scripts):
    replist = sorted(scripts, key=lambda script: script.type)

    scripts_reporting = Scripts()
    sr = scripts_reporting
    newscripts = []
    for scrp in replist:
        ptype = scrp.type
        try:
            n = ptype.index(",")
        except ValueError:
            n = len(ptype)
        ptype = ptype[0:n]
        if "symbolic" in ptype:
            continue
        script = Script(name=scrp.name, type=ptype, size=scrp.size)
        sr.add(script)

    n = sr.numscripts()

    categories = {}
    ptype = ""
    symlinks = []
    for script in sr.scripts:
        if script.type != ptype:
            ptype = script.type
            if not "symbolic" in ptype:
                categories[ptype] = 1
            else:
                symlinks.append(script)
        else:
            categories[ptype] += 1

    for k, v in categories.items():

        if "symbolic link" in k:
            continue
        else:
            x1 = len(k)
            d = 50 - x1
#            x2 = len(str(v))
#            d2 = 4 - x2
            print(f'{k}' + ('.' * d) +  str(v).rjust(4))
#            print(('%s' + ('.' * d) + '%3d') % k,v)


def main():
    global args

    print("scripts-search version 0.49, (c) 2020, Bryan A. Zimmer", end="\n\n")

    # 1. Parse cmdline args or get them from GTK+ box.
    # [ Done in if __name__ == '__main___': ]

    # 2. Create output filename base from outputdir
    sfile = startup_housekeeping()  # sfile names the file that will
    # be written in the output directory.

    # 4. Looping on 'file program' for the chosen directory, create scripts (i.e.,
    #   instances of the Script class, adding them one by one to the Scripts object.
    #    Write out a report, default sorted on name, ( --sortby changes this) and write the
    #    file out to the chosen outputdir.

    os.chdir(args.inputdir)

    programs = []
    programs = os.listdir(args.inputdir)
    numprograms = len(programs)

    print(f"Searching for scripts in {args.inputdir}...")

    if args.verbose > 0:
        print(f"\n==> There are {numprograms} programs in {args.inputdir}.")

    #    if args.verbose > 0:
    #        print(f"==> Please be patient. ")
    #        print(f"Processing {numprograms} programs takes time.")

    scripts = Scripts()  # Starts out empty

    script_list = process_programs(programs, scripts)

    sfile = scripts.writefile(sfile)

    # If report/statistics are desired, display them on the screen, but have them in
    #    an internal format ready to be printed.

    if args.report:
        report_module(scripts.scripts)

    path1 = args.outputdir + os.sep + sfile
        
    print(f'\nDetailed report saved as {path1}\n')

    print("** Processing Completed **")

    return 0


if __name__ == "__main__":
    global args
    here = os.getcwd()
    program = os.path.basename(sys.argv[0])
    args = parse_args(program)
    rc = main()
    os.chdir(here)
    sys.exit(rc)
