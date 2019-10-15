# Cartola Predictor

Just a study script to help Cartola lineup.

# How to

1. Install `Python3` if it is not already installed 
1. Install dependencies `pip3 install -r requirements.txt`
1. Add execution permission to Main file `chmod +x Main.py`
1. Create on the root folder a file `config.txt` with your cartola username and password as a follow:

```
email=yourCartola@email
password=youCartolaPassword
```	

# Run it

Just run it with `./Main.py` and you'll get the next turn score prediction of each player.

# Sample

- After follow the How to steps:

```
$ ./Main.py
Getting auth
Getting teams
Getting athletes
Getting scores
	Getting score of Fulano
	Getting score of Sicrano
	Getting score of Beltrano
	[All players will appear here]
Training using 2000 generations. It can take a long time to end
    |Population Average|    Best Individual     |
---- ------------------ ------------------------ ----------
 Gen   Length   Fitness   Length Fitness OOB Fit  Time Left
   0    12.53     24.14       13    1.37    4.83      2.07s
[All generations will appear here, it take a long time to finish]   
Getting results
```

Below the Getting results line we have a CSV of all players score prediction sorted by the best one. The columns are described below.

## COLUMNS

- Scale: Appears an * if you should scale otherwise a blank space. The rule to scale is:
	- The athlete has a `Probable` status
	- The athlete has a `Position` that still is vague in the escalation
	- The athlete has the big score projection possible
- Name: The athlete name
- Team: The athlete team
- Position: The athlete position
- Status: The athlete status
- Price: The athlete price
- Prediction: The algorithm score to the player 

# Customization

All customization need to be made in `Main.py`.

## Change escalation

In the main function of Main file change it:

```
escalation = {
    Position.GOALKEEPER: 1,
    Position.DEFENDER: 2,
    Position.SIDE: 2,
    Position.MIDFIELD: 4,
    Position.ATTACKER: 2,
    Position.COACH: 1
}
```

it is the default escalation `4:4:2`, you just need change the number of players of each escalation

## Change the number of generations

In the main function of Main file change it: `generations = 2000` to receive a number of generation that you want, for example `generations = 666`

## Change other algorithms params

All algorithms params are in the main function of Main file in the code:

```
est_gp = SymbolicRegressor(
        population_size=5000,
        generations=generations,
        stopping_criteria=0.01,
        p_crossover=0.7,
        p_subtree_mutation=0.1,
        p_hoist_mutation=0.05,
        p_point_mutation=0.1,
        max_samples=0.9,
        verbose=1,
        parsimony_coefficient=0.01,
        random_state=0,
        const_range=(-50., 50.),
        function_set=(
            'add', 'sub', 'mul', 'div', 'sqrt', 
            'log', 'abs', 'neg', 'inv', 'max', 
            'min', 'sin', 'cos', 'tan'))
```