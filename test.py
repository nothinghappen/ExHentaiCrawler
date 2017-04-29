from excrawler import Crawler
import re
from database.db import db 
from utils.log import error
import time
from config.configHelper import setConfig

setConfig("app","lastpage","19829")