from typing import List, Optional
from pydantic import BaseModel
from domain.models import Checkpoint


class UploadResponse(BaseModel):
    job_id: str
    filename: str
    duration: float


class StatusResponse(BaseModel):
    status: str
    message: str
    progress: int
    error: Optional[str] = None


class UnderstandAnswersRequest(BaseModel):
    answers: List[dict] = []


class ExportRequest(BaseModel):
    checkpoints: List[Checkpoint]
    learning_script: Optional[dict] = None


class RegenerateRequest(BaseModel):
    feedback: str = ""


class RegenerateLearningRequest(BaseModel):
    feedback: str = ""
