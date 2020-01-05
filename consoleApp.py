import requests
import json

username= input("Enter username:")
password= input("Enter password:")

def changeHref(href):
    href = href.replace('service', '0.0.0.0:80')
    return href

def main():
    while True:
        print('Type \'publications\' \
        to manage and display publications or \'files\' to manage files')
        mode = input()
        if mode =='publications':
            listPublications()

def listPublications():
    response = requests.get('http://0.0.0.0:80/publications', headers= {"Authorization": username + ':' + password})
    response = json.loads(response.text)
    pubs = {}
    print("Publications:")
    for _, v in response.items():
        href = v["_links"]["view"]["href"]
        id = v["id"]
        print (str(id))
        pubs[str(id)] = href

    while True:
        print("Enter publication id or \'back\' to go to previus screen")
        entry = input()
        if (entry == 'back'):
            return True
        if entry in pubs:
            details(entry, pubs[entry])

def displayPub(href):
    response = requests.get(changeHref(href), headers= {"Authorization": username + ':' + password})
    pub = response.json()
    print("Id:" + str(pub['id']))
    print("Title:" + pub['title'])
    print("Author:" + pub['author'])
    print("Year:" + str(pub['year']))
    print("Linked Files:")

    for k, v in pub['_links'].items():
        if (k[0:4] == 'file'):
            print(pub['_links'][k]['name'])

    
def details(fid, href):
    response = requests.get(changeHref(href), headers= {"Authorization": username + ':' + password})
    pub = response.json()
    print("Id:" + str(pub['id']))
    print("Title:" + pub['title'])
    print("Author:" + pub['author'])
    print("Year:" + str(pub['year']))
    allFiles = requests.get('http://0.0.0.0:80/files')
    allFiles = json.loads(allFiles.text)
    print("Linked Files:")

    for k, v in pub['_links'].items():
        if (k[0:4] == 'file'):
            print(pub['_links'][k]['name'])
    
    while True:
        print ("type \'link <fid>\' to link file, \'unlink <fid>'\ to unlink, \
         \'delete\' to deelete this publication or \'back'\ to go back. ")
        entry = input()
        entry=entry.split()
        if(entry[0] == 'link'):
            response = requests.post(changeHref(pub["_links"]["linkFile"]["href"]).replace('<fid>',entry[1]), \
                headers= {"Authorization": username + ':' + password})
            displayPub(href)
        if(entry[0] == 'unlink'):
            response = requests.delete(changeHref(pub["_links"]["unLinkFile"]["href"]).replace('<fid>',entry[1]), \
                headers= {"Authorization": username + ':' + password})
            displayPub(href)
        if(entry[0] == 'delete'):
            response = requests.delete(changeHref(pub["_links"]["delete"]["href"]), \
                headers= {"Authorization": username + ':' + password})
            return True
        if(entry[0] == 'back'):
            return True


if __name__ == '__main__':
    main()