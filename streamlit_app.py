"""Vika Wealth Macro Terminal - single-file Streamlit app (live free data: Yahoo, FRED, World Bank, NSE).
The code of the whole terminal is bundled below (compressed). Do not edit the blob; see GitHub source to change things."""
from __future__ import annotations

import base64, importlib.abc, importlib.util, json, linecache, sys, zlib

_BLOB = (
    "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"
    "yRhReOTIqePlOxENNnSRzt0ToanJY1h3Gc5wo3lHGpCpSlnS8TDZHasPq315ZsaHZ2pzrBLt151l6xt/UM0JhV+Bdk2ihkmo3hKr"
    "SXZ00GQQj8hRHtrJDymke3zSkqcjHqmOhflB3MJIMt4XliChusRPQ8l1iBZbLJITNAavLs8IWAL9z4Mkv86DozrxH4BpCoqoLc3s"
    "XIbJqvnHfNThPMKQL6M5cA2MQ/8wOu0TEbatcbjfRkUUShyChWAtQ5o8XDzDogrrJXkCOK3mId4oogZB6sC7HpONk+Y+wR9vXFCU"
    "ZtjeGIPGMhqYdshGTXfswCwZKEy/avTn7mSY5oYunqEqgYSUWziDAZ9gOldO4PAie8Dm2RTaZj5Df2br13o/fDw43m0csJTIF/vZ"
    "i0YVFnVXh4w2ONbhJQFcuEz8RqiMz0X29DhlepwfXRzaLmkBufJtvyfiLsS6ZOVVfrwXqXQ7+mZ9bJ5Yh5+7J9bnpvXnRwlyTiWE"
    "92YT5bLWwjl0IAYznvRQFfx4d47OibCdHzXFj2ZDvml//twSlPVTR/zY7yKeS6+OK4cicukOjuc/5zGiW9K1MTb/2VYHuzpMG49U"
    "m9FeY2/J1CQ+APB6v8Yv4amz/mlqvwJQT4VGLACM/Qlez3EnN3gln911yLyDptnE2NNpH/zROl3qioOtwCbAGAEm/jZeYlMge7Bb"
    "Lb6S16wERw+S5mbFqpQ3t0kfnzaNzcNKGYdThaNrBDzHPKAIteQodNaJHYXkc1V53G81e/tnR82OVmLv7PSPVjzexVQ6f8aG1zyf"
    "os4/TmSWe4bCydf17kSNTrPxe+KF1Pz6ZCeis4706mEwrPbqaX79FvdGvwtP9CPClTb+H3LqIWSorJjd7mnrqMuF2S6Iz0/vUhiT"
    "qQnp4rWsgcsfdrT5qEWEWeVnw0T1f83Xhrv7WX8bQcme5HMTa35kq4eCqRDtIpBsD8PKUlIdANQt8EQRgwq/9PBAwGve+Ddud6sq"
    "PVsO/UPDfClPjNg5PUX+1pmbVd89Zef9rCfDRyRNwIwRtdNZT/pkouuA/71APhq0F6BnKqx9YmqZZ2x/Av8ZOmjksoMFSlGZToqP"
    "d30R3GveHNjBZsksutbet8bRQx4uQylyjIgCHwjk9xxkNkwRVkgTCdTDZK3vBo0WjlX0wtiA/Tg2TMDv4Rxk/H8YHzvdQs4CQdkN"
    "KCnXB4+cJcvAXPxPnbm5jivsbIIpGaazeYR3+2lgd4biiqKDY5XvSCIa4bWpwYLS3KSEotbZqXRnoa0Az3z0Ykcfd0+0j/CcfNQd"
    "YZ4Ai4tn/zz5prULz9zuT2K9gq3KvKTeKDUjeN0++pyaSYLTyhhja3guZRZuPshfP97P50dpDBzeFDIIyWfOasqzvSbOdnpTFS/o"
    "CNwH4rsPsmNIWtLRzwJcg3nSewLGuH91FbRBrKAUiveZDkeFfXuEF5e4nspsnomOdCUYlKAA4QwjSJj0MQYG8m3YR8q1cjbLHxBV"
    "XrsNYSBDEAlskfopZWz9+i3eDsxnLSM9qzzesiBcfRJyTz/vwicdRUtAqIocNA8mdwW9pvGT0E5yzcJhX3j7xZ8UX34MgkatiE97"
    "8tPDjxJfAdPpz6p10qifxvF4SsleiKeyCuVTLqMbBnpdqk6XaejlXn+I4fSY7aGGACaqsmrRzo5ahycaek7X42e+Q0CyjfSZyS7W"
    "H2zBfOgYvjuBM33gS+9exY8xEBH8UtLExbMv3Xb8nn4zrlEbzMdM+oW4xN7xyUnr9OlYl7t/NdYs02PxiV7JCQrGk00QTsxSRcuc"
    "Ka483vK9V/MZtBSUFeA+3Q8n9hm7R/XVA1rBRXjrAfBGduCKKMB71m2/R9ryZReXWfWVspvQq+xs1fDOFGGR5rX6avHSHTYaunSl"
    "cfer9fmgazXbR39YX5rWx6b1Z0dVh8YmqSYbo9Dvnm0Dj54ydKVPGQmJP5LXadSp55GcpOQqEHAny0Dwy5SzndYeKiUvPP7Razc7"
    "nLG502t3hUKv1zjrHsvfJ58ap4cN+bR/uPdR/j5sdRsH8qF11Dr9+E0+4W2j7rekIF6HEw/to/3TpLn2US7tgm47Z/Jal+bBfKlc"
    "SGU3vaerlXP1ogk88EYrXg3Fu5gcJpFKYkxE5Fx2lMul4Q+oIpOOpB4v5LRE68v/qDKFHRpjIwSQKAr5jaTmB3UGW0twfbkKIUvk"
    "0E4VCouGCPag0Dv48kQli5ilfqspfIqKZet1WsUi2kxBbJkqiu7xKUzudr4yaquar4x6miIqBaBfRyHI6e3COzruEiE4bHSBU0Ia"
    "4cnLi3R75OSwbZiHozEqZZzgRlm/T53dPWCtUAPLajx+fRL4M6BnERzO7yiGKsKMnZIAzTFIDTrUTRyYepjYOlEw7nRx2SbOIA4m"
    "wy/3gEQOgD/ZME7au4LXkTiuNof3wsmKZgxsGLtM2hF3cOgEiCBDjIzzD4zqQLMh/yiM8jdJIH/oei7Z74Co7/nTKbo3Q/enu205"
    "R7Vb+mA0d9utdSNozAGZQnsinTf3G83Gz0wobcYsxlZMce4c7rf19hND5Jq2v6iX10AcaYujrXnSbndhyod+5yRuG34aTgfoyNXC"
    "vXbRpIm7pu8YDt8NoXilyrjZDW9gz7BYfGoCpdjYBWrxSm1caHHYVQwvEaKRk/34StjAyHGGoWGT0TNI9UOygsaZC4HKqHwzDk5O"
    "i4jdIfJxG/RaOkLvdhDXdv089D7y0VLvKNZb7lI9sTgEsHJghVEvjmaEknIqSrDqvOnPKXJ7zbgRpxJ5CVDYIfbApJpqgVC8wa//"
    "KZhw8hXx+6HeEIeoEAcc5dtKU3ckhWx3VdoXbzh0MN7YHPjBUCsSyFdUJtPmqe3hBQPzrLtX0KrZXs8WCp8Shk2qVXYulcQ0glMx"
    "pIAbhnMe2sWzd4aM9SAb47h9xGhdFqCpzXL5Mp7nQ25GHgoEAUBJhbxDgOLRwa5UCcDzL3ko9zfoWsHxZ3mjQC2F0oRe7osdeCJZ"
    "b17w1OX3Vqg2xdqTHS25LEJOdLaStHu5qyuGp8BbEijWhISCQB9scp0GCQU4alRNA/7OQj2n9PL7IRKI8R2RBLEUX6IUPilf1t4P"
    "8YWfN14JQd5+4ggvDcv4YrvoYDFyboWgyAnJAwd2bngVh7ZSPELvZhgStm6QTTGOvQes+kSwaPCraLzspWNg0iUxJeIeItV5vGcv"
    "CxqmiYoosecEWeT/RHPS8Ubxry9ysixDyRalFBuqxZpxsSXt6yHbKKbav+KYaiO6NmbcD9FDjSYwXp/YNLk8N07cOm5S1+TCYCBj"
    "AFLkaYpIjJBPp3JVA8wplTBwID4b/5HOs636gKIDMaxkNsw8xY1R3ectuvqURKrJySYGk1Du1yU4LIJBoRrW4bsdOEyd8Gqdab6r"
    "30rPp6XnQ8rdoveeS5UTdyOYmjkkGoqzhLr0J4nUnEyBdhahR010sLRVpHDi4tZhu9NpH31kUiPaTtqFoiALtpKvH9AfUXwCtO58"
    "SlL7AOB0Guo8noSKph5DRcWAMlN7BAlN5pomopro9bpobC8VvdKiCXkxwdSdwGY5RCO38IHPcBw0dOBPhmjCA54U4UjIaErpTQQd"
    "Q8aG9whLIsBTUa3CUiwRt/NuNOKrIE6a+goc0UivFGG249gPa4SyfbxsQyeDgxHyEB3xVl7sPbd0tBp8NFlES4DaxLs6SDOFSkFw"
    "SQlDBJzazGZRVHr9o6LncjnWk1+dfjZqfqr4fyeNjy2RzYSD/XDWbFTMXzxTrkEjTxNTI6IKdIOK7rwQWw6CDLvLoVlUcZbj4Cms"
    "q0GKwWNRx0zY0mX1MXN6D3mBq4BgrotaRcyAPQCRJ6R0Ot1bvAcyxNhegys/dDz9vkQNy7w0Xr7cd0FeefnSAPKJyacw+Oh71Cd+"
    "oMCjJuYnaH9u9PC2Zu/s9ED5CDTtDuQojOpL96jmKE6bt4EbRdBbf2H892wRXaHJY2oos+E8ov+NSX+w/wMg+9g99J9ENuVLWmNo"
    "3cGgvprXJA4f3t1eQSdYDug3XWmRvAtmDkN+gNvA5BtcCy+TZrAFY507U/TixhOMmYorQD/YqklAYQw1iR64uHgYA6wDuE9AOWj/"
    "0aqXSUHihiQwJDfUgPmjdTjwMV4j5wem62O36MNZM+IYpZTnzBEpxLDKj0QOo3w28sEP458c/B0Z0fgNHFJxjqJYHJetg4BjA8Qw"
    "drUoJON0xyXEM4eS/07HKRXEDTpx+7LcCTyuCG12enzcha2HpUyYJCBhr4dZK0N/gmF5rZlNuZP4z4VHl4VFcT+0HO/GDXxPyAYJ"
    "gjbbZP+nxjc4SrbN7ANnSlxRFQrEiTKtgF3QLp5tEBPZ7WLlt+VyHq35LeFC0bDjbASAUBFdMhzy9ULcGIAIgCw9bmlHhK7Nb0S5"
    "5ahUP211T7/1Gvvd1im0sKmP5TfBzQO+pmuLu42jiM4ieDXxERtahyfdb+nLQQpJVkLo6pmplfx2F16PtpUa6zyaA6t+TvFsi8Ap"
    "/QX4hTdH4fGSE3jQaK+dBcYaNIl9E6hPYX2hVQwCfx1qbUoktg7gEzajoKmpfy0gpD62OwAsrYnFzJEJRHqHrcMek121COWijHOM"
    "sKwvaZCJRI+yQgE1ncDgsD0p/sv+zrEQtjCYhEo0a8rL6ixk6SvyMWbAWfJbfJcWvxLxwlTCxE8iXwtvz0HcfU8/qpfZyIr4vqKH"
    "OGZGNx7FbE49EawZ0qIVHsk5fMOhm0rHStmkITVaM9QRMBl5VK7GKw3tSGQvUoDhmtH3iVnMifF7OvegOkxTxiAmVRA5P0UTQ6xu"
    "CVNVFd6xiMgRgJm0MwslsTz04UugxWG9ocCfvQyg8X1+DhQBP8w4xdFKAauwCUJLglMqzvDg2rIHf8/dwOGU8ICKdZx1TgRM2nXi"
    "fpy2ez06+wSm48DsCf5axGcJ7V1AV586/XvuzB3gFq8oyWkklANaWo7cia+dfB4A8lN+cPsjLVn4E/NocBO6RJaMjlYZYyBf2aEd"
    "RYFJ2JgkZKJ9Au/4tnkhd3gavFNNk1igTZK2g75RFKpb0GN411bW402zDKKY04N5sDgSDGKR0AurQekxq0TAW9TUd6xFn9SyPdI9"
    "AmOWUKtlAZBRyuYg8HDsPWywARl5Ohah8LAk8NCxu2HENmYukoduMoxLPAaSmOH4Dh1K9UGHikiXqmXmVIKpZ1Jb61ksV2avjqPl"
    "Sj/2cN4PnaiezciaQdKVuzQBL6XyWQtZEZ4dmWq2imAOiuRM1oNE4zFIywAAqzGEH0m3UttWlNYQQAFOCjmBLuuhdQkx43lqgd5x"
    "mki8a1qFfD4Kib4Iyor7k9Q4ZTX6MOVd8AM+PdaCklAqhroeeHg4ivMOpMaLbzFausgmFTMDOaiiTSmVhgD/xkuSZCLQz3pTSyVR"
    "UK3apNxSuIaYnxLP1L5+LC5PNnEM5EpqDJBDxH1UIu2TMxRHrlBOiIDxSdasVFRyCVJtFVhNhTgqAt5nQA7bKh3TIwkSnpvJIM4E"
    "tSwlg3y+/LekYtCWNtQTM6gpPzxkHDNYLlN8wBnLGb5tb5FirMMI7+QFcw+1/JTK7AqtjINrDEHkDTWoi2FAI+bE4gAlQq9KSlLK"
    "lMDsRWILVkappVZATou0y2h8ZutrwnVtbVvlXO4Ka3CPKMtyFDU014pW3xGXFnNg/y1b/m8D5eAosMfjCYa5xvVYPmcd1Z6cBZdZ"
    "RT3OGyeRoOhMGtOVDsLGEJb0HSrmZNHDCA9v1HhPsUcCdGueY/yBeX8KPwnEahB6iheXpE6T0InPEyu8mkeY7c3EpkQii2wyD9pT"
    "j1y3L3YwjdN7EOax3Sa1bGy5Ia4zTHJ6oIQnNY/qWrKEqaOmilsqYWB5yMJVhIODSRkak5TJx8TOVqk5xiiraeRcn9mhE6Di2WOv"
    "ElXZhNO5ZWvpreu9k0FQcLddw1GtjRsZE2t6PXQDk1UEMr8dqaR6/rVMQcR+INEVQHkVM0Px+aMrizVaWvB6vF2gszZY8lG8DdcT"
    "KbDO6TLCcHSZnwUrriFYGJUiLpPHL7MkEmmgICJLa8W9JcPOpmVTv1Ia2XwLR5zCAOomsOGZyY2gMK0zf2am+B3Ol/nLnF+EGhU2"
    "wdgwhW7vVRKnBjU0BZlnCrVO0lYvs5/W8rhb5onTKfHS2blzhKh0wmbmt7lP6y/hrRhnHi4XRArhzDGLr4nXCE1T4LF0DRDNFBg/"
    "KbVD4dGsrq7sUFwXUuAYhZIbTTwSlAhgYQ5PylU0GKc4UtW5YRTm8KX3L1/i+5cvFZWNMmBUNceNKwTo5cvrOIZfwG55+Ap3gPRJ"
    "qMV6TDIeSlWmNY8GBcsNfVbY0vtw5gwwmzJTz+RitjKmWPMDvSXog8IvpqYDikLnZUjueSVnNEK0MZFcY9puyueD8sIihIPGmNoL"
    "NAOR1gMFCAVoTyJ6RPgSqpfCllWSPYVLUhBuloNZa7ArbkbNOxlGWTjRKC1eSOqA+h3Op7PQxKCmSEi8qF59BEZzJs607YSSX6y1"
    "nTghkGQj8q8dL6wZuxPfn/bhnCoB2zhBm0JwbUQyK0iEt4uGbDL7Azoyvjj2BH7P5sEMCr+ii3HxYXXh7X4kF+ffyo3y60oV3500"
    "jloH/LJSKe9V9uOXvU/NU/Fht1LeIuFp9/i02RJvq7tVutt+4X08bTdFyVbl9SYleem2vnb5Xetta3v/Nb6jCEH88s3+m51drowX"
    "jundfnX3TXUbpH6piaIZ0Q1yc0gR9Nxogj6BHvvHi5Z2t/f2d0St34x+gIY1BzNBUnUBCXIcQND1xxdes9U64cqbu5XGmz2lS+qH"
    "07GLqhfemShcbTa3GjRmtPCKMW9t7m+TVRiviIhG3+w29wkIeGNNlntd3d3Bd+y8L97uvq1u7vHSdFqYGwvdGPg6gLwDgO3CE919"
    "OzspGlwf6cdvjc3WzuY2H6e/td68frv/lvyZD4+PjqmD9u6hcTIBJvTQ9/yi0dnHv6VTZzyfYHahQ8eb+JRoxQ9nNmfj7jSOOnrd"
    "jo2GxjZeYwPRkQhDae7CT3hfwkN9xBPAdMfAAY4pANzAFkAX3r5oNRV+tDUkhEOk6Z5jB6X+BGPHimWCl+PAcaC1Jsjvpx/bR4iw"
    "5+d0N+633a3q5uY+sRrnZWtzm15uNyqNzU35kt8Bwm4l73bEy+pWY2uLX1b4zf7u/htsjzzqCK693bNu9/iok7inkl6fXOcxAQA5"
    "Y9RlBhgMLVcX3tzyGe2c8A5FkVtyW5J2YaWhzaShzZ9qaCdpaOenGlKn9k1piBKd/eDMfqwdUcHmeIWyscbBQcb5EV2aexN7AeyK"
    "Ke3pZYqiOwZZWhxHUxsxUkQGokC7oTMh+y0fUCneAppDthcHklBz0Tj/KapUHoPq9sfk+QGDDMZ92ywX6f842OPEj1Z8VyP7Auyo"
    "15E9dSeLOm5h9EX67gAnhljNbXC2AqWimB7/4Ryf0MikvgXSZVDfqQJDV68ClvQBNGq9K3QcEQtxh9drRm7KdYJKMPipTTmN+GyA"
    "Rv0A6CS/5pOhuHomFTkPPB0K6njEmlFFH+QEj83KMDpC4ztE0EW9YsHyLmxvcEXw7PtR5JOfxl38jsg/MXHxQAQUtb6X+GqsWEuS"
    "vN3vaFBBpa8HLIwX6RG0wiv/VkyE/yjf7igfHY1nHLhD7gYPTlS/eY4OxO9O4ONbGbALGw5n7rUjmSx6UFAifzpUKrpyB9ce5mCv"
    "iHroUglzGPoEJ3olMAG5lDBkMWBwnYGgtmKLx0woB46ZubnUtVy33Inkj6YovEhoB6QDqPThtT2rl63qG8rpSdG4+U15R5RLhAaN"
    "MKimEBujtdHawTFxTjx7UpBlVd4dc0BFL6xrhwjibXkV3j7xHusK7KSIiALoyN7kbs6ndkct3LrD6Ipy3+gL8Fbfy5qsBGDLcr9z"
    "dx3rGye3w0TZFIcMeYm+sMGTAxhwIp9P2obI4ca5v/FUWaC7ATmKhT+W7g4Pk52t+NH1UNSKfsCdRLwM47nYqKDNZtBbnQkvyY34"
    "Aw4qjU6n1UUWhv2/QNgVlpHW4W6r2Ww1e1wCDSPA8+INYIeib4iE5airnzgl7IeXAbjb/Y/snIYB32F5J/7YR8lVbOL4/SEQkl07"
    "YDc/OkJUNEfGhL7v8nbp+qdAem7IX5N8mcPQrwr9EG8y+YQ7vYNMJb64BEGOHBt7zcY34TTXxDbeiMvJ8KssEijVjCrngiCPuu1y"
    "WZHZMbgTKUNHXkG3Kd1j6N8hslA1klap2MWzB6QV8SfSxzKeWCiz2Yhn2BYuBAiXkSPT9kJzc+BVMGGqDaQv6MWNI9lSRnQVTSeY"
    "DBMtUfGFDgvvoJBKN1RuLFxceLGPEF6QRa+EHnBN/m0PW5Hit2zZ9dD9pTcIE4Ui/AbYMSpgJLwwFJHsBP7Q0M3YfwkWx4kwhwE+"
    "SAnUolqavic7bBAQ3tMW/XAPxR/eb/ADxbRaN25EtN48cM1UQtB4mFk9UjwjWTeO3YeutksmhGWtENOViMn0F6jtTKf9xD1ac6f2"
    "2NmAwq/uppN3TDmK0M4rQUWs/s6W4w0A1c1+wQKREn/9yht1TAoFEnPsbZPVq3Jth3TLJ8xksiWdvTDfYTptzaObssuSA7fuvoPV"
    "hyFZ5oah6roeWxXIN5fEcwwoMOYL23WO4MXGAvGQhB6VZsg6OvdQGFsuce0siFsvxBw5hRavpyeamGC5QFbpBzvQJhcpkmc91vGL"
    "4Jp43SEKSh5O41lurO5Vvv3cJTv1qzolm9KdsLt6QqBY3xpg+j4tLC2Oj03uYgqY1Peef6uxezFz7wjvJnFqFXbpNu+hmwf0s+a0"
    "6Nh1ks1XuVUgpo+zpVI5FfCbfy3hQMok2L4xtTKZEeCdqUCIiNXoxXsQ+6Eb2E2wgrPS1RBI/of3cIB5ylvCDXh/Tz+QBMD3TCkO"
    "yvPhHv/GZTag/Q8vCiqcLRSsJoseBZE3CeHoOBViHt8fqcOZxeiErg2A+3j5ZFATI0AcePkyPgFSbaqqxfxpAsyMewDuQ2ayxFd/"
    "wHTHg5E6zw/3vBMe5ELeIwLIab5IMWfQYQo4uEcQOPg3Cxy5FVVnebEh0zYw41/i2gb2L3adGse5wL78MSyHelxdfkguSKmb9f8C"
    "3FGBmsUd8h9QPbpyvAmWjU84e324j+fOl/6S/EHiPhvnD7EBk9ANOz9n0EN2bGnjMeP6gm4pIX9rYsIlZaGSn7xg8L9ikjFJxWBo"
    "ghcPB4y25030+jWl88orTIT1ytgsGsktDLHRkGRyzAoYA6AACGuKqTDGiSveaLDDANmW7rC4Mc09Rc5NR9LHoKREKI9SC5wP8nKv"
    "kzV1aNkz10K3CzgRQ+nS1SMvETQuDi6TC5kLNnvSsCxheknCklf1sOTQ0gNsJxMGh6C9f8CzzO4FpMIqxYR4alMUF2DIATnRfZCA"
    "CdywPYttjpS4PFrgFbDJAj/I8y2BQy2NF9yuueaqkwv8PGorgG28KRqm60kv6ILwW4TTqrxENlx1uWl9u+8NNauZIdzgyJEimZWk"
    "tXF2q5FHAXYp3xoDVd5hzADAfAJACzGcsIv6yKuhNwpek5LuedD7ZcpbBzZ8jKkipregqn1/uPj/guwR2dAa8Eo4FiyJfx/0M+GX"
    "8Jsocr8S0rbgOgdXY8z1hfJcwqmhlWwWOHgZM4zTCBbj31WdrZQZ+ahGkoyPHMagWb46R9FfhS8YFi9R8WRRkhi97Eij+Xewaw52"
    "RFcomXOkSBm46KMRpuTGrs5fQDcv/vXC7ocvYLzzWW/s+8hbJU4eEXlR6pdMZbM5LcaN5KZpJPjIGMdZPpxmu8qZTU3kiBmdquls"
    "DjhYeZk0hW4AMEQ27VUJZoL4QxN6yEGx6xK6ZRJXU65sCQxboU5K91kCdDGmc7qe90Fw4qKb3GMQN5LrzdXbsdBAXUe75CMBGqgB"
    "FvpQN8oFxB2xAFlWGHN9IvhMqkbpfKDef1A9Qa2GHheRH+R7MQVFSgg44x+8A4avX02qfVBoH34aJJ/e65/sstqiCPxOQdiWbgX4"
    "O5tplvN/14rfJxsZjr97QPSH0cM9o/rDakTIRQLJM98T5B6Me9hzuG6FGp6tkvN/UrOkK0saTlRnsDke8rAsjwoDkEKsjTueoz0Q"
    "SAsPOSw20cEfozqMuE+jK4QBOWRE0g3JyhI5iMnKU+lCdJ1GkslKBLlJkQPt4+DnNrtOIB9JBNLbO7UJ1S39/n91R/9qqOduySft"
    "mcG6bfgo6vPovSUYh0fuLn/Wt5GhQw8h2sbSS90Zxrfe/MG1piTN7ZUaSoO3H9iYnuPDe3c6xqsn8Oo+0TECSDZSjFi/AqXxSoHx"
    "BWPQfcqR19OyOiLNh8PG3umx0W2dHraPGgfLuTdh+Ertnyt3lmEJUUl/D/+QymHpKAA9EtCt4BoJiLgm9ENby+yiUHwCbAm2HRrR"
    "Lp6FU870Vkvxy1LuUkvD/wpoD0KDECtdyRI0CPHvs/8jTB7zYGK+uIqiWVjb2EBjU2jBAT2eOCC7hdDsdAMqVP9TmJXbu4ev0D3l"
    "Fbq01G4Bhv9nq1x+tw3/2ymX/5EuhU4smVLvXkNJYbioh7f27EXhHc64Fvh+dI8TK5X645rwlnoHT6RXqQlPKXwBrHtN+EfhI7P9"
    "NeEbhW/QNloTflHvuEnCaeEWhUWIBNWESxTV8SfwzO5Q1Cs5x9SEqxO+GTrOrCa8l0Src3jBHkpUwKsJ3yTqAWH0QvMGelGcu6XY"
    "86fIrkDxM1ZC/x6lEkLwRTHx/0ncf2AAZMLYeGlorq9wPBqJSW9wFfgo1o99wxmOHbyoTn9fblx453hElFDv6Q4Rt6JP5IGFvjqZ"
    "T13fn9C+zvnWxPg+Mh5D8bdDkMVgYvPiCNbTCe7FUtdQ6/sfjHW2F8HYQdpvzGb3yfWBGiaytCewevDX8SKzUi2XZ3doP4J/7ch4"
    "s/3cKFXKz4sGmWLfVopbm8VqZatoVd6ARBkBlQnZHGfslJ/T9dXARGxCj02LTJqlWFosQv841l18vSff3s/sIRpAa2WjUoVeN3dm"
    "d8mo303tuxKZkWogMz3XppOBy6GwxMRto6Fnds+m81o5r0pr4mAUM7XGyvLZ8WMf6FuD6oVM8T+cgII/7DIVuixmofL4yvdAYGrW"
    "9nbgTPOG9skP3O/Yal4FDXC1WunW6V+7USkcYAxOwLN7hvGb2d071nXhz4ecgqXoaj7tqzgklpxIQuEd/y0hQs3D2hY0kt0zcGSh"
    "rwKG651MjP7EcYYF2iAWH2YxBo9gR76zJ+7YKzFXiLn5nOAdzquCY1VwZycZ+hb+lqsI+AtoJcfFPgm1CiBa6E/coaGPHmmMMjV0"
    "4IApx9vjbXnojIu/Vbcq5Z2GAdviNyB/u5tvjM03z4sx6qN0/5w3AJ7Cj5sNbLh3t1fwvkSUCTbvbWDP4kYMOMfvxfSqOD3ZKGFT"
    "UszqV+5ZicXDQRpbeIfHTInPCvEeyZp4f8utwiHxbuJEMCAaAULVqladKRdCX4hapWpt04LGnVW1zojC5/WGBLegNlTGhjLdVXag"
    "O7GkpYkzihgsYun4Rf7C4ZiIwxCblwujNf3do6CPEH3EsKH3d9kJY+fIyTxqoXcUrN2EybyNJ7gUKfUttYkVFAqOdLlaLlaqxa3t"
    "ovWaRgPck9jQr5Nd8ToBpWhqu/z8XWYji0WUc3E93ASlGM2gacu/zu7/+QwHelcKr2wgwbDtygZM1Yg/PlDNWzvwsnUZSZfWps9c"
    "3wmCbPWht6IyfKT1wfFryIrsSSGDguUdIq4ZikWsvTjsc8gWfdbX/4fojzK338rN8tvK23foXIIxj0p3hM84mej6HruoVQw8M1U6"
    "CLvKULujPZHpDZm15dt0CttHnLjYNndoWJP7ZCO8pe2bs/Uz4HwDOxohXSJWAe0MtTkq8wd26MiWb5SWK1tyJwqyhPxrzrIhTgq8"
    "rljVbdnU4D5NZPDLfKatPGHj0NPeIZpYNIn73A2eRgg8vuFEDPP5ui8usHzRgYhZCCzIElgrfE4KuMqXDJXcAphmB5luK4FfHrPQ"
    "ccbI9zjDPZ4IDpOd+wS7iS4ecPajmEevS+RZmBR70pSQcK6Ykdh06Y7ZNSrmrzIDi+wxMjlPG4jAiSVtZWgLCD5qS5mjVeOr0kiC"
    "9gRWfBGVQN1bTCNwD77Df2BVpjP0higJkbIWODPHjkzc7aWRGxVhQ6JrCrAas7tiZRQUCnSSiL0JrWaHTQJc4ZEHCzBdtWqqCEpe"
    "hZisvEaygq2sOCdpLKhv/RE6USEEsEgbq27htz9CDbilwdU4lxgIRar6bTPLi5QqMQsp4fPOx2/Roma9zeHUYjpdu3KHQydPVGR3"
    "pnyKofH6u7QuXwKbc4dcLltfBTFXr3SmoOQAysqXmJdeLWStHOkjhZhf28UJebTsoUMLdiDngSgNp4lR/gVdxPZ6tQNkMsQmJOOm"
    "fv7/NYfaowUJekBpa4Qspb4T3TqOp3GHSIUQhd+pDROv+ShxJCFURWYGXxcrO8UdlNG3C4XHMR48B7LA/qD4gDszTWezhP71GnaA"
    "/Vt+VKiQazGKUmuBOIfsbw5PLmG+JUncdsI94cZ/Gu+0nvTFIzSsoR8pVAgxyWL3p4wQg5XYe41rZbiZ2O0t+11wz3EJ8fG3wVt7"
    "c9vmD6gpytYUrDO5ASW7Co8AWkICpgTjj61YlVeMLftxF6QGIkYw7+TQaP32dkY8XYqtqhi5mV5VAhIujT12SqhHS0azxXTk3c8g"
    "5bOiEbvpojJ4uX/tyaej6p+L3a3+l7v54HvZtT+dlgdN/+Zgc7g5XGxvHi62bwbTwc3hX43bw72334fTgdv+9Ofsz6/Dvf7m+G37"
    "r8b4cK9RPaL/tV/tuY3xyad/Tr5t/j4eVifXw49Y5lu57e76f36ZePan3+Xz1P5yF5502n8dXp/dnv51tdt232j1nWbZPexif9dQ"
    "5xDrbNpfTss2vW+57Y9XE/vL0B/S8zd4/nPW/3j7tu0e7R5+328dllvuwfetz+29xpvB9I+/hnu7W9Df98NFe+x0sc7v0PZw9uen"
    "Ux/e3x122mP74x+zP6tXZSx35LbHf04nYR/ab3/f3z8+O6v83mnfnIz9cbt5t/jzy1G5/Qnn11rA2LahTuUI2kjm/futPu+2OsaP"
    "h9ftrcO/zmiMJwzbV3vjev3Zw8P/C1UbLvA="
)


