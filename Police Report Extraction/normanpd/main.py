#!/usr/bin/env python
# -*- coding: utf-8 -*-
import normanpd
from normanpd import normanpd
def main():
# Download data
    links=normanpd.fetchincidents()
    print("Incident PDF URLs from where the data extracted")
    print("-----------------------------------------------")
    for url_extract_pdf in links:
        print(url_extract_pdf)
# Extract Data
    incidents = normanpd.extractincidents()
    #print(incidents.read())
# Create Dataase
    normanpd.createdb()
# Insert Data
    normanpd.populatedb(incidents)
# Print Status
    normanpd.status("normanpd.db")
if __name__ == '__main__':
   main()
