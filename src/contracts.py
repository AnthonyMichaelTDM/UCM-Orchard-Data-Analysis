from datetime import datetime
from typing import Any, Callable, Optional

from configurations import SampleDetails
from sample import Sample


SampleFactoryContract = Callable[[dict[str, Any], SampleDetails], Sample]

FilenameGeneratorContract = Callable[[datetime, Optional[int]], str]