class _Loader(importlib.abc.Loader):
    def __init__(self, data):
        self.d = data

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        m = self.d["mods"][module.__spec__.name]
        if module.__spec__.name == "vika_macro.ui":
            module.EMBEDDED_ASSETS = self.d["assets"]
        fn = "<vika:" + module.__spec__.name + ">"
        module.__file__ = __import__("os").path.join(__import__("os").getcwd(), "vika_macro", module.__spec__.name.split(".")[-1] + ".py")
        linecache.cache[fn] = (len(m["src"]), None, m["src"].splitlines(True), fn)
        exec(compile(m["src"], fn, "exec"), module.__dict__)


class _Finder(importlib.abc.MetaPathFinder):
    def __init__(self, data):
        self.d = data

    def find_spec(self, name, path=None, target=None):
        m = self.d["mods"].get(name)
        if m is None:
            return None
        return importlib.util.spec_from_loader(name, _Loader(self.d), is_package=m["pkg"])


if not any(isinstance(f, _Finder) for f in sys.meta_path):
    sys.meta_path.insert(0, _Finder(json.loads(zlib.decompress(base64.b64decode(_BLOB)))))

# ------------------------------------------------------------------ app
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from vika_macro import config, st_pages, store
from vika_macro.data import fr, yf
from vika_macro.ui import cols, html, inject_css, ticker_strip, topbar

