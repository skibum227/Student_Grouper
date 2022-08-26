#docker run -d -p 6379:6379 --name redis redis
#docker start <container hash>
#docker exec -it redis redis-cli

import redis
import json
import pandas as pd

df = pd.read_csv('roster_test.csv', header=None)
test = json.dumps(df.iloc[:,0].tolist())

def main():
    r = redis.StrictRedis(host='127.0.0.1',
            port='6379',
            db=0,
            charset="utf-8",
            decode_responses=True
        )
    r['roster'] = test
    print(r.get('roster'))
    #r['name'] = 'bob' 
    #r.set('name', 'Bob')
    #print(r.get('name'))
    #print(r.exists('name'))
    #print(r.exists('age'))

if __name__ == '__main__':
    main()
