class EvaluationService:
    def __init__(self, storage):
        pass

    def create_evaluation(self, age: str, gender: str, impression: str, user: str) -> str:
        pass

    def add_ambiance(self, audio, sr: int, user:str):
        pass

    def process_attempt(self, user: str, evaluation_id: str, word: str, syllable_count: int, method: int, audio, sr: int):
        # Calculate WSD
        # Add attempt to DB
        pass