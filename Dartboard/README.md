# Dartboard Project

<p align="middle">
  <img src="/Dartboard/dartboard.svg" width="400"/>
</p>

If you've played some darts, you'll know that the highest-scoring region on a dartboard isn't actually the bullseye. The inner bullseye scores fifty points, while the triple-twenty scores sixty. So why not just aim for the triple-twenty instead? Well, it's riskier: if you miss the inner bullseye, you might hit the 25-point outer bullseye, but if you miss the triple-twenty, you might hit the five or the one, both very low scoring. 

This line of reasoning led me to hypothesize that a perfectly accurate player will aim for the triple-twenty, but there is some threshold of accuracy after which less accurate players should aim for the bullseye. (At the opposite extreme, a player with accuracy aproaching zero should aim for the bullseye, since it's at the center of the board, and maximizes the chances of hitting anything.)

I wanted to make this rigorous. I also had further questions: at that accuracy threshold, is it a discontinuous jump from the optimal target being the triple-twenty to the bullseye, or does that point move continuously? And what *is* that threshold?

## Methodology

<img align="right" width="600" src="/Dartboard/output/overlaid_images/015.png">

To get some answers and to explore the problem in more depth, I simulated over a billion throws at a dartboard. I modelled a throw as a sample of a symmetric bivariate normal distribution. By varying the normal distribution's standard deviation, I was able to approximate players with different accuracies. The scale of the units for the throw standard deviation are not really all that meaningful; it's just a useful metric in a relative sense. For some perspective, though, an amateur player might be around 0.4 - 0.5, a pro could be as low as 0.025, and a standard deviation of 1.0 misses the whole board around 60% of the time (when aiming at the center).

To the right you can see one of the output images I've created to visually represent my findings. Each point on the dartboard is colored to represent the score a player (with throw standard deviation 0.15, in this case) could expect, if they were aiming at that point. Particularly interesting for the case of σ = 0.15 is that the optimal target is neither the triple-twenty nor the bullseye, but the bottom-left side of the board, around the triple-19, which at least partially disproves my hypothesis.

High-res (3000x3000) images for various standard deviation values are in [`output/overlaid_images`](/Dartboard/output/overlaid_images) and [`output/raw_images`](/Dartboard/output/raw_images), for images with and without the dartboard outline, respectively. The filenames for each image are 100 times the standard deviation for that image, i.e. the example above is [`015.png`](/Dartboard/output/overlaid_images/015.png). As a final note about the visualizations: the colormap is normalized for each, so a particular color might represent different expected scores for two different images. This is to make visual patterns more distinct.
