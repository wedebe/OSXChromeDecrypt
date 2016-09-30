# OSXChromeDecrypt
Decrypt Google Chrome and Chromium Passwords on Mac OS X. No dependencies, quick, fast.

Great for if you want to export all of your passwords with one command, as oppposed to manually selecting each one through Chrome's UI.

Also great for forensic analysis, as you can obtain the safe storage key through a variety of methods.
____
This is a very lightweight python script that will

1.) Look for any Google Chrome Profiles
  
2.) Look for any stored passwords in those profiles (I.e. passwords saved via "Would you like to remember this password" in       chrome)
  
3.) Get the decryption key from the keychain WITHOUT having to confirm the keychain password.
  
4.) Use this key to decrypt the passwords
  
5.) Print out all of the passwords in a pretty format.
  
____

You can also run this without ever having the program touch the disk, by running the following command 

"curl https://raw.githubusercontent.com/manwhoami/OSXChromeDecrypt/master/ChromePasswords.py | python" 
