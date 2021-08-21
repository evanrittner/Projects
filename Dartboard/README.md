# Dartboard Project

<p align="middle">
  <img src="/Dartboard/dartboard.svg" width="400"/>
</p>

If you've played some darts, you'll know that the highest-scoring region on a dartboard isn't actually the bullseye. The inner bullseye scores fifty points, while the triple-twenty scores 60. So why not just aim for the triple-twenty instead? Well, it's riskier: if you miss the inner bullseye, you might hit the 25-point outer bullseye, but if you miss the triple-twenty, you might hit the five or the one, both very low scoring. 

This line of reasoning led me to hypothesize that a perfectly accurate player will aim for the triple-twenty, but there is some threshold of accuracy after which less accurate players should aim for the bullseye.

I wanted to make this rigorous. I also had further questions: at that accuracy threshold, is it a discontinuous jump from the optimal target being the triple-twenty to the bullseye, or does that point move continuously? And what *is* that threshold?


## Results

The optimal target on the board in darts varies as follows: For players with very high accuracy, the optimal target is the center of the triple-twenty. As accuracy decreases, the optimal target jumps discontinuously to the triple-19. As it decreases further, approaching no accuracy at all, the optimal target moves towards the center of the board, spiralling slightly clockwise to stay near the triple ring, eventually ending at the bullseye.

The threshold of accuracy at which the discontinuous jump occurs is difficult to quantify, as I'll explain in the next paragraph, but if you can hit either the inner or outer bullseye at least 1/3 of the time, you are accurate enough.


## Methodology

<img align="right" width="600" src="/Dartboard/output/overlaid_images/015.png">

To get some answers and to explore the problem in more depth, I simulated over a billion throws at a dartboard. I modelled a throw as a sample of a symmetric bivariate normal distribution. By varying the normal distribution's standard deviation, I was able to approximate players with different accuracies. The scale of the units for the throw standard deviation are not really all that meaningful; it's just a useful metric in a relative sense. For some perspective, though, an amateur player might be around 0.4 - 0.5, a pro could be as low as 0.025, and a standard deviation of 1.0 misses the whole board around 60% of the time (when aiming at the center). (To get an idea of your standard deviation, see [`determine_my_sigma.md`](/Dartboard/determine_my_sigma.md).)

To the right you can see one of the output images I've created to visually represent my findings. Each point on the dartboard is colored to represent the score a player (with throw standard deviation 0.15, in this case) could expect, if they were aiming at that point. Particularly interesting for the case of σ = 0.15 is that the optimal target is neither the triple-twenty nor the bullseye, but the bottom-left side of the board, around the triple-19, which at least partially disproves my hypothesis.

Another finding of interest: when following the optimal strategy, the expected score decreases roughly linearly with the throw standard deviation, though in two phases. As can be seen in the plot below, when the standard deviation is less than about 0.1, the score decreases sharply with an increase in standard deviation, and greater than 0.1, the decrease in score is more gradual.

High-res (3000x3000) images for various standard deviation values are in [`output/overlaid_images`](/Dartboard/output/overlaid_images) and [`output/raw_images`](/Dartboard/output/raw_images), for images with and without the dartboard outline, respectively. There are also plots with contour lines, to make the topography more clear, in [`output/contour_images`](/Dartboard/output/contour_images). The filenames for each image are 100 times the standard deviation for that image, i.e. the example above is [`015.png`](/Dartboard/output/overlaid_images/015.png). As a final note about the visualizations: the colormap is normalized for each, so a particular color might represent different expected scores for two different images. Also, the contours are not at equal spacings across images. These decisions were made to make visual patterns more distinct.

<p align="middle">
  <img src="/Dartboard/optimal_score_plot.png" width="800"/>
</p>


## Code

#### [`gen_array.c`](/Dartboard/gen_array.c)
This is the main number-crunching program. Based on arguments passed, it generated a Python Numpy .npy file holding the expected score of each point on a darboard, given the throw standard deviation. For each point in the output array, it randomly generates throws aimed at that point, following a bivariate normal distribution.

#### [`image_from_npy.py`](/Dartboard/image_from_npy.py)
This is a simple Python script to apply the "Magma" colormap and render the generated data as an image.

#### [`contours.py`](/Dartboard/contours.py)
Another script to convert the data to images, this time applying the contours.

#### [`determine_sigma.c`](/Dartboard/determine_sigma.c)
A modification to `gen_array.c` to calculate the data in [`determine_my_sigma.md`](/Dartboard/determine_my_sigma.md)

#### [`multiprocess.py`](/Dartboard/multiprocess.py)
A short script to keep `gen_array` processes running continuously on the Raspberry Pi I left overnight to do the computations.

#### [`draw_dartboard.py`](/Dartboard/draw_dartboard.py) and [`draw_dartboard_outline.py`](/Dartboard/draw_dartboard.py)
Two scripts to generate the dartboard vector graphics for use in this README and as the overlays for output images, respectively, using Pycairo.


## Gallery

Below are the three ways I generated images, for the data corresponding to σ = 0.1: with contours, with a dartboard overlay, and without anything extra.

<p align="middle">
  <img src="/Dartboard/output/contour_images/010.png" width="1000"/>
</p>

<p align="middle">
  <img src="/Dartboard/output/overlaid_images/010.png" width="1000"/>
</p>

<p align="middle">
  <img src="/Dartboard/output/raw_images/010.png" width="1000"/>
</p>
