#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request

base_url = os.environ.get('BASE_URL', 'http://127.0.0.1:8787').rstrip('/')
bbox = os.environ.get('BBOX', '-87.8,18.0,-73.0,32.5')
url = f'{base_url}/gfs/api/providers/rtofs?{urllib.parse.urlencode({"bbox": bbox})}'
with urllib.request.urlopen(url, timeout=10) as response:
    data = json.load(response)
if not data.get('ok'):
    raise SystemExit('RTOFS provider response was not ok')
frame = data.get('frame', {})
for key in ['sst_c', 'current_u', 'current_v', 'bait_score']:
    if key not in frame.get('channels', {}):
        raise SystemExit(f'missing ocean channel: {key}')
print(json.dumps({'ok': True, 'provider': data.get('status', {}).get('provider'), 'degraded': data.get('status', {}).get('degraded'), 'depth_levels': frame.get('depth_levels')}))
