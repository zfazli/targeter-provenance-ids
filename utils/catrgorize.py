import csv
import argparse
import fnmatch
import re
import random



#----------------------------------------------------theia-e3    and theia-e5
def categorize_unix(value ):

    unix_categories = {
1:{#Package Management and Installation
    'dpkg','apt-config','apt-get','dpkg-statoverride','update-notifier'},
2:{#Network Services 
    'NetworkManager','modem-manager','apache2','bluetooth-applet','nm-applet',"ntpd", "dhclient", "dhclient3","nginx","sshd","sshd:"},
3:{#User Interface and Desktop Environment
    'xterm','X','nautilus','fluxbox','unity-panel-service','gnome-terminal','gnome-session','unity-2d-spread','unity-2d-panel','unity-2d-shell','gnome-control-center','gnome-settings-daemon','gnome-screensaver','gtk-logout-helper','unity-applications-daemon','mission-control-5','unity-files-daemon','Xvnc4','metacity'
,"tumblerd", "xfdesktop", "Thunar", "xfsettingsd", "xfce4-session", "xfce4-settings-manager"," xfce4-power-manager", "xfwm4", "unity-greeter", "xscreensaver","gedit", "evince", "gnomine", "mahjongg", "sol", "helper-dialog", "exo-open", "exo-helper-1", "xfrun4"},
4:{#System and Core Services
    "stat", 
    'accounts-daemon','udevd','unity-musicstore-daemon','bamfdaemon','upowerd','gvfsd','zeitgeist-daemon','zeitgeist-datahub','zeitgeist-fts','whoopsie','rtkit-daemon','acpid',
    'logrotate','console-kit-daemon','upstart-socket-bridge','upstart-udev-bridge','anacron','cron','run-parts','CRON','cupsd','colord',"syslogd","devd","sysctl","dmesg","kldstat","newsyslog", 
    "adjkerntz", "dlogd", "atrun","pciconf","pfctl","ipfw","ipfstat","route","sendmail", "resizewin", "sync","mail.local","alpine" },
5:{#Desktop Notifications and Indicators
    'thunderbird' ,'notify-osd','hud-service','indicator-messages-service','indicator-datetime-service','indicator-session-service','indicator-application-service','indicator-printers-service','indicator-sound-service','telepathy-indicator','pulseaudio','unity-music-daemon'},
6:{#Web Browsers and WebView
    'firefox' },
7: {#Scripting and Programming Languages
    'python','perl', "python3.6", "python2.7","ld.lld", "csh", "rz","jq"},
8:{#login shell commands
    'sh','-bash'},
9:{# Command-Line and Shell Tools
     "bash", "vim", "tmux","tmux-1002", "at","pkg","tty" },
10:{#Database Services
    'postgres','postgres:',"prometheus-node-exporter"},
11:{# System and Text Processing Tools
    "grep", "sed", "ls", "sort", "cat", "uname","tee",
         "awk","nawk","head", "tail", "egrep","uniq", "cmp","diff", "wc","xxd"},
12: {  #  Security and Monitoring Tools
        "sudo","su","openssl","ssh","scp","ulog-helper","lockf"},
13: { #Network Command-Line Tools
        "ifconfig","netstat","wget", "ping","fetch" },
14: {  # Time, Randomness, and Expression Utilities
        "fortune", "expr", "date"},
15: {  # Messaging Tools
        "write", "msgs", "logger",  "kill"},
16: {  # Development and Build Tools
        "make", "md5", "jot", "main", "cc" },
17: {  # System Monitoring and Environment Tools
        "node_exporter","top", "uptime", "swapinfo","ps", "who","whoami", "hostname", "env","kenv" },

18: {  #File Management and Archiving Utilities
        "rm","unlink", "mkdir","mktemp", "cp", "mv", "du","df", "mount","bsdtar", "bzip2","xz", "bzcat","find" },
}


    
    
    try:
        item= (value.split()[0]).split('/')[-1]       
    except:
        item = "A"

    if value.startswith('/home/admin') or value.startswith('./'):  # User or Local Executed Scripts / Processes
             return 19
    for category, commands in unix_categories.items():
            if item in commands:
                return category
    return 20  # اگر آیتم در هیچ دسته‌ای نباشد

