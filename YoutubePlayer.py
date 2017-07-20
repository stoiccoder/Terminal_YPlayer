from colorama import Fore, Back, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from beautifultable import BeautifulTable
from mechanize import Browser
from random import randint, shuffle
from bs4 import BeautifulSoup
import sys, tty, termios
import pickle, multiprocessing, os, signal, time
import pyautogui, colorama
import lxml
from lxml import etree
import urllib, socket, copy

arr = dict()
flag = False
inoutermenu = False
pnow = []
copt = Options()
copt.add_argument("--disable-gesture-requirement-for-media-playback")
driver = webdriver.Chrome(chrome_options=copt)
time.sleep(0.5)
pyautogui.hotkey('alt', 'space')  # Minimise chrome on startup.
pyautogui.hotkey('n')
path = os.path.realpath("Open.html")
driver.get("file:" + str(path))
curr = 0
pids = multiprocessing.Queue()
cur = multiprocessing.Queue()  # multiprocessing function communication
state = multiprocessing.Queue()
state2 = multiprocessing.Queue()
ls = []
colorama.init()


def put_cursor(x, y):
    print "\x1b[{};{}H".format(y + 1, x + 1)


def clear():
    print "\x1b[2J"


def method2(link):
    try:
        youtube = etree.HTML(urllib.urlopen(link).read())
        video_title = youtube.xpath("//span[@id='eow-title']/@title")
        return ''.join(video_title)
    except:
        print "Method 2 also failed. Please check the link."
        return -1


def is_connected():
    try:
        # connect to the host -- tells us if the host is actually reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except:
        pass
    return False


def pushIntoFile():
    global arr
    try:
        file1 = open("MusicLinks.txt", 'w')
        pickle.dump(arr, file1)
    except Exception as e:
        print "Could not push into database."
        print e.message
    finally:
        file1.close()


def store():
    while True:
        link = raw_input("Enter link\n")
        link = link.strip()
        if (link == 'X') or (link == 'x'):
            break
        print "Collecting song info..."
        if link.find("www.youtube.com") == -1:
            print Fore.GREEN, "Not a valid YouTube link.", Fore.RESET
            continue
        br = Browser()
        global arr
        try:
            br.set_handle_robots(False)
            respo = br.open(link)

            soup = BeautifulSoup(respo, "html.parser")
            name = soup.find("title")
            name = name.text
        except Exception as e:
            print "Not working. Trying method 2..."
            name = method2(link)
            if name == -1:
                continue
        finally:
            br.close()

        try:
            fil = open("MusicLinks.txt", 'rb')
            arr = pickle.load(fil)
            fil.close()
        except Exception as e:
            print "Creating new file to store links."
        finally:
            if link in arr:
                print Fore.YELLOW, "Song link already present.", Fore.RESET
            else:
                arr[link] = name
                print Fore.YELLOW, "Song added successfully", Fore.RESET
        pushIntoFile()


def load():
    global arr
    try:
        fil = open("MusicLinks.txt", 'rb')
        arr = pickle.load(fil)
        fil.close()
    except Exception as e:
        print Fore.GREEN, "No song found. Please add some songs first.", Fore.RESET


def playSongNumber():
    load()
    global pnow, curr
    while True:
        x = raw_input("Enter number between 1 and {0} (x to go back) ".format(len(arr)))
        if (x == "X") or (x == "x"):
            chh = '-1'
            break
        try:
            x = int(x)
        except:
            print "Not a number."
            continue
        if (x > 0) and (x <= len(arr)):
            ind = arr.keys()[x - 1]
            pnow.append((arr[ind], ind))
            curr = len(pnow) - 1
            chh = '1'
            break
        else:
            print "Number not in range."
    return chh


def show(what):
    chh = '0'
    global pnow, curr, arr
    if what == '1':
        print Fore.WHITE
        print Back.BLUE
        x = 1
        for song in arr:
            print str(x) + "-" + arr[song]
            x += 1
        print Style.RESET_ALL
        chh = playSongNumber()
    elif what == '2':
        query = raw_input("Enter search query ")
        temp = []
        query = query.lower()
        for s in arr:
            if arr[s].lower().find(query) != -1:
                temp.append((arr[s], s))
        l = len(temp)
        if l == 0:
            print "No song found."
            chh = '-1'
            return chh
        elif l > 1:
            print "More than 1 result found: "
        print Fore.WHITE
        print Back.BLUE
        for so in temp:
            print so[0]
        print Style.RESET_ALL
        if l == 1:
            pnow.append(temp[0])
            curr = len(pnow) - 1
        if l > 1:
            print("Play all- 1 or Modify query- 2\n")
            chh = inp()
            if chh == '1':
                pnow = []
                pnow = copy.deepcopy(temp)
    elif what == '4':
        pnow = []
        chh = '1'
        r = arr.keys()[randint(0, len(arr) - 1)]
        pnow.append((arr[r], r))
        curr = 0
    elif what == '3':
        chh = playSongNumber()
    else:
        print "Invalid Input."
        chh = '-1'
    return chh


