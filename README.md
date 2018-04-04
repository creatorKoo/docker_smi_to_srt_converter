# docker_smi_to_srt_converter
docker image for smi subtitle file convert to srt subtitle file

## How to use
```
docker run --rm -v <dir_to_convert>:/videos creatorkoo/smi2srt

# Example
# docker run --rm -v $(pwd)/sample:/videos creatorkoo/smi2srt
```

## Result

* Recursive file searching
* Convert smi file to srt file
* Each file backup to each 'smi_backup' sub-directory

## Docker Hub
https://hub.docker.com/r/creatorkoo/smi2srt/
