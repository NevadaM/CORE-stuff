# Stuff I'm working on for CORE


* Interactive notebooks for the curriculum
* Game where student chooses interest rate policy
* question + answer framework


Primarily using IPython widgets

## Inflation Game
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NevadaM/CORE-stuff/main?urlpath=voila%2Frender%2Fgame.ipynb)
* when given a shock, player has to choose monetary policy to get back to equilibrium
* currently needs aesthetic help + maybe more data for students to work with?

## Question + Answer Framework Example
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NevadaM/CORE-stuff/main?urlpath=voila%2Frender%2Fquestions.ipynb)
* this is a standard framework that can be copy and pasted into any notebook
* just change questions.csv to any csv in the same format
* I might change this from csv to maybe JSON

## Inflation Example Notebook
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NevadaM/CORE-stuff/main?urlpath=voila%2Frender%2Finflation.ipynb)
* an example of what the best interactive notebook would look like
* with latex, interactive charts, the game + questions
* and obvously videos and textbook excerpts

## Optimal Smoothing
[[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NevadaM/CORE-stuff/main?urlpath=voila%2Frender%2Fsmoothing.ipynb)
* This is a notebook that plots optimal consumption given two random shocks
* not the most educational but does the job and can be used in class as ways to test students on consumption behaviour
* doesn't work with discount rates or interest rates - I still have reservations about how interest rates work in the model, and I can't implement them in a way that outputs something that matches theory

## Smoothing game
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NevadaM/CORE-stuff/main?urlpath=voila%2Frender%2Fsmoothinggame.ipynb)
* this is another interactive game where here a student is represented with ten periods and they must smooth their consumption throughout
* initially they know their expected shocks and act accordingly
* then at some point they hit an unexpected shock and they need to reevaluate
* at the end they get to see what optimal consumer would do
* again doesn't support discount rates, interest rates
* and really needs better aesthetics / clearer data

