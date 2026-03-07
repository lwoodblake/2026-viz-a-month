# 2026-viz-a-month

Between work, home life, and rest it's easy to blink and realise you haven't done any data related projects for fun in 7 months! I work with data every day, but the projects you create in your spare time are a valuable space for exploration, refinement, and tackling new problems.

To make sure I keep playing with data I set myself the pretty humble challenge of scoping out and finishing one data visualisation per month for 2026. I'll write up my experiences here, including any particular challenges or considerations that shaped my work.

## January
### NFL Win % 2024 -> 2025
I have followed the NFL casually for 4 seasons and I thought I had a pretty solid grasp of which teams were considered "strong" teams. Turns out the prevelance of injuries and the draft system ensures that the NFL remains more competititve than association football, where stronger teams attract the best players on the transfer market. The two teams that made it to the Super Bowl are teams I would have considered "weak" based on previous seasons, while previously dominant teams like the Kansas City Chiefs failed to make the play offs altogether. 

I wanted to visualise the change between the 2024 and 2025 seasons to see an overview of these changing fortunes. I typically work with event level data, but thought it would be interesting to fully think through how to effectively visualise just two data points, a metric to capture performance in 2024 and performance in 2025. Because the NFL is split into conferences and divisions I liked the idea of visualising each division as a mini multiple. I chose to use parallel coordinate charts as I only intended to visualise two data points for each team, one for 2024 and one for 2025. The parallel lines are a visual indication of whether performance has improved or declined.

My initial thought was to use team rank within their division to avoid data points overlapping, but quickly found that this gave a false impression of how performance had changed for a team. There were some teams that were ranked the same or even lower in their division, but who had reached the play offs in 2025 and had won far more often. I settled on win% as an overall measure of performance. I also chose to only include regular season games as I didn't want play off games to bring down the win rate of strong teams. This also ensured the teams had played the same number of games, making it a fairer comparison.

Visualising win% means that my visualisation also highlights some of the differences between divisions. For example, no team in the NFC South achieved a win% above 50% this season, while the NFC West was much stronger, with 3 teams all at or above around 75%.

I used team badges because these are relatively clear even with the overlapping data points and because they saved space, while I highlighted the most improved teams and the ones that dropped off the most so they could quickly be identified.

![january viz](https://github.com/lwoodblake/2026-viz-a-month/blob/main/january/nfl-change.png?raw=true)

## February
### One Twos
Because February is a shorter month I treated myself to working with a dataset I am already familiar with, but managed to run out of time anyway! 

I always liked that FIFA videogame concept of "chemistry" but the in game definition was fundamentally boring (players that play for the same nation or club get a positive chemistry score). This got me thinking about how we could define chemistry by what actually happens on the pitch. The concept of a one-two feels like a good proxy for chemistry, as it requires coordination and anticipation between the two players involved. A one-two would be a pass from player A → B → A. I read [this article from Soccerment](https://soccerment.com/one-twos-a-new-metric-for-associative-ball-progression-and-chance-creation/) where they define one-twos in event data and wanted to explore this myself.

The restrictions I applied when identifying one-twos were pretty much the same as those Soccerment applied, so I take no credit here.

* A chain of completed passes from A → B → A
* Completed within at least x nummber of seconds
* Excluding chains where player B carried the ball for more than x pseudo-yards before passing the ball back to player A
* Including only chains where the ball progressed towards the goal by at least x pseudo-yards

This work didn't exactly set the world on fire. Like I said, others have already defined this concept in almost identical terms. I did, however, find the process of writing python code to capture only these situations useful and I spent a long time tweaking my code to accurately capture these combinations. Writing the code to visualise these one-twos required a few details. I decided to:

* Colour code the first pass and the second pass, with ball receipts as circular points. I feel this creates a clear visual language where we can see player A's pass and then their subsequent receipt of the return pass all in red.
* Include a grey dotted line indicating player A's off ball movement to receive the return pass. This was drawn by creating a line from the start location of the first pass to the end location of the second pass. 
* Arrows in the middle of each pass to indicate direction, allowing the reader to follow the trajectory of the pass and quickly identify which pass came first.

The challenge to defining one-twos with event data is that a lot of A → B → A passing combinations are uninteresting moments. Picture two centre backs passing the ball between themselves on the edge of their own box. Soccerment took the approach of restricting their one-two definition to only situations where the one-two progressed the ball. In terms of my next steps, I would love to use the 360 contextual data we have in the Statsbomb dataset to identify situations where the one-two bypassed a defender. We could them consider the one-two to be a sort of line-breaking pass broken in half and performed in two passes instead of one.

![february viz](https://github.com/lwoodblake/2026-viz-a-month/blob/main/february/one-two-example.png?raw=true)