#!/usr/bin/env python3

import subprocess
import sys
import os
import argparse

'''
OPS445 Assignment 2 - Winter 2022
Program: duim.py 
Author: "Kiran Dangi"
The python code in this file (duim.py) is original work written by
"Bijay Sharma". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: Improved disk usage reporting with a horizontal bar graph showing
space utilization in subdirectories using percentage-based formatting. Optionally
supports human-readable sizes and custom bar length.

Date: April 13, 2025
'''

def parse_command_args():
    """Parses command-line arguments and returns them."""
    parser = argparse.ArgumentParser(description="DU Improved -- See Disk Usage Report with bar charts", epilog="Copyright 2022")
    parser.add_argument("target", nargs="?", default=".", help="The directory to scan.")
    parser.add_argument("-H", "--human-readable", action="store_true", help="print sizes in human readable format (e.g. 1K 23M 2G)")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    return parser.parse_args()

def percent_to_graph(percent, total_chars):
    """Returns a bar graph string that represents the percent value using '=' and spaces."""
    if not isinstance(percent, (int, float)) or percent < 0 or percent > 100:
        raise ValueError("percent must be a number between 0 and 100")
    equals = round((percent / 100) * total_chars)
    spaces = total_chars - equals
    return '=' * equals + ' ' * spaces

def call_du_sub(location):
    """Runs `du -d 1 <location>` and returns the output as a list of strings. Suppresses permission errors."""
    try:
        result = subprocess.run(['du', '-d', '1', location], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
        return result.stdout.decode().splitlines()
    except subprocess.CalledProcessError:
        print("Error running du command.", file=sys.stderr)
        return []


def create_dir_dict(alist):
    """Creates a dictionary from du output with directory names as keys and byte sizes as values."""
    result = {}
    for line in alist:
        parts = line.split('\t')
        if len(parts) == 2:
            size, name = parts
            try:
                result[name] = int(size)
            except ValueError:
                continue
    return result

def human_readable(num):
    """Converts bytes to human-readable format."""
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} P"

if __name__ == "__main__":
    args = parse_command_args()
    du_list = call_du_sub(args.target)
    dir_dict = create_dir_dict(du_list)

    total = dir_dict.get(args.target.rstrip('/'), sum(dir_dict.values()))
    if total == 0:
        print("No data to display.")
        sys.exit(0)

    for path, size in dir_dict.items():
        if path == args.target.rstrip('/'):
            continue
        percent = (size / total) * 100
        graph = percent_to_graph(percent, args.length)
        size_display = human_readable(size) if args.human_readable else f"{size} B"
        print(f"{percent:>3.0f} % [{graph}] {size_display:>8} {path}")

    total_display = human_readable(total) if args.human_readable else f"{total} B"
    print(f"Total: {total_display} {args.target}")

