def checkSum(content):
        content_hex = content.encode('hex')
        n = 4
        words = [content_hex[i:i+n] for i in range(0, len(content_hex), n)]

        hex_sum_32 = 0
        for w in words:
                hex_sum_32 = hex_sum_32 + int(w, 16)

		hex_sum_str = '{0:08X}'.format(hex_sum_32)

		ab = int(hex_sum_str[:4], 16)
		cd = int(hex_sum_str[4:], 16)

		hex_sum_16 = ab + cd
		complement = (~hex_sum_16 & 0xFFFF)

        return complement


print checkSum('Carol')
#43 61 72 6f 6c