IST = ZoneInfo("Asia/Kolkata")

st.set_page_config(page_title="Vika Macro Terminal", page_icon="📈", layout="wide",
                   initial_sidebar_state="collapsed")
inject_css()

# ------------------------------------------------------------------ live data (cached for hours, shared by all visitors)
NAMES = list(st_pages.PAGES)
_qp = st.query_params.get("page", "INDIA").upper()
_page_now = st.session_state.get("page") or (_qp if _qp in NAMES else "INDIA")
_WARM = {"FLOWS": ["flows"], "GLOBAL": ["worldbank"], "STATUS": ["flows", "worldbank"]}
with st.spinner("Loading live market data (first visit takes up to a minute, then it is cached)..."):
    store.prefetch(["yahoo", "fred"] + _WARM.get(_page_now, []))

if store.pending():  # some sources are still downloading in the background: re-draw automatically when done
    @st.fragment(run_every=6)
    def _poll():
        if not store.pending():
            st.rerun()
        st.caption("⏳ Still downloading some data in the background - this page refreshes by itself.")
    _poll()

# ------------------------------------------------------------------ header
status = store.read_status()
n_ok = sum(v.get("status") == "OK" for v in status.values())
n_bad = sum(v.get("status") == "Error" for v in status.values())
led = "err" if n_bad else "ok" if status and n_ok == len(status) else "warn" if status else ""
ran = [v["ran_at"] for v in status.values() if v.get("ran_at")]
upd = pd.Timestamp(max(ran)).tz_convert(IST).strftime("%d-%b %H:%M IST") if ran else "never"
topbar(("LOADING DATA... " if store.pending() else "") + f"DATA {n_ok}/{len(status) or '–'} OK · updated {upd}", led, datetime.now(IST).strftime("%a %d-%b-%Y  %H:%M IST"))

