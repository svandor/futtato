import torch
print('torch', torch.__version__)
print('cuda_available', torch.cuda.is_available())
print('cuda_version', getattr(torch.version, 'cuda', None))
if torch.cuda.is_available():
    print('device_count', torch.cuda.device_count())
    print('device_name', torch.cuda.get_device_name(0))
