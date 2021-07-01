# wechaty-puppet-service [![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/) 

[![Powered by Wechaty](https://img.shields.io/badge/Powered%20By-Wechaty-brightgreen.svg)](https://github.com/wechaty/wechaty)

![Service](https://wechaty.github.io/wechaty-puppet-service/images/hostie.png)

Python Service Puppet for Wechaty

## Features


## Usage

```python
import asyncio
from wechaty import Wechaty
from python_wechaty_puppet_itchat import PuppetService

bot = Wechaty(PuppetService())
bot.on('message', lambda x: print(x))

asyncio.run(bot.start())
```

## History

### v0.0.1 (July 1, 2021)

1. Init Code

## Authors

- [@Lyle](https://github.com/lyleshaw) - Lyle Shaw (肖良玉)
- [@wj-Mcat](https://github.com/wj-Mcat) - Jingjing WU (吴京京)

## Copyright & License

* Code & Docs © 2020-now Huan LI \<zixia@zixia.net\>
* Code released under the Apache-2.0 License
* Docs released under Creative Commons
