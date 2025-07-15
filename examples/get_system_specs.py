from statz import stats # import the statz module
import platform # import platform module to check os for cross-compatibility

specs = stats.get_system_specs() # get the system specs

# print them
print(specs)

print("-----------------------------------------")

# get platform
os = platform.system()

# sort them and print them after checking OS
if os == "Darwin" or os == "Linux":
    os_specs = specs[0]
    cpu_specs = specs[1]
    mem_specs = specs[2]
    disk_specs = specs[3]

    print(os_specs)
    print("-----------------------------------------")

    print(cpu_specs)
    print("-----------------------------------------")

    print(mem_specs)
    print("-----------------------------------------")

    print(disk_specs)
    print("-----------------------------------------")

elif os == "Windows":
    cpu_specs = specs[0]
    gpu_specs = specs[1]
    ram_specs = specs[2]
    storage_specs = specs[3]
    network_specs = specs[4]
    battery_specs = specs[5]

    print(cpu_specs)
    print("-----------------------------------------")

    print(gpu_specs)
    print("-----------------------------------------")

    print(ram_specs)
    print("-----------------------------------------")

    print(storage_specs)
    print("-----------------------------------------")

    print(network_specs)
    print("-----------------------------------------")

    print(battery_specs)
    print("-----------------------------------------")
else:
    raise OSError("Unsupported OS")

print(stats.get_system_temps())