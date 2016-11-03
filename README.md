# Match-Match Game API
This is a game api based on google api engine.

##Game Description:
[Concentration](https://en.wikipedia.org/wiki/Concentration_(game)) 
is a card game in which all of the cards are laid face down on a surface and two cards
are flipped face up over each turn. The object of the game is to turn over pairs of matching cards. 
Concentration can be played with any number of players or as solitaire. 
It is a particularly good game for young children, though adults may find it challenging and stimulating as well. 
The scheme is often used in quiz shows and can be employed as an educational game.
Many different Match Match games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
## Deployed API Demo:  
https://match-match.appspot.com/_ah/api/explorer

## How to play a game:
 - Create a new user, using the `create_user` endpoint.
 - Use `create_game` to create a game. Remember to copy the `urlsafe_key` property for later use.
 - Use `get_game` and `get_game_card` (need `urlsafe_key`) to get the whole information of created game.
 - Use `make_match`(need `urlsafe_key`) to try a match, it receives two different indexes between 0 and 52.
    - Response includes info of chosen cards, matched number of game and a message indicates 
        this match succeed, fail or you win the game.
 - Repeat `make_match` until you win, or you can use `make_game_easier`(need `urlsafe_key`) 
    which receives a hint_num,
    it will automatically make same count of success match for you.
 - After finishing a game, num of attempts made will be recorded as score.
 - Other helpful endpoints:
    - `get_game_history` gives a history of guesses a player made (including hint use).
    - `get_user_active_games` gives all active games of a user.
    - `get_user_finished_games`gives all finished games of a user.
    - `get_user_scores` gives all scores of a user.
    - `get_high_scores` receives an Integer n, gives top n scores.
    - `get_user_rankings` receives an Integer n, gives top n players (based on average attempts for each game).

## Cron job:
Cron job is set to send a remainder email for users with active games on every sunday 9:00 am. 

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_nam
    - Returns: GameForm
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user. Will raise a NotFoundException if not. 
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm.
    - Description: Returns the current state of a game.

 - **cancel_game**
    - Path: 'cancel_game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: GameForm
    - Description: Cancel an unfinished game, delete game and its cards entities.
    
 - **make_match**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess_pair_1, guess_pair_2
    - Returns: MatchResultForm.
    - Description: Try the input match guess and update game state.
    Will raise a ForbiddenException when: 
        - guess num is not between 0 and 52
        - two guess nums are equal
        - guess num refers to a card already matched

 - **make_game_easier**
    - Path: 'make_game_easier/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, hint_num
    - Returns: HistoryForms
    - Description: Given a number, automatically match same count of pairs and return match histories.
    Will raise a NotFoundException if the Game does not exist.
    Will raise a ForbiddenException if the Game is already over.
    Will raise a ForbiddenException if hint_num <= 0.
    Will raise a ForbiddenException if hint_num >= unmatched pair num, which means you can't
    use hint to win a game..
        
 - **get_game_card**
    - Path: 'game_card/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: CardForms
    - Description: Return all cards of given game.
    Will raise a NotFoundException if the Game does not exist.
    Will raise a ForbiddenException if the Game is already over.
    
 - **get_game_history**
    - Path: 'game_history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: HistoryForms
    - Description: Return the guess history of given game.
    Will raise a NotFoundException if the Game does not exist.

 - **get_user_games**
    - Path: 'get_user_games/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms
    - Description: Returns game states of user's all active game (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_user_finished_games**
    - Path: 'get_user_finished_games/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms 
    - Description: Returns game states of user's all finished game (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_high_scores**
    - Path: 'high_scores/{number_of_results}'
    - Method: GET
    - Parameters: number_of_results
    - Returns: ScoreForms
    - Description: Returns top n highest scores, n = number_of_results.(attempts asc order)
    Will raise a ForbiddenException if number_of_results <= 0.    
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_user_rankings**
    - Path: 'user_rankings/{number_of_results}'
    - Method: GET
    - Parameters: number_of_results
    - Returns: UserAverageForms
    - Description: Returns top n users considering average attempts they used to finish a game,
     n = number_of_results. Will raise a ForbiddenException if number_of_results <= 0.   