def play():
    load()
    global flag, inoutermenu, cur, curr, state2
    while (True):
        state2.put(1)
        print Fore.CYAN
        table = BeautifulTable()
        table.column_headers = ['Function', 'Key', 'Function', 'Key']
        table.append_row(["Show all tracks", "1", "Search song/artists", "2"])
        table.append_row(["Enter song number", "3", "Play a random song", "4"])
        table.append_row(["Go to main menu", "5", "Go back to player", "Backspace"])
        print table
        print Style.RESET_ALL
        while True:
            ch = inp()
            if (ch not in ['1', '2', '3', '4', '5']) and (ord(ch) != 127):
                continue
            else:
                break
        if ch == '5':
            return
        elif ord(ch) == 127:
            if inoutermenu:
                flag = True
                try:
                    curr = cur.get(timeout=0.1)
                except:
                    pass
                try:
                    temp = state2.get(timeout=0.1)
                except:
                    pass
                playing()
                continue
            else:
                print Fore.YELLOW, "Choose a song first.", Fore.RESET
                continue
        elif ch in ['1', '2', '3', '4']:
            chh = show(ch)

        if chh == '-1' or chh == '2' or ch == '-2':
            continue
        elif chh == '0' or chh == '1':
            flag = False
            try:
                temp = state2.get(timeout=0.1)
            except:
                pass
            playing()


def prettyPrint(c):
    os.system("tput reset")
    put_cursor(0, 0)
    print "Now Playing: " + pnow[c][0]
    put_cursor(0, 1)
    print Fore.GREEN
    print "spacebar-play/pause  n-next  p-previous  backspace-go back"
    print Fore.RESET


def playing():
    global inoutermenu
    inoutermenu = True
    global driver, curr, pnow, pids, flag, ls, state, cur, state2

    while True:
        if flag == False:
            driver.get(pnow[curr][1])
        try:
            num = state.get(timeout=0.1)
        except:
            prettyPrint(curr)
        try:
            temp = state2.get(timeout=0.1)
        except:
            prettyPrint(curr)

        for jobs in multiprocessing.active_children():
            jobs.terminate()

        t = multiprocessing.Process(target=change, args=(pids, cur, state))
        t.daemon = False
        t.start()

        while pids.qsize() != 0:
            ls.append(pids.get())

        for x in range(len(ls)):
            try:
                os.kill(ls[x], signal.SIGKILL)  # Save Memory Save Life
            except:
                continue
            finally:
                ls.pop(x)

        while True:
            flag = False
            com = inp()
            com = com.lower()
            try:
                curr = cur.get(timeout=0.1)
            except:
                pass
            if com == 'n':
                curr += 1
                if curr >= len(pnow):
                    curr = 0
                break
            if com == 'p':
                curr -= 1
                if curr < 0:
                    curr = len(pnow) - 1
                break
            if ord(com) == 127:  # Backspace
                return
            if ord(com) == 32:  # Space bar
                # driver.find_element_by_tag_name('body').send_keys(Keys.SPACE)
                # driver.execute_script('document.getElementsByTagName("video")[0].pause()')
                vid = driver.find_element_by_tag_name("video")
                vid.click()  # pause and play both by space bar.


def change(pids, cur, state):
    global curr, flag
    pids.put(os.getpid())
    status = -1
    while status != 0:
        time.sleep(0.5)
        status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
    curr += 1
    if curr > len(pnow) - 1:
        curr = 0
    cur.put(curr)
    state.put(1)
    flag = False
    playing()


def prand():
    load()
    global pnow, arr, curr
    for i in arr:
        pnow.append((arr[i], i))
    shuffle(pnow)
    curr = 0
    playing()


def inp():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def delete():
    global arr
    print Fore.WHITE
    print Back.BLUE
    x = 1
    for song in arr:
        print str(x) + "-" + arr[song]
        x += 1
    print Style.RESET_ALL
    s = raw_input("Enter song numbers (space separated) to delete.    (x to cancel)\n")
    if s.strip()=='x' or s.strip()=="X":
        print "No song deleted."
        return
    z = s.strip().split()
    if len(z) == 0:
        print "No number entered."
        return
    for x in z:
        try:
            x = int(x)
        except:
            print Fore.YELLOW, "Not a valid number {0}. Skipping it.".format(x), Fore.RESET
            continue
        if (x > 0) and (x <= len(arr)):
            ind = arr.keys()[x - 1]
            del arr[ind]
        else:
            print Fore.YELLOW, "Song number {0} not found. Skipping it.".format(x), Fore.RESET
    pushIntoFile()


def app():
    global driver, arr, state2
    if not is_connected():
        print "You are offline!"
        print "Press enter to continue anyway."
        ch = inp()
        if ord(ch) != 13:
            sys.exit(1)
    while True:
        state2.put(1)
        print Fore.RED
        table = BeautifulTable()
        table.column_headers = ['Function', 'Key']
        table.append_row(["Select songs to play", "1"])
        table.append_row(["Play all songs randomly", "2"])
        table.append_row(["Add links to new Songs", "3"])
        table.append_row(["Delete songs", "4"])
        table.append_row(["Exit Player", "5"])
        print table
        print Fore.RESET
        choice = inp()
        if choice == '1':
            load()
            if len(arr) > 0:
                try:
                    temp = state2.get(timeout=0.1)
                except:
                    pass
                play()
        elif choice == '2':
            load()
            if len(arr) > 0:
                try:
                    temp = state2.get(timeout=0.1)
                except:
                    pass
                prand()
        elif choice == '3':
            print Fore.YELLOW, "Enter x any time to exit.", Fore.RESET
            try:
                temp = state2.get(timeout=0.1)
            except:
                pass
            store()
        elif choice == '4':
            load()
            if len(arr) > 0:
                try:
                    temp = state2.get(timeout=0.1)
                except:
                    pass
                delete()
        elif choice == '5':
            kill()
            break
        else:
            print "Invalid Choice"


def kill():
    global pids, ls
    for p in multiprocessing.active_children():
        p.terminate()
    while pids.qsize() != 0:
        ls.append(pids.get())
    print "Processes", ls
    for pi in ls:
        try:
            os.kill(pi, signal.SIGKILL)
        except OSError:
            continue
    driver.quit()


app()
