# scripts-search.py

The purpose of this program, named "scripts-search.py," is to find the number of programs in the directories of executables (e.g. "bin" directories) that are not compiled ELF programs, but "scripts" (Python, Perl, Ruby , Bourne Shell, for example).

I am not biased toward these scripts. I am a C/C++/assembly programmer from the old days, and I like to compile/assemble my programs so that they run fast.

I wanted to scope out the scripts, partly becuase they are readable without going through an arduous process, and partly, as a Python Programmer, and a Perl programmer before that, I wanted to see fully-fledged Python and Perl programs to inspect and improve my own technique.

The output now comes in .csv files, perfect for browsing in a spreadsheet. I have tried LibreOffice Calc as well as MS-Excel, and it is quite an improvement over the raw data. There are four fields (or columns) to each program. The program's name, a "whatis" one line description of what the program does (when available), the "type" of the program (Bourne Shell, Perl, Python, Ruby,etc.), and the size, in bytes, of the program.

On average, about a fifth of the programs in /usr/bin and /usr/sbin have turned out to be scripts. Some of these are short "helper" scripts to get the "real" (ELF, compiled) program loaded. But many are fully operational Python or other "scripting language" programs, such as the Fedora 31/32/33 program "firewall-config," complete with a large body of code, high functionality and a Gtk+ GUI. And so on with Perl programs, and even Bourne-shell scripts. They can be instructional as well as just interesting to peruse.
