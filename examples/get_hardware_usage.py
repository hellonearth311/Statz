from statz import stats # import the statz module

usage = stats.get_hardware_usage() # call the function to get usage
print(usage) # print usage

# seperate out all the usages
cpu_usage = usage[0]
ram_usage = usage[1]
disk_usage = usage[2]
network_usage = usage[3]
battery_usage = usage[4]

# print them
print("-----------------------------------------")

print(cpu_usage)
print("-----------------------------------------")

print(ram_usage)
print("-----------------------------------------")

print(disk_usage)
print("-----------------------------------------")

print(network_usage)
print("-----------------------------------------")

print(battery_usage)
print("-----------------------------------------")