ticker_strip([("NIFTY 50", yf("NIFTY50"), 0, "pct"), ("SENSEX", yf("SENSEX"), 0, "pct"),
              ("BANK NIFTY", yf("BANKNIFTY"), 0, "pct"), ("INDIA VIX", yf("INDIAVIX"), 2, "pct"),
              ("USD/INR", yf("USDINR"), 2, "pct"), ("GOLD $", yf("GOLD"), 0, "pct"), ("BRENT $", yf("BRENT"), 2, "pct"),
              ("DXY", yf("DXY"), 2, "pct"), ("S&P 500", yf("SPX"), 0, "pct"), ("US 10Y %", fr("US_10Y"), 2, "abs")])

# ------------------------------------------------------------------ navigation + controls
qp = st.query_params.get("page", "INDIA").upper()
if "page" not in st.session_state:
    st.session_state["page"] = qp if qp in NAMES else "INDIA"
page = st.segmented_control("PAGE", NAMES, key="page", label_visibility="collapsed") or "INDIA"
st.query_params["page"] = page

WINDOWS = {"1Y": 1, "3Y": 3, "5Y": 5, "MAX": 0}
ctx = dict(lookback=3, group="Market Cap", countries=["IND", "USA", "CHN"], wb_ind="NY.GDP.MKTP.KD.ZG", months=6)

