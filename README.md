# RevShell
This is a simple reverse shell handler, which makes a listener (default on 0.0.0.0:4444) and listens for a reverse shell connection 
Then it tries to stabalise it currently with python, more options to be added later

## Usage
- `-l` : listen address
- `-p` : listen port
- `ctrl + ]` : To exit the script after a connection is made as ctrl + c is sent to the target as well  
## Example
```
python3 ./main -l 127.0.0.1 -p 8888
```
