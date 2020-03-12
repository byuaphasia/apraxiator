class ISender:
    def send_subject_waiver(self, waiver_file, recipient: str):
        raise NotImplementedError()

    def send_clinician_waiver(self, waiver_file, recipient: str, patient_name: str):
        raise NotImplementedError()

    def send_report(self, report_file, recipient: str, evaluation_id: str):
        raise NotImplementedError()
