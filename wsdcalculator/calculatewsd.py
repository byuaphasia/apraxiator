from .speechdetection.filterbythreshold import Filterer
from .speechdetection.findendpoints import EndpointFinder

class WSDCalculator():
    def __init__(self, storage):
        filterer = Filterer(storage)
        endpoint_finder = EndpointFinder(storage)
        self.measurers = {
            'filter': filterer,
            'endpoint': endpoint_finder
        }

    def calculate_wsd(self, recording, syllable_count, evaluation_id, method='average'):
        """ Uses the supplied method to calculate a Word Syllable Duration (WSD) measurement.

        Parameters:
        recording (str or file object): location of recording file or the file object itself
        syllable_count (int): number of syllables in the recorded word
        evaluation_id (str): id connecting this recording to an evaluation group
        method (str): specifies which version of calculation to use, options: ['filter','endpoint','average']

        Returns:
        float: WSD measurement, average milliseconds per syllable in the recording
        """
        m = self.measurers.get(method, None)
        # Default is to average all methods
        if m is None:
            total = 0
            for mes in self.measurers.values():
                total += mes.measure(recording, evaluation_id)
            duration = total / len(self.measurers)
        else:
            duration = m.measure(recording, evaluation_id)

        wsd = duration / syllable_count
        return wsd, duration
