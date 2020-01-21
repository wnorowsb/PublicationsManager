import requests
import json

username= input("Enter username:")
password= input("Enter password:")

def changeHref(href):
    href = href.replace('service', '0.0.0.0:80')
    return href

def main():
    while True:
        print('Type mode to enter: \'publications\', \'upload file\' or \'show files\'')
        mode = input()
        if mode =='publications':
            listPublications()
        if mode == 'upload file':
            uploadFile()
        if mode == 'show files':
            showFiles()
        

def showFiles():
    allFiles = requests.get('http://0.0.0.0:80/files', headers= {"Authorization": username + ':' + password})
    allFiles = json.loads(allFiles.text)
    fdict = {}
    for k, v in allFiles.items():
        print(v['id'])
        fdict[v['id']] = v
    while True:
        print("Type \'download\' or \'delete\' <fid> to action files \'back\' to exit this mode ")
        entry=input()
        entry=entry.split()
        if (entry[0]=='download'):
            downloadFile(fdict[entry[1]]['_links']['download']['href'])
        if (entry[0]=='delete'):
            requests.delete(fdict[entry[1]]['_links']['delete']['href'], headers= {"Authorization": username + ':' + password})
        if (entry[0]=='back'):
            return True





def newPublication():
    data = {}
    print('Enter author:')
    data['author'] = input()
    print('Enter title:')
    data['title'] = input()
    print('Enter year:')
    data['year'] = input()
    response = requests.post('http://0.0.0.0:80/publications', headers= {"Authorization": username + ':' + password}, data=data)
    return response

def listPublications():
    while True:
        response = requests.get('http://0.0.0.0:80/publications', headers= {"Authorization": username + ':' + password})
        response = json.loads(response.text)
        pubs = {}
        print("Publications:")
        for _, v in response.items():
            href = v["_links"]["view"]["href"]
            id = v["id"]
            print (str(id))
            pubs[str(id)] = href
        print("Enter publication id, \'create\' or \'back\' to go to previus screen")
        entry = input()
        if (entry == 'back'):
            return True
        if entry in pubs:
            details(entry, pubs[entry])
        if (entry == 'create'):
            newPublication()

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

def uploadFile():
    path = input("Enter file path or /'back/' to exit this mode.")
    if (path=='back'):
        return True
    files = { 'file': open(path, 'rb') }
    r = requests.post('http://0.0.0.0:80/files', files = files, headers= {"Authorization": username + ':' + password})
    return r.text

def downloadFile(href):
    response = requests.get(href, headers= {"Authorization": username + ':' + password})
    for k, v in request.files:
        v.save(k)
    return True

    
def details(fid, href):
    response = requests.get(changeHref(href), headers= {"Authorization": username + ':' + password})
    pub = response.json()
    print("Id:" + str(pub['id']))
    print("Title:" + pub['title'])
    print("Author:" + pub['author'])
    print("Year:" + str(pub['year']))
    allFiles = requests.get('http://0.0.0.0:80/files', headers= {"Authorization": username + ':' + password})
    allFiles = json.loads(allFiles.text)
    fids=[]
    for k, v in allFiles.items():
        fids.append(str(v['id']))
    print("Linked Files:")

    for k, v in pub['_links'].items():
        if (k[0:4] == 'file'):
            print(pub['_links'][k]['name'])
    
    while True:
        print ("type \'link <fid>\' to link file, \'unlink <fid>'\ to unlink, \
        or \'delete\' to delete this publication or \'back'\ to go back. ")
        entry = input()
        entry=entry.split()
        if(entry[0] == 'link'):
            if (entry[1] in fids):
                response = requests.post(changeHref(pub["_links"]["linkFile"]["href"]).replace('<fid>',entry[1]), \
                    headers= {"Authorization": username + ':' + password})
                displayPub(href)
            else:
                print('There is no file with this id.')
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