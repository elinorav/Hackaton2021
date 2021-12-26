

host = '192.168.1.96'
port = 5005
ip_start = host[:host.rfind('.')+1]

ip_range_list = ['{}{}'.format(ip_start,x) for x in range(0,256)]



ip_range_list.append('25.45.173.121')

# ip_list = list(filter(None, [re.findall('{}\d+'.format(ip_start), i) for i in os.popen('nmap -sP {}1-255'.format(ip_start))]))
# ip_list = [item for sublist in ip_list for item in sublist]