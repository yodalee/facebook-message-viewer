Facebook Message Viewer
=======================

Facebook Message Viewer is a local web service allows you to view your history message in a more convenient way.

# Usage


## Start Server

* Linux

You need to install python 3 with your package manager, and run the messageviewer.py
` python messageviewer.py`

Use your browser, visiting `http://localhost:8080/`

* Windows

Simply run the messageviewer.exe

Use your browser, visit `http://localhost:8080/`

## Upload message.htm

You can download "a copy of your Facebook data" in [Facebook setting page](https://www.facebook.com/settings). It includes Messenger (chat) messages log in file `messages.htm`, which we targets on. Currently we request that you download your archive in English interface.

In the website UI, click `upload` in the navigation bar above, and upload `messages.htm`.

The messages will be processed in background, which may takes about 1-2 minutes. Depend on how many messages log to be processed.

## View Messages

In `view` tab, you can view all the history message.

* You can select date in calendar to view messages on specific day.

* You can click on someone's name to change their name.

# Note

Facebook sometimes change user name in log file to their facebook id, which I cannot solve.

# Bugs or feature request

* Please report bugs / feature-request to github issue tracker.

* Contribution is always welcome.
