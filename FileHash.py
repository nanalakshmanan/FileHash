#!/usr/bin/env python

import sys
import hashlib
import glob
import os
import csv

#BUF_SIZE = 67108864
#BUF_SIZE = 268435456
BUF_SIZE=65536
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

        with open(self.filename, 'rb') as file:
            readcount = 1
            while True:
                data = file.read(BUF_SIZE * readcount)
                if not data:
                    break
                sha1.update(data)

                if readcount < 4096:
                    readcount += 1
    
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

def get_all_hash():
    get_hash_in_path("D:\\Nana\\OneDrive\\Sorted", "D:\\testpy.csv")

def get_hash_in_path(path, csvfilename, recursive=True):
    "Get hash of all files recursively in the given path and store details in the specified filename"
    count = 0
    printstr = ""
    hashes = []
    visitmap = {}

    csvfile = CSVFile(csvfilename, fieldnames=["Hash", "Filename"])

    if csvfile.exists():
        # create a map of already visited files
        rows = csvfile.get_rows()
        for row in rows:
            visitmap[row['Filename']] = row

    for filename in glob.iglob(path + '**/**', recursive=recursive):
        if os.path.isdir(filename):
            continue

        # if file has already been processed, skip
        if filename in visitmap.keys():
            continue

        count +=1

        f = FileHash(filename)
        f.compute_file_hash()

        hashes.append({"Hash":f.sha1, "Filename":f.filename})
        printstr += f.filename + "\n"

        if count == 10:
            # write 100 objects to csv file and print on screen
            csvfile.append(hashes)
            print(printstr)
            hashes = []
            printstr = ''
            count = 0
    
    # write the final set
    csvfile.append(hashes)
    print(printstr)

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


#test()
#get_all_files()
get_all_hash()
#find_duplicates()