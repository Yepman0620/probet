

def dict_value_to_list(dict):
  keys=dict.keys()
  results=[dict[key] for key in keys]
  return results


def dict_key_to_list(dict):
  keys=dict.keys()
  results=[key for key in keys]
  return results

def sorted_dict(dict):
  keys = dict.keys()

  sortKeys = sorted(keys)
  ret = {}
  for k in sortKeys:
    ret[k] = dict[k]
  return ret