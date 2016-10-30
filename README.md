#Full Stack Nanodegree Project 4 Refresh

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
[Concentration](https://en.wikipedia.org/wiki/Concentration_(game)) 
is a card game in which all of the cards are laid face down on a surface and two cards
are flipped face up over each turn. The object of the game is to turn over pairs of matching cards. 
Concentration can be played with any number of players or as solitaire. 
It is a particularly good game for young children, though adults may find it challenging and stimulating as well. 
The scheme is often used in quiz shows and can be employed as an educational game.
Many different Guess a Number games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
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
    - Parameters: user_name, min, max, attempts
    - Returns: GameForm.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Min must be less than
    max. Also adds a task to a task queue to update the average moves remaining
    for active games.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm.
    - Description: Returns the current state of a game.

 - **cancel_game**
    - Path: 'cancel_game/{urlsafe_game_key}'
    - Method: POST
    - Parameters: urlsafe_game_key
    - Returns: GameForm.
    - Description: Cancel an unfinished game, delete game and its cards entities.
    
 - **make_match**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess_pair_1, guess_pair_2
    - Returns: MatchResultForm.
    - Description: Try the input match guess and update game state.
    Will raise a BadRequestException when: 
        - guess num is not between 0 and 52
        - two guess nums are equal
        - guess num refers to a card already matched

 - **get_game_history**
    - Path: 'game_history/{urlsafe_game_key}'
    - Method: POST
    - Parameters: urlsafe_game_key
    - Returns: HistoryForms.
    - Description: Return the guess history of given game.
    Will raise a NotFoundException if the Game does not exist.

 - **get_user_games**
    - Path: 'get_user_games/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms. 
    - Description: Returns game states of user's all active game (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_user_finished_games**
    - Path: 'get_user_finished_games/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms. 
    - Description: Returns game states of user's all finished game (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_high_scores**
    - Path: 'high_scores/{number_of_results}'
    - Method: GET
    - Parameters: number_of_results
    - Returns: ScoreForms.
    - Description: Returns top n highest scores, n = number_of_results.(attempts asc order)
    Will raise a BadRequestException if number_of_results <= 0.    
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_user_rankings**
    - Path: 'user_rankings/{number_of_results}'
    - Method: GET
    - Parameters: number_of_results
    - Returns: UserAverageForms.
    - Description: Returns top n users considering average attempts they used to finish a game,
     n = number_of_results. Will raise a BadRequestException if number_of_results <= 0.   

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Card**
    - Records cards of an active game. Associated with Game model via KeyProperty.
     
 - **History**
    - Records history of guesses in a game. Associated with Game model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
 
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **GameForm**
    - Multiple GameForm container.
 - **UserNameForm**
    - Used to create a new game (user_name)
 - **MakeMatchForm**
    - Used to make a match guess in a game (guess_pair_1, guess_pair_2)
 - **MatchResultForm**
    - Representation of a match guess 
    (matched_card_value_1, matched_card_value_2,
    matched_card_suit_1, matched_card_suit_2,
    matched_count, matched_count)
 - **HistoryForms**
    - Multiple MatchResultForm container
 - **UserAverageForm**
    - Representation of a user's average attempts count.
 - **UserAverageForms**
    - Multiple UserAverageForm container
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.