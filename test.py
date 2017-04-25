from utils.cache import cache

c = cache(2)
c.put("haha","heheheheheh")
c.put("h","heheheheheh")
c.put("hhehe","heheheheheh")
c.put("123","heheheheheh")
c.put("321","heheheheheh")
c.put("hhe22123123he","heheheheheh")



print(c.get("h"))
print(c.get("hhehe"))
print(c.get("haha"))



