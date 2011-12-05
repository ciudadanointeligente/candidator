Feature: Create an Election
    In order to inform the comunity about the candidates
    I as a LoggedUser
    I will create a new election

    Scenario: Create a new Election and access it
        Given I as user "userone" create the election "election one" con slug "election-one"
        When I access "/user-one/election-one"
        Then I get the response code 200

    Scenario: Can not access an inexistent election
        Given I access the url "/user-one/wrong-election"
        Then I get the response code 404
