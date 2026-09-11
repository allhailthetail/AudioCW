from cw.methods import _one_pole_lowpass
from cw.methods import _mix_m_t, _ook_sr_convert, _save_wav, _word_to_ook_tau

def generate_audio(message, wpm = 10, frequency=700, sample_rate = 8000, filtering = "1p_lpf"):
    raw_ook_sn = _word_to_ook_tau(message)
    m_t = _ook_sr_convert(raw_ook_sn, wpm = wpm, sample_rate = sample_rate)
    ct_mt = _mix_m_t(m_t, frequency = frequency, sample_rate = sample_rate)
    
    if filtering == "1p_lpf":
        return _one_pole_lowpass(ct_mt, carrier_frequency = frequency, sample_rate = sample_rate)
    else:
        return ct_mt

def write_wav(signal, sample_rate = 8000, path = "output.wav"):
    _save_wav(signal = signal, sample_rate = sample_rate, path = path)
