#Put your AI file in folder ./ai

##Comunication Protocol:

All the communications are by stdin and stdout.

Every packet from the game to the ai are in the following form:

<HEADER>|<SUBHEADER>|<DATA>

<HEADER> could be either INFO or CMD. INFO requires no response from the AI
client, whereas CMD requires a single line of respose from stdout from the AI
client.

<SUBHEADER> is the type of the request. It defines what kind of message the 
game is sending.

<DATA> is the corresponding data for <SUBHEADER>, which will be explained below.

## Message explanation 

INFO|NEWGAME|<DATA>:

Send the signal that a new game is generated. <DATA> is a list of cards that you
will start with. This packet is **private** to the players.

_example:INFO|NEWGAME|[1,2,3,4,5,6,7,8,9,10]_

INFO|GAME|<DATA>:

Send the info of the game data. This packet will be sent before every new round.
 <DATA> is a dictionary where there are 2 keys:

 * "rows": a list of four lists, representing four rows of the current game
 * "players": a dictionary of all the players, in which the key is the name of 
   the player and the value is their score

_example:INFO|GAME|{"row":[[1],[2],[3],[4]],"players":{"p1":0, "p2":1}}_

INFO|MOVE|<DATA>:

Send the info of a move of the round of all players. <DATA> is a dictionary 
where the keys are the players' names and the corresponding value is the cards
they play.

_example: INFO|MOVE|{"p1":1, "p2":2}_

INFO|SCORE|<DATA>:

Send the info of the score the player gets. This packet happens after a player
puts the sixth card of a row, or a player puts the smallest card and picks
a row from the game. <DATA> is a dictionary where there are 3 keys:

 * "player": the player that gets the score
 * "cards": a list of cards the player gets
 * "score": the total score the player gets

_example:INFO|SCORE|{"player":"p1", "cards":[1,2], "score":2}_

CMD|PICKCARD:

Request the player to pick a card from their hand. They response should be a
number in stdout with '\n' in the end. 

CMD|PICKROW:

Request the player to pick a row of the current game. This only happens if a 
player plays the smallest card among all players and the card is smaller than
the smallest card of all the end card in rows. The response should be 0-3 with
'\n' in the end.
