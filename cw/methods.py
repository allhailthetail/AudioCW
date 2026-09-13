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

def _carrier_wave(x, frequency = 700, amplitude = 1, phase = 0, offset = 0, apply_pitch_drift=False, max_drift=2.0):
    """
    Generates a sine carrier wave at a particular amplitude and frequency, phase, offset.

    Args:
        x: time values
        frequency: carrier frequency (Hz)
        amplitude: wave amplitude
        phase: wave phase
        offset: wave offset
        apply_pitch_drift: whether to apply pitch drift
        max_drift: maximum frequency deviation for drift (Hz)
    """
    if apply_pitch_drift:
        # Generate time-varying frequency
        sample_rate = 1.0 / (x[1] - x[0]) if len(x) > 1 else 8000
        dt = 1.0 / sample_rate
        drift_changes = np.random.normal(0, max_drift/50, len(x))
        cumulative_drift = np.cumsum(drift_changes) * dt
        instantaneous_freq = frequency + cumulative_drift
        return (amplitude * np.sin(2 * np.pi * instantaneous_freq * x + phase) + offset)
    else:
        return (amplitude * np.sin(2 * np.pi * frequency * x + phase) + offset)


def _add_atmospheric_noise(signal, noise_level=0.01):
    """
    Add atmospheric noise to the signal.

    Args:
        signal: input audio signal
        noise_level: amplitude of noise (0.0 to 1.0)

    Returns:
        Signal with atmospheric noise added
    """
    noise = np.random.normal(0, noise_level, len(signal))
    return signal + noise


def _apply_rayleigh_fading(signal, fading_factor=0.5):
    """
    Apply Rayleigh fading to simulate ionospheric propagation changes.

    Args:
        signal: input audio signal
        fading_factor: controls the severity of fading (0.0 to 1.0)

    Returns:
        Signal with Rayleigh fading applied
    """
    # Generate Rayleigh distributed envelope
    # Using the fact that Rayleigh distribution can be generated from two normal random variables
    num_samples = len(signal)
    envelope = np.random.rayleigh(fading_factor, num_samples)

    # Apply the envelope to the signal
    return signal * envelope

def _mix_m_t(m_t, frequency = 700, sample_rate = 8000, drift = 0):
    """
    Mixes the carrier wave with the signal wave.
    """
    t_values = np.arange(len(m_t)) / sample_rate
    
    if drift == 0:
        c_t = _carrier_wave(t_values)
        return c_t * m_t
    else:
        c_t = _carrier_wave(t_values, apply_pitch_drift=True, max_drift=drift)
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

def _ook_sr_convert(key_sequence, wpm=10, sample_rate=8000, apply_timing_jitter=False, jitter_std=0.05):
    """
    Up-converts a list of binary on-off key signals to a particular sample rate.
    
    Args:
        key_sequence: List of binary values (0s and 1s)
        wpm: Words per minute
        sample_rate: Audio sampling rate
        apply_timing_jitter: Whether to apply human-like timing variations
        jitter_std: Standard deviation for timing jitter (default 5%)
    """
    tau = 1.2 / wpm
    samples_per_tau = tau * sample_rate          # keep as float, don't round yet

    # boundary[i] = sample index where unit i begins, computed from absolute
    # elapsed time (i * samples_per_tau), not by repeatedly stepping by a
    # truncated per-unit count
    if apply_timing_jitter:
        # Apply human-like timing variations
        boundaries = []
        for i in range(len(key_sequence) + 1):
            base_boundary = i * samples_per_tau
            # Add normal distribution jitter (±jitter_std of base tau)
            jitter = np.random.normal(0, jitter_std * samples_per_tau)
            jittered_boundary = base_boundary + jitter
            boundaries.append(jittered_boundary)
        boundaries = np.round(boundaries).astype(int)
    else:
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