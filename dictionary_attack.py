print("  _____________________________________________________________________________________________\n")
print("  ---------------------------------------------------------------------------------------------\n")

# Prompt for wordlist file
wordlist_file = ""
while True:
    wordlist_file = input("Now insert wordlist file's NAME or PATH: ")
    if wordlist_file.endswith(".txt") and os.path.isfile(wordlist_file):
        break
    else:
        print("Invalid wordlist file. Please make sure the file exists and has a valid format.")

# Import the .hc22000 file into hashcat, find out the password, and show it
subprocess.run(["hashcat", "-m", "22000", hc22000_file, wordlist_file, "--show"])

# Delete the hc22000 file
os.remove(hc22000_file)
