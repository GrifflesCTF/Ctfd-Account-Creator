import re
import requests
import random
import json
import os
import argparse
from colorama import init, Fore, Style
import time
import html

# Initialize colorama for cross-platform color support
init()

# Define color constants
SUCCESS = Fore.GREEN
ERROR = Fore.RED
INFO = Fore.BLUE
HEADER = Fore.MAGENTA
RESET = Style.RESET_ALL
HIGHLIGHT = Fore.YELLOW

def header():
    print(HEADER + r"""
   ______________________     ______                __            
  / ____/_  __/ ____/ __ \   / ____/_______  ____ _/ /_____  _____
 / /     / / / /_  / / / /  / /   / ___/ _ \/ __ `/ __/ __ \/ ___/
/ /___  / / / __/ / /_/ /  / /___/ /  /  __/ /_/ / /_/ /_/ / /    
\____/ /_/ /_/   /_____/   \____/_/   \___/\__,_/\__/\____/_/     
                                                                  
""" + RESET)

def Check_Ctfd(session,url):
    try:
        if('' in session.get(url).text):
            return True
        return False
    except Exception as ex:
        print(f" {ERROR}[❌] Error during CTFd check: {str(ex)}{RESET}")
        return False


def CheckTeam_Exist(url, req, user):
    try:
        resp = req.get(url+'/teams?field=name&q=%s'%user['team']).text
        all_ = list(zip(*list(re.findall(r'<a href="/teams/(.*?)">(.*?)</a>', resp))))
        if(len(all_) != 0):
            # Decode HTML entities before comparing
            decoded_names = list(map(lambda x: html.unescape(x).lower(), all_[1]))
            if(user["team"].lower() in decoded_names):
                return True        
        return False
    except Exception as ex:
        print(f" {ERROR}[❌] Error checking if team exists: {str(ex)}{RESET}")
        return False


def CheckUser_Exist(url,req,user):
    try:
        resp = req.get(url+'/users?field=name&q=%s'%user['pseudo']).text.replace("\n","").replace("\t","")
        all_ = list(zip(*list(re.findall(r'<a href="/users/(.*?)">(.*?)</a>',resp))))
        if(len(all_) != 0):
            if(user["pseudo"].lower() in list((map(lambda x: x.lower(), all_[1])))):
                return True        
        return False
    except Exception as ex:
        print(f" {ERROR}[❌] Error checking if user exists: {str(ex)}{RESET}")
        return False


def CheckTeam_User(url,req,user):
    try:
        verif = req.get(url+'/api/v1/users/me').text
        if(type(json.loads(verif)["data"]["team_id"]) == int):
            return True
        return False
    except Exception as ex:
        print(f" {ERROR}[❌] Error checking user account: {str(ex)}{RESET}")
        return False


def Join_Team(url,req,user):
    try:
        html = req.get(url + "/teams/join").text
        token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);    # Get token csrf
        post = {"name":user["team"],"password":user["team_password"],"_submit":"Join","nonce":token}    # Post Data
        resp = req.post(url+'/teams/join',post).text    # Create Team
        return CheckTeam_User(url,req,user)
    except Exception as ex:        
        print(f" {ERROR}[❌] Error joining the team: {str(ex)}{RESET}")
        return False


def Create_Team(url,req,user):
    try:
        time.sleep(4)
        html = req.get(url + "/teams/new").text
        token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);    # Get token csrf
        post = {"name":user["team"],"password":user["team_password"],"bracket_id": int(user["team_bracket"]),"_submit":"Create","nonce":token}    # Post Data
        resp = req.post(url+'/teams/new',post).text 
        return CheckTeam_User(url,req,user)
    except Exception as ex:
        print(f" {ERROR}[❌] Error during team creation: {str(ex)}{RESET}")
        return False
  

def Register_Account(req,user,url):
    try:
        html = req.get(url + "/register").text          # Get html page        
        token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);# Get token
        rep = req.post(url+'/register',{"name":user['pseudo'],"email":user['email'],"password":user['password'],"nonce":token,"_submit":"Submit"}).text# Post request
        if('Logout' in rep):
            return True
        return False
    except Exception as ex:
        print(f" {ERROR}[❌] Error during registration: {str(ex)}{RESET}")
        return False


def Login_Account(req,user,args):
    try:
        if(args.verbose):
            print(f"\n {INFO}[🔍] Checking if user '{user['pseudo']}' exists{RESET}")

        if(CheckUser_Exist(args.url,req,user)):
            # Login to account            
            if(args.verbose):
                print(f" {INFO}[🔑] Logging in to {user['pseudo']}'s account{RESET}")
            html = req.get(args.url + "/login").text          # Get html page        
            token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);# Get token
            rep = req.post(args.url+'/login',{"name":user['pseudo'],"password":user['password'],"_submit":"Submit","nonce":token}).text# Post request
            if('Logout' in rep):
                return True
            return False
        else:
            # Creating account
            if(args.verbose):
                print(f" {INFO}[✨] Creating account for {user['pseudo']}{RESET}")
            return Register_Account(req,user,args.url)
        
    except Exception as ex:
        print(f" {ERROR}[❌] Error during login: {str(ex)}{RESET}")
        return False


