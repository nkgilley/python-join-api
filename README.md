# python-join
Python API for Join by Joao

### Actions
Join actions should be provided as a dictionary. Each keys is an action name, and each value is a list of the custome inputs.  Use `None` for no custom input.  For example:
```json
{"Netflix":None, "Tweet": ["test tweet!"]}
```

### To use the listener:

``` python 
import pyjoin

def callback(data):
    print(data)

api_key = "<JOIN_API_KEY>"
l = pyjoin.Listener(name="server-test",port=5050, api_key=api_key)
l.add_callback(callback)
l.run()

```

#### Output:

``` python
{u'json': u'{"push":{"location":false,"fromTasker":false,"toTasker":false,"find":false,"id":"89a694e8-d71b-440e-ad26-0a7034c4b972","deviceId":"0d2aa1c3c16b4e9e9251c2301f37641c","text":"hello"}}', u'type': u'GCMPush'}
```
