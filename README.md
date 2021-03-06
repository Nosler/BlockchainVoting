## Authors

Sam champer <br/> Andrea Nosler

## Installation

This project uses Python 3.7.2.
Get it at: https://www.python.org/downloads/

You may need to install python-pip seperately depending on you OS.

This project uses pipenv to create an environment. To install it, run:
```
pip install pipenv
```
Then install project dependencies with:
```
pipenv install
```
This project can optionally expose a locally hosted node by giving it a public URL.
If you want to run the project in this way,
one of the best tools to do so is ngrok.
Get it at: https://ngrok.com/. For maximum convenience, place ngrok in
the project root directory.

## Usage

### How to quickly start the app 
Install as above. Let's say I want to allow 20 people to vote.
Open two terminals (or PowerShell windows - anything like that will work). 
In one of them, run:
```
pipenv run init -n 20
```
When the keys are done being generated, use the other terminal window to run:
```
pipenv run node
```
Now, to expose this server to the web
(assuming you put ngrok it in the directory), run:
```
./ngrok.exe http 5000
```
Now your server can be accessed online. Copy one of the "Forwarding" links from ngrok.
This is where you'll send the people who are allowed to vote.

But before people can vote, they'll each need a vote key. Send all the people who get
to vote a secret key from the /secret_keys folder. You can use email, a messenging program,
or even better, send them a snail mail with a floppy disk containing the key.

If you're a voter and you have a key, you can vote by navigating to the ngrok address,
entering the number corresponding with the key in the "Voter ID #" field, and then linking
the key in the "Upload Voter Key" field.

That's it!

----------------------

### Detailed description of commands and command line args:

* 1: After installing, setup a node to mine as many votes as you'll need,
and build the initial blockchain. Do this by running ``init``.
This has optional arguments:<br>
``-p`` to specify a port (default 4999) <br>
``-n`` to specify number of votes (default 10)<br>
For example, to start an election with 100 people and run the startup server
on port 7777, run the following command:
```
pipenv run init -p 7777 -n 100
```
* 2: After the miner has finished generating the keys and mining the votes,
a standard vote manager node can be started and import the chain from the miner.
To do so, *while the miner is still running,* use a separate terminal
to run ``node``. This command has optional arguments: <br>
``-p`` to specify a port (default 5000) <br>
``-src`` to specify an IP address of a server with the current
        blockchain (default http://127.0.0.1:4999) <br>
``-log`` include this argument to enable more verbose logging of node status. <br>
For example, to spool up a new vote manager node on port 5001 with verbose
logging and to take the blockchain generated by ``init`` command above, run:
```
pipenv run node -p 5001 -src http://127.0.0.1:7777 -log
```
* 3: Now, a server has been initialized and can accept votes.
However, for people to vote, they must be given a vote.
Voting requires each voter to attach a special RSA key.
These are generated in advance and deposited in the
``/secret_keys`` folder. One must be sent to each voter See:
https://github.com/Nosler/cis433-BlockchainVoting/blob/master/secret_keys/secret_key_info.md

The server can be exposed to the internet using ngrok.
To establish a secure tunnel to port 5001, run:
```
./ngrok.exe http 5001
```
For more details on ngrok, see https://ngrok.com/.

## List of commands:

Server that mines initial votes:
```
pipenv run init <-p port_number> <-n number_of_votes> <-h help>
```
Server that operates as a node during an election:
```
pipenv run node <-p port_number> <-src source_ip> <-log> <-h help>
```
Give your locally hosted server a URL on the internet:
```
./ngrok https <port_number>
```
Run unit tests for the blockchain and cryptography functions:
```
pipenv run python -m unittest
```
<br>
