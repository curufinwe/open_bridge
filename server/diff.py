def calc_diff(prev, now):
  if type(prev) != type(now):
    return now

  if type(now) == dict:
    res = {}
    for k in now:
      if k not in prev:
        res[k] = now[k]
      else:
        diff = calc_diff(prev[k], now[k])
        if type(diff) != dict or len(diff) > 0:
          res[k] = diff
    for k in prev:
      if k not in now:
        res[k] = None
    return res
  else:
    return now if prev != now else {}
