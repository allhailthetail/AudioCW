import numpy as np
from scipy.io import wavfile

# CW Alphabet, currently alphanumeric only.
alphabet = {
    "a": "10111",
    "b": "111010101",
    "c": "11101011101",
    "d": "1110101",
    "e": "1",
    "f": "101011101",
    "g": "111011101",
    "h": "1010101",
    "i": "101",
    "j": "1011101110111",
    "k": "111010111",
    "l": "101110101",
    "m": "1110111",
    "n": "11101",
    "o": "11101110111",
    "p": "10111011101",
    "q": "1110111010111",
    "r": "1011101",
    "s": "10101",
    "t": "111",
    "u": "1010111",
    "v": "101010111",
    "w": "101110111",
    "x": "11101010111",
    "y": "1110101110111",
    "z": "11101110101",
    "0": "1110111011101110111",
    "1": "10111011101110111",
    "2": "101011101110111",
    "3": "1010101110111",
    "4": "10101010111",
    "5": "101010101",
    "6": "11101010101",
    "7": "1110111010101",
    "8": "111011101110101",
    "9": "11101110111011101"
}

def _carrier_wave(x, frequency = 700, amplitude = 1, phase = 0, offset = 0):
    """
    Generates a sine carrier wave at a particular amplitude and frequency, phase, offset.
    """
    return (amplitude * np.sin(2 * np.pi * frequency * x + phase) + offset)

def _mix_m_t(m_t, frequency = 700, sample_rate = 8000):
    """
    Mixes the carrier wave with the signal wave.
    """
    t_values = np.arange(len(m_t)) / sample_rate
    c_t = _carrier_wave(t_values)
    return c_t * m_t

def _word_to_ook_tau(word):
    """
    Converts input word/phrase into valid CW code of 0's and 1's. 
    Output is list of single-digit binary values.
    """
    cw_code = [0]
    for letter in word.lower():
        mapping = alphabet.get(letter)
        cw_code += list(mapping)
        cw_code += list("000")       # Don't forget the intra-word spacing!
        
    cw_code += list("000")    # nor the inter-word spacing (3 from last letter)!

    return [int(x) for x in cw_code]

def _ook_sr_convert(key_sequence, wpm=10, sample_rate=8000):
    """
    Up-converts a list of binary on-off key signals to a particular sample rate.
    """
    tau = 1.2 / wpm
    samples_per_tau = tau * sample_rate          # keep as float, don't round yet

    # boundary[i] = sample index where unit i begins, computed from absolute
    # elapsed time (i * samples_per_tau), not by repeatedly stepping by a
    # truncated per-unit count
    boundaries = np.round(np.arange(len(key_sequence) + 1) * samples_per_tau).astype(int)

    converted = np.zeros(boundaries[-1], dtype=int)
    for i, level in enumerate(key_sequence):
        converted[boundaries[i]:boundaries[i + 1]] = level

    return converted.tolist()

def _one_pole_lowpass(signal, carrier_frequency, sample_rate):
    """A one-pole IIR low-pass filter: y[n] = alpha*x[n] + (1-alpha)*y[n-1].

    Each output sample is a weighted blend of the current input and the
    *previous output* -- so a sudden jump in the input only shows up
    gradually in the output, over several samples, instead of instantly.
    """

    fc = 1.5 * carrier_frequency
    RC = 1 / (2 * np.pi * fc)
    dt = 1 / sample_rate
    alpha = dt / (RC + dt)

    y = np.zeros_like(signal, dtype=float)
    y[0] = signal[0]
    for n in range(1, len(signal)):
        y[n] = alpha * signal[n] + (1 - alpha) * y[n - 1]
    
    return y

def _save_wav(signal, path, sample_rate = 8000):
    audio_int16 = (signal * 32767).astype(np.int16)
    wavfile.write(f"{path}", sample_rate, audio_int16)