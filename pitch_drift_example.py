import numpy as np
from scipy.io import wavfile

# Existing functions from methods.py (for reference)
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

# New function for pitch drift
def _pitch_drift_carrier(x, base_frequency=700, max_drift=2.0, sample_rate=8000):
    """
    Generate a carrier wave with simple pitch drift.

    Args:
        x: time values
        base_frequency: nominal carrier frequency (Hz)
        max_drift: maximum frequency deviation (Hz)
        sample_rate: audio sampling rate

    Returns:
        Array of carrier wave values with varying frequency
    """
    # Simple random walk drift - add small random changes to frequency over time
    dt = 1.0 / sample_rate
    drift_changes = np.random.normal(0, max_drift/50, len(x))  # Small changes per sample
    cumulative_drift = np.cumsum(drift_changes) * dt

    # Apply drift to base frequency
    instantaneous_freq = base_frequency + cumulative_drift

    return np.sin(2 * np.pi * instantaneous_freq * x)

# Example usage:
def generate_cw_with_drift(text, wpm=10, sample_rate=8000, max_drift=2.0):
    """
    Generate CW audio with pitch drift.

    Args:
        text: text to encode
        wpm: words per minute
        sample_rate: audio sampling rate
        max_drift: maximum pitch drift in Hz

    Returns:
        Audio signal with drift applied
    """
    # This would integrate with your existing CW generation functions
    # For now, showing the concept

    # Create time array
    t_values = np.arange(0, 5, 1/sample_rate)  # 5 seconds of audio

    # Generate pitch-drift carrier
    drift_carrier = _pitch_drift_carrier(t_values, base_frequency=700,
                                       max_drift=max_drift, sample_rate=sample_rate)

    # For demonstration - combine with simple tone
    # In real implementation, this would integrate with your existing OOK generation
    simple_tone = np.sin(2 * np.pi * 700 * t_values)  # Basic 700Hz tone

    # Apply drift to the carrier
    drifted_signal = drift_carrier * simple_tone

    return drifted_signal

# Simple test
if __name__ == "__main__":
    # Generate a short sample with pitch drift
    signal = generate_cw_with_drift("PARIS", max_drift=1.0)

    # Convert to int16 for wav file
    audio_int16 = (signal * 32767).astype(np.int16)
    wavfile.write("test_pitch_drift.wav", 8000, audio_int16)

    print("Generated test_pitch_drift.wav with pitch drift")