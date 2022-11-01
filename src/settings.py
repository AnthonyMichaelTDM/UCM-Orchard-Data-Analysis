import argparse
from datetime import datetime
import configurations


class Settings:
    def __init__(self, options: argparse.Namespace) -> None:
        self.startdate: datetime = options.startdate
        self.enddate: datetime = options.enddate
        self.configs: configurations.ConfigList = configurations.Configurations.CONFS[options.configuration_key]
    
    ...