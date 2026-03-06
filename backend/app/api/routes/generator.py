from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...services.generator_service import GeneratorService
from ..schemas.generator import GeneratorJobCreate

router = APIRouter()
service = GeneratorService()


@router.post('/generator/jobs', status_code=201)
def create_generator_job(payload: GeneratorJobCreate):
    return service.create(payload)


@router.get('/generator/jobs/{job_id}')
def get_generator_job(job_id: str):
    job = service.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Generator job not found')
    return job


@router.post('/generator/jobs/{job_id}/stop')
def stop_generator_job(job_id: str):
    job = service.stop(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Generator job not found')
    return job
