import os
import dsa
import time
import base64
import secrets 
import hashlib
import binascii 
import database
from Crypto import Random
from tinyec import registry 
from Crypto.Cipher import AES

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
def compress(pubKey):
    return hex(pubKey.x) + hex(pubKey.y % 2)[2:]

def eecdh():
    curve = registry.get_curve('brainpoolP256r1')
    PrivKey1 = secrets.randbelow(curve.field.n)
    PubKey1 = PrivKey1 * curve.g 
    PrivKey2 = secrets.randbelow(curve.field.n)
    PubKey2 = PrivKey2 * curve.g
    SharedKey1 = PrivKey1 * PubKey2
    SharedKey2 = PrivKey2 * PubKey1
    if SharedKey1 == SharedKey2: 
        password = compress(SharedKey1)
        print("\nThe shared keys are equal.")
        print("ECDH has successfully been implemented.")
    else:
        print("Shared keys are not equal.")
        exit()
    return password 

def encrypt(raw):
    password = eecdh()
    send = base64.b64encode(password.encode("utf-8"))
    private_key = hashlib.sha256(send).digest()
    raw = pad(raw)
    iv = Random.new().read(AES.block_size) 
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    encrypted_data = base64.b64encode(iv + cipher.encrypt(raw.encode('utf-8')))
    l = dsa.signature(str(encrypted_data)) 
    return encrypted_data , password , l 
                    
def decrypt(enc, password,p,q,g,r,s,y):
    enc = base64.b64decode(enc)
    isvalid = dsa.verification(str(enc),p,q,g,r,s,y) 
    if isvalid:
        send = base64.b64encode(password.encode("utf-8"))
        private_key = hashlib.sha256(send).digest()
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:])) 
    else:
        print("Signature invalid.") 
 
def SendRetrieve(name):
    while True:
        print(f"\n{name}, do you want to send data(0), retrieve data(1) or exit(2) ?")
        choice = int(input("Choice : "))
        if not choice :
            plaintext = input("Text to send : ")
            encrypted_message, sharedkey, l = encrypt(plaintext)
            database.Store_in_Cloud(name, binascii.hexlify(base64.b64encode(encrypted_message)).decode('utf-8'), sharedkey, l)
            print("Shared key for this transaction : ",sharedkey.upper())
            print("Verifying digital signature . . .")
            time.sleep(1) 
            print("Data encrypted using AES.")
            print("\nData sent successfully!")
        elif choice == 1:
            print("\nDecrypting the data using AES ......")
            time.sleep(1)
            print("\nDecryption complete !")
            print("\n---------- Displaying the data saved -------------------\n")
            k = 0
            l = database.Retrieve_from_Cloud(name)
            for i in l:
                k+=1
                decrypted_message = decrypt(i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8]).decode('utf-8')
                print(f'{k}] ',decrypted_message)
            print()
            print("--------------------------------------------------------")
        else: 
            break       

def Login(name): 
    if database.ifExists(name) == 0:
        print("Please Sign up to Login.") 
        return False   
    l = database.fetchData(name)
    name, salt, key = l[0],l[1],l[2]
    salt, key = base64.b64decode(salt), base64.b64decode(key)
    new_key = hashlib.pbkdf2_hmac('sha256', input("Password : ").encode('utf-8'), salt, 100000)
    if new_key == key:
        print("Login successful ! ")
    else: 
        print("Invalid password. Try again.") 
        return False 
    return True

def Signup(name):
    if database.ifExists(name):
        print("Username already exists!") 
        return False   
    salt = os.urandom(32) 
    key = hashlib.pbkdf2_hmac('sha256', input("Password : ").encode('utf-8'), salt, 100000)
    database.insert(name ,binascii.hexlify(base64.b64encode(salt)).decode('utf-8'),binascii.hexlify(base64.b64encode(key)).decode('utf-8'))
    print("Signed up successfully !")
    return True
 
while True:
    print("\n1.Login\n2.Sign up\n3.Exit\n")
    ch = int(input("Choice : "))
    if (ch!=3): name = input("Enter username : ")
    if ch==1:
        if Login(name):
            SendRetrieve(name)
        continue
    if ch==2:
        if Signup(name):
            SendRetrieve(name)
        continue
    else:
       break      