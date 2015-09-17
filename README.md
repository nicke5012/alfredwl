# alfredwl

Wunderlist integration for Alfred2. Allows you to add tasks, show your lists, and show incomplete tasks through Alfred.

---

## Requirements
- [Alfred 2](https://www.alfredapp.com/)
- [Alfred Powerpack](https://www.alfredapp.com/powerpack/)

## Installation
In this repo you'll find a file called `alfredwl.alfredworkflow`. Download that and double-click. If you have Alfred 2 it should automatically open and import the workflow.

## Setup
You must set up this workflow before it can access your account. Setup involves two steps:
1. Getting a Client ID and Access Token from Wunderlist
2. Inputting the Client ID and Access Token to Alfred

Just follow the two steps below to set up the workflow!

#### Step 1: Get a Client ID and Access Token
1. https://developer.wunderlist.com/apps
2. Click the `Create App` button
3. Give the app a name and description, and input some url for the app url and callback url. It doesn't really matter what's input here, but here's an example:
    - *Name*: Alfred2 Workflow
    - *Description*: Integrate Wunderlist with Alfred
    - *App URL*: https://github.com/nicke5012/alfredwl
    - *Auth Callback URL*: https://github.com/nicke5012/alfredwl
4. Click `save` for your app. Once your app is created you'll see details for your app in a greyed-out section on https://developer.wunderlist.com/apps. Copy down the Client ID shown.
5. Click `Create Access Token`. Copy down the Access Token that is displayed.

#### Step 2: Input the Client ID and Access Token to Alfred
1. With the alfredwl workflow installed, start Alfred and type `wlsetup` followed by a space. Then paste in your Client ID and Access Token, separated by the characters ">>".
    - For example, if your Client ID is "abcdef" and your Access Token is "ghijk", the full command to Alfred would be `wlsetup abcdef>>ghijk`
2. Press `enter` to input your credentials. Off you go!


## Actions
Actions are initiated by keywords in Alfred. Start Alfred and type any of the following to access the workflow

- `wladd`: Add a task to your Wunderlist. You can specify which list to add the task by typing `wladd [list name]>>[task name]`. If no list name is specified, the task gets added to your Inbox.

- `wlshow`: Show your lists. From there you can select a list to see its incomplete tasks. You can also type `wlshow [list name]` to directly see the incomplete tasks in that list. When viewing a list's tasks, you can select a task to mark it as complete.
- `wlsetup`: Set up the workflow

![](/screenshots/wladd.jpg)
![](/screenshots/wladd-2.jpg)
![](/screenshots/wlshow.jpg)
![](/screenshots/wlshow-demo-list.jpg)

## Version History
1. Aug 23 2015: v1 - launch!
2. Sep 9 2015: v1.1 - fixed bugs caused by special characters
3. Sep 17 2015: v1.2 - 
    - New features:
      - added ability to mark tasks as completed through `wlshow`
      - added ability to specify which list to add a task to in `wladd`
    - Security improvements:
      - Moved storage of credentials to the Keychain. Also, this means that from now on you'll no longer have to go through setup when updating the workflow!