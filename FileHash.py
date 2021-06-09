#!/usr/bin/env python

import time
import hashlib
import glob
import os
import csv
from collections import defaultdict

#BUF_SIZE = 67108864
#BUF_SIZE = 268435456
#BUF_SIZE=65536
BUF_SIZE=5242880
BLOCK_SIZE=100

class FileHash:
    "Representing a file hash object"

    def __init__(self, filename):
        self.filename = filename
        self.sha1 = ''

    def get_file_hash(self):        
        self.compute_file_hash()
        return self.sha1

    def compute_file_hash(self):
        sha1 = hashlib.sha1()

        lastwritetime = time.time()
        with open(self.filename, 'rb') as file:
            readcount = 1
            while True:
                data = file.read(BUF_SIZE * readcount)
                if not data:
                    break
                sha1.update(data)

                if readcount < 4096:
                    readcount += 1
                
                if second_passed(lastwritetime):
                    print('.', end='',flush=True)
                    lastwritetime = time.time()
    
        self.sha1 = sha1.hexdigest()

class CSVFile:
    "class for handling reads and writes to CSV files"

    def __init__(self, filename, newline = '', dialect = csv.excel, fieldnames = []):
        self.filename = filename
        self.fieldnames = fieldnames
        self.newline = newline
        self.dialect = dialect

    def append(self, rows = []):
        # if file is created newly enter header details
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w', newline = self.newline) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, dialect=self.dialect)
                writer.writeheader()

        with open(self.filename, 'a', newline = self.newline) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, dialect=self.dialect)
            for row in rows:
                writer.writerow(row)

    def exists(self):
        if not self.filename:
            return False

        if os.path.isfile(self.filename):
            return True

    def get_rows(self):

        rows = []
        with open(self.filename, 'r', newline=self.newline) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)

        return rows
        
def test():

    f = FileHash("D:\\dest\\photos.csv")
    print("SHA1: {0}".format(f.get_file_hash()))

def get_all_files():
    count = 0
    for filename in glob.iglob("D:\\" + '**/**', recursive=True):
        if os.path.isdir(filename):
            continue

        print(filename)
        count += 1

        if count == 1000:
            break

def second_passed(oldtime):
    currenttime = time.time()
    elapsed = (int)(currenttime-oldtime)
    return True if elapsed > 1 else False

def five_seconds_passed(oldtime):
    currenttime = time.time()
    elapsed = (int)(currenttime-oldtime)
    return True if elapsed> 5 else False

def get_hash_in_path(path, csvfilename, recursive=True):
    "Get hash of all files recursively in the given path and store details in the specified filename"
    count = 0
    printstr = ""
    hashes = []
    visitmap = {}

    csvfile = CSVFile(csvfilename, fieldnames=["Hash", "Filename"])

    starttime = time.time()

    if csvfile.exists():
        # create a map of already visited files
        rows = csvfile.get_rows()
        for row in rows:
            visitmap[row['Filename']] = row

    lastwritetime = time.time()

    for path, subdirs, files in os.walk(path):
        for name in files:
            filename = os.path.join(path, name)    
    #for filename in glob.iglob(path + '**/**', recursive=recursive):
            if second_passed(lastwritetime) and hashes:
                # write current objects to csv file and print on screen
                csvfile.append(hashes)
                print(printstr, flush=True)
                hashes = []
                printstr = ''
                lastwritetime = time.time()

            if os.path.isdir(filename):
                continue

            # if file has already been processed, skip
            if filename in visitmap.keys():
                continue

            f = FileHash(filename)
            f.compute_file_hash()

            hashes.append({"Hash":f.sha1, "Filename":f.filename})
            printstr += f.filename + "\n"
            
    # write the final set
    csvfile.append(hashes)
    print(printstr)

    endtime = time.time()
    elapsed = endtime - starttime
    elapsedtime = time.gmtime(elapsed)

    print("Completed in {0}:{1}:{2}".format(elapsedtime.tm_hour, elapsedtime.tm_min, elapsedtime.tm_sec))

def find_duplicates():
    csvfile = CSVFile("D:\\testpy.csv", fieldnames=["Hash", "Filename"])

    filemap = {}

    if csvfile.exists():
        rows = csvfile.get_rows()

        for row in rows:
            hash = row["Hash"]
            filename = row["Filename"]

            if hash in filemap.keys():
                filemap[hash].append(filename)
            else:
                filemap[hash] = [filename]

        for hash in filemap.keys():
            
            if len(filemap[hash]) > 1:
                print(filemap[hash])

def find_missing_source(sourcepath, destpath):
    csvsource = CSVFile(sourcepath, fieldnames=["Hash", "Filename"])
    if not csvsource.exists():
        return
    sourcerows = csvsource.get_rows()

    csvdest = CSVFile(destpath, fieldnames=["Hash", "Filename"])
    if not csvdest.exists():
        return
    destrows = csvdest.get_rows()

    sourcemap = defaultdict(list)
    for row in sourcerows:
        sourcemap[row["Hash"]].append(row["Filename"])

    destmap = defaultdict(list)
    for row in destrows:
        destmap[row["Hash"]].append(row["Filename"])

    for hash in sourcemap.keys():
        if not hash in destmap.keys():
            print(sourcemap[hash])


#test()
#get_all_files()
#get_all_hash()
#get_hash_in_path("D:\\Nana\\OneDrive\\Orig", "D:\\Orig.csv")
#get_hash_in_path("D:\\Nana\\OneDrive\\Laptop_Nana_Personal", "D:\\laptop_nana_personal.csv")
#find_missing_source("D:\\Orig.csv", "D:\\Testpy.csv")
#find_missing_source("D:\\laptop_nana_personal.csv", "D:\\sorted.csv")
#find_duplicates()
#get_hash_in_path("D:\\Nana\\OneDrive\\Sorted", "D:\\sorted.csv")
#get_hash_in_path("C:\\dest\\Photos\\FromPaapaGift\\7D\\Edited", "c:\dest\photos_frompaapagift_7d_edited.csv")
#get_hash_in_path("C:\\dest\\Photos\\FromPaapaGift\\7D\\Original", "c:\dest\photos_frompaapagift_7d_original.csv")
#get_hash_in_path("C:\\dest\\Photos\\FromPaapaGift\\7D\\", "c:\\dest\\photos_frompaapagift_7d_album_and_staging.csv")
#get_hash_in_path("C:\\dest\\Photos\\FromPaapaGift\\Anaga", "c:\\dest\\photos_frompaapagift_Anaga.csv")
#get_hash_in_path("C:\\dest\\Photos\\FromPaapaGift", "c:\\dest\\photos_frompaapagift.csv")
#get_hash_in_path("F:\\Photos.old", "c:\\dest\\photos.old.csv")
get_hash_in_path("z:\\Photos", "c:\\dest\\nas_photos.csv")
#find_missing_source("c:\\dest\\photos_frompaapagift_7d_original.csv", "d:\\sorted.csv")
#find_missing_source("c:\\dest\\photos_frompaapagift_7d_edited.csv", "d:\\sorted.csv")
#find_missing_source("c:\\dest\\photos_frompaapagift_7d_album_and_staging.csv", "d:\\sorted.csv")
#find_missing_source("c:\\dest\\photos_frompaapagift_anaga.csv", "d:\\sorted.csv")
#find_missing_source("c:\\dest\\photos_frompaapagift.csv", "d:\\sorted.csv")
#find_missing_source("c:\\dest\\photos.old.csv", "D:\\sorted.csv")