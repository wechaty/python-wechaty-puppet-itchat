# wechaty-puppet-itchat [![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/) 

[![Powered by Wechaty](https://img.shields.io/badge/Powered%20By-Wechaty-brightgreen.svg)](https://github.com/wechaty/wechaty)

![Service](https://wechaty.github.io/wechaty-puppet-service/images/hostie.png)

Python Puppet for Wechaty

## Features


## Usage

```python
import asyncio
from wechaty import Wechaty
from wechaty_puppet_itchat import PuppetItChat

bot = Wechaty(PuppetItChat())
bot.on('message', lambda x: print(x))

asyncio.run(bot.start())
```

## History

### v0.0.2 (September 18, 2021)

1. Fix Bugs
2. Add Receive Message

### v0.0.1 (September 10, 2021)

1. Add CI/CD
2. Add Scan/Login
3. Add Send Message

### v0.0.0 (July 1, 2021)

1. Init Code

## Authors

- [@Lyle](https://github.com/lyleshaw) - Lyle Shaw (肖良玉)
- [@wj-Mcat](https://github.com/wj-Mcat) - Jingjing WU (吴京京)

## Copyright & License

* Code & Docs © 2020-now Huan LI \<zixia@zixia.net\>
* Code released under the Apache-2.0 License
* Docs released under Creative Commons
