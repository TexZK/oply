
import heapq
import io
import struct


class IMF(object):

    class Event(object):
        __slots__ = ('address', 'data', 'time')

        def __init__(self, register, data, time=0):
            self.address = register
            self.data = data
            self.time = time

        def __repr__(self):
            fmt = ('Event('
                   'address=0x{0.address:02X}, '
                   'data=0x{0.data:02X}, '
                   'time={0.time:d})')
            return fmt.format(self)

        @classmethod
        def load(cls, stream):
            return cls(*struct.unpack('<BBH', stream.read(4)))

        def store(self, stream, previous_time=0):
            delay = self.time - previous_time
            stream.write(struct.pack('<BBH', self.address, self.data, delay))

    def __init__(self, stream=None, chunk_size=None, rate=560):
        self.rate = rate
        self.version = 0
        self.size = 0
        self.events = ()
        self.extra = b''

        if stream is not None:
            self.load(stream, chunk_size)

    def load(self, stream, chunk_size=None):
        if chunk_size is None:
            offset = stream.tell()
            stream.seek(0, io.SEEK_END)
            chunk_size = stream.tell() - offset
            stream.seek(offset)

        size = struct.unpack('<H', stream.read(2))[0]
        if not size:
            version = 0
            size = chunk_size - 2
        else:
            version = None

        count = size // 4
        Event = self.Event
        events = [Event.load(stream) for _ in range(count)]

        if version is None:
            sum1 = 0
            sum2 = 0
            for event in events[:42]:
                sum1 += event.address | event.data << 8
                sum2 += event.time
            version = int(sum1 > sum2)

        if version == 1:
            extra = stream.read(chunk_size - stream.tell())
        else:
            extra = b''

        self.version = version
        self.size = size
        self.events = events
        self.extra = extra

    def store(self, stream):
        stream.write('<H', self.size if self.version else 0)

        for event in self.events:
            event.store(stream)

        stream.write(self.extra)

    def to_sequence(self, sequencer):
        imf_time = 0
        imf_rate = self.rate
        seq_rate = sequencer.rate

        for event in self.events:
            seq_time = sequencer.time + (imf_time * imf_rate) // seq_rate
            sequencer.insert(seq_time, event.address, event.data)
            imf_time += event.time

        seq_time = sequencer.time + (imf_time * imf_rate) // seq_rate
        sequencer.insert(seq_time, 0, 0)


class Sequencer(object):

    class Event(object):
        __slots__ = ('order', 'time', 'address', 'data')

        def __init__(self, time, order, address, data):
            self.time = time
            self.order = order
            self.address = address
            self.data = data

        def __repr__(self):
            fmt = ('Event('
                   'time={0.time:d}, '
                   'order={0.order:d}, '
                   'address=0x{0.address:03X}, '
                   'data=0x{0.data:02X})')
            return fmt.format(self)

        def __lt__(self, other):
            return (self.time < other.time or
                    (self.time == other.time and self.order < other.order))

    def __init__(self, rate=560):
        self.rate = rate
        self.reset()

    def reset(self):
        self.time = 0
        self.order = 0
        self._heap = []

    def insert(self, time, address, data):
        if time >= self.time:
            event = self.Event(time, self.order, address, data)
            heapq.heappush(self._heap, event)
            self.order += 1

    def pop(self):
        heap = self._heap
        synchronous = []
        while heap and heap[0].time == self.time:
            synchronous.append(heapq.heappop(heap))
        return synchronous

    def advance(self):
        heap = self._heap
        while heap and heap[0].time < self.time:
            heapq.heappop(heap)
        self.time += 1

    def wrap(self):
        delta = max(event.time for event in self._heap) - self.time
        self.time -= delta
        self.order = -len(self._heap)
        for i, event in enumerate(self._heap):
            event.time -= delta
            event.order = self.order + i
        return delta

    def __iter__(self):
        heap = self._heap
        while heap:
            yield self.pop()
            self.advance()