def categorize_andriod(value , type ):
    android_process_categories = {
    1: [  # System and Core Services
        "kernel",
        "system_server",
        "dex2oat",
        "crash_dump64",
        "app_process64",
        "com.android.internal.os.WebViewZygoteInit",
        "WebViewLoader-armeabi-v7a",
        "WebViewLoader-arm64-v8a",
        "android.ext.services",
        "com.android.settings:CryptKeeper",
        "com.android.managedprovisioning",
        "com.android.provision",
        "com.android.onetimeinitializer",
        "android.process.acore",
        "android.process.media",
        "com.android.smspush", 
        "com.android.calculator2", 
        "com.motorola.android.buacontactadapter", 
        "com.svox.pico",
        "com.android.externalstorage"
    ],
    2: [  # Package Management and Installation
        "com.android.packageinstaller",
        "com.vsrevogroup.revouninstallermobile",
        "com.fluxii.android.sideloaderforfiretv",
        "com.android.defcontainer",
    ],
    3: [  # Security and Monitoring Tools
        "com.bloketech.lockwatch",
    ],
    4: [  # Hardware and Communication Services
        "com.android.bluetooth",
        "com.android.nfc",
        "com.android.cellbroadcastreceiver",
        "com.android.printspooler",
        "com.android.keychain",
    ],
    5: [  #  User Interface and Desktop Environment
        "com.android.systemui",
        "com.android.deskclock",
        "com.android.phone",
        "com.android.contacts",
        "com.android.dialer",
        "com.android.messaging",
        "com.android.settings",
        "com.android.calendar",
        "com.android.gallery3d",
        "com.android.quicksearchbox",
        "com.android.email",
        "com.android.inputmethod.latin",
        "com.android.launcher3",
        "com.android.providers.calendar",
        "com.android.musicfx",      
        "com.android.music",
        "com.android.camera2",
        "system:ui",
         "com.android.documentsui", 
         "com.android.quicksearchbox"
    ],
    6: [  # Web Browsers and WebView
        "com.android.browser", 
        "org.mozilla.fennec_firefox_dev",
        "org.chromium.webview_shell",
        "com.kk.browser",
        "org.mozilla.fennec_vagrant",
        "org.mozilla.fennec_vagrant.CrashReporter",
    ],
    7: [  # Command-Line and Shell Tools
        "sh",
        "cmd",
        "toybox",
        "ping",
        "folio_daemon",
        "busybox"
    ],
    8: [  # Misc Apps
        "com.bhanu.torch",
        "com.dacic.torche",
        "com.jmt.clockwidget",
        "com.google.android.diskusage",
        "com.openinwhatapp",
        "com.googlecode.eyesfree.setorientation",
        "com.ap.SnapPhoto_Pro",
        "com.maxflame.barephone",
    ],
    9: [  #  Games, Media
        "com.antimony.heartache",
        "com.explusalpha.A2600Emu",
        "ca.jamdat.flight.bejeweled",
        "flenix.net.flenixapk",
        "com.tveazy.online",
        "de.belu.appstarter",
        "com.shkmishra.instadict",
        "com.socialnmobile.dictapps.notepad.color.note",
        "ch.blinkenlights.android.vanilla",
        "com.shinycore.picsaypro",
        "com.melodis.midomi",
        "com.Zee18IPTVAndrodidTV",
    ]}
    # android_file_categoris = {
    # 11: 
    # #'browser_cache_entries': 
    # {
    #     '/data/data/org.mozilla.fennec_firefox_dev/cache/nz9885vc.default/cache2/entries/'
    # },
    # 12: # 'browser_cache_metadata': 
    # {
    #     '/data/data/org.mozilla.fennec_firefox_dev/cache/'
    # },
    # 13: {"/system", "/system/bin", "/system/etc", "/system/framework", "/system/lib", "/system/vendor", "/sys/devices/system"},
    # 14: {"/data", "/data/data", "/data/user", "/data/media"},
    # 15: {"/proc", "/dev", "/dev/socket"},
    # 16: {"/system/fonts", "/system/media", "/system/media/audio"},
    # 17: {"/system/app", "/system/priv-app"},
    # 19:{ "/acct/"}
    
# } 

    if type == 'process' : 
        for category, commands in android_process_categories.items():
            if value in commands:
                return category
        return 10
    # if type == 'file':
    #     for category, paths in android_file_categoris.items():
    #         for p in paths:
    #             if value.startswith(p):
    #                 return category
    #     return 18
        

#----------------------------------------------------------------unix
def set_unix_categry (infile ): 
    data = []
    file = open(infile, "r", encoding="utf-8") 
    
    lines = file.readlines()
    for line in lines :
        row = line.split('$')
        if len(row) >= 3 :
                if  row[1] == "Subject": 
                    row[2] = categorize_unix( row[3] )
                else: 
                     row[2] = 0
                row[-1] = row[-1].split('\n')[0]
                data.append(row)

    with open(infile, "w", encoding="utf-8" , newline="" ) as file:
        writer = csv.writer(file, delimiter="$")
        writer.writerows(data)



def set_android_category (infile): 
    data = []
    file = open(infile, "r", encoding="utf-8") 
    lines = file.readlines()
    for line in lines :
        row = line.split('$')
        if len(row) >= 3 :
                if  row[1] == "Subject":  # بررسی مقدار دوم
                    row[2] = categorize_andriod( row[3] , 'process')
                if row[1] == 'FileObject' : 
                        # row[2] = categorize_andriod(row[3], 'file')
                        row[2] = 0
                if row[1] == 'NetFlowObject': 
                        row[2] = 0
                row[-1] = row[-1].split('\n')[0]
                data.append(row)

    with open(infile, "w", encoding="utf-8" , newline="" ) as file:
        writer = csv.writer(file, delimiter="$")
        writer.writerows(data)


def set_categry (infile , name): 
    if name == 'unix':
        set_unix_categry (infile )
    else:
        set_android_category(infile)


