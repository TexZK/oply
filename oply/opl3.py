# Copyright (C) 2013-2016 Alexey Khokholov (Nuke.YKT)
# Python port by Andrea Zoppi (TexZK)
#
# This program is free software; you can redistribute it and//or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
#
#  Nuked OPL3 emulator.
#  Thanks:
#      MAME Development Team(Jarek Burczynski, Tatsuyuki Satoh):
#          Feedback and Rhythm part calculation information.
#      forums.submarine.org.uk(carbon14, opl3):
#          Tremolo and phase generator calculation information.
#      OPLx decapsulated(Matthew Gambrell, Olli Niemitalo):
#          OPL2 ROMs.
#
# version: 1.7.4
#


class Noise(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.output = 0x306600

    def next(self):
        value = self.output
        value = (((value & 1) * 0x800302) ^ value) >> 1
        self.output = value
        return value

    __next__ = next

    def __iter__(self):
        return self


class Envelope(object):

    EXP = (
        0x000, 0x003, 0x006, 0x008, 0x00B, 0x00E, 0x011, 0x014,
        0x016, 0x019, 0x01C, 0x01F, 0x022, 0x025, 0x028, 0x02A,
        0x02D, 0x030, 0x033, 0x036, 0x039, 0x03C, 0x03F, 0x042,
        0x045, 0x048, 0x04B, 0x04E, 0x051, 0x054, 0x057, 0x05A,
        0x05D, 0x060, 0x063, 0x066, 0x069, 0x06C, 0x06F, 0x072,
        0x075, 0x078, 0x07B, 0x07E, 0x082, 0x085, 0x088, 0x08B,
        0x08E, 0x091, 0x094, 0x098, 0x09B, 0x09E, 0x0A1, 0x0A4,
        0x0A8, 0x0AB, 0x0AE, 0x0B1, 0x0B5, 0x0B8, 0x0BB, 0x0BE,
        0x0C2, 0x0C5, 0x0C8, 0x0CC, 0x0CF, 0x0D2, 0x0D6, 0x0D9,
        0x0DC, 0x0E0, 0x0E3, 0x0E7, 0x0EA, 0x0ED, 0x0F1, 0x0F4,
        0x0F8, 0x0FB, 0x0FF, 0x102, 0x106, 0x109, 0x10C, 0x110,
        0x114, 0x117, 0x11B, 0x11E, 0x122, 0x125, 0x129, 0x12C,
        0x130, 0x134, 0x137, 0x13B, 0x13E, 0x142, 0x146, 0x149,
        0x14D, 0x151, 0x154, 0x158, 0x15C, 0x160, 0x163, 0x167,
        0x16B, 0x16F, 0x172, 0x176, 0x17A, 0x17E, 0x181, 0x185,
        0x189, 0x18D, 0x191, 0x195, 0x199, 0x19C, 0x1A0, 0x1A4,
        0x1A8, 0x1AC, 0x1B0, 0x1B4, 0x1B8, 0x1BC, 0x1C0, 0x1C4,
        0x1C8, 0x1CC, 0x1D0, 0x1D4, 0x1D8, 0x1DC, 0x1E0, 0x1E4,
        0x1E8, 0x1EC, 0x1F0, 0x1F5, 0x1F9, 0x1FD, 0x201, 0x205,
        0x209, 0x20E, 0x212, 0x216, 0x21A, 0x21E, 0x223, 0x227,
        0x22B, 0x230, 0x234, 0x238, 0x23C, 0x241, 0x245, 0x249,
        0x24E, 0x252, 0x257, 0x25B, 0x25F, 0x264, 0x268, 0x26D,
        0x271, 0x276, 0x27A, 0x27F, 0x283, 0x288, 0x28C, 0x291,
        0x295, 0x29A, 0x29E, 0x2A3, 0x2A8, 0x2AC, 0x2B1, 0x2B5,
        0x2BA, 0x2BF, 0x2C4, 0x2C8, 0x2CD, 0x2D2, 0x2D6, 0x2DB,
        0x2E0, 0x2E5, 0x2E9, 0x2EE, 0x2F3, 0x2F8, 0x2FD, 0x302,
        0x306, 0x30B, 0x310, 0x315, 0x31A, 0x31F, 0x324, 0x329,
        0x32E, 0x333, 0x338, 0x33D, 0x342, 0x347, 0x34C, 0x351,
        0x356, 0x35B, 0x360, 0x365, 0x36A, 0x370, 0x375, 0x37A,
        0x37F, 0x384, 0x38A, 0x38F, 0x394, 0x399, 0x39F, 0x3A4,
        0x3A9, 0x3AE, 0x3B4, 0x3B9, 0x3BF, 0x3C4, 0x3C9, 0x3CF,
        0x3D4, 0x3DA, 0x3DF, 0x3E4, 0x3EA, 0x3EF, 0x3F5, 0x3FA
    )

    LOG = (
        0x859, 0x6C3, 0x607, 0x58B, 0x52E, 0x4E4, 0x4A6, 0x471,
        0x443, 0x41A, 0x3F5, 0x3D3, 0x3B5, 0x398, 0x37E, 0x365,
        0x34E, 0x339, 0x324, 0x311, 0x2FF, 0x2ED, 0x2DC, 0x2CD,
        0x2BD, 0x2AF, 0x2A0, 0x293, 0x286, 0x279, 0x26D, 0x261,
        0x256, 0x24B, 0x240, 0x236, 0x22C, 0x222, 0x218, 0x20F,
        0x206, 0x1FD, 0x1F5, 0x1EC, 0x1E4, 0x1DC, 0x1D4, 0x1CD,
        0x1C5, 0x1BE, 0x1B7, 0x1B0, 0x1A9, 0x1A2, 0x19B, 0x195,
        0x18F, 0x188, 0x182, 0x17C, 0x177, 0x171, 0x16B, 0x166,
        0x160, 0x15B, 0x155, 0x150, 0x14B, 0x146, 0x141, 0x13C,
        0x137, 0x133, 0x12E, 0x129, 0x125, 0x121, 0x11C, 0x118,
        0x114, 0x10F, 0x10B, 0x107, 0x103, 0x0FF, 0x0FB, 0x0F8,
        0x0F4, 0x0F0, 0x0EC, 0x0E9, 0x0E5, 0x0E2, 0x0DE, 0x0DB,
        0x0D7, 0x0D4, 0x0D1, 0x0CD, 0x0CA, 0x0C7, 0x0C4, 0x0C1,
        0x0BE, 0x0BB, 0x0B8, 0x0B5, 0x0B2, 0x0AF, 0x0AC, 0x0A9,
        0x0A7, 0x0A4, 0x0A1, 0x09F, 0x09C, 0x099, 0x097, 0x094,
        0x092, 0x08F, 0x08D, 0x08A, 0x088, 0x086, 0x083, 0x081,
        0x07F, 0x07D, 0x07A, 0x078, 0x076, 0x074, 0x072, 0x070,
        0x06E, 0x06C, 0x06A, 0x068, 0x066, 0x064, 0x062, 0x060,
        0x05E, 0x05C, 0x05B, 0x059, 0x057, 0x055, 0x053, 0x052,
        0x050, 0x04E, 0x04D, 0x04B, 0x04A, 0x048, 0x046, 0x045,
        0x043, 0x042, 0x040, 0x03F, 0x03E, 0x03C, 0x03B, 0x039,
        0x038, 0x037, 0x035, 0x034, 0x033, 0x031, 0x030, 0x02F,
        0x02E, 0x02D, 0x02B, 0x02A, 0x029, 0x028, 0x027, 0x026,
        0x025, 0x024, 0x023, 0x022, 0x021, 0x020, 0x01F, 0x01E,
        0x01D, 0x01C, 0x01B, 0x01A, 0x019, 0x018, 0x017, 0x017,
        0x016, 0x015, 0x014, 0x014, 0x013, 0x012, 0x011, 0x011,
        0x010, 0x00F, 0x00F, 0x00E, 0x00D, 0x00D, 0x00C, 0x00C,
        0x00B, 0x00A, 0x00A, 0x009, 0x009, 0x008, 0x008, 0x007,
        0x007, 0x007, 0x006, 0x006, 0x005, 0x005, 0x005, 0x004,
        0x004, 0x004, 0x003, 0x003, 0x003, 0x002, 0x002, 0x002,
        0x002, 0x001, 0x001, 0x001, 0x001, 0x001, 0x001, 0x001,
        0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000, 0x000
    )

    KSL = (0, 32, 40, 45, 48, 51, 53, 55, 56, 58, 59, 60, 61, 62, 63, 64)

    KSL_SHIFT = (8, 1, 2, 0)

    INC_STEP = (
        (
            (0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0)
        ),
        (
            (0, 1, 0, 1, 0, 1, 0, 1),
            (0, 1, 0, 1, 1, 1, 0, 1),
            (0, 1, 1, 1, 0, 1, 1, 1),
            (0, 1, 1, 1, 1, 1, 1, 1)
        ),
        (
            (1, 1, 1, 1, 1, 1, 1, 1),
            (2, 2, 1, 1, 1, 1, 1, 1),
            (2, 2, 1, 1, 2, 2, 1, 1),
            (2, 2, 2, 2, 2, 2, 1, 1)
        )
    )

    INC_DESC = (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2)

    INC_SHIFT = (0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 0, -1, -2)

    OFF = 0
    ATTACK = 1
    DECAY = 2
    SUSTAIN = 3
    RELEASE = 4

    def __init__(self, slot):
        self.slot = slot
        self.reset()

    def __str__(self):
        return str(self.log)

    def reset(self):
        self.level = 0x1FF
        self.log = 0x1FF
        self.inc = 0
        self.state = self.OFF
        self.rate = 0
        self.ksl = 0

    def _exp(self, level):
        if level > 0x1FFF:
            level = 0x1FFF
        return ((self.EXP[(level & 0xFF) ^ 0xFF] | 0x400) << 1) >> (level >> 8)

    def _sin0(self, phase):
        phase &= 0x3FF
        if phase & 0x100:
            log = self.LOG[(phase & 0xFF) ^ 0xFF]
        else:
            log = self.LOG[phase & 0xFF]
        output = self._exp((self.log << 3) + log)
        if phase & 0x200:
            return -output - 1
        else:
            return output

    def _sin1(self, phase):
        phase &= 0x3FF
        if phase & 0x200:
            log = 0x1000
        elif phase & 0x100:
            log = self.LOG[(phase & 0xFF) ^ 0xFF]
        else:
            log = self.LOG[phase & 0xFF]
        return self._exp((self.log << 3) + log)

    def _sin2(self, phase):
        phase &= 0x3FF
        if phase & 0x100:
            log = self.LOG[(phase & 0xFF) ^ 0xFF]
        else:
            log = self.LOG[phase & 0xFF]
        return self._exp((self.log << 3) + log)

    def _sin3(self, phase):
        phase &= 0x3FF
        if phase & 0x100:
            log = 0x1000
        else:
            log = self.LOG[phase & 0xFF]
        return self._exp((self.log << 3) + log)

    def _sin4(self, phase):
        phase &= 0x3FF
        if phase & 0x200:
            log = 0x1000
        elif phase & 0x80:
            log = self.LOG[((phase ^ 0xFF) << 1) & 0xFF]
        else:
            log = self.LOG[(phase << 1) & 0xFF]
        output = self._exp((self.log << 3) + log)
        if (phase & 0x300) == 0x100:
            return -output - 1
        else:
            return output

    def _sin5(self, phase):
        phase &= 0x3FF
        if phase & 0x200:
            log = 0x1000
        elif phase & 0x80:
            log = self.LOG[((phase ^ 0xFF) << 1) & 0xFF]
        else:
            log = self.LOG[(phase << 1) & 0xFF]
        return self._exp((self.log << 3) + log)

    def _sin6(self, phase):
        phase &= 0x3FF
        output = self._exp(self.log << 3)
        if phase & 0x200:
            return -output - 1
        else:
            return output

    def _sin7(self, phase):
        phase &= 0x3FF
        if phase & 0x200:
            phase = (phase & 0x1FF) ^ 0x1FF
        output = self._exp((self.log + phase) << 3)
        if phase & 0x200:
            return -output - 1
        else:
            return output

    sin = (_sin0, _sin1, _sin2, _sin3, _sin4, _sin5, _sin6, _sin7)

    def update_ksl(self):
        channel = self.slot.channel
        ksl = ((self.KSL[channel.fnum >> 6] << 2) -
               ((0x08 - channel.block) << 5))
        if ksl < 0:
            ksl = 0
        self.ksl = ksl

    def update_rate(self):
        if self.state <= self.ATTACK:
            rate = self.slot.ar
        elif self.state == self.DECAY:
            rate = self.slot.dr
        else:
            rate = self.slot.rr

        if rate:
            channel = self.slot.channel
            ksv = channel.ksv if self.slot.ksr else (channel.ksv >> 2)
            rate = (rate << 2) + ksv
            if rate > 0x3C:
                rate = 0x3C
        else:
            rate = 0x00
        self.rate = rate

    def _process_off(self):
        self.level = 0x1FF

    def _process_attack(self):
        level = self.level
        if level:
            level += ((-level - 1) * self.inc) >> 3
            if level < 0:
                level = 0
            self.level = level
        else:
            self.state = self.DECAY
            self.update_rate()

    def _process_decay(self):
        if self.level >= (self.slot.sl << 4):
            self.state = self.SUSTAIN
            self.update_rate()
        else:
            self.level += self.inc

    def _process_sustain(self):
        if not self.slot.egt:
            self._process_release()

    def _process_release(self):
        if self.level >= 0x1FF:
            self.state = self.OFF
            self.level = 0x1FF
            self.update_rate()
        else:
            self.level += self.inc

    _process = (
        _process_off,
        _process_attack,
        _process_decay,
        _process_sustain,
        _process_release,
    )

    def update_output(self):
        slot = self.slot
        inc = 0
        high = self.rate >> 2
        low = self.rate & 3
        shift = self.INC_SHIFT[high]
        timer = slot.chip.timer
        inc_steps = self.INC_STEP[self.INC_DESC[high]][low]
        if shift > 0:
            if not (timer & ((1 << shift) - 1)):
                inc = inc_steps[(timer >> shift) & 0x07]
        else:
            inc = inc_steps[timer & 0x07] << -shift
        self.inc = inc
        self.log = (self.level +
                       (slot.tl << 2) +
                       (self.ksl >> self.KSL_SHIFT[slot.ksl]) +
                       slot.tremolo[0])
        self._process[self.state](self)

    def set_key(self, on):
        if on:
            self.state = self.ATTACK
            self.update_rate()
            if (self.rate >> 2) == 0x0F:
                self.state = self.DECAY
                self.update_rate()
                self.level = 0
        else:
            self.state = self.RELEASE
            self.update_rate()


class Slot(object):

    FREQ_MULT_X2 = (1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 20, 24, 24, 30, 30)

    def __init__(self, channel=None, chip=None):
        self.channel = channel
        self.chip = chip
        self.envelope = Envelope(self)
        self.feedback = [0]
        self.output = [0]

        self.reset(None, None)

    def __str__(self):
        return str(self.output[0])

    def reset(self, modulation, tremolo):
        self.envelope.reset()

        self.modulation = modulation
        self.tremolo = tremolo

        self.output[0] = 0
        self.feedback[0] = 0
        self.previous = 0
        self.key = 0
        self.phase = 0
        self.timer = 0

        self.vib = 0
        self.egt = 0
        self.ksr = 0
        self.mult = 0
        self.ksl = 0
        self.tl = 0
        self.ar = 0
        self.dr = 0
        self.sl = 0
        self.rr = 0
        self.ws = 0

    def set_key(self, on, drum):
        if on:
            if not self.key:
                self.envelope.set_key(True)
                self.phase = 0
            self.key |= 0x02 if drum else 0x01
        else:
            if self.key:
                self.key &= ~0x02 if drum else ~0x01
                if not self.key:
                    self.envelope.set_key(False)

    def update_phase(self):
        fnum = self.channel.fnum
        if self.vib:
            chip = self.chip
            frange = (fnum >> 7) & 7
            vibrato_phase = chip.vibrato_phase

            if not (vibrato_phase & 3):
                frange = 0
            elif vibrato_phase & 1:
                frange >>= 1
            frange >>= chip.vibrato_shift

            if vibrato_phase & 4:
                frange = -frange
            fnum += frange
            fnum &= 0xFFFF

        basefreq = (fnum << self.channel.block) >> 1
        self.phase += (basefreq * self.FREQ_MULT_X2[self.mult]) >> 1
        self.phase &= 0xFFFFFFFF

    def write_2x(self, data):
        if data & (0x01 << 7):
            self.tremolo = self.chip.tremolo
        else:
            self.tremolo = self.chip.SILENCE
        self.vib = (data >> 6) & 0x01
        self.egt = (data >> 5) & 0x01
        self.ksr = (data >> 4) & 0x01
        self.mult = data & 0x0F
        self.envelope.update_rate()

    def write_4x(self, data):
        self.ksl = (data >> 6) & 0x03
        self.tl = data & 0x3F
        self.envelope.update_ksl()

    def write_6x(self, data):
        self.ar = (data >> 4) & 0x0F
        self.dr = data & 0x0F
        self.envelope.update_rate()

    def write_8x(self, data):
        self.sl = (data >> 4) & 0x0F
        if self.sl == 0x0F:
            self.sl = 0x1F
        self.rr = data & 0x0F
        self.envelope.update_rate()

    def write_ex(self, data):
        self.ws = data & (0x07 if self.chip.new else 0x03)

    def update_output_custom(self, phase):
        envelope = self.envelope
        generator = envelope.sin[self.ws]
        self.output[0] = generator(envelope, phase)

    def update_output_modulated(self):
        phase = (self.phase >> 9) + self.modulation[0]
        envelope = self.envelope
        generator = envelope.sin[self.ws]
        self.output[0] = generator(envelope, phase)

    def update_output_normal(self):
        phase = self.phase >> 9
        envelope = self.envelope
        generator = envelope.sin[self.ws]
        self.output[0] = generator(envelope, phase)

    def update_feedback(self):
        fb = self.channel.fb
        output = self.output[0]
        if fb:
            self.feedback[0] = (self.previous + output) >> (0x09 - fb)
        else:
            self.feedback[0] = 0
        self.previous = output


class Channel(object):

    TWO_OP = 0
    FOUR_OP = 1
    FOUR_OP2 = 2
    DRUM = 3

    def __init__(self, chip=None):
        self.chip = chip
        self.reset()

    def __str__(self):
        outputs = [None] * 2
        for side in range(2):
            total = 0
            if self.ch & (1 << side):
                for output in self.outputs:
                    total += output[0]
            outputs[side] = total
        return str(outputs)


    def reset(self):
        self.slots = [None] * 2
        self.outputs = [None] * 4
        self.pair = None

        self.mode = self.TWO_OP
        self.fnum = 0x00
        self.block = 0x00
        self.fb = 0x00
        self.cnt = 0x00
        self.wiring = 0x00
        self.ch = 0x00
        self.ksv = 0

    def write_ax(self, data):
        if self.chip.new and self.mode == self.FOUR_OP2:
            return

        fnum = (self.fnum & 0x300) | data
        self.fnum = fnum
        self.ksv = ((self.block << 1) |
                    ((fnum >> (0x09 - self.chip.nts)) & 0x01))

        for slot in self.slots:
            slot.envelope.update_ksl()
            slot.envelope.update_rate()

        if self.chip.new and self.mode == self.FOUR_OP:
            pair = self.pair
            pair.fnum = fnum
            pair.ksv = self.ksv

            for slot in pair.slots:
                slot.envelope.update_ksl()
                slot.envelope.update_rate()

    def write_bx(self, data):
        if self.chip.new and self.mode == self.FOUR_OP2:
            return

        self.fnum = (self.fnum & 0xFF) | ((data & 0x03) << 8)
        self.block = (data >> 2) & 0x07
        self.ksv = ((self.block << 1) |
                    ((self.fnum >> (0x09 - self.chip.nts)) & 0x01))

        for slot in self.slots:
            slot.envelope.update_ksl()
            slot.envelope.update_rate()

        if self.chip.new and self.mode == self.FOUR_OP:
            pair = self.pair
            pair.fnum = self.fnum
            pair.block = self.block
            pair.ksv = self.ksv

            for slot in pair.slots:
                slot.envelope.update_ksl()
                slot.envelope.update_rate()

        self.set_key(data & 0x20)

    def write_cx(self, data):
        self.fb = (data >> 1) & 0x07
        self.cnt = data & 0x01
        self.wiring = self.cnt

        if self.chip.new:
            pair = self.pair

            if self.mode == self.FOUR_OP:
                pair.wiring = 0x04 | (self.cnt << 1) | (pair.cnt)
                self.wiring = 0x08
                pair.rewire()

            elif self.mode == self.FOUR_OP2:
                self.wiring = 0x04 | (pair.cnt << 1) | (self.cnt)
                pair.wiring = 0x08
                self.rewire()

            else:
                self.rewire()
        else:
            self.rewire()

        if self.chip.new:
            self.ch = (data >> 4) & 0x03
        else:
            self.ch = 0x03

    def rewire(self):
        self_slots = self.slots
        self_outputs = self.outputs
        SILENCE = self.chip.SILENCE

        if self.mode == self.DRUM:
            if self.wiring & 0x01:
                self_slots[0].modulation = self_slots[0].feedback
                self_slots[1].modulation = SILENCE
            else:
                self_slots[0].modulation = self_slots[0].feedback
                self_slots[1].modulation = self_slots[0].output

        elif self.wiring & 0x08:
            pass

        elif self.wiring & 0x04:
            pair = self.pair
            pair_slots = pair.slots
            pair_outputs = pair.outputs
            case = self.wiring & 0x03

            pair_outputs[0] = SILENCE
            pair_outputs[1] = SILENCE
            pair_outputs[2] = SILENCE
            pair_outputs[3] = SILENCE

            if case == 0x00:
                pair_slots[0].modulation = pair_slots[0].feedback
                pair_slots[1].modulation = pair_slots[0].output

                self_slots[0].modulation = pair_slots[1].output
                self_slots[1].modulation = self_slots[0].output

                self_outputs[0] = self_slots[1].output
                self_outputs[1] = SILENCE
                self_outputs[2] = SILENCE
                self_outputs[3] = SILENCE

            elif case == 0x01:
                pair_slots[0].modulation = pair_slots[0].feedback
                pair_slots[1].modulation = pair_slots[0].output

                self_slots[0].modulation = SILENCE
                self_slots[1].modulation = self_slots[0].output

                self_outputs[0] = pair_slots[1].output
                self_outputs[1] = self_slots[1].output
                self_outputs[2] = SILENCE
                self_outputs[3] = SILENCE

            elif case == 0x02:
                pair_slots[0].modulation = pair_slots[0].feedback
                pair_slots[1].modulation = SILENCE

                self_slots[0].modulation = pair_slots[1].output
                self_slots[1].modulation = self_slots[0].output

                self_outputs[0] = pair_slots[0].output
                self_outputs[1] = self_slots[1].output
                self_outputs[2] = SILENCE
                self_outputs[3] = SILENCE

            elif case == 0x03:
                pair_slots[0].modulation = pair_slots[0].feedback
                pair_slots[1].modulation = SILENCE

                self_slots[0].modulation = pair_slots[1].output
                self_slots[1].modulation = SILENCE

                self_outputs[0] = pair_slots[0].output
                self_outputs[1] = self_slots[0].output
                self_outputs[2] = self_slots[1].output
                self_outputs[3] = SILENCE

        else:
            if self.wiring & 0x01:
                self_slots[0].modulation = self_slots[0].feedback
                self_slots[1].modulation = SILENCE

                self_outputs[0] = self_slots[0].output
                self_outputs[1] = self_slots[1].output
                self_outputs[2] = SILENCE
                self_outputs[3] = SILENCE

            else:
                self_slots[0].modulation = self_slots[0].feedback
                self_slots[1].modulation = self_slots[0].output

                self_outputs[0] = self_slots[1].output
                self_outputs[1] = SILENCE
                self_outputs[2] = SILENCE
                self_outputs[3] = SILENCE

    def set_key(self, on):
        if self.chip.new:
            if self.mode == self.FOUR_OP:
                for slot in self.slots:
                    slot.set_key(on, False)

                for slot in self.pair.slots:
                    slot.set_key(on, False)

            elif self.mode == self.TWO_OP or self.mode == self.DRUM:
                for slot in self.slots:
                    slot.set_key(on, False)
        else:
            for slot in self.slots:
                slot.set_key(on, False)


def default_mixer(side, channels):
    side_mask = 1 << side
    total = 0
    for channel in channels:
        if channel.ch & side_mask:
            for output in channel.outputs:
                total += output[0]
    return total


class Chip(object):

    RATE = 49716

    AD_SLOT = (
        0, 1, 2, 3, 4, 5, None, None,
        6, 7, 8, 9, 10, 11, None, None,
        12, 13, 14, 15, 16, 17, None, None,
        None, None, None, None, None, None, None, None
    )

    CH_SLOT = (0, 1, 2, 6, 7, 8, 12, 13, 14,
               18, 19, 20, 24, 25, 26, 30, 31, 32)

    CH_PAIR = (3, 4, 5, 0, 1, 2, 6, 7, 8,
               3, 4, 5, 0, 1, 2, 6, 7, 8)

    SILENCE = (0,)

    def __init__(self):
        self.channels = [Channel(chip=self) for _ in range(18)]
        self.slots = [Slot(chip=self) for _ in range(36)]
        self.noise = Noise()
        self.outputs = [0] * 2

        self._channels_6_8 = self.channels[6:9]
        self._slots_0_11 = self.slots[0:12]
        self._slots_12_14 = self.slots[12:15]
        self._slots_15_17 = self.slots[15:18]
        self._slots_18_32 = self.slots[18:33]
        self._slots_33_35 = self.slots[33:36]

        self.reset()

    def reset(self):
        SILENCE = self.SILENCE

        self.noise.reset()
        for i in range(len(self.outputs)):
            self.outputs[i] = 0

        self.timer = 0
        self.new = 0
        self.nts = 0
        self.ryt = 0x00
        self.vibrato_phase = 0
        self.vibrato_shift = 1
        self.tremolo = [0]
        self.tremolo_phase = 0
        self.tremolo_shift = 4

        for slot in self.slots:
            slot.reset(SILENCE, SILENCE)

        for channel_index, channel in enumerate(self.channels):
            channel.reset()
            ch_slot = self.CH_SLOT[channel_index]

            for j in range(2):
                slot_index = ch_slot + j * 3
                channel.slots[j] = self.slots[slot_index]
                self.slots[slot_index].channel = channel

            for j in range(4):
                channel.outputs[j] = SILENCE

            channel.pair = self.channels[self.CH_PAIR[channel_index]]
            channel.mode = channel.TWO_OP
            channel.ch = 0x03
            channel.rewire()

    def _set_connection(self, connection):
        channels = self.channels
        TWO_OP = Channel.TWO_OP
        FOUR_OP = Channel.FOUR_OP
        FOUR_OP2 = Channel.FOUR_OP2

        for bit in range(6):
            index = bit
            if bit >= 3:
                index += 9 - 3

            if connection & (1 << bit):
                channels[index].mode = FOUR_OP
                channels[index + 3].mode = FOUR_OP2
            else:
                channels[index].mode = TWO_OP
                channels[index + 3].mode = TWO_OP

    def _generate_rhythm1(self):
        channel6 = self.channel[6]
        channel7 = self.channel[7]
        channel8 = self.channel[8]

        channel6.slots[0].update_output_modulated()

        phase14 = (channel7.slots[0].phase >> 9) & 0x3FF
        phase17 = (channel8.slots[1].phase >> 9) & 0x3FF

        phasebit = ((phase14 & 0x08) |
                    (((phase14 >> 5) ^ phase14) & 0x04) |
                    (((phase17 >> 2) ^ phase17) & 0x08))
        phasebit = 1 if phasebit else 0

        phase = ((phasebit << 9) |
                 (0x34 << ((phasebit ^ (self.noise.output & 0x01)) << 1)))
        channel7.slots[0].update_output_custom(phase)

        channel8.slots[0].update_output_normal()

    def _generate_rhythm2(self):
        channel6 = self.channel[6]
        channel7 = self.channel[7]
        channel8 = self.channel[8]

        channel6.slots[1].update_output_modulated()

        phase14 = (channel7.slots[0].phase >> 9) & 0x3FF
        phase17 = (channel8.slots[1].phase >> 9) & 0x3FF

        phasebit = ((phase14 & 0x08) |
                    (((phase14 >> 5) ^ phase14) & 0x04) |
                    (((phase17 >> 2) ^ phase17) & 0x08))
        phasebit = 1 if phasebit else 0

        phase = ((0x100 << ((phase14 >> 8) & 0x01)) ^
                 ((self.noise.output & 0x01) << 8))
        channel7.slots[1].update_output_custom(phase)

        phase = 0x100 | (phasebit << 9)
        channel8.slots[1].update_output_custom(phase)

    def set_rhythm(self, data):
        self.tremolo_shift = (((data >> (7 - 1)) & 0x02) ^ 0x02) + 0x02
        self.vibrato_shift = ((data >> 6) & 0x01) ^ 0x01

        ryt = data & 0x3F
        self.ryt = ryt

        if ryt & 0x20:
            channel6 = self.channels[6]
            channel7 = self.channels[7]
            channel8 = self.channels[8]

            channel6.outputs[0] = channel6.slots[1].output
            channel6.outputs[1] = channel6.slots[1].output
            channel6.outputs[2] = self.SILENCE
            channel6.outputs[3] = self.SILENCE

            channel7.outputs[0] = channel7.slots[0].output
            channel7.outputs[1] = channel7.slots[0].output
            channel7.outputs[2] = channel7.slots[1].output
            channel7.outputs[3] = channel7.slots[1].output

            channel8.outputs[0] = channel8.slots[0].output
            channel8.outputs[1] = channel8.slots[0].output
            channel8.outputs[2] = channel8.slots[1].output
            channel8.outputs[3] = channel8.slots[1].output

            for channel in self._channels_6_8:
                channel.mode = channel.DRUM

            channel6.rewire()

            channel7.slots[0].set_key(ryt & 0x01, True)
            channel8.slots[1].set_key(ryt & 0x02, True)
            channel8.slots[0].set_key(ryt & 0x04, True)
            channel7.slots[1].set_key(ryt & 0x08, True)
            channel6.slots[0].set_key(ryt & 0x10, True)
            channel6.slots[1].set_key(ryt & 0x10, True)

        else:
            for channel in self._channels_6_8:
                channel.mode = channel.TWO_OP
                channel.rewire()
                for slot in channel.slots:
                    slot.set_key(False, True)

    def update_output(self, mixer=default_mixer):
        for slot in self._slots_0_11:
            slot.update_feedback()
            slot.update_phase()
            slot.envelope.update_output()
            slot.update_output_modulated()

        for slot in self._slots_12_14:
            slot.update_feedback()
            slot.update_phase()
            slot.envelope.update_output()

        if self.ryt & 0x20:
            self._generate_rhythm1()
        else:
            for slot in self._slots_12_14:
                slot.update_output_modulated()

        self.outputs[0] = mixer(0, self.channels)

        for slot in self._slots_15_17:
            slot.update_feedback()
            slot.update_phase()
            slot.envelope.update_output()

        if self.ryt & 0x20:
            self._generate_rhythm2()
        else:
            for slot in self._slots_15_17:
                slot.update_output_modulated()

        for slot in self._slots_18_32:
            slot.update_feedback()
            slot.update_phase()
            slot.envelope.update_output()
            slot.update_output_modulated()

        self.outputs[1] = mixer(1, self.channels)

        for slot in self._slots_33_35:
            slot.update_feedback()
            slot.update_phase()
            slot.envelope.update_output()
            slot.update_output_modulated()

        self.noise.next()

        if (self.timer & 0x3F) == 0x3F:
            self.tremolo_phase = (self.tremolo_phase + 1) % 210

        if self.tremolo_phase < 105:
            self.tremolo[0] = self.tremolo_phase >> self.tremolo_shift
        else:
            self.tremolo[0] = (210 - self.tremolo_phase) >> self.tremolo_shift

        if (self.timer & 0x3FF) == 0x3FF:
            self.vibrato_phase = (self.vibrato_phase + 1) & 7

        self.timer += 1

    def write(self, address, data):
        bank = (address >> 8) & 0x01
        register = address & 0xFF

        offset = register & 0x0F
        if offset < 9:
            channel = self.channels[9 * bank + offset]
        else:
            channel = None

        slot_offset = self.AD_SLOT[register & 0x1F]
        if slot_offset is None:
            slot = None
        else:
            slot = self.slots[18 * bank + slot_offset]

        if 0x00 <= register <= 0x0F:
            if bank:
                if register == 0x04:
                    self._set_connection(data & 0x3F)
                elif register == 0x05:
                    self.new = data & 0x01
            else:
                if register == 0x00:
                    self.reset()
                elif register == 0x08:
                    self.nts = (data >> 6) & 0x01

        elif 0x20 <= register <= 0x35:
            if slot is not None:
                slot.write_2x(data)

        elif 0x40 <= register <= 0x55:
            if slot is not None:
                slot.write_4x(data)

        elif 0x60 <= register <= 0x75:
            if slot is not None:
                slot.write_6x(data)

        elif 0x80 <= register <= 0x95:
            if slot is not None:
                slot.write_8x(data)

        elif 0xA0 <= register <= 0xA8:
            if channel is not None:
                channel.write_ax(data)

        elif 0xB0 <= register <= 0xB8:
            if channel is not None:
                channel.write_bx(data)

        elif register == 0xBD and not bank:
            self.set_rhythm(data)

        elif 0xC0 <= register <= 0xC8:
            if channel is not None:
                channel.write_cx(data)

        elif 0xE0 <= register <= 0xF5:
            if slot is not None:
                slot.write_ex(data)

    def render(self, sequence):
        self_rate = self.RATE
        seq_rate = sequence.rate
        remainder = self_rate % seq_rate
        error = 0

        for events in sequence:
            for event in events:
                self.write(event.address, event.data)

            length = (self_rate + error) // seq_rate
            error = (error + remainder) % seq_rate

            for _ in range(length):
                self.update_output()
                yield self.outputs
