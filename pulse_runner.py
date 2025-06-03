--- a/pulse_runner.py
+++ b/pulse_runner.py
@@ -1,7 +1,7 @@
 import os
 import json
 from fetch import detect, fetch_rows
 from generate import craft
-from post_to_twitter_v2 import tweet_v2 as tweet  # previous v2+fallback
+from post_to_twitter_v2 import tweet_v2 as tweet     # now purely OAuth1/text-only

 def run_once():
     # 1) Fetch raw rows from Dune
     rows = fetch_rows()
@@ -17,7 +17,7 @@ def run_once():
         print(f"\n── Crafting tweet #{idx} for token {event['token']} ──")
         copy = craft(event)

-        text       = copy["tweet"]
-        image_file = copy["image_file"]
+        text = copy["tweet"]
+        image_file = copy["image_file"]  # still passed, but ignored by tweet_v2()

         # 5) Post the tweet (text-only under Essential) via OAuth1/v1.1
         try:
