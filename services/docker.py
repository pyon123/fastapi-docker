import docker
from pydantic import BaseModel, field_validator
import requests.exceptions
import psutil
import pynvml

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
        self.client = docker.from_env()

        self.image = image
        self.resource = resource
        self.code = code
        self.timeout = timeout

    def validate_resources(self):
        containers = self.client.containers.list(filters= {'status': 'running'})
        allowcatedCpus = 0
        allowcatedMemory = 0
        for container in containers:
            allowcatedCpus += container.attrs['HostConfig']['CpuCount']
            allowcatedMemory += container.attrs['HostConfig']['Memory']
            
        # check available CPU
        cpu_count = psutil.cpu_count(logical=False)  # Physical CPU count
        if self.resource.cpu > cpu_count - allowcatedCpus:
            raise ValueError(f"Requested {self.resource.cpu} CPUs, but only {cpu_count} available.")

        # check available GPU
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            pynvml.nvmlShutdown()
        except pynvml.NVMLError as e:
            device_count = 0  # No GPUs available or error accessing NVML
        if self.resource.gpu > device_count:
            raise ValueError(f"Requested {self.resource.gpu} GPUs, but only {device_count} available.")

        # check available RAM
        available_memory = psutil.virtual_memory().available
        requested_memory = int(self.resource.ram[:-2])
        if self.resource.ram.upper().endswith('MB'):
            requested_memory *= 1024 * 1024  # Convert MB to bytes
        elif self.resource.ram.upper().endswith('GB'):
            requested_memory *= 1024 * 1024 * 1024  # Convert GB to bytes

        if requested_memory > available_memory - allowcatedMemory:
            raise ValueError(f"Requested {self.resource.ram} RAM, but only {available_memory} available.")

        # check available storage

        pass

    async def execute(self):
        self.validate_resources()

        try:
            # Pull Docker image if not available locally
            try:
                self.client.images.get(self.image)
            except docker.errors.ImageNotFound:
                print(f"Image '{self.image}' not found locally. Pulling from Docker Hub...")
                self.client.images.pull(self.image)

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

            container = self.client.containers.run(**run_kwargs)

            try:
                container.wait(timeout=self.timeout)
            except requests.exceptions.ReadTimeout:
                container.kill()
                # container.stop()
                # container.remove(force=True)
                raise RuntimeError("Container execution timed out")

            logs = container.logs().decode('utf-8')
            container.remove(force=True)

            return logs
        except Exception as e:
            raise RuntimeError(f"Failed to execute container: {str(e)}")