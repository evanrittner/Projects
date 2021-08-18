# Dartboard Project

<p align="middle">
  <img src="/Dartboard/dartboard.svg" width="400"/>
</p>

If you've played some darts, you'll know that the highest-scoring region on a dartboard isn't actually the bullseye. The inner bullseye scores fifty points, while the triple-twenty scores sixty. So why not just aim for the triple-twenty instead? Well, it's riskier: if you miss the inner bullseye, you might hit the 25-point outer bullseye, but if you miss the triple-twenty, you might hit the five or the one, both very low scoring. 

This line of reasoning led me to hypothesize that a perfectly accurate player will aim for the triple-twenty, but there is some threshold of accuracy after which less accurate players should aim for the bullseye. (At the opposite extreme, a player with accuracy aproaching zero should aim for the bullseye, since it's at the center of the board, and maximizes the chances of hitting anything.)

I wanted to make this rigorous. I also had further questions: at that accuracy threshold, is it a discontinuous jump from the optimal target being the triple-twenty to the bullseye, or does that point move continuously? And what *is* that threshold?

## Results