def Ctfd_Register(req,user,args):
    try:
        # Login/Create Account
        if(Login_Account(req,user,args)):

            if(args.verbose):
                print(f" {SUCCESS}[✅] Logged in successfully{RESET}")
                print(f" {INFO}[🔍] Checking if team '{user['team']}' exists{RESET}")

            # Check if team exist
            in_team = False
            if not CheckTeam_User(args.url,req,user):
                if(CheckTeam_Exist(args.url,req,user)):
                    # Join Team
                    if(args.verbose):
                        print(f" {INFO}[👥] Joining team '{user['team']}'{RESET}")
                    in_team = Join_Team(args.url,req,user)
                else:
                    # Create Team
                    if(args.verbose):
                        print(f" {INFO}[🛠️] Creating team '{user['team']}'{RESET}")
                    in_team = Create_Team(args.url,req,user)

                if(args.verbose and not in_team):
                    print(f" {ERROR}[❌] Error in the team process{RESET}")

            else:
                print(f" {INFO}[ℹ️] User {user['pseudo']} is already in a team{RESET}")


            return True,in_team
        else:
            return False,False
    except Exception as ex:
        print(f" {ERROR}[❌] Error during registration: {str(ex)}{RESET}")
        return False,False

def parse_args():
    parser = argparse.ArgumentParser(add_help=True, description='This tool is used to automatically create accounts on CTFd platform.')
    parser.add_argument("-u", "--url", dest="url", required=True, help="URL of the CTFd.")
    parser.add_argument("-c", "--config", dest="config_path", required=True, help="Path of the config (*.json).")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Use verbose mode.")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true", default=False, help="Use quiet mode.")
    parser.add_argument("-d", "--discord", dest="discord", action="store_true", default=False, help="Displays the account created in a Discord Message template")
    args = parser.parse_args()
    return args


def main():
    ## INIT
    args = parse_args()
    if(not args.quiet):
        header()
    os.chdir(os.path.abspath(os.getcwd()))
    session = requests.session()

    ## SANITIZE URL
    if not args.url.startswith("http://") and not args.url.startswith("https://"):
        args.url = "https://" + args.url    
    args.target = args.url.rstrip('/')

    ## CHECK IF VALID INPUT
    if(not Check_Ctfd(session,args.url)):
        print(f" {ERROR}[❌] Please provide a valid URL!{RESET}")
        return
    elif(not os.path.exists(args.config_path)):
        print(f" {ERROR}[❌] Please provide a valid path, config not found: {args.config_path}{RESET}")
        return
    else:
        ## Load config file
        try:
            config = json.loads(open(args.config_path, "r", encoding="UTF-8").read())
            print(f" {SUCCESS}[📂] Successfully loaded configuration file{RESET}")
        except Exception as e:
            print(f" {ERROR}[❌] Error loading config file: {str(e)}{RESET}")
            return

        ## Create account for all users
        total_users = sum(len(team["users"]) for team in config)
        success_count = 0
        
        print(f" {INFO}[🚀] Starting account creation for {total_users} users{RESET}")
        
        for i in range(len(config)):
            team_name = config[i]["team"]
            print(f" {HEADER}[👥] Processing team: {team_name}{RESET}")

            for user in config[i]["users"]:
                session.cookies.clear()

                # If Mail/Password Empty in Json
                if(user[1] == ""):
                    user[1] = "%s@tempmail.com"%(''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(12)))
                if(user[2] == ""):
                    user[2] = ''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12))

                data = {
                    "pseudo":user[0],
                    "email":user[1],
                    "password":user[2],
                    "team":config[i]["team"],
                    "team_password":config[i]["teampwd"],
                    "team_bracket":config[i]["teambracket"]
                    }

                print(f" {INFO}[⏳] Processing user: {user[0]}{RESET}")
                succeed,in_team = Ctfd_Register(session,data,args)
                
                if(succeed):
                    success_count += 1
                    if(not args.discord):
                        print(f" {SUCCESS}[✅] User successfully created!{RESET}\n")
                    else:
                        print("```")
                    
                    print(f"    \t- {'Name:':<12}\t{HIGHLIGHT}{data['pseudo']:>12}{RESET}")
                    print(f"    \t- {'Password:':<12}\t{HIGHLIGHT}{data['password']:>12}{RESET}")
                    print(f"    \t- {'Email:':<12}\t{HIGHLIGHT}{data['email']:>12}{RESET}")
                    if(in_team):
                        print(f"    \t- {'Team:':<12}\t{HIGHLIGHT}{data['team']:>12}{RESET}")
                        print(f"    \t- {'Team Pass:':<12}\t{HIGHLIGHT}{data['team_password']:>12}{RESET}")
                    if(args.discord):
                        print("```")        
                else:
                    print(f" {ERROR}[❌] Failed to login/create account for {user[0]}{RESET}")
                time.sleep(4)
        print(f"\n {SUCCESS}[🏁] Process completed! Created {success_count}/{total_users} accounts successfully{RESET}")


if __name__ == '__main__': 
    main()