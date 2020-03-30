
import json, io
from pprint import pprint

# Purpose built importer to import an openlibrary dump into the database

INPUT_FILE = "/mnt/g/ol_dump_2020-02-29.txt/ol_dump_2020-02-29.txt"
DELIMTER = "\t"
IGNORE_LIST = ["/type/page", "/type/redirect", "/type/delete", "/type/library",
 "/type/usergroup", "/type/template", "/type/i18n", "/type/rawtext",
 "/type/macro", "/type/backreference", "/type/type", "/type/home",
 "/type/page", "/type/local_id", "/type/i18n_page",
 "/type/doc", "/type/permission", "/type/about",
 "/type/content", "/type/user", "/type/scan_record",
 "/type/scan_location", "/type/object", "/type/collection"]

def doImport():
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            line_split = line.split(DELIMTER)
            #pprint(line_split)

            record_type = line_split[0]

            source_key = line_split[1] #keep this to give credit to openlibrary

            #these are probably not needed
            #revision = line_split[2]
            #last_modified = line_split[3]

            json = line_split[4]

            if record_type == "/type/author":
                pass
            elif record_type == "/type/edition":
                pass
            elif record_type == "/type/work":
                pass
            elif record_type == "/type/subject":
                pass
            elif record_type == "/type/language":
                pass
            elif record_type == "/type/volume":
                pass
            elif record_type == "/type/series":
                pass
            elif record_type in IGNORE_LIST: # we don't need to care about pages, redirects, deletions, etc
                pass
            else:
                print("WARN: unknown record type: ", record_type)
                print(json)
            

if __name__ == "__main__":
    doImport()




