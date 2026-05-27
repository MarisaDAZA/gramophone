from logging import getLogger, FileHandler, Formatter
from .配置 import 日志等级

日志 = getLogger(__name__)
日志.setLevel(日志等级)
文件处理器 = FileHandler('留声机.log')
文件处理器.setLevel(日志等级)
日志格式 = Formatter("%(asctime)s - %(message)s")
文件处理器.setFormatter(日志格式)
日志.addHandler(文件处理器)