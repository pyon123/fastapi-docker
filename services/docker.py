import docker
from pydantic import BaseModel, field_validator
import requests.exceptions

class ResourceType(BaseModel):
    cpu: str
    gpu: str
    ram: str
    storage: str

    @field_validator('cpu', 'gpu')
    def validate_positive_int(cls, v: str) -> int:
        if not v.isdigit():
            raise ValueError(f'{v} should be a valid non-negative integer string.')
        return int(v)

    @field_validator('ram', 'storage')
    def validate_memory_format(cls, v: str) -> str:
        if not v[:-2].isdigit() or v[-2:].upper() not in ['MB', 'GB']:
            raise ValueError(f'{v} is not a valid format.')
        return v
    
class DockerContainer:
    def __init__(self, resource: ResourceType, code: str, image: str = 'python:3.9-slim', timeout: int = 30):
        self.image = image
        self.resource = resource
        self.code = code
        self.timeout = timeout

    def validate_resources(self):
        # check available CPU

        # check available GPU

        # check available RAM

        # check available storage

        pass

    async def execute(self):
        self.validate_resources()

        client = docker.from_env()

        try:
            # Pull Docker image if not available locally
            try:
                client.images.get(self.image)
            except docker.errors.ImageNotFound:
                print(f"Image '{self.image}' not found locally. Pulling from Docker Hub...")
                client.images.pull(self.image)

            run_kwargs = {
                'image': self.image,
                'command': f'python -c "{self.code}"',
                'detach': True,
            }

            if self.resource.cpu is not None:
                run_kwargs['cpu_count'] = self.resource.cpu
            if self.resource.gpu is not None:
                run_kwargs['runtime'] = 'nvidia'
                # run_kwargs['environment'] = ['NVIDIA_VISIBLE_DEVICES=all']
                run_kwargs['device_requests'] = [
                    docker.types.DeviceRequest(count=self.resource.gpu, capabilities=[['gpu']])
                ]
            if self.resource.ram is not None:
                run_kwargs['mem_limit'] = self.resource.ram
            # if self.resource.storage is not None:
            #     run_kwargs['storage_opt'] = {
            #         'size': self.resource.storage
            #     }

            container = client.containers.run(**run_kwargs)

            try:
                container.wait(timeout=self.timeout)
            except requests.exceptions.ReadTimeout:
                # container.kill()
                container.stop()
                container.remove(force=True)
                raise RuntimeError("Container execution timed out")

            logs = container.logs().decode('utf-8')
            container.remove(force=True)

            return logs
        except Exception as e:
            raise RuntimeError(f"Failed to execute container: {str(e)}")