if page in ("INDIA", "VALUATIONS", "GLOBAL", "SECTORS"):
    widths = {"INDIA": [2, 8], "VALUATIONS": [2, 3, 5], "GLOBAL": [2, 4, 3, 3], "SECTORS": [2, 2, 6]}[page]
    c = cols(widths)
    with c[0]:
        w = st.segmented_control("WINDOW", list(WINDOWS), default="3Y", key="win") or "3Y"
        ctx["lookback"] = WINDOWS[w]
    if page == "VALUATIONS":
        with c[1]:
            ctx["group"] = st.segmented_control("INDEX GROUP", list(config.PE_GROUPS), default="Market Cap", key="grp") or "Market Cap"
    if page == "GLOBAL":
        with c[1]:
            ctx["countries"] = st.multiselect("COUNTRIES (WORLD BANK PANELS)", list(config.WB_COUNTRIES),
                                              default=["IND", "USA", "CHN"], format_func=config.WB_COUNTRIES.get, key="cty")
        with c[2]:
            ctx["wb_ind"] = st.selectbox("WORLD BANK INDICATOR", list(config.WB_INDICATORS),
                                         format_func=lambda k: config.WB_INDICATORS[k][0], key="wbi")
    if page == "SECTORS":
        with c[1]:
            ctx["months"] = st.segmented_control("MONTHS", [3, 6, 9, 12], default=6, key="mon") or 6

# ------------------------------------------------------------------ page
try:
    st_pages.PAGES[page](ctx)
except Exception as e:  # a bad series must never blank the terminal
    st.error(f"Page error: {type(e).__name__}: {e}")

html('<div class="page-foot">Sources: Yahoo Finance · FRED · World Bank · NSE. Free public data, may be delayed; '
     'for research use only.</div>')
