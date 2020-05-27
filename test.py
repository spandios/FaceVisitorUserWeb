import datetime

import pandas as pd

countDf = pd.DataFrame(data={"user_name": [], "count": [], "timestamp": []})
newCount = pd.DataFrame(data={"user_name": ["test"], "count": [1],
                              "timestamp": [datetime.datetime.now()]})
countDf.append(newCount)
countDf = countDf.reset_index(drop=True)
