# About

This new branch is a revamp of the project, aimed at understanding the specifics of how Morse Code propagates as sound. 

**Built on Python 3.14.6**

# How CW works:

CW is transmitted via Amplitude Modulation (AM). A single constant-frequency carrier signal, dentoed $c(t)$ is mixed with a modulating signal $m(t)$. In this sense, CW is transmitted via a special form of Amplitude-shift keying, called on-off keying. That is, rather than the modulating signal being a dynamic, complex signal like a voice, it's a simple binarysignal with only two values: ${On,Off} = {0,1}$. Though in many ways this makes for a very simple signal (perhaps the simplest non-trivial signal possible), it also introduces some challenges.

## Challenge #1: Key clicks

A quick internet search on key-clicks reveals that the cause is the modulating frequency having too sharp of an edge, i.e. a nearly instantaneous rise/fall time. Mathematically, if $m(t)$ very closely resembles a square wave (unfiltered), it's discontinuous, which when mixed with the carrier, which can (randomly?) create unintentional interference several kHz in either direction. 

Here again, Audio is a great vehicle to understand this phenomenon, since most humans can hear tones from 20Hz - 20 kHz.
So, it should be an interesting experiment to attempt to create some very bad on-off-keying audio and compare with ARRL's recommended $5ms$ rise/fall interval. A fourier transform should reveal the offending frequencies. :)

## Challenge #2: Synthetic Data Augmentation

Somehow, my perfect synthetic data needs to be modified to have some variance in it.

- Human timing variance
    > "Introduce normal distribuitions of variances to the dits, dashes, and spacing"

- Pitch drift
    > "Transmitters are seldom perfectly stable."

- Atmospheric noise

- Interference
    > Superimpose a second, weaker CW signal at a slightly different CW frequency (100Hz offset)

- Fading
    > Apply Rayleigh fading to the signal amplitude to simulate ionospheric propagation changes.

# Model Specifications

The recommended model setup (per Gemini) is to use PyTorch and torchaudio. The neural net should be a CNN (Convolutional Neural Net) paried with CTC (Connectionist Temporal Classification) loss function.