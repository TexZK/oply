
import struct
import unittest
import wave

import oply.opl3
import oply.utils


class TestIMF(unittest.TestCase):

    def _render(self, imf_path, wav_path, rate=700):
        with open(imf_path, 'rb') as file:
            imf = oply.utils.IMF(stream=file, rate=rate)
        sequencer = oply.utils.Sequencer(imf.rate)
        imf.to_sequence(sequencer)
        opl3 = oply.opl3.Chip()

        with wave.open(wav_path, 'wb') as wave_stream:
            wave_stream.setnchannels(2)
            wave_stream.setsampwidth(2)
            wave_stream.setframerate(opl3.RATE)
            wave_stream.setnframes(0)

            for sample in opl3.render(sequencer):
                wave_stream.writeframesraw(struct.pack('<hh', *sample))

    def test_music(self):
        self._render('tests/Intermission Fuck Yeah.imf', 'tests/Intermission Fuck Yeah.wav')
