class IWaiverFileStorage:
    def save_waiver(self, waiver_id: str, waiver_file: str):
        raise NotImplementedError()

    def get_waiver(self, waiver_id: str):
        raise NotImplementedError()