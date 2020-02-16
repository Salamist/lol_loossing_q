# LoL Losing Queue 
The say there's a Losing Queue in LoL
Let's try to find out :)

## To start
#### Prepare Python stuff
- Make sure to have Python 3.6+ installed
- Create and activate virtual environment (because you know it's good for you ;) )
- install requirements: `pip intall -r requirements.txt` 
#### Prepare Riot stuff
- Go to https://developer.riotgames.com/ 
- Create API key
- Store the key in `.api_key` file in root the of the repository

## run script
use `python run.py --help ` to see parameters

Dispays history `--depth` amount of matches. For each one scripts also desplays their history in compacted way. <br>
In the output `_` represents vicrory, while `X` stands for lose.

Can anyone spot some patterns? To prove/disprove the Losing Queue hypothesis? :D

