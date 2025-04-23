from fastapi import UploadFile, File


class PredictRequest:
    file: UploadFile = File(...)
