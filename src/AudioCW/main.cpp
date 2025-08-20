// [[file:../../AudioCW.org::main][main]]
#include <iostream>
#include <sstream>
#include <filesystem>
#include <format>
#include <cmath>
#include <random>
#include <vector>
#include <sndfile.h>

namespace {
    // Global Constants
    constexpr double SAMPLE_RATE = 8000.0;
    constexpr double PI = 3.14159265358979323846;

    // Begin tangling supporting functions
    // [[file:AudioCW.org::fn_genWavFilename][fn_genWavFilename]]
    // Description: Generate a random filename for WAV file
    auto genWavFilename() -> std::filesystem::path {
        std::random_device rd {};
        std::mt19937 eng { rd() };
        std::uniform_int_distribution<> distr { 1000,9999 };
    
        auto randomNum { distr(eng) };
    
        auto tempDir { std::filesystem::temp_directory_path() };
        auto file { tempDir / std::format("audiocw{}.wav", randomNum) };
    
        return file;
    }
    // fn_genWavFilename ends here
    
    // [[file:AudioCW.org::fn_generateTone][fn_generateTone]]
    // Evaluates amplitudes at the specified sample rate
    auto generateTone(const auto frequency,
                      const auto duration,
                      auto &samples) {
        auto totalSamples { static_cast<size_t>(SAMPLE_RATE * duration) };
    
        for (size_t i = 0; i < totalSamples; ++i) {
            // Append amplitude at given time to samples
            samples.push_back(static_cast<float>
                              (sin(2.0 * PI * frequency * (i / SAMPLE_RATE))));
        }
    }
    // fn_generateTone ends here
    
    // [[file:AudioCW.org::fn_saveWavFile][fn_saveWavFile]]
    // Writes the audio to a file
    auto saveWavFile(const auto &filename,
                     const auto &samples) {
        SF_INFO sfinfo {};
    
        // Configure formatting for the .WAV file...
        sfinfo.frames = samples.size();
        sfinfo.samplerate = SAMPLE_RATE;
        sfinfo.channels = 1; // Mono
        sfinfo.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16; //combine format with logical or...
    
        SNDFILE *outfile { sf_open(filename.c_str(), SFM_WRITE, &sfinfo) };
        if (!outfile) {
            std::cerr << "Error opening file for writing: " << sf_strerror(nullptr) << std::endl;
            return;
        }
    
        sf_write_float(outfile, samples.data(), samples.size());
        sf_close(outfile);
    }
    // fn_saveWavFile ends here
    
    // [[file:AudioCW.org::fn_generateMorseCodeWav][fn_generateMorseCodeWav]]
    auto generateMorseCodeWav(const auto &morseVec,
                              const auto wpm,
                              const auto freq,
                              const auto filename) {
    
        // This'll be essentially the list of amplitudes for each "slice" of the wavefrorm
        auto samples { std::vector<float>() };
    
        // Timing based on international Morse code standards
        auto dotDuration { 1.2 / wpm }; // Duration of a dot per PARIS standard
        auto dashDuration { dotDuration * 3 }; // Duration of a dash
    
        // character grouping (word-wise) write to samples
        for (auto i = 0u; i < morseVec.size(); i++) {
            auto charGroup { morseVec[i] };
            // dit-dash wise write to samples...
            for (char c : charGroup) {
                if (c == '.') {
                    generateTone(freq, dotDuration, samples);  // write DOT to WAV
                    // Add space between each DOT or DASH of one DOT duration
                    auto silenceSamples { static_cast<size_t>(SAMPLE_RATE * dotDuration) };
                    samples.insert(samples.end(), silenceSamples, 0.0f);
                } else if (c == '-') {
                    generateTone(freq, dashDuration, samples); // write DASH to wav
                    // Add space between each DOT or DASH of one DOT duration
                    auto silenceSamples { static_cast<size_t>(SAMPLE_RATE * dotDuration) };
                    samples.insert(samples.end(), silenceSamples, 0.0f);
                } else if (c == ' ') {
                    /*
                      If a <SPC> is encountered, we're at a letter boundary...
                      NOTE: -1 b/c 1 <dit> already added previously.
                    */
                    auto silenceSamples { static_cast<size_t>(SAMPLE_RATE * dotDuration * 2) };
                    samples.insert(samples.end(), silenceSamples, 0.0f);
                }else { std::cerr << "generateMorseCodeWav encountered unexpected char: " << c << '\n'; }
            }
            /*
              Add space between morse char groups (words) if it's not the last word in morseVec
              NOTE: Some sort of -1 issue preventing me from implementing this as I'd like...
            */
            if (i != morseVec.size() - 1) {
                auto silenceSamples { static_cast<size_t>(SAMPLE_RATE * dotDuration * 6) };
                samples.insert(samples.end(), silenceSamples, 0.0f);
            }
        }
    
        // Padding at the beginning
        auto paddingSamples { static_cast<size_t>(SAMPLE_RATE * dashDuration) };
        samples.insert(samples.begin(), paddingSamples, 0.0f);
    
        saveWavFile(filename, samples);
    }
    // fn_generateMorseCodeWav ends here
    
