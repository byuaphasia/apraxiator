from flask import Request

class IRecordingController:
    @staticmethod
    def get_request_recording(r: Request):
        try:
            return r.files['recording']
        except Exception as e:
            pass