    // [[file:AudioCW.org::fn_textToMorse][fn_textToMorse]]
    // Convert text gathered from STDIN into -. string format:
    auto textToMorse(const char* text) -> std::vector <std::string> {
        // First order of business is to split string into words
        std::istringstream iss(text);
        std::string word {};
        std::vector<std::string> words {};
    
        // We've now stored the collection of words in a vector
        while (iss >> word) words.push_back(word);
    
        // Set list of characters and symbols we'll be recognizing as valid morse
        const std::string morseCode[] = {
            ".-",       // A
            "-...",     // B
            "-.-.",     // C
            "-..",      // D
            ".",        // E
            "..-.",     // F
            "--.",      // G
            "....",     // H
            "..",       // I
            ".---",     // J
            "-.-",      // K
            ".-..",     // L
            "--",       // M
            "-.",       // N
            "---",      // O
            ".--.",     // P
            "--.-",     // Q
            ".-.",      // R
            "...",      // S
            "-",        // T
            "..-",      // U
            "...-",     // V
            ".--",      // W
            "-..-",     // X
            "-.--",     // Y
            "--..",     // Z
            "-----",    // 0 :26
            ".----",    // 1
            "..---",    // 2
            "...--",    // 3
            "....-",    // 4
            ".....",    // 5
            "-....",    // 6
            "--...",    // 7
            "---..",    // 8
            "----.",    // 9
            ".-.-.-",   // <PERIOD> 36
            "--..--",   // <COMMMA> 37
            "..--..",   // <QUESTION MARK> 38
            "-.-.--",   // <Exclamation MARK> 39
            "-..-.",    // <SLASH> 40
            ".-...",    // <AMPERSAND> 41
            "---...",   // <COLON> 42
            "-.-.-.",   // <SEMICOLON 43
            "..--.-",   // <UNDERSCORE> 44
            "...-..-",  // <DOLLAR SIGN> 45
            ".--.-.",   // <AT SIGN> 46
        };
    
        std::vector<std::string> morseToSend {};
        for (auto word : words) {
            // Empty string to hold our DITS and DASHES
            std::string morseWord {};
    
            // for each ch in a word, we'll append the string
            for (size_t i = 0; i < word.length(); i++) {
                auto ch { std::toupper(word[i]) };
                if (ch >= 'A' && ch <= 'Z') {
                    morseWord.append(morseCode[ch - 'A']);
                } else if (ch >= '0' && ch <= '9') {
                    morseWord.append(morseCode[ch - '0' + 26]); // Numbers start at 26
                } else {
                    switch (ch) {
                        case '.': {morseWord.append(morseCode[36]); break;}
                        case ',': {morseWord.append(morseCode[37]); break;}
                        case '?': {morseWord.append(morseCode[38]); break;}
                        case '!': {morseWord.append(morseCode[39]); break;}
                        case '/': {morseWord.append(morseCode[40]); break;}
                        case '&': {morseWord.append(morseCode[41]); break;}
                        case ':': {morseWord.append(morseCode[42]); break;}
                        case ';': {morseWord.append(morseCode[43]); break;}
                        case '_': {morseWord.append(morseCode[44]); break;}
                        case '$': {morseWord.append(morseCode[45]); break;}
                        case '@': {morseWord.append(morseCode[46]); break;}
                        default: break; // TEMP: Ignore unrecognized characters
                    }
                }
    
                /*
                  After each character converted, add a single <SPACE>
                  SKIP very last letter
                */
                if (i != word.length() - 1) { morseWord.append(" "); }
            }
            // Append morseWord to morseToSend:
            morseToSend.push_back(morseWord);
        }
    
        // Return an array of words converted to DASH-DITs.
        return morseToSend;
    }
    // fn_textToMorse ends here
    
    // End tangling supporting functions
}


int main(int argc, char** argv) {
    // Get a pseudorandom filename to store audio file to:
    const auto filename = genWavFilename();

    auto freq { 750 }; // Default frequency if not specified.
    auto wpm { 10 };

    // Print help if nothing specified or invalid syntax...
    if (argc == 1 || argc > 4) {
        std::cerr << "Usage: ./main <text> [freq] [wpm]" << '\n';
        return 1; // Exit with error if nothing is passed
    }

    // If provided text and freq:
    if (argc == 3) freq = std::atof(argv[2]);

    // If provided text, freq and wpm:
    if (argc == 4) {
        freq = std::atof(argv[2]);
        wpm = std::atoi(argv[3]);
    }

    // Send your text off to be converted to .- format vector:
    const auto morseVec { textToMorse(argv[1]) };

    generateMorseCodeWav(morseVec, wpm, freq, filename);

    std::cout << "AUDIO OUT: " << filename << std::endl;

    // Program End - Exit Successfully
    return 0;
}
// main ends here
